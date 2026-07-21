# -*- coding: utf-8 -*-
"""Testes do soj_financeiro — a conversão de moeda BR e a agregação do razão."""
import soj_financeiro as fin

fin.soj.console_utf8()
ok = falhas = 0


def checa(nome, obtido, esperado):
    global ok, falhas
    if obtido == esperado:
        ok += 1
        print(f"  ok  {nome}")
    else:
        falhas += 1
        print(f"  XX  {nome}: obtido {obtido!r}, esperado {esperado!r}")


print("— conversão de moeda (R$ X.XXX,YY → float) —")
checa("milhar+centavo", fin._valor("R$ 2.728,19"), 2728.19)
checa("redondo", fin._valor("R$ 900,00"), 900.0)
checa("dezena de milhar", fin._valor("R$ 12.211,88"), 12211.88)
checa("travessão vazio", fin._valor("—"), 0.0)
checa("célula vazia", fin._valor(""), 0.0)
checa("sem símbolo", fin._valor("682,28"), 682.28)

print("\n— agregação do razão —")
r = fin.resumo()
checa("resumo é dict", isinstance(r, dict), True)
checa("recebido é número", isinstance(r["recebido"], float), True)
checa("recebido > 0 (há lançamentos)", r["recebido"] > 0, True)
checa("a_vencer é lista", isinstance(r["a_vencer"], list), True)
checa("contratos_a_formalizar é lista",
      isinstance(r["contratos_a_formalizar"], list), True)

print("\n— coerência: soma das linhas 'recebido' bate com o agregado —")
soma = round(sum(l["valor"] for l in fin.lancamentos()
                 if l["status"] == "recebido"), 2)
checa("recebido = Σ linhas recebido", r["recebido"], soma)

print(f"\n{ok} ok, {falhas} falha(s).")
raise SystemExit(1 if falhas else 0)
