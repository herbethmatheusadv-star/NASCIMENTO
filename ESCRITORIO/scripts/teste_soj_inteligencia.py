# -*- coding: utf-8 -*-
"""teste_soj_inteligencia.py — parser da tabela da capa + relevancia (sem PDF)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_inteligencia as intel

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


# capa real (formato do PJe): Num<sp>data / hora / nome(multi-linha) / tipo
CAPA = """Documentos
Id.
Data
Documento
Tipo
139782043 26/03/2025
20:32
Petição Inicial
Petição Inicial
139782050 26/03/2025
20:32
0.1. 2024-04-16 - PROCURAÇÃO COOPVALE -
Aualizada 2024
Documento de Identificação
Número do documento: 250326...
Num. 139782043 - Pág. 1
"""

print("=" * 60)
print("  soj_inteligencia — tabela da capa + relevancia")
print("=" * 60)

capa = intel.texto_capa({1: CAPA})
check("texto_capa corta o rodape", "Número do documento" in capa, False)

tab = intel.parse_tabela_documentos(capa)
check("achou as 2 pecas", sorted(tab), ["139782043", "139782050"])
check("peca 1 nome=tipo (linha unica)", tab["139782043"],
      {"data": "26/03/2025", "nome": "Petição Inicial", "tipo": "Petição Inicial"})
check("peca 2 nome multi-linha, tipo na ultima",
      (tab["139782050"]["tipo"], "PROCURAÇÃO" in tab["139782050"]["nome"]),
      ("Documento de Identificação", True))

print("\n=== relevancia (piramide de leitura) ===")
check("peticao inicial -> alta", intel.relevancia("Petição Inicial", ""), "alta")
check("sentenca -> alta", intel.relevancia("Sentença", ""), "alta")
check("certidao -> baixa", intel.relevancia("Certidão de intimação", ""), "baixa")
check("identificacao/procuracao -> baixa",
      intel.relevancia("Documento de Identificação", "procuração"), "baixa")
check("desconhecido -> media", intel.relevancia("Ofício", "algo"), "media")

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. Tabela da capa e relevancia OK.")
print("=" * 60)
