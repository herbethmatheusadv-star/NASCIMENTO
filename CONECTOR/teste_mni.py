#!/usr/bin/env python3
"""
teste_mni.py — o envelope do MNI, conferido contra o WSDL REAL do TJPA.

Nada aqui toca a rede e nada precisa de credencial: monta o XML e confere.
O que este teste protege e o erro mais provavel de quem escreve SOAP a mao —
namespace errado no filho. O WSDL do TJPA poe `form="qualified"` em CADA
elemento de `tipoConsultarProcesso`, o que SOBREPOE o `elementFormDefault` do
schema. Quem le rapido escreve os filhos sem prefixo e leva um fault opaco.

E protege a promessa da Emenda 05: a senha nao vaza para repr, str nem log.
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mni
import regras

falhas = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado!r}")
        print(f"          obtido  : {obtido!r}")
        falhas.append(nome)

print("=" * 74)
print("  MNI — envelope contra o contrato do WSDL")
print("=" * 74)

CRED = mni.Credencial("12345678901", "sen" + "ha-secreta-do-pje")

print("\n=== 1. A senha nao vaza ===")
check("repr nao mostra o segredo", "secreta" in repr(CRED), False)
check("str nao mostra o segredo", "secreta" in str(CRED), False)
check("repr mascara o CPF", "12345678901" in repr(CRED), False)
check("f-string usa __str__ (nao vaza)", "secreta" in f"{CRED}", False)

print("\n=== 2. Estrutura do envelope de consultarProcesso ===")
env = mni._envelope("consultarProcesso", [
    ("idConsultante", CRED.cpf),
    ("senhaConsultante", CRED._segredo),
    ("numeroProcesso", "08050588720258140040"),
    ("movimentos", True),
    ("incluirDocumentos", False),
])
raiz = ET.fromstring(env)          # se nao for XML valido, quebra aqui
check("envelope e XML valido", raiz.tag,
      "{http://schemas.xmlsoap.org/soap/envelope/}Envelope")

corpo = raiz.find("{http://schemas.xmlsoap.org/soap/envelope/}Body")
op = list(corpo)[0]
check("wrapper esta no namespace do SERVICO",
      op.tag, "{http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/}consultarProcesso")

filhos = {f.tag: (f.text or "") for f in op}
# o ponto do teste: qualified, no namespace dos TIPOS
tip = "{http://www.cnj.jus.br/tipos-servico-intercomunicacao-2.2.2}"
check("idConsultante e qualified no ns dos TIPOS",
      filhos.get(tip + "idConsultante"), "12345678901")
check("numeroProcesso e qualified no ns dos TIPOS",
      filhos.get(tip + "numeroProcesso"), "08050588720258140040")
check("nenhum filho ficou sem namespace",
      [t for t in filhos if not t.startswith("{")], [])
check("booleano vira 'true'/'false' (nao 'True')",
      filhos.get(tip + "movimentos"), "true")
check("False tambem e enviado (nao sumiu)",
      filhos.get(tip + "incluirDocumentos"), "false")

print("\n=== 3. R7 no envelope ===")
for proibida in ("confirmar" + "Recebimento", "entregar" + "ManifestacaoProcessual",
                 "consultarTeorComunicacao", "operacaoInventada"):
    try:
        mni._envelope(proibida, [])
        check(f"{proibida} deveria ser barrada", "nao barrou", "ViolacaoR7")
    except regras.ViolacaoR7:
        check(f"{proibida} barrada por ViolacaoR7", True, True)

print("\n=== 4. As unicas funcoes de operacao que EXISTEM ===")
publicas = {n for n in dir(mni) if n.startswith("consultar") or n.startswith("confirmar")
            or n.startswith("entregar")}
check("existem exatamente as 3 consultas", sorted(publicas),
      ["consultar_alteracao", "consultar_avisos_pendentes", "consultar_processo"])
check("nao existe funcao de tomar ciencia",
      hasattr(mni, "confirmar_recebimento"), False)
check("nao existe funcao de peticionar",
      hasattr(mni, "entregar_manifestacao_processual"), False)

print("\n=== 5. Validacao do numero CNJ ===")
for ruim in ("123", "0805058-87.2025.8.14", ""):
    try:
        mni.consultar_processo(CRED, ruim)
        check(f"numero invalido {ruim!r} deveria falhar", "passou", "ValueError")
    except ValueError:
        check(f"numero invalido {ruim!r} barrado antes da rede", True, True)
    except Exception as e:
        check(f"numero invalido {ruim!r} barrado antes da rede",
              f"{type(e).__name__}", "ValueError")

print("\n=== 6. Escape de XML (numero nao injeta) ===")
env2 = mni._envelope("consultarAlteracao", [("idConsultante", 'a<b&c"d')])
ET.fromstring(env2)
check("caractere especial nao quebra o XML", "&lt;b&amp;c" in env2.decode(), True)

print("\n=== 7. Endpoints do contrato (lidos do WSDL, nao inventados) ===")
check("1o grau", mni.ENDPOINTS[1], "https://pje.tjpa.jus.br/pje/intercomunicacao")
check("2o grau", mni.ENDPOINTS[2], "https://pje.tjpa.jus.br/pje-2g/intercomunicacao")
check("soapAction segue o padrao do namespace",
      f"{mni.NS_SERVICO}consultarProcesso",
      "http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/consultarProcesso")

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Envelope confere com o WSDL. Falta o teste decisivo — com a senha dele.")
print("=" * 74)
