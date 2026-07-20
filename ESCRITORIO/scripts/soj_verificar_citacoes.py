# -*- coding: utf-8 -*-
"""
soj_verificar_citacoes.py — CONFERE as citacoes de autos de uma peca (Fase 3;
/soj-verificar-citacoes do PLANO_SOJ, linha 274).

Antes de protocolar, checa se cada "fls. X" e cada "Num. Y" que a peca cita
existe DE VERDADE nos autos indexados — e localiza os TRECHOS entre aspas na
folha certa. E o antidoto contra citar pagina errada (o erro que corroi a
credibilidade de uma peca).

  O QUE CONFERE (contra index/soj.sqlite, por processo)

  - fls. N ......... a pagina N existe nos autos? (e a que Num./peca ela pertence)
  - fls. N/M ....... o intervalo cabe nos autos?
  - Num. NNN ....... existe peca com esse id? (em que folhas)
  - "trecho citado"  o texto entre aspas aparece mesmo? em QUE folha? bate com a
                     fls. que voce citou por perto?

  CAVEAT honesto: "fls." aqui = pagina do PDF integral dos autos. Se a peca usa
  outra numeracao, a ancora segura e o carimbo do PJe (Num./Pag.). Por isso o
  verificador cruza os dois: se voce escreve "fls. 31 (Num. 139782054)", ele
  confirma que a folha 31 e mesmo daquela peca.

Uso:
  python soj_verificar_citacoes.py MINUTA.md
  python soj_verificar_citacoes.py MINUTA.md --cnj 0805058-87.2025.8.14.0040
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

import soj_lib as soj

DB = soj.ROOT / "index" / "soj.sqlite"

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
# fls. 31 | fl. 31 | fls 31/33 | e-fls. 31 | às fls. 31
# (?:e-?)? torna o prefixo "e"/"e-" OPCIONAL — sem isso "e-?" exigia o 'e' e
# "fls. 31" nao casava (so "e-fls"). Pego no teste em 16/07/2026.
RE_FLS = re.compile(r"\b(?:e-?)?fls?\.?\s*(\d+)(?:\s*/\s*(\d+))?", re.I)
# Num. 139782054 | ID 139782054 | id. 139782054  (ids do PJe tem 6+ digitos)
RE_NUM = re.compile(r"\b(?:num|id)\.?\s*(\d{6,})", re.I)
# fls. 31 seguido de Num. na mesma frase (checagem cruzada)
RE_FLS_NUM = re.compile(r"\b(?:e-?)?fls?\.?\s*(\d+)\D{0,40}?\bnum\.?\s*(\d{6,})", re.I)
# trechos entre aspas (retas, curvas, angulares)
RE_ASPAS = re.compile(r"[\"“«]([^\"”»]{12,})[\"”»]")


def norm_cnj(t: str) -> str:
    return re.sub(r"\D", "", t or "")


def _colapsar(t: str) -> str:
    """normaliza + remove TUDO que nao e alfanumerico (tolera espaco, quebra,
    hifenizacao e pontuacao entre o PDF e a peca)."""
    return re.sub(r"[^a-z0-9]", "", soj.normaliza(t))


def extrair_citacoes(texto: str) -> dict:
    """{fls:set, ranges:set, nums:set, fls_num:list} — puro, testavel."""
    fls, ranges, nums, fls_num = set(), set(), set(), []
    for m in RE_FLS.finditer(texto):
        fls.add(int(m.group(1)))
        if m.group(2):
            ranges.add((int(m.group(1)), int(m.group(2))))
    for m in RE_NUM.finditer(texto):
        nums.add(m.group(1))
    for m in RE_FLS_NUM.finditer(texto):
        fls_num.append((int(m.group(1)), m.group(2)))
    return {"fls": fls, "ranges": ranges, "nums": nums, "fls_num": fls_num}


def extrair_aspas(texto: str, min_palavras: int = 5) -> list[str]:
    out = []
    for m in RE_ASPAS.finditer(texto):
        trecho = re.sub(r"\s+", " ", m.group(1)).strip()
        if len(trecho.split()) >= min_palavras:
            out.append(trecho)
    return out


def ler_peca(caminho: Path) -> str:
    if caminho.suffix.lower() == ".docx":
        try:
            import docx  # python-docx
        except ImportError:
            print("[verificar] .docx precisa de python-docx (pip install python-docx)."
                  " Salve como .md/.txt ou instale.")
            sys.exit(1)
        return "\n".join(p.text for p in docx.Document(str(caminho)).paragraphs)
    return caminho.read_text(encoding="utf-8", errors="ignore")


def _paginas_do_processo(con, cnj_fmt: str) -> dict:
    """{pagina: (num_pje, pag_doc, texto_colapsado)} do processo."""
    out = {}
    for r in con.execute(
            "SELECT pagina,num_pje,pag_doc,texto FROM paginas WHERE cnj=?",
            (cnj_fmt,)):
        out[r[0]] = (r[1], r[2], _colapsar(r[3]))
    return out


def _cnj_no_index(con, cnj: str) -> str | None:
    alvo = norm_cnj(cnj)
    for (c,) in con.execute("SELECT DISTINCT cnj FROM paginas"):
        if norm_cnj(c) == alvo:
            return c
    return None


def verificar(caminho: Path, cnj_arg: str) -> int:
    if not DB.exists():
        print("[verificar] index nao existe. Rode: python soj_reindex.py")
        return 2
    texto = ler_peca(caminho)
    cnj = cnj_arg or (RE_CNJ.search(texto).group(0) if RE_CNJ.search(texto) else "")
    if not cnj:
        print("[verificar] nao achei o CNJ na peca. Passe --cnj <numero>.")
        return 2

    con = sqlite3.connect(DB)
    try:
        cnj_fmt = _cnj_no_index(con, cnj)
        if not cnj_fmt:
            print(f"[verificar] {cnj} nao esta no index. Importe: "
                  f"python soj_import.py --cnj {cnj} && python soj_reindex.py")
            return 2
        paginas = _paginas_do_processo(con, cnj_fmt)
        proc_id = con.execute("SELECT proc_id FROM paginas WHERE cnj=? LIMIT 1",
                              (cnj_fmt,)).fetchone()[0]
    finally:
        con.close()

    maxpg = max(paginas) if paginas else 0
    por_num: dict[str, list[int]] = {}
    for p, (num, _pag, _t) in paginas.items():
        if num:
            por_num.setdefault(num, []).append(p)

    cit = extrair_citacoes(texto)
    aspas = extrair_aspas(texto)
    print(f"[verificar] peca: {caminho.name} | {cnj} ({proc_id or '-'}) | "
          f"autos: {maxpg} paginas")
    print("=" * 66)

    problemas = 0

    # fls.
    for n in sorted(cit["fls"]):
        if n in paginas:
            num, pag, _ = paginas[n]
            sel = f" (= Num. {num}{f', Pag. {pag}' if pag else ''})" if num else ""
            print(f"  fls. {n:<6} CONFERE{sel}")
        else:
            problemas += 1
            print(f"  fls. {n:<6} FORA — os autos tem {maxpg} paginas")

    # intervalos
    for a, b in sorted(cit["ranges"]):
        ok = a in paginas and b in paginas
        if ok:
            print(f"  fls. {a}/{b}   CONFERE (intervalo cabe)")
        else:
            problemas += 1
            print(f"  fls. {a}/{b}   FORA — os autos tem {maxpg} paginas")

    # Num.
    for num in sorted(cit["nums"]):
        if num in por_num:
            ps = sorted(por_num[num])
            faixa = f"fls. {ps[0]}" + (f"-{ps[-1]}" if ps[-1] != ps[0] else "")
            print(f"  Num. {num:<12} CONFERE (= {faixa})")
        else:
            problemas += 1
            print(f"  Num. {num:<12} NAO ACHADO neste processo")

    # checagem cruzada fls.+Num.
    for n, num in cit["fls_num"]:
        real = paginas.get(n, (None, None, None))[0]
        if real == num:
            print(f"  fls. {n} + Num. {num}: CONFERE (a folha e mesmo dessa peca)")
        elif n in paginas:
            problemas += 1
            print(f"  fls. {n} + Num. {num}: DIVERGE — a fls. {n} e da peca "
                  f"Num. {real}, nao {num}")

    # trechos entre aspas
    if aspas:
        print("-" * 66)
    for tr in aspas:
        alvo = _colapsar(tr)
        achados = [p for p, (_n, _pg, tx) in paginas.items() if alvo and alvo in tx]
        amostra = (tr[:52] + "...") if len(tr) > 55 else tr
        if achados:
            fls_str = ", ".join(f"fls. {p}" for p in sorted(achados)[:4])
            print(f'  trecho "{amostra}"\n      localizado em {fls_str}')
        else:
            problemas += 1
            print(f'  trecho "{amostra}"\n      NAO LOCALIZADO nos autos — conferir')

    print("=" * 66)
    if problemas:
        print(f"[verificar] {problemas} ponto(s) a conferir antes de protocolar.")
    else:
        print("[verificar] todas as citacoes conferem. Pode citar com seguranca.")
    return 1 if problemas else 0


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Confere citacoes de autos de uma peca.")
    ap.add_argument("peca", help="arquivo .md/.txt/.docx com a peca")
    ap.add_argument("--cnj", default="", help="CNJ do processo (senao, le da peca)")
    args = ap.parse_args()
    p = Path(args.peca)
    if not p.exists():
        print(f"[verificar] arquivo nao encontrado: {p}")
        sys.exit(2)
    sys.exit(verificar(p, args.cnj))


if __name__ == "__main__":
    main()
