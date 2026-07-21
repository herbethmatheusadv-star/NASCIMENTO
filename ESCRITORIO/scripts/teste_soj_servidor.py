# -*- coding: utf-8 -*-
"""
teste_soj_servidor.py — leva a R7 para dentro do servidor do painel.

Nao basta o CONECTOR ser so-leitura: o servidor e uma porta nova, entao ele
tambem precisa provar que (1) so roda a allowlist de leitura e (2) /ver nao
escapa de AUTOS/ e PROCESSOS/. Sobe o servidor de verdade numa porta efemera e
ataca as rotas.
"""
import json
import sys
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_servidor as sv

FALHAS = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        FALHAS.append(nome)


def checkv(nome, cond):
    check(nome, bool(cond), True)


print("=" * 64)
print("  soj_servidor — R7 na porta nova")
print("=" * 64)

print("\n=== 1. Allowlist so tem leitura (sem vocabulario de acao) ===")
PROIBIDO = ("assin", "peticion", "protocol", "ciencia", "ciência",
            "confirmarrecebimento", "entregarmanifest", "baixar", "download")
alvo = " ".join(sv.ACOES).lower() + " " + " ".join(sv.SCRIPTS_PERMITIDOS).lower()
for termo in PROIBIDO:
    checkv(f"'{termo}' nao aparece na allowlist", termo not in alvo)
check("as acoes sao exatamente as 5 de leitura", sorted(sv.ACOES),
      ["audiencia", "buscar", "inteligencia", "reindexar", "resumo"])

print("\n=== 2. Todo comando montado usa um script permitido ===")
for nome, (_, monta, _exige) in sv.ACOES.items():
    script = monta("0000000-00.0000.0.00.0000", "termo")[0]
    checkv(f"{nome} -> {script} esta em SCRIPTS_PERMITIDOS",
           script in sv.SCRIPTS_PERMITIDOS)

print("\n=== 3. Servidor no ar: rotas e sandbox ===")
srv = ThreadingHTTPServer(("127.0.0.1", 0), sv.Painel)
porta = srv.server_address[1]
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{porta}"


def get(caminho):
    try:
        r = urllib.request.urlopen(base + caminho, timeout=8)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


def post(caminho, obj):
    req = urllib.request.Request(base + caminho, data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        r = urllib.request.urlopen(req, timeout=8)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")


try:
    st, corpo = get("/")
    check("GET / responde 200", st, 200)
    checkv("o painel diz 'Painel do dia'", "Painel do dia" in corpo)
    checkv("modo servidor injeta a gaveta", "id='drawer'" in corpo or 'id="drawer"' in corpo)

    st, _ = get("/ver?p=" + urllib.request.quote("../../segredo.txt"))
    checkv("'..' no caminho e recusado (400/404)", st in (400, 404))

    st, _ = get("/ver?p=CONECTOR/regras.py")
    check("arquivo fora de AUTOS/PROCESSOS da 404", st, 404)

    # um arquivo real dentro do sandbox: primeira ficha de PROCESSOS/
    fichas = sorted((sv.soj.ROOT / "PROCESSOS").glob("PROC-*.md"))
    if fichas:
        rel = "PROCESSOS/" + fichas[0].name
        st, corpo = get("/ver?p=" + urllib.request.quote(rel))
        check(f"ficha real dentro do sandbox abre (200): {fichas[0].name}", st, 200)
        checkv("ficha renderizada tem o link de voltar", "voltar ao painel" in corpo)

    st, corpo = post("/acao", {"acao": "peticionar", "cnj": ""})
    j = json.loads(corpo)
    check("acao fora da allowlist e recusada", j.get("ok"), False)
    checkv("recusa explica que so le e prepara", "R7" in j.get("saida", ""))

    st, corpo = post("/acao", {"acao": "buscar", "cnj": "", "termo": ""})
    check("buscar sem termo nao roda nada", json.loads(corpo).get("ok"), False)

    st, corpo = post("/acao", {"acao": "resumo", "cnj": "rm -rf /"})
    check("cnj com caracteres estranhos e barrado", json.loads(corpo).get("ok"), False)
finally:
    srv.shutdown()
    srv.server_close()

print("=" * 64)
if FALHAS:
    print(f"  {len(FALHAS)} FALHA(S): " + ", ".join(FALHAS))
    sys.exit(1)
print("  Tudo verde. O servidor so le, so nesta maquina, so no sandbox.")
print("=" * 64)
