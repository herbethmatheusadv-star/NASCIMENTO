#!/usr/bin/env python3
"""teste_trt8_kz.py — o driver de download dos autos, conferido SEM rede/token.

Protege o contrato mapeado na sessao logada (MAPA_PJE.md §13.10), a allowlist de
rotas do Kz (R7 camada 2) e a leitura da timeline sobre a FIXTURE REAL (os 39
documentos do processo 843832, capturados em 21/07/2026)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import regras
import trt8_kz as kz

FIX = Path(__file__).resolve().parent / "_fixtures" / "timeline_843832.json"
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
print("  trt8_kz — download de autos no PJe-Kz (offline)")
print("=" * 74)

print("\n=== 1. allowlist de rotas (R7 camada 2) — so leitura passa ===")
for rota in ["/pje-comum-api/api/processos/id/843832",
             "/pje-comum-api/api/processos/id/843832/timeline",
             "/pje-comum-api/api/processos/id/843832/documentos/id/54715015/conteudo"]:
    check(f"permitida: ...{rota[-30:]}", kz._rota_permitida(rota), True)
# o que NAO pode entrar de carona
for rota in ["/pje-comum-api/api/quadroavisos/",
             "/pje-comum-api/api/processos/id/843832/documentos/id/1/ciencia",
             "/pje-comum-api/api/qualquer/coisa"]:
    check(f"barrada: ...{rota[-26:]}", kz._rota_permitida(rota), False)

print("\n=== 2. _fetch recusa rota fora da allowlist ANTES da rede ===")
sess = kz.Sessao("https://pje.trt8.jus.br", "tok" + "en-de-mentira")
check_levanta("rota fora da allowlist levanta ViolacaoR7", regras.ViolacaoR7,
              kz._fetch, sess, "/pje-comum-api/api/quadroavisos/")

print("\n=== 3. o token nao vaza (Emenda 05) ===")
check("repr esconde o token", "mentira" in repr(sess), False)
check("str esconde o token", "mentira" in str(sess), False)

print("\n=== 4. as URLs reais do Kz passam pela guarda de URL (nao sao acao) ===")
for u in ["https://pje.trt8.jus.br/pje-comum-api/api/processos/id/843832/timeline"
          "?buscarMovimentos=false&buscarDocumentos=true",
          "https://pje.trt8.jus.br/pje-comum-api/api/processos/id/843832/"
          "documentos/id/54715015/conteudo?incluirCapa=false&grau=1"]:
    regras.guarda_de_url(u)  # nao pode levantar
    print(f"  [ok ] guarda permite: ...{u[-40:]}")

print("\n=== 5. leitura da timeline sobre a FIXTURE REAL (39 docs) ===")
crus = json.loads(FIX.read_text(encoding="utf-8"))
docs = [kz._normalizar_doc(d) for d in crus if d.get("documento")]
check("39 documentos normalizados", len(docs), 39)
check("campos do doc", sorted(docs[0]),
      ["data", "expediente_aberto", "id", "id_unico", "responsavel",
       "sigiloso", "tipo", "titulo"])
check("primeiro doc e o Alvara id 54715015", (docs[0]["tipo"], docs[0]["id"]),
      ("Alvará", 54715015))
check("data cortada em 19 chars (YYYY-MM-DDTHH:MM:SS)", len(docs[0]["data"]), 19)

print("\n=== 6. R7 camada 4 — QUARENTENA pela timeline ===")
# a fixture real nao tem expediente aberto: processo LIVRE para baixar
tem_pendente = any(d["expediente_aberto"] for d in docs)
check("fixture real: nenhum expediente aberto", tem_pendente, False)
# e se UM documento estivesse com expediente aberto? -> quarentena
docs_sim = [dict(d) for d in docs]
docs_sim[3]["expediente_aberto"] = True
q = regras.Quarentena()
quarentenado = q.avaliar(regras.Processo(
    "0000483-10.2025.5.08.0130",
    ciencia_pendente=any(d["expediente_aberto"] for d in docs_sim),
    origem="TRT8/Kz"))
check("com 1 expediente aberto -> quarentena", quarentenado, True)

print("\n=== 7. ordem cronologica (mais antigo primeiro no integral) ===")
ordenados = sorted(docs, key=lambda d: d["data"])
check("apos ordenar, o 1o e mais antigo que o ultimo",
      ordenados[0]["data"] <= ordenados[-1]["data"], True)

print("\n=== 8. deteccao de PDF (so PDF entra no integral) ===")
check("bytes com %PDF- viram PDF", kz._eh_pdf(b"%PDF-1.7\n...", ""), True)
check("content-type application/pdf vira PDF", kz._eh_pdf(b"xx", "application/pdf"), True)
check("HTML nao e PDF", kz._eh_pdf(b"<html>", "text/html"), False)

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Driver de autos confere. Falta o teste decisivo — com o Bearer do titular.")
print("=" * 74)
