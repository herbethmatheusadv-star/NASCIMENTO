#!/usr/bin/env python3
"""
baixar_autos.py — baixa os autos de UM processo pela API REST do PJe/TJPA.

LEITURA, e so leitura. Roda DENTRO da sessao que o titular autenticou
(`sessao.py`, certificado + 2FA). Fecha a Fase de coleta do PLANO_SOJ: entrega
os PDFs em AUTOS/{cnj}/ para o importador (Fase 3) transformar em texto com
marcador de pagina.

  COMO FUNCIONA (desenho fechado em 16/07/2026 — ver CONECTOR/MAPA_PJE.md §11)

  1. O titular loga (o robo para no portao; ele digita cert + 2FA).
  2. O titular ABRE os autos de UM processo pela Acervo (nova janela). Isso e
     leitura; e ele quem clica.
  3. O robo detecta a pagina `listProcessoCompletoAdvogado`, LE o HTML e extrai:
       - o numero CNJ (do cabecalho);
       - todos os `idProcessoDocumento` (cada peca dos autos).
  4. Para cada peca, GET no UNICO endpoint de leitura:
         /pje/seam/resource/rest/pje-legacy/documento/download/{id}
     autenticado pelo COOKIE da sessao (JSESSIONID) que o navegador do titular
     ja tem — o robo NUNCA extrai nem guarda esse cookie.
  5. Salva em AUTOS/{cnj}/, com sha256, dedup e indice.

  R7 — POR QUE ISTO SO SABE LER

  Existe UMA rota construida aqui: `documento/download/{id}` (GET). Qualquer
  outra rota do `rest/pje-legacy/` — inclusive as de escrita — simplesmente NAO
  tem funcao neste arquivo. E allowlist, como no MNI, nao blocklist. Toda URL
  passa por `regras.guarda_de_url`. Nao ha clique em botao de acao: o robo so
  faz GET de documento. `teste_regras.py` varre este arquivo e quebra o build se
  aparecer capacidade de agir.

Uso:
    python CONECTOR/baixar_autos.py        # abre a sessao; voce loga e abre 1 processo
    python CONECTOR/baixar_autos.py --limite 5 --pausa 2
"""
from __future__ import annotations

import argparse
import hashlib
import html as htmlmod
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import regras
import sessao

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://pje.tjpa.jus.br/pje"

# A UNICA rota de leitura que este arquivo constroi e chama. Allowlist.
REST_DOWNLOAD = BASE + "/seam/resource/rest/pje-legacy/documento/download/{id}"

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
# nome da peca: title="177919838 - Peticao Inicial"
RE_DOC_NOME = re.compile(r'title="(\d{6,})\s*-\s*([^"]{2,80})"')
# id de qualquer peca (aparece em varios lugares: lembretes, download, arvore)
RE_DOC_ID = re.compile(r'(?:idProcessoDocumento=|documento/download/)(\d{6,})')


def extrair_cnj(html: str) -> str:
    m = RE_CNJ.search(html or "")
    return m.group(0) if m else ""


def extrair_documentos(html: str) -> list[tuple[str, str]]:
    """
    Lista (idProcessoDocumento, nome) de todas as pecas, na ordem de aparicao.

    A arvore dos autos e lazy: nem toda peca traz o nome no HTML estatico. Entao
    junta duas fontes — os `title="{id} - {nome}"` (quando ha nome) e todos os
    ids soltos — e usa o nome onde existir, o id onde nao. Nenhuma peca fica de
    fora so por nao ter rotulo renderizado.
    """
    html = html or ""
    nomes: dict[str, str] = {}
    for m in RE_DOC_NOME.finditer(html):
        nomes.setdefault(m.group(1), htmlmod.unescape(m.group(2)).strip())

    # ids em ordem de aparicao, das DUAS fontes: o title="{id} - nome" (peca
    # nomeada na arvore) E os links (idProcessoDocumento=/download/). Uma peca
    # que so aparece no title — porque a arvore lazy nao renderizou o link —
    # nao pode sumir. Foi o bug que o teste_baixar §2 pegou em 16/07/2026.
    pares: list[tuple[int, str]] = []
    for m in RE_DOC_NOME.finditer(html):
        pares.append((m.start(), m.group(1)))
    for m in RE_DOC_ID.finditer(html):
        pares.append((m.start(), m.group(1)))
    pares.sort()

    vistos: list[str] = []
    seen: set[str] = set()
    for _, i in pares:
        if i not in seen:
            seen.add(i)
            vistos.append(i)
    return [(i, nomes.get(i, "")) for i in vistos]


def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return (t or "peca")[:40]


def _url_download(iddoc: str) -> str:
    url = REST_DOWNLOAD.format(id=iddoc)
    # allowlist + guarda: so passa o que comeca pelo prefixo de leitura, e a
    # guarda ainda barra qualquer verbo de acao que porventura aparecesse.
    if not url.startswith(BASE + "/seam/resource/rest/pje-legacy/documento/download/"):
        raise regras.ViolacaoR7(f"rota fora da allowlist de leitura: {url!r}")
    regras.guarda_de_url(url)
    return url


def baixar_uma(contexto, iddoc: str) -> tuple[bool, bytes, int, str]:
    """GET de uma peca pela sessao (cookie automatico). Devolve (ok, bytes, status, ct)."""
    url = _url_download(iddoc)
    try:
        r = contexto.request.get(url, timeout=90_000)
    except Exception as e:  # noqa: BLE001
        return False, b"", 0, f"{type(e).__name__}: {e}"
    ct = (r.headers or {}).get("content-type", "")
    if r.status != 200:
        return False, b"", r.status, ct
    try:
        dados = r.body()
    except Exception:  # noqa: BLE001
        return False, b"", r.status, ct
    return True, dados, r.status, ct


def _extensao(ct: str, dados: bytes) -> str:
    if dados[:5] == b"%PDF-":
        return "pdf"
    if "pdf" in (ct or "").lower():
        return "pdf"
    if "html" in (ct or "").lower():
        return "html"
    return "bin"


def coletar(s: "sessao.SessaoEfemera", limite: int, pausa: float) -> Path | None:
    """
    Espera o titular abrir UM processo, le os autos e baixa as pecas.
    O robo nao clica em nada — o titular abre; o robo le e baixa (GET).
    """
    print()
    print("=" * 70)
    print("  BAIXAR AUTOS — VOCE ABRE O PROCESSO, EU BAIXO (so leitura)")
    print("=" * 70)
    print("  1. Pela ACERVO, clique no NUMERO de UM processo para abrir os")
    print("     AUTOS digitais (nova janela).")
    print("  2. Pode fechar depois — assim que eu vir a pagina dos autos, leio")
    print("     a lista de pecas e baixo cada uma pela API (GET).")
    print()
    print("  NAO abra expediente 'pendente de ciencia'. Autos pela Acervo e")
    print("  leitura — pode.")
    print("=" * 70)

    autos = {"pagina": None}

    def viu_pagina(pag):
        try:
            if "listProcessoCompletoAdvogado" in (pag.url or ""):
                autos["pagina"] = pag
        except Exception:  # noqa: BLE001
            pass

    s.contexto.on("page", viu_pagina)

    limite_espera = time.time() + 8 * 60
    while time.time() < limite_espera and autos["pagina"] is None:
        # tambem olha a aba principal, caso ele navegue nela mesma
        try:
            if "listProcessoCompletoAdvogado" in (s.pagina.url or ""):
                autos["pagina"] = s.pagina
        except Exception:  # noqa: BLE001
            pass
        if s.pagina.is_closed():
            print("[baixar] janela fechada antes de abrir um processo. Nada baixado.")
            return None
        time.sleep(2)

    pag = autos["pagina"]
    if pag is None:
        print("[baixar] nao vi nenhum processo aberto no tempo limite.")
        return None

    try:
        pag.wait_for_load_state("networkidle", timeout=30_000)
    except Exception:  # noqa: BLE001
        pass
    try:
        html = pag.content()
    except Exception as e:  # noqa: BLE001
        print(f"[baixar] nao consegui ler a pagina dos autos: {e}")
        return None

    cnj = extrair_cnj(html)
    docs = extrair_documentos(html)
    if not cnj:
        print("[baixar] nao achei o numero CNJ na pagina — abortando por seguranca.")
        return None
    print(f"\n[baixar] processo {cnj} — {len(docs)} peca(s) na arvore dos autos.")
    if limite and len(docs) > limite:
        print(f"[baixar] baixando as {limite} primeiras (--limite).")
        docs = docs[:limite]

    destino = RAIZ / "AUTOS" / cnj / "originais"
    destino.mkdir(parents=True, exist_ok=True)

    indice = destino.parent / f"documentos_baixados_{datetime.now():%Y-%m-%d}.md"
    linhas = [f"# Autos baixados — {cnj} — {datetime.now():%Y-%m-%d %H:%M}",
              "", "Baixado pela API REST (documento/download), sessao do titular,",
              "somente leitura. Originais imutaveis.", "",
              "| ordem | idProcessoDocumento | nome | bytes | sha256 | arquivo |",
              "|---|---|---|---|---|---|"]

    baixados = hashes = 0
    for ordem, (iddoc, nome) in enumerate(docs, 1):
        ok, dados, status, ct = baixar_uma(s.contexto, iddoc)
        if not ok:
            print(f"  [{ordem:>3}] {iddoc}  FALHA (status={status} {ct[:30]})")
            linhas.append(f"| {ordem} | {iddoc} | {nome} | - | FALHA {status} | - |")
            time.sleep(pausa)
            continue
        sha = hashlib.sha256(dados).hexdigest()
        ext = _extensao(ct, dados)
        arquivo = f"{ordem:04d}_{_slug(nome) or iddoc}_{sha[:8]}.{ext}"
        alvo = destino / arquivo
        if any(p.name.endswith(f"_{sha[:8]}.{ext}") for p in destino.glob("*")):
            print(f"  [{ordem:>3}] {iddoc}  ja existe (sha {sha[:8]}) — pulado")
        else:
            alvo.write_bytes(dados)
            baixados += 1
            print(f"  [{ordem:>3}] {iddoc}  {len(dados):>8} B  {ext}  "
                  f"{(nome or '(sem nome)')[:40]}")
        hashes += 1
        linhas.append(f"| {ordem} | {iddoc} | {nome} | {len(dados)} | "
                      f"{sha[:16]} | {arquivo} |")
        time.sleep(pausa)   # rate limit humanizado

    indice.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\n[baixar] {baixados} peca(s) nova(s) salva(s) em {destino}")
    print(f"[baixar] indice: {indice}")
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description="Baixa os autos de um processo (leitura).")
    ap.add_argument("--limite", type=int, default=0,
                    help="baixar no maximo N pecas (0 = todas)")
    ap.add_argument("--pausa", type=float, default=1.5,
                    help="segundos entre downloads (rate limit; padrao 1.5)")
    args = ap.parse_args()

    ok, faltas = sessao.ambiente_ok()
    print("[ambiente]", "pronto" if ok else "INCOMPLETO")
    for f in faltas:
        print("  -", f)
    if not ok:
        sys.exit(1)

    with sessao.SessaoEfemera() as s:
        if not s.esperar_login_humano():
            return
        coletar(s, args.limite, args.pausa)


if __name__ == "__main__":
    main()
