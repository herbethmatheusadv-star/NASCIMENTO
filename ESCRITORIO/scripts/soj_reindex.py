# -*- coding: utf-8 -*-
"""
soj_reindex.py — RECONSTROI o index FTS5 dos autos (Fase 3 do PLANO_SOJ).

Le os textos importados (AUTOS/{cnj}/texto/autos_integral.txt + manifesto.json)
e monta index/soj.sqlite: uma tabela FTS5 com UMA LINHA POR PAGINA, guardando o
processo, a folha (pagina) e o carimbo do PJe (Num./Pag.) para citar a fonte.

O index e DESCARTAVEL: nao e segunda verdade, e derivado do texto. Pode apagar e
rodar de novo a qualquer momento (DROP + CREATE do zero). Fica em index/ (fora do
Git). Busca-se com `soj_search.py`.

Uso:
  python soj_reindex.py            # reconstroi tudo
"""
import json
import re
import sqlite3
import sys
from pathlib import Path

import soj_lib as soj

AUTOS = soj.ROOT / "AUTOS"
INDEX_DIR = soj.ROOT / "index"
DB = INDEX_DIR / "soj.sqlite"

MARCADOR_RE = re.compile(r"^===\[p\.(\d+)\]===\s*$", re.M)


def paginas_do_texto(txt: str) -> dict:
    """{numero_pagina: texto} a partir dos marcadores ===[p.N]===."""
    out: dict[int, str] = {}
    marcas = list(MARCADOR_RE.finditer(txt))
    for i, m in enumerate(marcas):
        n = int(m.group(1))
        ini = m.end()
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(txt)
        out[n] = txt[ini:fim].strip()
    return out


def criar_schema(con: sqlite3.Connection) -> None:
    con.executescript("""
        DROP TABLE IF EXISTS paginas;
        CREATE VIRTUAL TABLE paginas USING fts5(
            cnj UNINDEXED,
            proc_id UNINDEXED,
            pagina UNINDEXED,
            num_pje UNINDEXED,
            pag_doc UNINDEXED,
            texto,
            tokenize = 'unicode61 remove_diacritics 2'
        );
    """)


def reindexar() -> tuple[int, int]:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    try:
        try:
            criar_schema(con)
        except sqlite3.OperationalError as e:
            print(f"[reindex] FTS5 indisponivel no SQLite desta maquina: {e}")
            sys.exit(2)

        n_proc = n_pag = 0
        for d in sorted(AUTOS.iterdir()) if AUTOS.exists() else []:
            texto_f = d / "texto" / "autos_integral.txt"
            manif_f = d / "texto" / "manifesto.json"
            if not (texto_f.exists() and manif_f.exists()):
                continue
            manif = json.loads(manif_f.read_text(encoding="utf-8"))
            cnj = manif.get("cnj", d.name)
            proc_id = manif.get("proc_id", "")
            # Num/Pag por pagina, do manifesto (autoritativo)
            meta = {p["p"]: p for p in manif.get("por_pagina", [])}
            paginas = paginas_do_texto(texto_f.read_text(encoding="utf-8"))
            linhas = []
            for n, texto in paginas.items():
                if not texto:
                    continue
                m = meta.get(n, {})
                linhas.append((cnj, proc_id, n, m.get("num"), m.get("pag_doc"),
                               texto))
            con.executemany(
                "INSERT INTO paginas(cnj,proc_id,pagina,num_pje,pag_doc,texto)"
                " VALUES (?,?,?,?,?,?)", linhas)
            n_proc += 1
            n_pag += len(linhas)
        con.commit()
        return n_proc, n_pag
    finally:
        con.close()


def main() -> None:
    soj.console_utf8()
    if not AUTOS.exists():
        print("[reindex] AUTOS/ nao existe. Rode soj_import.py primeiro.")
        sys.exit(1)
    n_proc, n_pag = reindexar()
    if n_pag == 0:
        print("[reindex] nada indexado. Rode soj_import.py antes.")
        sys.exit(1)
    print(f"[reindex] index reconstruido: {n_proc} processo(s), {n_pag} paginas.")
    print(f"[reindex] {DB}")
    print('[reindex] busque: python soj_search.py "termo"')


if __name__ == "__main__":
    main()
