# -*- coding: utf-8 -*-
"""
soj_import.py — IMPORTADOR DE AUTOS (Fase 3 do PLANO_SOJ).

Transforma os PDFs integrais baixados pelo CONECTOR (AUTOS/{cnj}/
autos_integral_*.pdf) em TEXTO pesquisavel e citavel por pagina. Fecha o elo
entre "baixei os autos" e "encontro e cito qualquer trecho".

  O QUE FAZ

  1. Mapeia CNJ -> PROC-XXXX (le o `numero:` das fichas em PROCESSOS/).
  2. Para cada autos_integral_*.pdf:
       - SHA-256 do PDF (cadeia de custodia; cache por hash).
       - Extrai o texto pagina a pagina (PyMuPDF/fitz — os PDFs do PJe ja vem
         com camada de texto; sem OCR).
       - Grava AUTOS/{cnj}/texto/autos_integral.txt com marcadores ===[p.N]===
         (N = pagina do PDF = folha dos autos) — e isso que permite citar pagina.
       - Le o carimbo do rodape do PJe "Num. <id> - Pag. <n>" de cada pagina:
         `Num` = id do documento (delimita as pecas), `Pag` = pagina dentro da
         peca. Vira a citacao autoritativa e agrupa as pecas SEM fatiar o PDF.
       - Escreve texto/manifesto.json (sha, paginas, por_pagina, documentos).
  3. Idempotente: mesmo PDF (mesmo sha) nao e re-extraido (use --forcar).

O texto fica sob AUTOS/ (gitignored) porque e conteudo de cliente, como o PDF.
Depois, `soj_reindex.py` constroi o index FTS5 e `soj_search.py` busca.

Uso:
  python soj_import.py                  # importa todos os processos com PDF
  python soj_import.py --cnj 0805058-87.2025.8.14.0040
  python soj_import.py --forcar         # re-extrai mesmo com cache
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import soj_lib as soj

AUTOS = soj.ROOT / "AUTOS"
PROCESSOS = soj.ROOT / "PROCESSOS"

# carimbo do rodape do PJe: "Num. 171591788 - Pag. 1" (P[aá]g cobre Pag/Pág).
PJE_NUM_PAG_RE = re.compile(r"Num\.\s*(\d+)\s*-\s*P[aá]g\.?\s*(\d+)", re.I)
# numero CNJ no frontmatter das fichas
NUMERO_RE = re.compile(r"^numero:\s*\"?(\d[\d.\-]{15,})\"?\s*$", re.M)
ID_RE = re.compile(r"^id:\s*\"?(PROC-\d+)\"?\s*$", re.M)


def norm_cnj(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


def mapa_cnj_proc() -> dict:
    """{cnj_normalizado: PROC-XXXX} lido do frontmatter das fichas."""
    out = {}
    if not PROCESSOS.exists():
        return out
    for ficha in sorted(PROCESSOS.glob("PROC-*.md")):
        try:
            cab = ficha.read_text(encoding="utf-8")[:1500]
        except Exception:  # noqa: BLE001
            continue
        mnum = NUMERO_RE.search(cab)
        mid = ID_RE.search(cab)
        if mnum:
            pid = mid.group(1) if mid else ficha.stem
            # setdefault + sorted(): a ficha CANONICA (PROC-0013.md) vem antes da
            # sub-ficha (PROC-0013_audiencia_...md, mesmo numero) e vence.
            out.setdefault(norm_cnj(mnum.group(1)), pid)
    return out


def parse_num_pag(texto: str) -> tuple[str | None, int | None]:
    """(num_pje, pag_doc) do carimbo do RODAPE (ultima ocorrencia na pagina)."""
    achados = PJE_NUM_PAG_RE.findall(texto or "")
    if not achados:
        return None, None
    num, pag = achados[-1]
    return num, (int(pag) if pag.isdigit() else None)


def marcador(n: int) -> str:
    return f"===[p.{n}]==="


def montar_texto(paginas: list[dict]) -> str:
    """Junta as paginas com marcador ===[p.N]=== antes de cada uma."""
    partes: list[str] = []
    for i, pg in enumerate(paginas):
        if i:
            partes.append("")            # linha em branco entre paginas
        partes.append(marcador(pg["n"]))
        partes.append((pg["texto"] or "").rstrip())
    return "\n".join(partes) + "\n"


def montar_documentos(por_pagina: list[dict]) -> list[dict]:
    """Agrupa paginas consecutivas com o mesmo Num (peca)."""
    docs: list[dict] = []
    for pg in por_pagina:
        num = pg.get("num")
        if docs and docs[-1]["num"] == num:
            docs[-1]["p_fim"] = pg["p"]
            docs[-1]["n_pag"] += 1
        else:
            docs.append({"num": num, "p_ini": pg["p"], "p_fim": pg["p"],
                         "n_pag": 1})
    return docs


def extrair(pdf: Path) -> tuple[list[dict], list[dict]]:
    """Le o PDF com fitz. Devolve (paginas_texto, por_pagina_meta)."""
    import fitz  # PyMuPDF
    paginas: list[dict] = []
    por_pagina: list[dict] = []
    doc = fitz.open(pdf)
    try:
        for i in range(doc.page_count):
            t = doc[i].get_text("text")
            num, pag_doc = parse_num_pag(t)
            n = i + 1
            paginas.append({"n": n, "texto": t})
            por_pagina.append({"p": n, "num": num, "pag_doc": pag_doc,
                               "chars": len(t)})
    finally:
        doc.close()
    return paginas, por_pagina


def importar_um(cnj: str, pdf: Path, proc_id: str, forcar: bool) -> dict:
    texto_dir = AUTOS / cnj / "texto"
    manifesto = texto_dir / "manifesto.json"
    sha = soj.sha256_arquivo(pdf)

    if manifesto.exists() and not forcar:
        try:
            antigo = json.loads(manifesto.read_text(encoding="utf-8"))
            if antigo.get("pdf_sha256") == sha:
                return {"cnj": cnj, "status": "cache",
                        "paginas": antigo.get("paginas", 0)}
        except Exception:  # noqa: BLE001
            pass

    paginas, por_pagina = extrair(pdf)
    documentos = montar_documentos(por_pagina)
    texto_dir.mkdir(parents=True, exist_ok=True)
    (texto_dir / "autos_integral.txt").write_text(
        montar_texto(paginas), encoding="utf-8")

    dados = {
        "cnj": cnj,
        "proc_id": proc_id,
        "pdf": pdf.name,
        "pdf_sha256": sha,
        "paginas": len(paginas),
        "caracteres": sum(p["chars"] for p in por_pagina),
        "documentos": len(documentos),
        "extraido_em": datetime.now().isoformat(timespec="seconds"),
        "ferramenta": "PyMuPDF",
        "por_pagina": por_pagina,
        "docs": documentos,
    }
    manifesto.write_text(json.dumps(dados, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    return {"cnj": cnj, "status": "ok", "paginas": len(paginas),
            "documentos": len(documentos)}


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Importa autos (PDF -> texto+manifesto).")
    ap.add_argument("--cnj", default="", help="importa so este processo")
    ap.add_argument("--forcar", action="store_true", help="re-extrai mesmo com cache")
    args = ap.parse_args()

    if not AUTOS.exists():
        print("[import] pasta AUTOS/ nao existe — baixe os autos primeiro.")
        sys.exit(1)

    mapa = mapa_cnj_proc()
    alvo_norm = norm_cnj(args.cnj) if args.cnj else ""
    processos = []
    for d in sorted(AUTOS.iterdir()):
        if not d.is_dir():
            continue
        cnj = d.name
        if alvo_norm and norm_cnj(cnj) != alvo_norm:
            continue
        pdfs = sorted(d.glob("autos_integral_*.pdf"))
        if pdfs:
            processos.append((cnj, pdfs[-1]))

    if not processos:
        print("[import] nenhum autos_integral_*.pdf encontrado"
              + (f" para {args.cnj}" if args.cnj else "") + ".")
        sys.exit(1)

    print(f"[import] {len(processos)} processo(s) com PDF. Extraindo...")
    tot_pg = novos = 0
    for cnj, pdf in processos:
        proc_id = mapa.get(norm_cnj(cnj), "(sem ficha)")
        r = importar_um(cnj, pdf, proc_id, args.forcar)
        tot_pg += r.get("paginas", 0)
        if r["status"] == "ok":
            novos += 1
            print(f"  OK    {cnj}  {proc_id:>9}  {r['paginas']:>4} pgs  "
                  f"{r['documentos']:>3} pecas")
        else:
            print(f"  cache {cnj}  {proc_id:>9}  {r['paginas']:>4} pgs (inalterado)")

    print(f"[import] {novos} extraido(s), {len(processos)} no total, "
          f"{tot_pg} paginas. Agora: python soj_reindex.py")


if __name__ == "__main__":
    main()
