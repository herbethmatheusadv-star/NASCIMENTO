# -*- coding: utf-8 -*-
"""teste_soj_verificar.py — os parsers de citacao, sem index nem peca real."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_verificar_citacoes as v

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 60)
print("  soj_verificar_citacoes — parsers")
print("=" * 60)

txt = ("Conforme fls. 31 (Num. 139782054), e ainda as fls. 123/125. "
       "Ver ID 175489381. Cf. e-fls. 9. Diz a decisao: "
       "“acesso pelo Sicoob Central Rio a todos os dados contabeis”.")
c = v.extrair_citacoes(txt)
check("fls simples", sorted(c["fls"]), [9, 31, 123])
check("intervalo", sorted(c["ranges"]), [(123, 125)])
check("nums (Num e ID, 6+ digitos)", sorted(c["nums"]), ["139782054", "175489381"])
check("cruzado fls+Num", c["fls_num"], [(31, "139782054")])

asp = v.extrair_aspas(txt)
check("aspas curvas com 5+ palavras", len(asp), 1)
check("conteudo da aspa", asp[0].startswith("acesso pelo Sicoob"), True)

check("colapsar tolera pontuacao/acento/espaco",
      v._colapsar("Petição  In-\ncial!"), "peticaoincial")
check("norm_cnj so digitos", v.norm_cnj("0805058-87.2025.8.14.0040"),
      "08050588720258140040")

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. Parsers de citacao OK.")
print("=" * 60)
