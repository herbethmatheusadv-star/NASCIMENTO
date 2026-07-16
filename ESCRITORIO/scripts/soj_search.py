# -*- coding: utf-8 -*-
"""
soj_search.py — BUSCA nos autos, com citacao por pagina (Fase 3 do PLANO_SOJ).

Pergunta em linguagem natural sobre o texto de TODOS os autos importados e
devolve onde esta: processo, folha (pagina) e o carimbo do PJe (Num./Pag.) — a
fonte exata para citar. O acento nao importa (o index remove diacriticos).

Uso:
  python soj_search.py "penhora online"
  python soj_search.py "SICOOB" --processo 0805058-87.2025.8.14.0040
  python soj_search.py "gratuidade" --limite 30
  python soj_search.py '"tutela de urgencia"'      # frase exata entre aspas
"""
import argparse
import re
import sqlite3
import sys

import soj_lib as soj

DB = soj.ROOT / "index" / "soj.sqlite"


def norm_cnj(t: str) -> str:
    return re.sub(r"\D", "", t or "")


def buscar(termo: str, processo: str, limite: int) -> list[dict]:
    if not DB.exists():
        print("[busca] index nao existe. Rode: python soj_reindex.py")
        sys.exit(1)
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        sql = ("SELECT cnj, proc_id, pagina, num_pje, pag_doc, "
               "snippet(paginas, 5, '>>>', '<<<', ' ... ', 14) AS trecho, "
               "bm25(paginas) AS rank FROM paginas "
               "WHERE paginas MATCH ? ")
        params: list = [termo]
        if processo:
            sql += "AND cnj = ? "
            # tenta casar o formato exato salvo (com pontuacao)
            params.append(_cnj_formatado(con, processo))
        sql += "ORDER BY rank LIMIT ?"
        params.append(limite)
        try:
            return [dict(r) for r in con.execute(sql, params).fetchall()]
        except sqlite3.OperationalError as e:
            print(f"[busca] consulta invalida ({e}). Dica: aspas para frase, "
                  f"ex.: '\"tutela de urgencia\"'.")
            sys.exit(2)
    finally:
        con.close()


def _cnj_formatado(con, entrada: str) -> str:
    """Casa o CNJ pedido (com ou sem pontuacao) ao formato guardado."""
    alvo = norm_cnj(entrada)
    for (cnj,) in con.execute("SELECT DISTINCT cnj FROM paginas"):
        if norm_cnj(cnj) == alvo:
            return cnj
    return entrada


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Busca nos autos (FTS5, cita pagina).")
    ap.add_argument("termo", help="termo(s); use aspas para frase exata")
    ap.add_argument("--processo", default="", help="restringe a um CNJ")
    ap.add_argument("--limite", type=int, default=20, help="max resultados (20)")
    args = ap.parse_args()

    achados = buscar(args.termo, args.processo, args.limite)
    if not achados:
        print(f"[busca] nada para {args.termo!r}"
              + (f" em {args.processo}" if args.processo else "") + ".")
        return

    print(f"[busca] {len(achados)} resultado(s) para {args.termo!r}:\n")
    for a in achados:
        proc = a["proc_id"] or "(sem ficha)"
        carimbo = ""
        if a["num_pje"]:
            pag = f" Pag.{a['pag_doc']}" if a["pag_doc"] else ""
            carimbo = f" · Num. {a['num_pje']}{pag}"
        trecho = re.sub(r"\s+", " ", a["trecho"] or "").strip()
        print(f"  {proc} · {a['cnj']} · fls. {a['pagina']}{carimbo}")
        print(f"      {trecho}\n")


if __name__ == "__main__":
    main()
