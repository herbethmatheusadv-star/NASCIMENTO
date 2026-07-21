#!/usr/bin/env python3
"""
trt8_kz.py — DOWNLOAD dos autos no PJe-Kz (PDPJ). LEITURA, e so leitura.

O TRT-8 roda o PJe NOVO (PDPJ / "Meu Painel", SPA Angular "CARAUBA"). O acervo
(a LISTA) sai pelo trt8_api.py. Os AUTOS (os documentos de cada processo) saem
pelo app Kz, que se alimenta da MESMA API REST `/pje-comum-api/api/`. Este modulo
percorre essa API e junta os documentos num PDF integral por processo, do jeito
que o soj_import.py (Fase 3) espera: AUTOS/{cnj}/autos_integral_{sha8}.pdf.

  A RECEITA (mapeada na sessao logada do titular em 21/07/2026 — MAPA_PJE.md
  §13.10, dado real, nada de chute):
    1. lista de documentos:
         GET /pje-comum-api/api/processos/id/{id}/timeline
             ?buscarMovimentos=false&buscarDocumentos=true
    2. baixar 1 documento (devolve o PDF):
         GET /pje-comum-api/api/processos/id/{id}/documentos/id/{idDoc}/conteudo
             ?incluirCapa=false&grau=1

  R7 (a MESMA do trt8_api.py e do mni.py, nas mesmas camadas):
    1. AUSENCIA — nao existe neste arquivo funcao que escreva no tribunal. Nao ha
       o que chamar; a capacidade de agir simplesmente nao esta escrita.
    2. ALLOWLIST — `ROTAS_PERMITIDAS` deixa passar so um punhado de rotas de
       LEITURA. A rota de avisos/expedientes e a de abrir expediente ficam DE
       FORA de proposito (candidatas a gatilho da ciencia).
    3. GUARDA DE URL — regras.guarda_de_url em toda chamada. As URLs do Kz nao
       contem verbo de acao, entao passam limpas (de proposito: o download usa
       `?incluirCapa=false&grau=1`, SEM o `incluirAssinatura`; e a lista dispensa
       o `somenteDocumentosAssinados` — provado 21/07 que traz os mesmos docs).
    4. QUARENTENA — antes de baixar, olha a timeline: se algum documento estiver
       com expediente ABERTO (ciencia pendente), o processo nao e baixado (nem os
       autos) e vira fila humana. Ver regras.Quarentena.

  CREDENCIAL (Emenda 05): o token (access_token) e do titular, colado A CADA
  EXECUCAO pelo trt8_api.pedir_token(). Nao vai para disco, env, codigo nem log —
  vive na memoria e morre com o processo.

Uso:
  python CONECTOR/trt8_kz.py --processo 843832
  python CONECTOR/trt8_kz.py --processo 843832 --cnj 0000483-10.2025.5.08.0130
  python CONECTOR/trt8_kz.py --todos --advogado 837986
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import instancias
import regras
from trt8_api import Sessao, base_host, pedir_token

RAIZ = Path(__file__).resolve().parents[1]
TIMEOUT = 120  # o /conteudo devolve o PDF inteiro; o download pode demorar mais

# Allowlist de rotas de LEITURA do app Kz (autos). Cada uma e um GET de consulta.
# A rota de avisos/expedientes (`/quadroavisos/`) e a de abrir expediente ficam
# FORA de proposito — sao candidatas a gatilho da ciencia, mesma disciplina do
# trt8_api.py. Adicionar rota aqui e decisao consciente, nunca de carona.
ROTAS_PERMITIDAS = (
    r"^/pje-comum-api/api/processos/id/\d+$",
    r"^/pje-comum-api/api/processos/id/\d+/timeline\b",
    r"^/pje-comum-api/api/processos/id/\d+/documentos/id/\d+/conteudo\b",
)


def _rota_permitida(rota: str) -> bool:
    return any(re.search(p, rota) for p in ROTAS_PERMITIDAS)


def _fetch(sessao: Sessao, rota: str, params: dict | None = None) -> tuple[bytes, str]:
    """GET cru numa rota da allowlist Kz. Devolve (bytes, content_type). Leitura.

    Mesma autenticacao do trt8_api: a sessao logada autentica o GET pelo cookie
    access_token (mandamos tambem como Bearer por robustez). So GET, entao nao
    entra Xsrf-Token (o anti-CSRF de escrita)."""
    if not _rota_permitida(rota):
        raise regras.ViolacaoR7(
            f"rota {rota!r} fora da allowlist de leitura {ROTAS_PERMITIDAS}. "
            "Se for rota de escrita, ela nao deve existir neste cliente.")
    qs = ""
    if params:
        qs = "?" + "&".join(f"{k}={urllib.request.quote(str(v))}"
                            for k, v in params.items())
    url = sessao.host.rstrip("/") + rota + qs
    regras.guarda_de_url(url)
    req = urllib.request.Request(url, method="GET")
    req.add_header("Cookie", f"access_token={sessao._token}")
    req.add_header("Authorization", f"Bearer {sessao._token}")
    req.add_header("Accept", "application/pdf, application/json, */*")
    req.add_header("User-Agent", "SOJ-Conector/1.0 (leitura; OAB 39261/PA)")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read(), r.headers.get("Content-Type", "")


# ---------------------------------------------------------------------------
# As consultas — todas GET de leitura
# ---------------------------------------------------------------------------

def processo(sessao: Sessao, id_proc: int) -> dict:
    """Metadados do processo (para descobrir o numero CNJ)."""
    dados, _ = _fetch(sessao, f"/pje-comum-api/api/processos/id/{id_proc}")
    return json.loads(dados.decode("utf-8", "ignore"))


def _normalizar_doc(d: dict) -> dict:
    """Do JSON da timeline para os campos que o driver usa."""
    info = d.get("infoExpedientes") or {}
    return {
        "id": d.get("id"),
        "id_unico": d.get("idUnicoDocumento"),
        "tipo": d.get("tipo"),
        "titulo": d.get("titulo"),
        "data": (d.get("data") or "")[:19],
        "sigiloso": bool(d.get("documentoSigiloso")),
        "responsavel": d.get("nomeSignatario") or d.get("nomeResponsavel"),
        # sinal de ciencia pendente — a QUARENTENA olha isto (R7 camada 4)
        "expediente_aberto": bool(info.get("expedienteAberto")),
    }


def timeline(sessao: Sessao, id_proc: int) -> list[dict]:
    """Lista de documentos do processo, em ordem da API (mais novo primeiro).

    Dispensa o parametro `somenteDocumentosAssinados` de proposito: provado em
    21/07/2026 que a lista vem identica sem ele — e assim a URL nao encosta na
    palavra que a guarda de URL bloqueia."""
    dados, _ = _fetch(sessao, f"/pje-comum-api/api/processos/id/{id_proc}/timeline",
                      {"buscarMovimentos": "false", "buscarDocumentos": "true"})
    lista = json.loads(dados.decode("utf-8", "ignore"))
    return [_normalizar_doc(d) for d in lista if d.get("documento")]


def baixar_conteudo(sessao: Sessao, id_proc: int, id_doc: int) -> tuple[bytes, str]:
    """Baixa 1 documento. Devolve (bytes, content_type). So leitura.

    Usa `?incluirCapa=false&grau=1` SEM `incluirAssinatura` — o /conteudo devolve
    o PDF do mesmo jeito (provado 21/07) e a URL fica limpa para a guarda."""
    return _fetch(
        sessao, f"/pje-comum-api/api/processos/id/{id_proc}/documentos/id/{id_doc}/conteudo",
        {"incluirCapa": "false", "grau": "1"})


# ---------------------------------------------------------------------------
# Empacotamento — junta os PDFs num integral (o que o soj_import espera)
# ---------------------------------------------------------------------------

def _eh_pdf(dados: bytes, ctype: str) -> bool:
    return dados[:5] == b"%PDF-" or "pdf" in (ctype or "").lower()


def _merge_pdfs(pedacos: list[bytes]) -> bytes:
    """Junta uma lista de PDFs (em bytes) num PDF so, na ordem dada. pymupdf."""
    import fitz  # PyMuPDF — ja usado pelo soj_import (Fase 3)
    saida = fitz.open()
    try:
        for b in pedacos:
            origem = fitz.open(stream=b, filetype="pdf")
            try:
                saida.insert_pdf(origem)
            finally:
                origem.close()
        return saida.tobytes(garbage=3, deflate=True)
    finally:
        saida.close()


def baixar_autos(sessao: Sessao, id_proc: int, cnj: str | None = None,
                 forcar: bool = False) -> dict:
    """Baixa TODOS os documentos de um processo e grava o PDF integral.

    Grava em AUTOS/{cnj}/autos_integral_{sha8}.pdf (idempotente: pula se ja existe
    um integral e nao for --forcar). Guarda os originais por documento em
    AUTOS/{cnj}/originais/ e um manifesto em AUTOS/{cnj}/manifesto_kz.json.
    Devolve um dict com o resultado."""
    cnj = cnj or (processo(sessao, id_proc).get("numeroProcesso") or "")
    if not cnj:
        return {"status": "erro", "id": id_proc,
                "erro": "nao achei o numero CNJ (passe --cnj)"}

    docs = timeline(sessao, id_proc)

    # R7 camada 4 — QUARENTENA: ciencia pendente = nao toca (nem os autos)
    q = regras.Quarentena()
    if q.avaliar(regras.Processo(
            cnj, ciencia_pendente=any(d["expediente_aberto"] for d in docs),
            origem="TRT8/Kz", observacao="expediente aberto na timeline")):
        q.registrar()
        return {"status": "quarentena", "id": id_proc, "cnj": cnj,
                "docs": len(docs)}

    destino = RAIZ / "AUTOS" / cnj
    ja = sorted(destino.glob("autos_integral_*.pdf")) if destino.exists() else []
    if ja and not forcar:
        return {"status": "ja_existe", "id": id_proc, "cnj": cnj,
                "arquivo": str(ja[0].relative_to(RAIZ)), "docs": len(docs)}

    # do mais ANTIGO para o mais NOVO — a leitura dos autos e cronologica
    docs_ord = sorted(docs, key=lambda d: d["data"])
    originais = destino / "originais"
    originais.mkdir(parents=True, exist_ok=True)

    pdfs: list[bytes] = []
    manifesto: list[dict] = []
    fora_do_padrao: list[dict] = []
    for i, d in enumerate(docs_ord, 1):
        dados, ctype = baixar_conteudo(sessao, id_proc, d["id"])
        time.sleep(regras.CONDUTA["pausa_entre_requisicoes_seg"])  # nao castigar o tribunal
        sha = hashlib.sha256(dados).hexdigest()[:8]
        pdf_ok = _eh_pdf(dados, ctype)
        ext = "pdf" if pdf_ok else "bin"
        tipo_slug = re.sub(r"[^a-zA-Z0-9]+", "-", (d["tipo"] or "doc")).strip("-")[:28]
        arq = originais / f"{i:03d}_{tipo_slug}_{sha}.{ext}"
        if not arq.exists():
            arq.write_bytes(dados)
        manifesto.append({"ordem": i, "id": d["id"], "tipo": d["tipo"],
                          "titulo": d["titulo"], "data": d["data"],
                          "sigiloso": d["sigiloso"], "sha8": sha,
                          "pdf": pdf_ok, "arquivo": arq.name})
        if pdf_ok:
            pdfs.append(dados)
        else:
            fora_do_padrao.append({"ordem": i, "tipo": d["tipo"], "ctype": ctype})
        print(f"    [{i:>3}/{len(docs_ord)}] {d['data'][:10]} {d['tipo'][:34]:34} "
              f"{len(dados)//1024:>5} KB{'' if pdf_ok else '  (NAO-PDF: so no original)'}")

    if not pdfs:
        return {"status": "sem_pdf", "id": id_proc, "cnj": cnj, "docs": len(docs)}

    integral = _merge_pdfs(pdfs)
    sha_int = hashlib.sha256(integral).hexdigest()[:8]
    arq_int = destino / f"autos_integral_{sha_int}.pdf"
    arq_int.write_bytes(integral)

    (destino / "manifesto_kz.json").write_text(json.dumps({
        "cnj": cnj, "id_processo": id_proc,
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "integral": arq_int.name, "total_docs": len(docs_ord),
        "pdfs_no_integral": len(pdfs), "fora_do_padrao": fora_do_padrao,
        "documentos": manifesto,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    return {"status": "ok", "id": id_proc, "cnj": cnj,
            "arquivo": str(arq_int.relative_to(RAIZ)),
            "docs": len(docs_ord), "pdfs": len(pdfs),
            "fora_do_padrao": len(fora_do_padrao),
            "tamanho_mb": round(len(integral) / 1_048_576, 1)}


# NAO existe funcao de escrita neste arquivo (peca, ciencia, resposta, ato). E R7:
# a API tem as duas faces na mesma porta; a unica defesa que nao depende de
# disciplina e a operacao nao estar escrita. Ver regras.py e MAPA_PJE.md §13.10.


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Download dos autos no PJe-Kz (PDPJ) — leitura.")
    ap.add_argument("--instancia", default="trt8", help="instancia PDPJ (ex.: trt8)")
    ap.add_argument("--processo", type=int, help="id interno do processo (ex.: 843832)")
    ap.add_argument("--cnj", default="", help="numero CNJ (opcional; senao vem da API)")
    ap.add_argument("--todos", action="store_true",
                    help="baixa o acervo + arquivados do advogado")
    ap.add_argument("--advogado", type=int, help="id do advogado (com --todos)")
    ap.add_argument("--forcar", action="store_true", help="rebaixa mesmo se ja existe")
    args = ap.parse_args()

    if not args.processo and not args.todos:
        sys.exit("  Informe --processo <id> ou --todos --advogado <id>.")
    if args.todos and not args.advogado:
        sys.exit("  --todos exige --advogado <id>.")

    try:
        inst = instancias.definir(args.instancia)
        host = base_host(inst)
    except (KeyError, RuntimeError) as e:
        sys.exit(f"  {e}")

    print("=" * 74)
    print("  PJe-Kz — DOWNLOAD DE AUTOS (CONECTOR SOJ, somente leitura)")
    print(f"  instancia: {inst.nome}")
    print(f"  base     : {host}/pje-comum-api/api")
    print("=" * 74)

    sessao = Sessao(host, pedir_token())

    # monta a fila (id, cnj)
    alvos: list[tuple[int, str]] = []
    if args.todos:
        import trt8_api
        for enum in (1, 5):  # 1=acervo geral, 5=arquivados
            for p in trt8_api.processos(sessao, args.advogado, enum):
                alvos.append((p["id_pje"], p["numero"]))
    else:
        alvos.append((args.processo, args.cnj or ""))

    print(f"\n  {len(alvos)} processo(s) na fila.\n")
    resumo: list[dict] = []
    for id_proc, cnj in alvos:
        print(f"  >> processo {id_proc} {('· ' + cnj) if cnj else ''}")
        try:
            r = baixar_autos(sessao, id_proc, cnj or None, forcar=args.forcar)
        except urllib.error.HTTPError as e:
            dica = " (token expirado? pegue um novo)" if e.code in (401, 403) else ""
            r = {"status": "http", "id": id_proc, "erro": f"HTTP {e.code}{dica}"}
        except (regras.ViolacaoR7, Exception) as e:  # noqa: BLE001
            r = {"status": "erro", "id": id_proc, "erro": f"{type(e).__name__}: {e}"}
        resumo.append(r)
        print(f"     -> {r.get('status')}: {r.get('arquivo') or r.get('erro') or ''}\n")

    print("=" * 74)
    ok = sum(1 for r in resumo if r["status"] == "ok")
    print(f"  {ok}/{len(resumo)} baixado(s). "
          f"Agora: python ESCRITORIO/scripts/soj_import.py  (PDF -> texto)")
    print("  R7: o cliente so LE (GET de consulta). Agir no PJe segue so do titular.")
    print("=" * 74)


if __name__ == "__main__":
    main()
