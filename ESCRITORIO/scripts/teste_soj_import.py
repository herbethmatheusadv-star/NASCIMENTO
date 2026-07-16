# -*- coding: utf-8 -*-
"""
teste_soj_import.py — as funcoes puras do importador/reindexador, sem PDF nem DB.

Testa o que pode quebrar sem fitz e sem SQLite: ler o carimbo Num./Pag., montar
o texto com marcadores, recuperar as paginas de volta (round-trip), agrupar as
pecas por Num, e normalizar CNJ. Dados sinteticos, nenhum autos real.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_import as imp
import soj_reindex as rdx

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}")
        print(f"        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 64)
print("  soj_import — funcoes puras (sem PDF, sem DB)")
print("=" * 64)

print("\n=== 1. carimbo do rodape do PJe (Num. - Pag.) ===")
rodape = ("...decisao...\nNumero do documento: 26032310405840200000152820329\n"
          "Num. 171591788 - Pág. 1\n")
check("le Num e Pag", imp.parse_num_pag(rodape), ("171591788", 1))
check("sem carimbo -> (None, None)", imp.parse_num_pag("nada aqui"), (None, None))
# se o corpo cita "Num. 999 - Pag. 9" e o RODAPE traz outro, vale o rodape (ultimo)
doismesmo = "cf. Num. 999 - Pág. 9 no corpo\n...\nNum. 171591788 - Pág. 3\n"
check("dois carimbos -> vale o do rodape (ultimo)",
      imp.parse_num_pag(doismesmo), ("171591788", 3))
check("aceita 'Pag' sem acento", imp.parse_num_pag("Num. 5 - Pag. 2"), ("5", 2))

print("\n=== 2. marcador de pagina ===")
check("marcador canonico", imp.marcador(7), "===[p.7]===")

print("\n=== 3. montar texto + round-trip (importa -> reindexa) ===")
paginas = [{"n": 1, "texto": "Peticao inicial\ncorpo um"},
           {"n": 2, "texto": "Contestacao\ncorpo dois"}]
txt = imp.montar_texto(paginas)
check("tem os dois marcadores",
      ("===[p.1]===" in txt and "===[p.2]===" in txt), True)
recuperado = rdx.paginas_do_texto(txt)
check("round-trip recupera pagina 1",
      recuperado.get(1), "Peticao inicial\ncorpo um")
check("round-trip recupera pagina 2",
      recuperado.get(2), "Contestacao\ncorpo dois")

print("\n=== 4. agrupa pecas por Num (sem fatiar o PDF) ===")
por_pagina = [{"p": 1, "num": "A"}, {"p": 2, "num": "A"},
              {"p": 3, "num": "B"}, {"p": 4, "num": "B"}, {"p": 5, "num": "B"},
              {"p": 6, "num": "A"}]
docs = imp.montar_documentos(por_pagina)
check("3 pecas (A:1-2, B:3-5, A:6)", [(d["num"], d["p_ini"], d["p_fim"]) for d in docs],
      [("A", 1, 2), ("B", 3, 5), ("A", 6, 6)])

print("\n=== 5. normaliza CNJ ===")
check("so digitos", imp.norm_cnj("0805058-87.2025.8.14.0040"),
      "08050588720258140040")

print("\n" + "=" * 64)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Tudo verde. Parser e round-trip OK — falta so rodar nos autos reais.")
print("=" * 64)
