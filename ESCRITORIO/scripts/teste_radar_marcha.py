#!/usr/bin/env python3
"""teste_radar_marcha.py — a logica do detector diario, sem rede.

Protege a derivacao da sigla do tribunal a partir do CNJ e a regra do 'mexeu
desde a regua'. Nao chama o DataJud (isso e --sem-rede na pratica)."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import radar_marcha as rm

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado {esperado!r}, veio {obtido!r}")
        falhas.append(nome)


print("=" * 74)
print("  radar_marcha — logica do detector diario (offline)")
print("=" * 74)

print("\n=== 1. sigla do tribunal a partir do CNJ ===")
check("TRT-8 (trabalho, J=5, TR=08)", rm.sigla_do_cnj("0000483-10.2025.5.08.0130"), "TRT8")
check("TRT-1 (J=5, TR=01)", rm.sigla_do_cnj("0000001-00.2025.5.01.0001"), "TRT1")
check("TJPA (estadual, J=8, TR=14)", rm.sigla_do_cnj("0808548-83.2026.8.14.0040"), "TJPA")
check("TJMA (estadual, J=8, TR=10)", rm.sigla_do_cnj("0805885-75.2026.8.10.0040"), "TJMA")
check("TRF-1 (federal, J=4, TR=01)", rm.sigla_do_cnj("0000001-00.2025.4.01.0001"), "TRF1")
check("estadual desconhecido -> None", rm.sigla_do_cnj("0000001-00.2025.8.99.0001"), None)
check("lixo -> None", rm.sigla_do_cnj("nao-e-cnj"), None)

print("\n=== 2. digitos do CNJ ===")
check("so digitos", rm.so_digitos("0000483-10.2025.5.08.0130"), "00004831020255080130")

print("\n=== 3. regua = peca mais nova do baseline ===")
base = {"pecas": [{"data": "2025-11-11T09:00:00"}, {"data": "2026-03-03T17:42:00"},
                  {"data": "2026-02-10T10:00:00"}]}
check("regua e a data mais nova", rm.regua_do_baseline(base), date(2026, 3, 3))
check("baseline sem datas -> None", rm.regua_do_baseline({"pecas": [{}]}), None)

print("\n=== 4. precisa_captura: mexeu desde a regua? ===")
r = date(2026, 3, 3)
check("movimento DEPOIS da regua -> captura", rm.precisa_captura(r, date(2026, 3, 10)), True)
check("movimento ANTES da regua -> nao", rm.precisa_captura(r, date(2026, 2, 1)), False)
check("movimento NA regua -> nao", rm.precisa_captura(r, date(2026, 3, 3)), False)
check("sem movimento -> nao afirma", rm.precisa_captura(r, None), False)
check("sem regua -> nao afirma", rm.precisa_captura(None, date(2026, 3, 10)), False)

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Detector diario confere. Sabe QUE mexeu (DataJud), sem login.")
print("=" * 74)
