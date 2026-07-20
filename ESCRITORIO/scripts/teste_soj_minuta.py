# -*- coding: utf-8 -*-
"""teste_soj_minuta.py — citacao e limpeza de rodape (sem PDF real)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_minuta as m

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 60)
print("  soj_minuta — citacao + limpeza de rodape")
print("=" * 60)

check("_cita intervalo", m._cita({"p_ini": 600, "p_fim": 603,
      "num": "181885273", "data": "04/07/2026"}),
      "fls. 600–603 · Num. 181885273 · 04/07/2026")
check("_cita pagina unica + s/data",
      m._cita({"p_ini": 4, "p_fim": 4, "num": "X", "data": ""}),
      "fls. 4 · Num. X · s/data")

paginas = {
    1: ("Do que se trata a peca.\n"
        "Assinado eletronicamente por: FULANO DE TAL - 01/01/2026 10:00:00\n"
        "https://pje.tjpa.jus.br/x\nNumero do documento: 123\nNum. 999 - Pag. 1"),
    2: "Continuacao do corpo.",
}
tr = m._texto_peca(paginas, 1, 2)
check("tira o rodape (assinatura/URL/Num-Pag)",
      ("Assinado eletronicamente" not in tr and "pje.tjpa" not in tr), True)
check("preserva o corpo das duas paginas",
      ("Do que se trata" in tr and "Continuacao do corpo" in tr), True)

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. Citacao e limpeza OK.")
print("=" * 60)
