# -*- coding: utf-8 -*-
"""teste_soj_prazos.py — a matemática do motor de prazos. Um erro aqui é um prazo
perdido, então este teste é a rede de segurança do watchdog."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_prazos as pz

pz.soj.console_utf8()   # console Windows lê "→" e acentos sem quebrar
falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 62)
print("  soj_prazos — cálculo de prazos")
print("=" * 62)

print("\n=== Páscoa (Meeus/Butcher) ===")
check("Páscoa 2024", pz.pascoa(2024), date(2024, 3, 31))
check("Páscoa 2025", pz.pascoa(2025), date(2025, 4, 20))
check("Páscoa 2026", pz.pascoa(2026), date(2026, 4, 5))

print("\n=== Feriados móveis 2026 (derivados da Páscoa) ===")
nac = pz.feriados_nacionais(2026)
check("Sexta-feira Santa 2026 (03/04) é feriado", date(2026, 4, 3) in nac, True)
check("Carnaval terça 2026 (17/02) é feriado", date(2026, 2, 17) in nac, True)
check("Corpus Christi 2026 (04/06) é feriado", date(2026, 6, 4) in nac, True)
check("Consciência Negra (20/11) é feriado", date(2026, 11, 20) in nac, True)

print("\n=== eh_util ===")
check("Corpus Christi não é útil", pz.eh_util(date(2026, 6, 4)), False)
check("Sexta Santa não é útil", pz.eh_util(date(2026, 4, 3)), False)
check("sábado não é útil", pz.eh_util(date(2026, 3, 7)), False)
check("quinta comum é útil", pz.eh_util(date(2026, 3, 5)), True)
check("dentro do recesso (05/01) não é útil", pz.eh_util(date(2026, 1, 5)), False)

print("\n=== vencimento em dias ÚTEIS (exclui o dia do começo — art. 224) ===")
# 04/03/2026 é quarta; +5 úteis, sem feriado na janela → 11/03 (quarta)
check("04/03 (qua) + 5 úteis = 11/03", pz.vencimento(date(2026, 3, 4), 5, "uteis"),
      date(2026, 3, 11))
# o dia do termo não conta
check("termo não conta (1 útil após quarta = quinta)",
      pz.vencimento(date(2026, 3, 4), 1, "uteis"), date(2026, 3, 5))

print("\n=== RECESSO forense suspende o prazo processual (art. 220) ===")
# 18/12/2025 (qui) + 5 úteis: conta 19/12, pula 20/12–20/01, retoma 21/01 → 26/01
check("18/12 + 5 úteis pula o recesso → 26/01/2026",
      pz.vencimento(date(2025, 12, 18), 5, "uteis"), date(2026, 1, 26))

print("\n=== dias CORRIDOS: protrai fim de semana/feriado, mas NÃO o recesso ===")
# 04/03 + 3 corridos = 07/03 (sáb) → protrai p/ 09/03 (seg)
check("04/03 + 3 corridos protrai sáb → 09/03",
      pz.vencimento(date(2026, 3, 4), 3, "corridos"), date(2026, 3, 9))
# 15/12 + 10 corridos = 25/12 (feriado) → protrai p/ 26/12 (recesso NÃO conta p/ corridos)
check("corridos ignora recesso: 15/12 + 10 → 26/12/2025",
      pz.vencimento(date(2025, 12, 15), 10, "corridos"), date(2025, 12, 26))

print("=" * 62)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Tudo verde. O cálculo de prazos está correto.")
print("=" * 62)
