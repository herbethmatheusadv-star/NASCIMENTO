#!/usr/bin/env python3
"""teste_trt8_api.py — o cliente REST do PJe novo, conferido SEM rede e SEM token.

Protege o contrato lido na sessao logada (MAPA_PJE.md §13.9), a allowlist de
rotas (R7 camada 2) e a promessa da Emenda 05 (o Bearer nao vaza para repr/str).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instancias
import regras
import trt8_api as api

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado {esperado!r}, veio {obtido!r}")
        falhas.append(nome)


def check_levanta(nome, exc, fn, *a):
    try:
        fn(*a)
    except exc:
        print(f"  [ok ] {nome}")
        return
    print(f"  [FALHA] {nome} — nao levantou {exc.__name__}")
    falhas.append(nome)


print("=" * 74)
print("  trt8_api — cliente REST do PJe novo (offline)")
print("=" * 74)

print("\n=== 1. base so para instancias PDPJ ===")
check("trt8 da o host da API", api.base_host(instancias.REGISTRO["trt8"]),
      "https://pje.trt8.jus.br")
check_levanta("tjpa (Seam, sem PDPJ) recusa", RuntimeError,
              api.base_host, instancias.REGISTRO["tjpa"])

print("\n=== 2. allowlist de rotas (R7 camada 2) ===")
for rota in ["/pje-comum-api/api/paineladvogado/837986/processos",
             "/pje-comum-api/api/paineladvogado/837986/totalizadores",
             "/pje-comum-api/api/paineladvogado/837986/orgaojulgadores",
             "/pje-comum-api/api/parametros/PARAMETRO_X"]:
    check(f"permitida: ...{rota[-24:]}", api._rota_permitida(rota), True)
# a rota de avisos/expedientes fica FORA de proposito (candidata a gatilho de ato)
check("avisos/expedientes NAO entra",
      api._rota_permitida("/pje-comum-api/api/quadroavisos/"), False)
check("rota desconhecida NAO entra",
      api._rota_permitida("/pje-comum-api/api/qualquer/coisa"), False)

print("\n=== 3. _get recusa rota fora da allowlist ANTES da rede ===")
sess = api.Sessao("https://pje.trt8.jus.br", "tok" + "en-de-mentira")
check_levanta("rota fora da allowlist levanta ViolacaoR7", regras.ViolacaoR7,
              api._get, sess, "/pje-comum-api/api/quadroavisos/")

print("\n=== 4. o token nao vaza (Emenda 05) ===")
check("repr esconde o token", "mentira" in repr(sess), False)
check("str esconde o token", "mentira" in str(sess), False)

print("\n=== 5. normalizacao para a ficha PROC ===")
amostra = {"id": 111, "numeroProcesso": "0000000-00.2025.5.08.0130",
           "classeJudicial": "ATSum", "descricaoOrgaoJulgador": "1a VT de X",
           "nomeParteAutora": "FULANO DE TAL", "nomeParteRe": "EMPRESA Y LTDA",
           "dataAutuacao": "2025-04-14T09:44:06.499", "dataArquivamento": None,
           "segredoDeJustica": False, "codigoStatusProcesso": "DISTRIBUIDO"}
n = api._normalizar(amostra)
check("numero", n["numero"], "0000000-00.2025.5.08.0130")
check("classe", n["classe"], "ATSum")
check("autuacao cortada em YYYY-MM-DD", n["autuacao"], "2025-04-14")
check("arquivamento None quando ausente", n["arquivamento"], None)
check("segredo vira bool", n["segredo"], False)

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Cliente REST confere. Falta o teste decisivo — com o Bearer do titular.")
print("=" * 74)
