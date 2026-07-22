# -*- coding: utf-8 -*-
"""
baixar_por_chave.py — baixa documentos do PJe pela CHAVE DE ACESSO publicada no
DJEN. Sem login, sem certificado, sem captcha, sem navegador.

CORRECAO DO MAPA_PJE (22/07/2026): o mapa registrava que a rota so funcionava
"clicada no navegador" e que "POST as cegas nao e". ESTA ERRADO — funciona por
script, desde que o POST leve o `javax.faces.ViewState` colhido da propria
pagina e os parametros do RichFaces (`AJAXREQUEST=_viewRoot` + o nome do botao
como chave E valor). O que NAO funciona e setar o campo por JavaScript no
navegador (o RichFaces so registra digitacao real) — o script nao tem esse
problema porque manda o valor no corpo do POST.

Fluxo (3 passos por documento):
  1. GET  listView.seam            -> cookies + ViewState
  2. POST listView.seam            -> "A assinatura e valida" + <a href=...idBin=...>
  3. GET  aquele href (mesma sessao) -> application/pdf

Idempotente: arquivo ja baixado nao se rebaixa (regra de ouro do cache).

Uso:
  python CONECTOR/baixar_por_chave.py ADVERSARIOS/ferreira_representacoes/chaves.json
  python CONECTOR/baixar_por_chave.py --chave 23051717484217000000088069886 --pasta X
"""
from __future__ import annotations

import argparse
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
URL = "https://pje.tjpa.jus.br/pje/Processo/ConsultaDocumento/listView.seam"
FORM = "pesquisaProcessoDocumentoForm"
UA = "Mozilla/5.0"


def sessao():
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.addheaders = [("User-Agent", UA)]
    return op


def viewstate(op) -> str | None:
    h = op.open(URL, timeout=60).read().decode("utf-8", "replace")
    m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', h)
    return m.group(1) if m else None


def consultar(op, vs: str, chave: str):
    """Devolve (url_download, nome_do_arquivo) ou (None, motivo)."""
    data = {
        "AJAXREQUEST": "_viewRoot", FORM: FORM,
        f"{FORM}:numeroDocumento:numeroDocumentoinputDecoration:numeroDocumentoinput": chave,
        f"{FORM}:numeroDocumento:abrirModalMotivoDataExclusaoOpenedState": "",
        "javax.faces.ViewState": vs,
        f"{FORM}:botaoConsultar": f"{FORM}:botaoConsultar",
    }
    req = urllib.request.Request(
        URL, data=urllib.parse.urlencode(data).encode(),
        headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded",
                 "Faces-Request": "partial/ajax", "Referer": URL})
    r = op.open(req, timeout=120).read().decode("utf-8", "replace")
    m = re.search(r'href="([^"]*idBin=[^"]+)"', r)
    if not m:
        if "sigilo" in r.lower():
            return None, "documento sigiloso"
        if "n&atilde;o" in r.lower() or "não foi" in r.lower():
            return None, "chave nao localizada"
        return None, "sem link de download na resposta"
    href = html.unescape(m.group(1))
    nome = "documento.pdf"
    q = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
    if q.get("nomeArqProcDocBin"):
        nome = q["nomeArqProcDocBin"][0]
    return urllib.parse.urljoin("https://pje.tjpa.jus.br", href), nome


def baixar(op, url: str, destino: Path) -> tuple[bool, str]:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": URL})
    with op.open(req, timeout=180) as r:
        b = r.read()
        ct = r.headers.get("Content-Type", "")
    if not b.startswith(b"%PDF"):
        return False, f"nao e PDF (Content-Type: {ct}, {len(b)} bytes)"
    destino.write_bytes(b)
    return True, f"{len(b)//1024} KB"


def limpo(s: str) -> str:
    s = re.sub(r"[^\w\s\.\-]", "", s, flags=re.UNICODE).strip()
    return re.sub(r"\s+", "_", s)[:110] or "documento"


def main():
    ap = argparse.ArgumentParser(description="Baixa documentos do PJe por chave de acesso.")
    ap.add_argument("json", nargs="?", help="JSON com {categoria: [{chave, cnj, tipo}]}")
    ap.add_argument("--chave", help="Uma chave avulsa")
    ap.add_argument("--pasta", default=None, help="Pasta de destino")
    ap.add_argument("--limite", type=int, help="Baixa so os N primeiros (teste)")
    ap.add_argument("--pausa", type=float, default=1.0, help="Segundos entre documentos")
    args = ap.parse_args()

    alvos = []
    if args.chave:
        alvos = [{"chave": args.chave, "cnj": "", "tipo": ""}]
        pasta = Path(args.pasta or ".")
    elif args.json:
        p = Path(args.json)
        if not p.is_absolute():
            p = RAIZ / p
        d = json.loads(p.read_text(encoding="utf-8"))
        for cat, itens in d.items():
            for i in itens:
                i["_cat"] = cat
                alvos.append(i)
        pasta = Path(args.pasta) if args.pasta else p.parent / "docs"
    else:
        ap.error("informe o JSON de chaves ou --chave")
    if not pasta.is_absolute():
        pasta = RAIZ / pasta
    pasta.mkdir(parents=True, exist_ok=True)
    if args.limite:
        alvos = alvos[:args.limite]

    print(f"[..] {len(alvos)} documento(s) · destino {pasta}")
    op = sessao()
    vs = viewstate(op)
    if not vs:
        sys.exit("[ERRO] nao consegui o ViewState (pagina mudou?).")

    ok = pulados = falhas = 0
    indice = []
    for n, a in enumerate(alvos, 1):
        chave = str(a["chave"]).strip()
        marca = f"{(a.get('_cat') or a.get('tipo') or 'doc')}_{a.get('cnj','').replace('.','').replace('-','')}"
        ja = list(pasta.glob(f"*_{chave[-12:]}.pdf"))
        if ja:
            pulados += 1
            print(f"[{n:>3}/{len(alvos)}] {chave[-12:]} ja baixado")
            indice.append({**a, "arquivo": ja[0].name, "status": "cache"})
            continue
        try:
            url, nome = consultar(op, vs, chave)
        except Exception as e:
            falhas += 1
            print(f"[{n:>3}/{len(alvos)}] {chave[-12:]} ERRO consulta: {str(e)[:60]}")
            continue
        if not url:
            falhas += 1
            print(f"[{n:>3}/{len(alvos)}] {chave[-12:]} {nome}")
            indice.append({**a, "status": nome})
            continue
        destino = pasta / f"{limpo(marca)}__{limpo(Path(nome).stem)}_{chave[-12:]}.pdf"
        try:
            bom, info = baixar(op, url, destino)
        except Exception as e:
            bom, info = False, str(e)[:60]
        if bom:
            ok += 1
            print(f"[{n:>3}/{len(alvos)}] OK  {info:>8}  {nome[:64]}")
            indice.append({**a, "arquivo": destino.name, "nome_pje": nome, "status": "ok"})
        else:
            falhas += 1
            print(f"[{n:>3}/{len(alvos)}] FALHA {info}")
            indice.append({**a, "status": info})
        time.sleep(args.pausa)
        if n % 25 == 0:                      # renova a sessao de tempos em tempos
            op = sessao()
            vs = viewstate(op) or vs

    (pasta / "_indice.json").write_text(
        json.dumps(indice, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n[FIM] {ok} baixado(s), {pulados} em cache, {falhas} falha(s).")
    print(f"      {pasta}")


if __name__ == "__main__":
    main()
