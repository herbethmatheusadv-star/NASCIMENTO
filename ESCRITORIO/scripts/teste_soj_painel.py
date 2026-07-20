# -*- coding: utf-8 -*-
"""teste_soj_painel.py — helpers puros do painel (sem gerar HTML nem ler disco)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_painel as pn

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 60)
print("  soj_painel — helpers")
print("=" * 60)

print("\n=== _data ===")
check("ISO vira date", pn._data("2026-07-22"), date(2026, 7, 22))
check("vazio vira None", pn._data(""), None)
check("lixo vira None", pn._data("amanha"), None)

print("\n=== _cliente (resolve CLI-XXXX, limpa 'a cadastrar') ===")
m = {"CLI-0006": "DANIEL AUGUSTO"}
check("resolve pelo mapa", pn._cliente("[[CLI-0006]]", m), "DANIEL AUGUSTO")
check("sem mapa mantém o codigo", pn._cliente("[[CLI-9999]]", {}), "CLI-9999")
check("'a cadastrar' vira rotulo curto",
      pn._cliente("(a cadastrar — cadastro assistido)"), "cliente a cadastrar")
check("vazio vira travessao", pn._cliente(""), "—")

print("\n=== _urg (urgencia por dias) ===")
check("vencido", pn._urg(-2), ("c-dan", "vencido há 2d"))
check("hoje", pn._urg(0), ("c-dan", "hoje"))
check("amanha", pn._urg(1), ("c-dan", "amanhã"))
check("em 5 dias = warning", pn._urg(5)[0], "c-war")
check("em 10 dias = accent", pn._urg(10)[0], "c-acc")

print("\n=== _jsq (texto seguro no onclick) ===")
check("tira aspas e barras",
      pn._jsq("d'agua \\x\nfim"), "dagua x fim")

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. Helpers do painel OK.")
print("=" * 60)
