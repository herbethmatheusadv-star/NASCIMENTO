# -*- coding: utf-8 -*-
"""teste_soj_pendencias.py — o gestor de pendências (helpers + derivação real)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_pendencias as pd

pd.soj.console_utf8()
falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


def checkv(nome, cond):
    check(nome, bool(cond), True)


print("=" * 60)
print("  soj_pendencias — gestor de pendências")
print("=" * 60)

print("\n=== _norm ===")
check("tira aspas e baixa a caixa", pd._norm('"Assinada"'), "assinada")
check("None vira vazio", pd._norm(None), "")

print("\n=== resumo (contagem por tipo) ===")
amostra = [{"tipo": "procuração"}, {"tipo": "procuração"}, {"tipo": "protocolo"}]
check("conta por tipo", pd.resumo(amostra),
      {"procuração": 2, "protocolo": 1})

print("\n=== derivação do acervo real ===")
pend = pd.pendencias_do_acervo()
checkv("retorna pendências (>0)", len(pend) > 0)
checkv("toda pendência tem tipo/ref/o_que/quem/status",
       all(all(k in p for k in ("tipo", "ref", "o_que", "quem", "status")) for p in pend))
checkv("há procuração pendente (clientes sem procuração assinada)",
       any(p["tipo"] == "procuração" for p in pend))
checkv("há protocolo (minuta pronta em AUTOS)",
       any(p["tipo"] == "protocolo" for p in pend))
checkv("nenhuma procuração 'assinada' entra na fila",
       all("assinada" not in p["o_que"] for p in pend if p["tipo"] == "procuração"))

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. O gestor de pendências OK.")
print("=" * 60)
