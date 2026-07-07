# -*- coding: utf-8 -*-
"""
anexar_autos.py — MOTOR DE AUTOS (Onda 5/F6; blueprint secao 13).
Comando "anexar autos do caso X": o PDF dos autos entra UMA vez, barato,
e vira indice + plano de leitura com orcamento. Sessoes futuras leem a
FICHA (CASO.yaml + _views/AUTOS_INDICE.md), jamais o PDF de novo.

Piramide de leitura (aprovada no blueprint):
  ler_integral -> pecas das partes, decisoes, sentencas, atas
  nunca_ler    -> certidoes de praxe, ARs, guias/custas, termos de juntada
  sob_demanda  -> todo o resto (procuracoes, documentos, laudos)

Fluxo:
  1. LACRE: PDF + midias em 00_originais/autos_<slug>/ com SHA-256.
  2. Extracao de texto por SCRIPT (pypdf — custo zero de token).
  3. Pagina SEM camada de texto -> OCR LOCAL (Windows.Media.Ocr, pt-BR,
     nada sai da maquina); sem o motor, fica marcada "OCR pendente".
  4. FATIAMENTO por documento: marcadores "Num. ... - Pag." do PJe quando
     existirem; senao, deteccao de cabecalhos (PETICAO INICIAL, CONTESTACAO,
     SENTENCA, CERTIDAO, ...).
  5. _views/AUTOS_INDICE.md (1 linha por fatia: fls, tipo, data, classe,
     custo estimado, lido em) — gerado do bloco `autos:` do CASO.yaml.
  6. PLANO DE LEITURA COM ORCAMENTO: >100 fls = Tier B, NADA e lido antes
     do ok do advogado; <=100 fls = Tier A (D11, registrado no DIARIO).
  7. CACHE: reanexar o mesmo PDF (mesmo hash) NAO re-extrai nem rele nada.
     Fatia destilada: `--marcar-lido "1,3" --diario "#NNN"` grava a data.

Uso:
  python anexar_autos.py CLIENTE CAMINHO(pdf|pasta) [--descricao "..."]
                         [--processo "0800..."]
  python anexar_autos.py CLIENTE --marcar-lido "2,5" --diario "#052"
"""
import argparse
import io
import re
import shutil
import sys
from pathlib import Path

import soj_lib as soj

MIDIA_EXT = {".opus", ".ogg", ".mp3", ".m4a", ".wav", ".mp4", ".avi"}
MIN_CHARS_TEXTO = 25          # pagina com menos que isso = sem camada de texto
CHARS_POR_TOKEN = 3.3         # estimativa p/ portugues (orcamento de leitura)

# cabecalhos que ABREM uma fatia nova (ordem = prioridade: o mais
# especifico PRIMEIRO — "replica a contestacao" nao pode cair em
# "contestacao", nem "ata ... conclusos para sentenca" cair em "sentenca")
TIPOS = [
    (r"autua[cç][aã]o|capa\s+dos\s+autos", "capa", "nunca_ler"),
    (r"ata\s+de\s+audi[eê]ncia|termo\s+de\s+audi[eê]ncia", "ata_audiencia", "ler_integral"),
    (r"r[eé]plica|impugna[cç][aã]o\s+[aà]\s+contesta", "replica", "ler_integral"),
    (r"contesta[cç][aã]o", "contestacao", "ler_integral"),
    (r"embargos|apela[cç][aã]o|agravo|recurso", "recurso", "ler_integral"),
    (r"senten[cç]a", "sentenca", "ler_integral"),
    (r"decis[aã]o", "decisao", "ler_integral"),
    (r"despacho", "despacho", "ler_integral"),
    (r"peti[cç][aã]o\s+inicial|a[cç][aã]o\s+de\s+", "peticao_inicial", "ler_integral"),
    (r"termo\s+de\s+juntada|certid[aã]o\s+de\s+juntada", "termo_juntada", "nunca_ler"),
    (r"certid[aã]o", "certidao", "nunca_ler"),
    (r"aviso\s+de\s+recebimento|(?:^|\s)AR(?:\s|$)", "ar", "nunca_ler"),
    (r"guia\s+de\s+custas|GRU|DAJE|comprovante\s+de\s+recolhimento", "guia_custas", "nunca_ler"),
    (r"procura[cç][aã]o", "procuracao", "sob_demanda"),
    (r"laudo", "laudo", "sob_demanda"),
    (r"documento|comprovante|extrato|anexo", "documento", "sob_demanda"),
]
PJE_NUM_RE = re.compile(r"Num\.\s*(\d+)\s*-\s*P[aá]g", re.I)
DATA_RE = re.compile(r"\b(\d{2}/\d{2}/\d{4})\b")


# ------------------------------------------------------------------ OCR local
def ocr_disponivel():
    try:
        from winrt.windows.media.ocr import OcrEngine
        return OcrEngine.try_create_from_user_profile_languages() is not None
    except Exception:
        return False


def ocr_pagina(pdf_path, indice):
    """OCR 100% local (Windows.Media.Ocr) de UMA pagina renderizada."""
    import asyncio
    import pypdfium2 as pdfium
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.storage.streams import (InMemoryRandomAccessStream,
                                               DataWriter)

    doc = pdfium.PdfDocument(str(pdf_path))
    pagina = doc[indice]
    # OCR do Windows tem limite de dimensao: paginas escaneadas gigantes
    # sao renderizadas em escala menor (bug pego no 1o BO real)
    w_pt, h_pt = pagina.get_size()
    escala = 300 / 72
    maior = max(w_pt, h_pt) * escala
    if maior > 7000:
        escala = 7000 / max(w_pt, h_pt)
    pil = pagina.render(scale=escala).to_pil().convert("RGB")
    doc.close()
    buf = io.BytesIO()
    pil.save(buf, "PNG")
    dados = buf.getvalue()

    async def _rodar():
        stream = InMemoryRandomAccessStream()
        writer = DataWriter(stream.get_output_stream_at(0))
        try:
            writer.write_bytes(dados)
        except TypeError:
            writer.write_bytes(list(dados))
        await writer.store_async()
        decoder = await BitmapDecoder.create_async(stream)
        bmp = await decoder.get_software_bitmap_async()
        eng = OcrEngine.try_create_from_user_profile_languages()
        res = await eng.recognize_async(bmp)
        return "\n".join(l.text for l in res.lines)

    return asyncio.run(_rodar())


# --------------------------------------------------------------- fatiamento
def classifica_pagina(texto):
    """(tipo, classe) pela ZONA DE TITULO — None se a pagina nao abre fatia.

    Zona de titulo = linhas CURTAS (<=60 caracteres) entre as 3 primeiras
    linhas nao vazias. Corpo de texto corrido (linhas longas) nao conta:
    e o que impede pagina de continuacao de abrir fatia nova so porque o
    texto menciona 'sentenca' ou 'contestacao' no meio do paragrafo.
    """
    linhas = [l.strip() for l in texto.splitlines() if l.strip()][:3]
    cabeca = soj.normaliza(" | ".join(l for l in linhas if len(l) <= 60))
    if not cabeca:
        return None
    for rx, tipo, classe in TIPOS:
        if re.search(rx, cabeca, re.I):
            return tipo, classe
    return None


def fatiar(paginas):
    """[{n, fls:(ini,fim), tipo, classe, texto}] por marcador PJe ou cabecalho."""
    nums_pje = [PJE_NUM_RE.search(t or "") for t in paginas]
    fatias, atual = [], None
    usa_pje = sum(1 for m in nums_pje if m) >= len(paginas) * 0.6

    for i, texto in enumerate(paginas):
        if usa_pje:
            marcador = nums_pje[i].group(1) if nums_pje[i] else None
            nova = atual is None or (marcador and marcador != atual.get("pje"))
        else:
            nova = atual is None or classifica_pagina(texto) is not None
        if nova:
            tc = classifica_pagina(texto) or ("documento", "sob_demanda")
            atual = {"ini": i + 1, "fim": i + 1, "tipo": tc[0], "classe": tc[1],
                     "texto": texto or "",
                     "pje": nums_pje[i].group(1) if usa_pje and nums_pje[i] else None}
            fatias.append(atual)
        else:
            atual["fim"] = i + 1
            atual["texto"] += "\n" + (texto or "")
    return fatias


# ------------------------------------------------------------------- indice
def gerar_indice(pasta, dados):
    autos = dados.get("autos")
    if not autos:
        return
    linhas = [f"# ÍNDICE DOS AUTOS — {autos.get('descricao', '')}",
              f"Processo: {autos.get('processo', '(nao informado)')} · "
              f"{autos.get('paginas')} fls. · anexado em {autos.get('anexado_em')} · "
              f"SHA-256 `{str(autos.get('sha256'))[:16]}…`",
              "",
              "> Gerado do bloco `autos:` do CASO.yaml (cache de leitura). "
              "Sessões futuras leem ESTA ficha — nunca o PDF.",
              "",
              "| # | fls. | tipo | data | classe | custo est. (tokens) | lido |",
              "|---|------|------|------|--------|--------------------:|------|"]
    tot = {"ler_integral": 0, "sob_demanda": 0, "nunca_ler": 0}
    for f in autos.get("fatias", []):
        tot[f["classe"]] = tot.get(f["classe"], 0) + int(f.get("tokens_est", 0))
        linhas.append(
            f"| {f['n']} | {f['fls']} | {f['tipo']} | {f.get('data') or '—'} | "
            f"{f['classe']} | {f.get('tokens_est', 0):,} | "
            f"{f.get('lido') or '—'} |".replace(",", "."))
    linhas += ["",
               f"**Orçamento:** ler_integral ≈ {tot['ler_integral']:,} tokens · "
               f"sob_demanda ≈ {tot['sob_demanda']:,} tokens · "
               f"nunca_ler = 0 (excluído por regra)".replace(",", "."),
               "",
               "Mídias nos autos: " + (", ".join(
                   f"`{m}` (degravação sob demanda)" for m in autos.get("midias", []))
                   or "nenhuma")]
    (pasta / "_views" / "AUTOS_INDICE.md").write_text(
        "\n".join(linhas) + "\n", encoding="utf-8", newline="\n")


# --------------------------------------------------------------------- main
def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Motor de autos (SOJ, Onda 5/F6).")
    ap.add_argument("cliente")
    ap.add_argument("caminho", nargs="?", help="PDF dos autos ou pasta (PDF + midias)")
    ap.add_argument("--descricao", default="AUTOS DO PROCESSO")
    ap.add_argument("--processo", default=None)
    ap.add_argument("--marcar-lido", dest="marcar", default=None,
                    help='Numeros de fatia destiladas, ex.: "2,5,9"')
    ap.add_argument("--diario", default=None,
                    help="Entrada do DIARIO com a destilacao (p/ --marcar-lido)")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)

    # ---------- modo cache: marcar fatias destiladas
    if args.marcar:
        autos = dados.get("autos")
        if not autos:
            sys.exit("[ERRO] Este caso nao tem autos anexados.")
        ns = {int(x) for x in args.marcar.split(",")}
        for f in autos.get("fatias", []):
            if f["n"] in ns:
                f["lido"] = soj.agora()[:10] + (f" ({args.diario})" if args.diario else "")
        soj.save_caso(pasta, dados)
        gerar_indice(pasta, dados)
        restam = [f["n"] for f in autos["fatias"]
                  if f["classe"] == "ler_integral" and not f.get("lido")]
        print(f"[OK] Fatias {sorted(ns)} marcadas como destiladas (cache). "
              f"Integrais ainda nao lidas: {restam or 'nenhuma'}.")
        return

    if not args.caminho:
        sys.exit("[ERRO] Informe o PDF/pasta dos autos (ou use --marcar-lido).")
    origem = Path(args.caminho)
    if origem.is_dir():
        pdfs = sorted(origem.glob("*.pdf"), key=lambda a: -a.stat().st_size)
        if not pdfs:
            sys.exit("[ERRO] Nenhum PDF na pasta.")
        pdf_origem = pdfs[0]
        midias = [a for a in sorted(origem.iterdir())
                  if a.is_file() and a.suffix.lower() in MIDIA_EXT]
    elif origem.suffix.lower() == ".pdf":
        pdf_origem, midias = origem, []
    else:
        sys.exit("[ERRO] Caminho precisa ser um PDF ou uma pasta.")

    # ---------- CACHE de segunda rodada: mesmo hash = nada se refaz
    h_pdf = soj.sha256_arquivo(pdf_origem)
    autos_atual = dados.get("autos")
    if autos_atual and autos_atual.get("sha256") == h_pdf:
        gerar_indice(pasta, dados)
        lidas = sum(1 for f in autos_atual["fatias"] if f.get("lido"))
        print("[CACHE] Estes autos JA estao anexados (mesmo SHA-256). Nada foi "
              "re-extraido nem relido.")
        print(f"        {len(autos_atual['fatias'])} fatias no indice; "
              f"{lidas} ja destiladas. Use a FICHA: _views/AUTOS_INDICE.md.")
        return
    if autos_atual:
        sys.exit("[ERRO] Caso ja tem OUTROS autos anexados (hash diferente) — "
                 "falar com o titular antes de substituir.")

    # ---------- 1. lacre
    slugname = soj.slug(args.descricao)[:40]
    dest = pasta / "00_originais" / f"autos_{slugname}"
    if dest.exists():
        sys.exit(f"[ERRO] {dest} ja existe — nao sobrescrevo originais.")
    dest.mkdir(parents=True)
    shutil.copy2(pdf_origem, dest / pdf_origem.name)
    manifesto = [(pdf_origem.name, h_pdf)]
    for m in midias:
        shutil.copy2(m, dest / m.name)
        manifesto.append((m.name, soj.sha256_arquivo(dest / m.name)))

    # ---------- 2/3. extracao por script + OCR local das paginas sem texto
    from pypdf import PdfReader
    reader = PdfReader(str(dest / pdf_origem.name))
    paginas, ocr_feitas, ocr_pendentes = [], [], []
    tem_ocr = ocr_disponivel()
    for i, pg in enumerate(reader.pages):
        try:
            txt = pg.extract_text() or ""
        except Exception:
            txt = ""
        if len(txt.strip()) < MIN_CHARS_TEXTO:
            if tem_ocr:
                try:
                    txt = ("[pagina digitalizada — OCR local Windows pt-BR]\n"
                           + ocr_pagina(dest / pdf_origem.name, i))
                    ocr_feitas.append(i + 1)
                except Exception as e:
                    txt = f"[OCR falhou nesta pagina: {e}]"
                    ocr_pendentes.append(i + 1)
            else:
                txt = "[pagina sem camada de texto — OCR pendente]"
                ocr_pendentes.append(i + 1)
        paginas.append(txt)

    # ---------- 4. fatiamento + custo
    fatias = fatiar(paginas)
    texto_dir = pasta / "_efemeros" / "autos_texto"
    texto_dir.mkdir(parents=True, exist_ok=True)
    registro_fatias = []
    for n, f in enumerate(fatias, 1):
        m_data = DATA_RE.search(f["texto"])
        tokens = int(len(f["texto"]) / CHARS_POR_TOKEN)
        (texto_dir / f"fatia_{n:02d}_{f['tipo']}.txt").write_text(
            f["texto"], encoding="utf-8", newline="\n")
        registro_fatias.append({
            "n": n, "fls": f"{f['ini']}-{f['fim']}", "tipo": f["tipo"],
            "classe": f["classe"], "data": m_data.group(1) if m_data else None,
            "tokens_est": tokens, "lido": None})

    dados["autos"] = {
        "descricao": args.descricao, "processo": args.processo,
        "arquivo": f"00_originais/autos_{slugname}/{pdf_origem.name}",
        "sha256": h_pdf, "paginas": len(paginas),
        "anexado_em": soj.agora(),
        "ocr_local": ocr_feitas, "ocr_pendente": ocr_pendentes,
        "midias": [f"00_originais/autos_{slugname}/{m.name}" for m in midias],
        "fatias": registro_fatias}
    soj.save_caso(pasta, dados)
    gerar_indice(pasta, dados)

    # ---------- 5. plano de leitura com orcamento
    integrais = [f for f in registro_fatias if f["classe"] == "ler_integral"]
    nunca = [f for f in registro_fatias if f["classe"] == "nunca_ler"]
    demanda = [f for f in registro_fatias if f["classe"] == "sob_demanda"]
    orc_int = sum(f["tokens_est"] for f in integrais)
    orc_dem = sum(f["tokens_est"] for f in demanda)
    tier_b = len(paginas) > 100

    corpo = (f"AUTOS ANEXADOS: {args.descricao} "
             f"({len(paginas)} fls., SHA-256 {h_pdf}). Extracao por script; "
             f"OCR local nas fls. {ocr_feitas or 'nenhuma'}"
             + (f"; OCR PENDENTE nas fls. {ocr_pendentes}" if ocr_pendentes else "")
             + f". {len(registro_fatias)} fatias no indice "
             f"(_views/AUTOS_INDICE.md). PLANO: {len(integrais)} integrais "
             f"(~{orc_int} tokens), {len(nunca)} nunca-ler (excluidas), "
             f"{len(demanda)} sob demanda (~{orc_dem} tokens). "
             + ("TIER B (>100 fls.): NADA sera lido antes do ok do titular."
                if tier_b else
                "Tier A (<=100 fls.): destilacao das integrais autorizada "
                "pelo D11 — fundamento: piramide da secao 13; alternativa "
                "descartada: leitura completa; confianca: alta.")
             + " Midias: " + (", ".join(m.name for m in midias) or "nenhuma")
             + ". Cadeia de custodia: manifesto SHA-256 por arquivo.")
    num_d = soj.append_diario(pasta, "AUTOS_ANEXADOS", corpo, origem="sistema")

    import gerar_views
    gerar_views.gerar_views(args.cliente)

    print(f"[OK] Autos anexados e fatiados (DIARIO #{num_d:03d}). "
          f"{len(paginas)} fls. -> {len(registro_fatias)} fatias.")
    if ocr_feitas:
        print(f"     OCR local (Windows pt-BR) nas fls.: {ocr_feitas}")
    if ocr_pendentes:
        print(f"     OCR PENDENTE nas fls.: {ocr_pendentes}")
    print(f"\n     PLANO DE LEITURA (orcamento):")
    print(f"     LER INTEGRAL ({len(integrais)} fatias, ~{orc_int} tokens):")
    for f in integrais:
        print(f"       #{f['n']:>2} fls. {f['fls']:<9} {f['tipo']:<16} "
              f"~{f['tokens_est']} tokens")
    print(f"     NUNCA LER ({len(nunca)}): "
          + ", ".join(f"#{f['n']} {f['tipo']} fls.{f['fls']}" for f in nunca))
    print(f"     SOB DEMANDA ({len(demanda)}): "
          + ", ".join(f"#{f['n']} {f['tipo']} fls.{f['fls']}" for f in demanda))
    decisoes = [f for f in registro_fatias
                if f["tipo"] in ("sentenca", "decisao", "despacho")]
    if decisoes:
        print("\n     ATENCAO (roteador): ha decisao/sentenca/despacho nos autos "
              "-> PRAZO ANTES DE TUDO (registrar PZ## no vigia).")
    if tier_b:
        print("\n     [TIER B] Autos com mais de 100 fls.: NADA sera lido antes "
              "do OK do advogado ao plano acima.")
    else:
        print("\n     [Tier A] Ate 100 fls.: destilacao das integrais pode "
              "seguir (D11) — texto das fatias em _efemeros/autos_texto/.")


if __name__ == "__main__":
    main()
