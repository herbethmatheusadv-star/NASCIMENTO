# -*- coding: utf-8 -*-
"""
soj_inteligencia.py — LINHA DO TEMPO das pecas de cada processo (Fase 3).

Gera, por processo, um indice navegavel dos autos: cada peca com data, tipo,
nome, folhas e relevancia de leitura. FATOS, nao analise — extraidos da tabela
"Documentos" da capa do PJe (nome/tipo/data autoritativos) cruzada com os
intervalos de pagina do manifesto. Sem narrativa inventada: e o esqueleto que o
advogado (ou um passo de IA, depois) preenche.

Todo artefato leva cabecalho de proveniencia (gerado_por, gerado_em,
baseado_em+hash, status: rascunho) — a regra do PLANO_SOJ contra "analise antiga
tratada como verdade atual". Fica em AUTOS/{cnj}/inteligencia/ (gitignored).

Uso:
  python soj_inteligencia.py                 # todos os processos importados
  python soj_inteligencia.py --cnj 0805058-87.2025.8.14.0040
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import soj_lib as soj
import soj_reindex as rdx   # reusa paginas_do_texto (split por ===[p.N]===)

AUTOS = soj.ROOT / "AUTOS"

# linha da tabela da capa: "139782043 26/03/2025" (Num SPACE data, sem "Num.")
TABELA_ROW = re.compile(r"(?m)^\s*(\d{6,})\s+(\d{2}/\d{2}/\d{4})\b")
HORA_RE = re.compile(r"^\d{1,2}:\d{2}$")
RODAPE_RE = re.compile(
    r"(?m)^\s*(?:N[uú]mero do documento:|Este documento foi gerado|"
    r"Num\.\s*\d+\s*-\s*P[aá]g|https?://pje)")

# relevancia de leitura (piramide do anexar_autos): pecas das partes e atos
# decisorios valem leitura integral; praxe cartoraria, quase nunca.
ALTA = ("peticao inicial", "contestacao", "replica", "impugnacao", "sentenca",
        "decisao", "despacho", "acordao", "embargos", "recurso", "apelacao",
        "agravo", "contrarrazoes", "laudo", "parecer", "ata", "voto",
        "manifestacao", "peticao")
BAIXA = ("certidao", "juntada", "termo de", "guia", "custas", "aviso",
         "intimacao", "citacao", "comprovante", "procuracao", "substabelec",
         "identificacao", "etiqueta", "expediente", "ar ")


def relevancia(tipo: str, nome: str) -> str:
    t = soj.normaliza(f"{tipo} {nome}")
    if any(k in t for k in ALTA):
        return "alta"
    if any(k in t for k in BAIXA):
        return "baixa"
    return "media"


def _sem_rodape(t: str) -> str:
    m = RODAPE_RE.search(t)
    return t[:m.start()] if m else t


def texto_capa(paginas: dict) -> str:
    """Concatena as paginas de CAPA (as que tem varias linhas da tabela)."""
    partes = []
    for n in sorted(paginas):
        if len(TABELA_ROW.findall(paginas[n])) >= 2:
            partes.append(_sem_rodape(paginas[n]))
        elif partes:
            break   # ja passou a capa
    return "\n".join(partes)


def parse_tabela_documentos(texto: str) -> dict:
    """{num: {data, nome, tipo}} da tabela 'Documentos' da capa. Puro/testavel.

    Cada bloco: '<num> <data>' / (hora) / <nome...multi-linha> / <tipo>."""
    out = {}
    ms = list(TABELA_ROW.finditer(texto))
    for i, m in enumerate(ms):
        num, data = m.group(1), m.group(2)
        fim = ms[i + 1].start() if i + 1 < len(ms) else len(texto)
        linhas = [l.strip() for l in texto[m.end():fim].splitlines() if l.strip()]
        if linhas and HORA_RE.match(linhas[0]):
            linhas = linhas[1:]
        if not linhas:
            out[num] = {"data": data, "nome": "", "tipo": ""}
        elif len(linhas) == 1:
            out[num] = {"data": data, "nome": linhas[0], "tipo": linhas[0]}
        else:
            out[num] = {"data": data, "nome": " ".join(linhas[:-1]),
                        "tipo": linhas[-1]}
    return out


def tipo_por_palavra(texto_pagina: str) -> str:
    """Fallback quando a peca nao esta na tabela: cabecalho da 1a pagina."""
    cab = soj.normaliza(texto_pagina[:400])
    for chave, rotulo in (
            ("peticao inicial", "Petição Inicial"), ("contestacao", "Contestação"),
            ("sentenca", "Sentença"), ("despacho", "Despacho"),
            ("decisao", "Decisão"), ("certidao", "Certidão"),
            ("procuracao", "Procuração"), ("ata", "Ata")):
        if chave in cab:
            return rotulo
    return "(não classificado)"


def gerar_um(cnj: str) -> dict:
    texto_dir = AUTOS / cnj / "texto"
    manif_f = texto_dir / "manifesto.json"
    texto_f = texto_dir / "autos_integral.txt"
    if not (manif_f.exists() and texto_f.exists()):
        return {"cnj": cnj, "status": "sem_texto"}

    manif = json.loads(manif_f.read_text(encoding="utf-8"))
    paginas = rdx.paginas_do_texto(texto_f.read_text(encoding="utf-8"))
    tabela = parse_tabela_documentos(texto_capa(paginas))

    itens = []
    for doc in manif.get("docs", []):
        num = doc.get("num")
        if not num:
            # paginas sem carimbo Num: no comeco e a capa/indice dos autos; no
            # meio, folha sem stamp. Nao classificar por palavra (a capa lista
            # nomes de pecas e enganava o detector).
            tipo = "(capa/índice)" if doc["p_ini"] == 1 else "(sem carimbo)"
            nome, data, rel = tipo, "", "baixa"
        else:
            info = tabela.get(num, {})
            nome = info.get("nome", "")
            tipo = info.get("tipo", "") or tipo_por_palavra(paginas.get(doc["p_ini"], ""))
            data = info.get("data", "")
            rel = relevancia(tipo, nome)
        itens.append({
            "num": num or "-", "data": data, "tipo": tipo or "-",
            "nome": (nome or tipo or "-"),
            "p_ini": doc["p_ini"], "p_fim": doc["p_fim"], "n_pag": doc["n_pag"],
            "relevancia": rel,
        })

    # escreve a linha do tempo
    intel = AUTOS / cnj / "inteligencia"
    intel.mkdir(parents=True, exist_ok=True)
    saida = intel / "linha_do_tempo.md"
    _escrever(saida, cnj, manif, itens)
    n_alta = sum(1 for i in itens if i["relevancia"] == "alta")
    return {"cnj": cnj, "status": "ok", "pecas": len(itens), "alta": n_alta,
            "arquivo": str(saida)}


def _data_key(d: str):
    """DD/MM/YYYY -> (YYYY,MM,DD) para ordenar CRONOLOGICAMENTE (nao string)."""
    try:
        dd, mm, yy = d.split("/")
        return (int(yy), int(mm), int(dd))
    except Exception:  # noqa: BLE001
        return None


def _escrever(saida: Path, cnj: str, manif: dict, itens: list) -> None:
    sha = (manif.get("pdf_sha256") or "")[:8]
    datados = [(i["data"], _data_key(i["data"])) for i in itens if i["data"]]
    datados = [x for x in datados if x[1]]
    periodo = (f"{min(datados, key=lambda x: x[1])[0]} a "
               f"{max(datados, key=lambda x: x[1])[0]}") if datados else "-"
    L = [
        "---",
        "gerado_por: soj_inteligencia.py",
        f"gerado_em: {datetime.now():%Y-%m-%d %H:%M}",
        "baseado_em:",
        f"  - {manif.get('pdf', 'autos_integral.pdf')} (sha {sha})",
        "status: rascunho",
        "tipo: linha_do_tempo",
        f"processo: {cnj}",
        f"proc_id: {manif.get('proc_id', '')}",
        "---",
        "",
        f"# Linha do tempo das pecas — {cnj}",
        "",
        f"> **FATOS extraidos por script** (tabela da capa do PJe + folhas do "
        f"manifesto). Nao e analise; nao substitui a leitura. `status: rascunho` "
        f"ate revisao humana.",
        "",
        f"- Pecas: **{len(itens)}** · Paginas: **{manif.get('paginas', 0)}** · "
        f"Periodo: **{periodo}**",
        f"- Leitura prioritaria (alta): "
        f"**{sum(1 for i in itens if i['relevancia'] == 'alta')}** pecas",
        "",
        "| # | Data | Relev. | Tipo | Documento | fls | Num |",
        "|---|---|---|---|---|---|---|",
    ]
    marca = {"alta": "🔴 alta", "media": "🟡 media", "baixa": "⚪ baixa"}
    for k, it in enumerate(itens, 1):
        fls = f"{it['p_ini']}" if it["p_ini"] == it["p_fim"] else f"{it['p_ini']}–{it['p_fim']}"
        nome = re.sub(r"\s+", " ", it["nome"]).strip()[:70]
        L.append(f"| {k} | {it['data'] or '-'} | {marca.get(it['relevancia'])} | "
                 f"{it['tipo']} | {nome} | {fls} | {it['num']} |")
    L += ["", "_Para ler uma peca: os autos estao em `../texto/autos_integral.txt` "
          "(marcadores `===[p.N]===`). Buscar no acervo: `soj_search.py`._", ""]
    saida.write_text("\n".join(L), encoding="utf-8")


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Linha do tempo das pecas (por processo).")
    ap.add_argument("--cnj", default="", help="so este processo")
    args = ap.parse_args()

    alvo = re.sub(r"\D", "", args.cnj) if args.cnj else ""
    dirs = [d for d in sorted(AUTOS.iterdir()) if d.is_dir()] if AUTOS.exists() else []
    if alvo:
        dirs = [d for d in dirs if re.sub(r"\D", "", d.name) == alvo]
    if not dirs:
        print("[intel] nada a fazer. Rode soj_import.py antes.")
        sys.exit(1)

    ok = 0
    for d in dirs:
        r = gerar_um(d.name)
        if r["status"] == "ok":
            ok += 1
            print(f"  {d.name}  {r['pecas']:>3} pecas ({r['alta']} alta) -> "
                  f"inteligencia/linha_do_tempo.md")
        else:
            print(f"  {d.name}  ** {r['status']} ** (importe primeiro)")
    print(f"[intel] {ok}/{len(dirs)} linha(s) do tempo geradas (status: rascunho).")


if __name__ == "__main__":
    main()
