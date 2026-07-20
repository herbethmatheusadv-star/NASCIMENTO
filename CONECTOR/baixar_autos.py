#!/usr/bin/env python3
"""
baixar_autos.py — baixa os autos dos processos do PJe/TJPA. UM login, todos.

LEITURA, e so leitura. Roda DENTRO da sessao que o titular autenticou
(`sessao.py`, certificado + 2FA). Fecha a Fase de coleta do PLANO_SOJ: entrega
os PDFs em AUTOS/{cnj}/ para o importador (Fase 3) transformar em texto com
marcador de pagina.

  COMO FUNCIONA — metodo INTEGRAL (primario; execucao real de 16/07/2026)

  1. O titular loga UMA vez (o robo para no portao; ele digita cert + 2FA) e
     deixa a aba ACERVO aberta, com as comarcas expandidas.
  2. O robo LE o Acervo do painel e monta {cnj: url_dos_autos}.
  3. Para CADA processo (todos, ou o --cnj pedido), o robo abre a tela de autos,
     dispara "Download autos do processo" (o botao da navbar), o servidor
     EMPACOTA os autos e devolve a URL de um PDF unico e completo, servido por
     pje-docs.tjpa.jus.br (S3 assinado). O robo busca o PDF pela sessao (GET).
  4. Salva em AUTOS/{cnj}/autos_integral_{sha8}.pdf. Idempotente por sha.

  E assim que "um login" vira "N processos baixados" — 16 processos, 280 MB, em
  ~100 s numa unica sessao (16/07/2026). Ver CONECTOR/MAPA_PJE.md §12.

  Fallback (--pecas): metodo antigo, peca a peca pela REST de leitura
  /pje/seam/resource/rest/pje-legacy/documento/download/{id} (GET, cookie da
  sessao). Fica para quando so se quer uma peca especifica.

  R7 — POR QUE ISTO SO SABE LER

  "Download autos do processo" entrega os autos em PDF: e leitura. O UNICO clique
  e no botao rotulado "Download", e ele passa antes por `regras.guarda_de_clique`
  — se o seletor um dia pegasse um botao de acao, o rotulo casaria com o
  vocabulario proibido e a guarda recusaria. As URLs (autos, e o PDF empacotado)
  passam por allowlist + `regras.guarda_de_url`. Nao existe, neste arquivo,
  funcao que assine, protocole ou tome ciencia — e `teste_regras.py` varre o
  fonte e quebra o build se aparecer capacidade de agir.

Uso:
    python CONECTOR/baixar_autos.py --todos            # o acervo inteiro
    python CONECTOR/baixar_autos.py --cnj 0809135-08.2026.8.14.0040
    python CONECTOR/baixar_autos.py --cnj <n> --pecas  # fallback peca a peca
"""
from __future__ import annotations

import argparse
import hashlib
import html as htmlmod
import re
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

import instancias
import regras
import sessao

RAIZ = Path(__file__).resolve().parents[1]

# Endereco por INSTANCIA (instancias.py): o default e o TJPA 1o grau, o unico
# confirmado em execucao real. --instancia troca para TJMA/TRT-8/2o grau — o
# fluxo e o mesmo, so muda o host. A UNICA rota REST de leitura construida aqui
# (allowlist) e este sufixo, aplicado sobre a raiz da instancia.
REST_REL = "/seam/resource/rest/pje-legacy/documento/download/"

RE_CNJ = re.compile(r"\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")
# nome da peca: title="177919838 - Peticao Inicial"
RE_DOC_NOME = re.compile(r'title="(\d{6,})\s*-\s*([^"]{2,80})"')
# id de qualquer peca (aparece em varios lugares: lembretes, download, arvore)
RE_DOC_ID = re.compile(r'(?:idProcessoDocumento=|documento/download/)(\d{6,})')


def extrair_cnj(html: str) -> str:
    m = RE_CNJ.search(html or "")
    return m.group(0) if m else ""


def extrair_documentos(html: str) -> list[tuple[str, str]]:
    """
    Lista (idProcessoDocumento, nome) de todas as pecas, na ordem de aparicao.

    A arvore dos autos e lazy: nem toda peca traz o nome no HTML estatico. Entao
    junta duas fontes — os `title="{id} - {nome}"` (quando ha nome) e todos os
    ids soltos — e usa o nome onde existir, o id onde nao. Nenhuma peca fica de
    fora so por nao ter rotulo renderizado.
    """
    html = html or ""
    nomes: dict[str, str] = {}
    for m in RE_DOC_NOME.finditer(html):
        nomes.setdefault(m.group(1), htmlmod.unescape(m.group(2)).strip())

    # ids em ordem de aparicao, das DUAS fontes: o title="{id} - nome" (peca
    # nomeada na arvore) E os links (idProcessoDocumento=/download/). Uma peca
    # que so aparece no title — porque a arvore lazy nao renderizou o link —
    # nao pode sumir. Foi o bug que o teste_baixar §2 pegou em 16/07/2026.
    pares: list[tuple[int, str]] = []
    for m in RE_DOC_NOME.finditer(html):
        pares.append((m.start(), m.group(1)))
    for m in RE_DOC_ID.finditer(html):
        pares.append((m.start(), m.group(1)))
    pares.sort()

    vistos: list[str] = []
    seen: set[str] = set()
    for _, i in pares:
        if i not in seen:
            seen.add(i)
            vistos.append(i)
    return [(i, nomes.get(i, "")) for i in vistos]


def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()
    return (t or "peca")[:40]


def _url_download(iddoc: str, inst=None) -> str:
    inst = inst or instancias.atual()
    prefixo = inst.raiz + REST_REL
    url = prefixo + str(iddoc)
    # allowlist + guarda: so passa o que comeca pelo prefixo de leitura, e a
    # guarda ainda barra qualquer verbo de acao que porventura aparecesse.
    if not url.startswith(prefixo):
        raise regras.ViolacaoR7(f"rota fora da allowlist de leitura: {url!r}")
    regras.guarda_de_url(url)
    return url


def baixar_uma(contexto, iddoc: str) -> tuple[bool, bytes, int, str]:
    """GET de uma peca pela sessao (cookie automatico). Devolve (ok, bytes, status, ct)."""
    url = _url_download(iddoc)
    try:
        r = contexto.request.get(url, timeout=90_000)
    except Exception as e:  # noqa: BLE001
        return False, b"", 0, f"{type(e).__name__}: {e}"
    ct = (r.headers or {}).get("content-type", "")
    if r.status != 200:
        return False, b"", r.status, ct
    try:
        dados = r.body()
    except Exception:  # noqa: BLE001
        return False, b"", r.status, ct
    return True, dados, r.status, ct


def _extensao(ct: str, dados: bytes) -> str:
    if dados[:5] == b"%PDF-":
        return "pdf"
    if "pdf" in (ct or "").lower():
        return "pdf"
    if "html" in (ct or "").lower():
        return "html"
    return "bin"


def _norm_cnj(texto: str) -> str:
    return re.sub(r"\D", "", texto or "")


# URL dos autos por processo, lida da aba Acervo. Captura o caminho a partir da
# `/` inicial (href OU dentro de um onclick window.open) — NAO assume `/pje/`
# (o TRT usa `/primeirograu/`). O NOME do link de autos MUDA por deployment:
#   TJPA: listProcessoCompletoAdvogado.seam?id=<n>&ca=<hex>
#   TJMA: listAutosDigitais.seam?idProcesso=<n>   (descoberto em 20/07/2026)
# Ambos abrem os autos digitais; casamos os dois.
RE_ACERVO = re.compile(
    r"(/[^\"'<>\s]*?(?:"
    r"listProcessoCompletoAdvogado\.seam\?id=\d+&(?:amp;)?ca=[a-f0-9]+"
    r"|listAutosDigitais\.seam\?idProcesso=\d+"
    r"))")
CNJ_DUMMY = "9999999-99.9999.9.99.9999"   # linha-modelo oculta do RichFaces


def extrair_acervo(html: str, inst=None) -> dict[str, str]:
    """{cnj: url_dos_autos} a partir do HTML do painel (aba Acervo aberta)."""
    inst = inst or instancias.atual()
    out: dict[str, str] = {}
    html = html or ""
    for m in RE_ACERVO.finditer(html):
        caminho = htmlmod.unescape(m.group(1))
        if caminho.startswith("http"):
            url = caminho
        else:   # href relativo, comeca com "/": prefixa o host da instancia
            url = f"https://{inst.host}" + caminho
        # o CNJ vem DEPOIS do link, no texto da linha, ~600 chars a frente
        # (medido no HTML real 16/07/2026; 400 nao alcancava). Janela de 1200
        # cobre com folga sem invadir a proxima linha (~1700 a frente).
        cm = RE_CNJ.search(html[m.start():m.start() + 1200])
        if cm and cm.group(0) != CNJ_DUMMY:
            out.setdefault(cm.group(0), url)
    return out


# --- Acervo em ÁRVORE por comarca (descoberto em 20/07/2026) -----------------
# A aba Acervo do painel e uma arvore RichFaces agrupada por COMARCA, e ela e um
# ACCORDION: expandir uma comarca RECOLHE a outra. Por isso o 1o download so viu
# Parauapebas — Canaa estava recolhida. A saida e o robo PERCORRER comarca a
# comarca sozinho: troca para a aba Acervo, e para cada no de comarca expande,
# le os processos e junta. Tudo LEITURA — cada clique passa por guarda_de_clique
# (o rotulo e "Acervo"/nome de comarca, nunca um verbo de acao).

def _ir_para_acervo(pagina) -> bool:
    """Troca para a aba Acervo (se ainda nao estiver). True se a arvore montou."""
    ativo = pagina.evaluate(
        "() => { const c=document.getElementById('tabAcervo_cell');"
        " return !!(c && (c.className||'').includes('active')); }")
    if not ativo:
        lbl = (pagina.evaluate(
            "() => (document.getElementById('tabAcervo_lbl')||{}).innerText||''")
            or "").strip().split("\n")[0]
        if not lbl:
            return False
        regras.guarda_de_clique(lbl)   # R7: "Acervo" e leitura
        pagina.evaluate("() => { const e=document.getElementById('tabAcervo_lbl');"
                        " if(e) e.click(); }")
    for _ in range(20):
        time.sleep(1)
        if pagina.evaluate("() => document.querySelectorAll(\"a[id$='::jNd']\").length>0"):
            return True
    return False


def acervo_completo(pagina) -> dict[str, str]:
    """{cnj: url} de TODAS as comarcas do Acervo. Percorre a arvore accordion,
    expandindo cada comarca. Devolve {} se nao houver a arvore (outro layout /
    instancia) — ai o chamador usa extrair_acervo do que ja esta na tela."""
    if not _ir_para_acervo(pagina):
        return {}
    comarcas = pagina.evaluate(
        r"""() => [...document.querySelectorAll("a[id$='::jNd']")]
              .map(a => [a.id, (a.innerText||'').replace(/\s+/g,' ').trim()])""")
    if not comarcas:
        return {}
    todos: dict[str, str] = {}
    for node_id, rot in comarcas:
        regras.guarda_de_clique(rot or "comarca")   # R7 (nome de comarca = leitura)
        antes = set(extrair_acervo(pagina.content()))
        pagina.evaluate(f"() => {{ const e=document.getElementById({node_id!r});"
                        f" if(e) e.click(); }}")
        ac: dict[str, str] = {}
        for _ in range(30):     # espera o conteudo MUDAR (accordion troca a lista)
            time.sleep(1)
            ac = extrair_acervo(pagina.content())
            if set(ac) != antes:
                break
        if not ac:              # colapsou (ja estava aberta) -> reexpande
            pagina.evaluate(f"() => {{ const e=document.getElementById({node_id!r});"
                            f" if(e) e.click(); }}")
            for _ in range(20):
                time.sleep(1)
                ac = extrair_acervo(pagina.content())
                if ac:
                    break
        todos.update(ac)
        print(f"[baixar]   comarca {rot!r}: {len(ac)} processo(s)")
    return todos


# ---------------------------------------------------------------------------
#  DOWNLOAD INTEGRAL — "Download autos do processo" (um clique = autos inteiros)
# ---------------------------------------------------------------------------
#
# Descoberto na execucao real de 16/07/2026 (ver MAPA_PJE.md §12). A tela de
# autos tem o botao "Download autos do processo" (dropdown na navbar). Ele
# dispara um A4J.AJAX.Submit que EMPACOTA os autos no servidor; ao terminar, um
# link oculto (`linkDownloadOculto`) chama window.open(URL) com o PDF pronto,
# servido por pje-docs.tjpa.jus.br (S3, URL assinada, valida ~30 min).
#
# Um clique = autos inteiros num PDF unico. Na pratica: 16 processos, 280 MB, em
# ~100 s, com UM login. E o que torna a escala viavel (100 processos ~ 10 min).
#
# Isto RENDERIZA a tela de autos — o que a 1a versao evitava por medo do
# anti-debug. A execucao real provou que, sob connect_over_cdp (Chrome comum, sem
# flags de automacao), o `debugger;` da pagina e inofensivo: os 16 processos
# renderizaram sem travar. Continua sendo LEITURA: "Download autos do processo"
# entrega os autos em PDF; nao ha, neste arquivo, qualquer capacidade de escrita
# (R7). O unico clique e no botao rotulado "Download", que passa antes por
# regras.guarda_de_clique — se um dia o seletor pegasse um botao de acao, o
# rotulo casaria com o vocabulario proibido e a guarda recusaria.

# O PDF empacotado vem de um host de documentos do PJe — no TJPA e
# `pje-docs.tjpa.jus.br` (S3 assinado). A allowlist aceita a FAMILIA
# `pje-docs.<tribunal>.jus.br` (ou o proprio host da instancia), sempre .pdf.
RE_HOST_DOCS = re.compile(r"^pje-docs\.[a-z0-9-]+\.jus\.br$")

# O botao vive num dropdown oculto (display:none); .click() no elemento dispara
# o A4J mesmo sem visibilidade. O id do <input> e j_idNNN — auto-gerado pelo
# JSF e INSTAVEL entre renders (16/07 vi j_id211 e depois j_id207 no MESMO
# processo). Ancorar sempre pelo container de id ESTAVEL `navbar:botoesDownload`,
# nunca pelo j_id. (Em raw-string, `\\:` vira `\:` na string JS = escape CSS do
# ':' do id "navbar:botoesDownload".)
_JS_ACHAR_BOTAO = r"""() => {
  const b = document.querySelector('#navbar\\:botoesDownload input.btn-primary')
        || document.querySelector('#navbar\\:botoesDownload input[value="Download"]')
        || Array.from(document.querySelectorAll('input[type=button],input[type=submit]'))
               .find(x => (x.value||'').trim().toLowerCase()==='download');
  return b ? (b.value || 'Download') : '';
}"""
_JS_CLICAR_BOTAO = r"""() => {
  const b = document.querySelector('#navbar\\:botoesDownload input.btn-primary')
        || document.querySelector('#navbar\\:botoesDownload input[value="Download"]')
        || Array.from(document.querySelectorAll('input[type=button],input[type=submit]'))
               .find(x => (x.value||'').trim().toLowerCase()==='download');
  if (!b) return false;
  b.click();
  return true;
}"""
# Sobrescreve window.open ANTES do clique: em vez de abrir popup, guarda a URL
# do pacote. O oncomplete do A4J faz $('linkDownloadOculto').click() -> open(URL).
_JS_CAPTURAR_OPEN = (r"() => { window.__cap = []; window.__oo = window.open;"
                     r" window.open = function(u){ window.__cap.push(String(u));"
                     r" return null; }; }")
_JS_LER_CAP = "() => window.__cap || []"
_JS_LER_LINK = ("() => { const e = document.getElementById('linkDownloadOculto');"
                " return e ? (e.getAttribute('onclick') || '') : ''; }")

RE_OPEN_URL = re.compile(r"window\.open\('([^']+)'\)")


def _url_pacote_ok(url: str, inst=None) -> str:
    """Allowlist do PDF empacotado: host de documentos do PJe (pje-docs.*.jus.br
    ou o host da instancia) e caminho terminando em .pdf. Como o _url_download da
    REST: uma rota de LEITURA conhecida; o resto e ausencia."""
    inst = inst or instancias.atual()
    if url.startswith("/"):
        url = f"https://{inst.host}" + url
    limpo = url.split("?", 1)[0].lower()
    host = re.sub(r"^https?://([^/]+).*", r"\1", url).lower()
    host_ok = bool(RE_HOST_DOCS.match(host)) or host == inst.host
    if not (url.startswith("https://") and host_ok and limpo.endswith(".pdf")):
        raise regras.ViolacaoR7(
            f"URL de pacote fora da allowlist de leitura: {url[:80]!r}")
    regras.guarda_de_url(url)   # ainda barra qualquer verbo de acao que aparecesse
    return url


def _esperar_botao_download(pagina, seg: float = 20.0) -> str:
    """Espera a navbar montar; devolve o rotulo do botao (ou '' se nao veio)."""
    alvo = time.time() + seg
    while time.time() < alvo:
        rot = pagina.evaluate(_JS_ACHAR_BOTAO)
        if rot:
            return rot
        time.sleep(0.5)
    return ""


def disparar_pacote(pagina, espera_max: float = 300.0) -> str | None:
    """
    Na tela de autos JA carregada: dispara 'Download autos do processo' e captura
    a URL do PDF empacotado. So leitura — o unico clique passa pela guarda de R7
    (o rotulo tem de ser 'Download', nunca um verbo de acao).
    """
    rotulo = _esperar_botao_download(pagina)
    if not rotulo:
        return None
    regras.guarda_de_clique(rotulo)        # RAIL R7: recusa se nao for leitura
    pagina.evaluate(_JS_CAPTURAR_OPEN)     # intercepta o window.open
    if not pagina.evaluate(_JS_CLICAR_BOTAO):
        return None
    alvo = time.time() + espera_max
    while time.time() < alvo:
        cap = [u for u in (pagina.evaluate(_JS_LER_CAP) or [])
               if u and u not in ("", "undefined", "null")]
        if cap:
            return cap[-1]
        m = RE_OPEN_URL.search(pagina.evaluate(_JS_LER_LINK) or "")
        if m and m.group(1).strip():
            return m.group(1)
        time.sleep(2)
    return None


# TJMA (e outros deployments): o botao de download e um <input type=submit> e o
# PDF vem NA RESPOSTA de um POST normal do form 'navbar' (nao ha window.open do
# S3 nem linkDownloadOculto; o cookie so avisa o fim do empacotamento). Replicamos
# o POST pela sessao e recebemos o PDF direto. Descoberto no TJMA em 20/07/2026.
_JS_SERIALIZA_NAVBAR = r"""() => {
  const f = document.getElementById('navbar');
  if (!f) return null;
  const sub = f.querySelector("input[type=submit][name*='downloadProcesso']")
        || [...f.querySelectorAll("input[type=submit]")].find(b => /download/i.test(b.value||''));
  if (!sub) return null;                    // sem submit de download -> outro fluxo
  const d = {};
  for (const el of f.querySelectorAll('input,select,textarea')) {
    if (!el.name) continue;
    if ((el.type==='checkbox'||el.type==='radio') && !el.checked) continue;
    if (el.type==='submit') continue;       // exclui TODOS os submits
    d[el.name] = el.value;
  }
  d[sub.name] = sub.value;                   // adiciona SO o submit de download
  return {action: f.action, campos: d, rotulo: sub.value || 'Download'};
}"""


def _pacote_via_submit(pagina, contexto, espera_max: float):
    """Fluxo TJMA: se o botao de download for <input type=submit>, replica o POST
    do form 'navbar' pela sessao e devolve (body, content_type). Devolve
    (None, '') quando NAO e este fluxo. So leitura: envia apenas o submit de
    download (nenhum verbo de acao), e o rotulo passa pela guarda de R7."""
    dados = pagina.evaluate(_JS_SERIALIZA_NAVBAR)
    if not dados or not dados.get("campos"):
        return None, ""
    regras.guarda_de_clique(dados.get("rotulo") or "Download")   # RAIL R7
    regras.guarda_de_url(dados["action"])
    r = contexto.request.post(dados["action"], form=dados["campos"],
                              timeout=int(espera_max * 1000))
    ct = (r.headers or {}).get("content-type", "")
    return (r.body() if r.status == 200 else b""), ct


def baixar_integral(contexto, cnj: str, url_autos: str,
                    espera_max: float = 300.0) -> dict:
    """
    Autos INTEGRAIS de um processo: abre a tela de autos, dispara o empacotamento,
    pega a URL assinada e busca o PDF pela sessao (GET). Salva em
    AUTOS/{cnj}/autos_integral_{sha8}.pdf. Idempotente por sha (pula se ja existe).
    """
    destino = RAIZ / "AUTOS" / cnj
    ja = sorted(destino.glob("autos_integral_*.pdf")) if destino.exists() else []
    if ja:
        return {"cnj": cnj, "status": "ja_existe",
                "arquivo": str(ja[-1]), "bytes": ja[-1].stat().st_size}
    regras.guarda_de_url(url_autos)
    pagina = contexto.new_page()
    try:
        pagina.on("dialog", lambda d: d.accept())   # "confirma download?" -> sim
        pagina.set_default_timeout(60_000)
        pagina.goto(url_autos, wait_until="domcontentloaded")
        if not _esperar_botao_download(pagina):
            return {"cnj": cnj, "status": "sem_pacote"}
        # DOIS fluxos: (a) submit -> PDF na resposta do POST (TJMA); (b) window.open
        # de URL assinada em S3 (TJPA). Tenta o submit; se nao for esse fluxo (body
        # None), cai no window.open.
        body, ct = _pacote_via_submit(pagina, contexto, espera_max)
        if body is None:
            url = disparar_pacote(pagina, espera_max)
            if not url:
                return {"cnj": cnj, "status": "sem_pacote"}
            url = _url_pacote_ok(url)
            r = contexto.request.get(url, timeout=180_000)
            body = r.body() if r.status == 200 else b""
        if not body or body[:5] != b"%PDF-":
            return {"cnj": cnj, "status": "nao_pdf", "bytes": len(body or b"")}
        sha = hashlib.sha256(body).hexdigest()
        destino.mkdir(parents=True, exist_ok=True)
        arq = destino / f"autos_integral_{sha[:8]}.pdf"
        arq.write_bytes(body)
        return {"cnj": cnj, "status": "ok", "arquivo": str(arq),
                "bytes": len(body), "sha256": sha}
    except Exception as e:  # noqa: BLE001
        return {"cnj": cnj, "status": "erro", "detalhe": str(e)[:160]}
    finally:
        try:
            pagina.close()
        except Exception:  # noqa: BLE001
            pass


def coletar_integral(s: "sessao.SessaoEfemera", cnj_alvo: str, todos: bool,
                     espera_max: float, pausa: float) -> list[dict]:
    """
    UM login -> autos integrais de UM processo (--cnj) ou de TODO o acervo
    (--todos). Le a aba Acervo do painel e baixa cada um. So leitura.

    E aqui que "um login" vira "N processos baixados": o titular autentica uma
    vez; o robo percorre o acervo sozinho. Escala sem reautenticar.
    """
    import json
    print()
    print("=" * 70)
    print("  BAIXAR AUTOS INTEGRAIS — um login, o robo percorre o acervo")
    print("=" * 70)
    # percorre a arvore do Acervo comarca a comarca (o robo abre a aba e expande
    # cada comarca sozinho — accordion); se nao houver arvore, le o que ja esta
    # na tela.
    try:
        acervo = acervo_completo(s.pagina)
        if not acervo:
            acervo = extrair_acervo(s.pagina.content())
    except regras.ViolacaoR7:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"[baixar] nao consegui ler o Acervo: {e}")
        return []
    if not acervo:
        print("[baixar] nenhum processo no Acervo. Abra a aba ACERVO no painel")
        print("         e rode de novo (ou confira se ha processos na conta).")
        return []
    print(f"[baixar] {len(acervo)} processo(s) no Acervo.")

    if todos:
        alvos = sorted(acervo.items())
    else:
        chave = _norm_cnj(cnj_alvo)
        alvos = [(c, u) for c, u in sorted(acervo.items()) if _norm_cnj(c) == chave]
        if not alvos:
            print(f"[baixar] {cnj_alvo} nao esta no Acervo. Vejo:")
            for c in sorted(acervo):
                print(f"           {c}")
            return []

    resultados: list[dict] = []
    for i, (cnj, url) in enumerate(alvos, 1):
        print(f"[{i:>2}/{len(alvos)}] {cnj} ... ", end="", flush=True)
        r = baixar_integral(s.contexto, cnj, url, espera_max)
        resultados.append(r)
        if r["status"] == "ok":
            print(f"OK  {r['bytes'] / 1024 / 1024:.1f} MB")
        elif r["status"] == "ja_existe":
            print(f"ja existe ({r['bytes'] / 1024 / 1024:.1f} MB) - pulado")
        else:
            print(f"** {r['status']} ** {r.get('detalhe', '')}")
        time.sleep(pausa)

    man = RAIZ / "AUTOS" / "_manifesto_integral.json"
    man.parent.mkdir(parents=True, exist_ok=True)
    man.write_text(json.dumps(
        {"gerado_em": datetime.now().isoformat(timespec="seconds"),
         "resultados": resultados}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    oks = [r for r in resultados if r["status"] in ("ok", "ja_existe")]
    mb = sum(r.get("bytes", 0) for r in oks) / 1024 / 1024
    falhas = [r for r in resultados if r["status"] not in ("ok", "ja_existe")]
    print("=" * 70)
    print(f">>> {len(oks)}/{len(resultados)} com autos ({mb:.1f} MB). Manifesto: {man}")
    if falhas:
        print(">>> pendencias: " + ", ".join(f"{r['cnj']}={r['status']}" for r in falhas))
    return resultados


def coletar(s: "sessao.SessaoEfemera", cnj_alvo: str,
            limite: int, pausa: float) -> Path | None:
    """
    Le o Acervo do painel, acha os autos do processo alvo e baixa as pecas —
    SEM abrir a tela de autos no navegador.

    Por que assim: a tela de autos tem anti-debug (um `debugger;` que congela a
    aba sob automacao — foi o "Debugger pausado" que travou o titular ao clicar
    no processo, em 16/07/2026). A saida e NAO renderizar: pega-se a URL dos
    autos no Acervo e busca-se o HTML por `context.request` (cookie da sessao,
    SEM executar o JS da pagina). Anti-debug e client-side; num GET puro ele nao
    roda. O titular so loga e deixa a comarca aberta — nao clica em nada.
    """
    print()
    print("=" * 70)
    print("  BAIXAR AUTOS — VOCE SO LOGA; EU BUSCO (leitura, sem anti-debug)")
    print("=" * 70)
    print("  NAO clique em processo (a tela de autos trava sob automacao).")
    print("  Deixe a aba ACERVO aberta, com a COMARCA do processo EXPANDIDA")
    print("  (para a linha dele aparecer). Eu leio o Acervo e busco os autos")
    print("  do CNJ pedido pela API, sem renderizar a pagina.")
    print("=" * 70)

    print(f"[baixar] lendo o Acervo do painel ({(s.pagina.url or '')[:60]})...")
    try:
        html_painel = s.pagina.content()
    except Exception as e:  # noqa: BLE001
        print(f"[baixar] nao consegui ler o painel: {e}")
        return None
    print(f"[baixar] painel lido ({len(html_painel)} bytes). Procurando processos...")

    acervo = extrair_acervo(html_painel)
    if not acervo:
        print("[baixar] nao vi processos no Acervo. Abra a aba ACERVO e expanda")
        print("         a comarca do processo, depois rode de novo.")
        return None
    print(f"[baixar] {len(acervo)} processo(s) visiveis no Acervo.")

    if not cnj_alvo:
        print("[baixar] diga qual baixar: rode com --cnj <numero>. Vejo estes:")
        for c in sorted(acervo):
            print(f"           {c}")
        return None

    chave = _norm_cnj(cnj_alvo)
    cnj = alvo_url = None
    for c, u in acervo.items():
        if _norm_cnj(c) == chave:
            cnj, alvo_url = c, u
            break
    if not alvo_url:
        print(f"[baixar] {cnj_alvo} nao esta visivel no Acervo. Expanda a comarca")
        print("         dele no painel. Processos que vejo agora:")
        for c in sorted(acervo):
            print(f"           {c}")
        return None

    regras.guarda_de_url(alvo_url)
    print(f"[baixar] {cnj}: buscando os autos pela API (sem renderizar)...")
    try:
        r = s.contexto.request.get(alvo_url, timeout=60_000)
        # paginas do legado sao ISO-8859-1; r.text() assume utf-8 e quebra.
        # os ids sao ASCII, entao decodificar com errors=ignore basta.
        html_autos = r.body().decode("utf-8", "ignore") if r.status == 200 else ""
    except Exception as e:  # noqa: BLE001
        print(f"[baixar] falha ao buscar os autos: {e}")
        return None
    if not html_autos:
        print(f"[baixar] os autos nao vieram (status={getattr(r, 'status', '?')}).")
        return None

    docs = extrair_documentos(html_autos)
    if not docs:
        print("[baixar] nao achei pecas na arvore dos autos — nada a baixar.")
        return None
    print(f"[baixar] {len(docs)} peca(s) na arvore.")
    if limite and len(docs) > limite:
        print(f"[baixar] baixando as {limite} primeiras (--limite).")
        docs = docs[:limite]

    destino = RAIZ / "AUTOS" / cnj / "originais"
    destino.mkdir(parents=True, exist_ok=True)

    indice = destino.parent / f"documentos_baixados_{datetime.now():%Y-%m-%d}.md"
    linhas = [f"# Autos baixados — {cnj} — {datetime.now():%Y-%m-%d %H:%M}",
              "", "Baixado pela API REST (documento/download), sessao do titular,",
              "somente leitura. Originais imutaveis.", "",
              "| ordem | idProcessoDocumento | nome | bytes | sha256 | arquivo |",
              "|---|---|---|---|---|---|"]

    baixados = hashes = 0
    for ordem, (iddoc, nome) in enumerate(docs, 1):
        ok, dados, status, ct = baixar_uma(s.contexto, iddoc)
        if not ok:
            print(f"  [{ordem:>3}] {iddoc}  FALHA (status={status} {ct[:30]})")
            linhas.append(f"| {ordem} | {iddoc} | {nome} | - | FALHA {status} | - |")
            time.sleep(pausa)
            continue
        sha = hashlib.sha256(dados).hexdigest()
        ext = _extensao(ct, dados)
        arquivo = f"{ordem:04d}_{_slug(nome) or iddoc}_{sha[:8]}.{ext}"
        alvo = destino / arquivo
        if any(p.name.endswith(f"_{sha[:8]}.{ext}") for p in destino.glob("*")):
            print(f"  [{ordem:>3}] {iddoc}  ja existe (sha {sha[:8]}) — pulado")
        else:
            alvo.write_bytes(dados)
            baixados += 1
            print(f"  [{ordem:>3}] {iddoc}  {len(dados):>8} B  {ext}  "
                  f"{(nome or '(sem nome)')[:40]}")
        hashes += 1
        linhas.append(f"| {ordem} | {iddoc} | {nome} | {len(dados)} | "
                      f"{sha[:16]} | {arquivo} |")
        time.sleep(pausa)   # rate limit humanizado

    indice.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\n[baixar] {baixados} peca(s) nova(s) salva(s) em {destino}")
    print(f"[baixar] indice: {indice}")
    return destino


def main() -> None:
    ap = argparse.ArgumentParser(description="Baixa os autos de processos (leitura).")
    ap.add_argument("--cnj", default="",
                    help="CNJ de UM processo (deixe a comarca dele aberta no Acervo)")
    ap.add_argument("--todos", action="store_true",
                    help="autos INTEGRAIS de TODO o acervo — um login, todos os processos")
    ap.add_argument("--pecas", action="store_true",
                    help="metodo antigo: peca a peca pela REST documento/download (fallback)")
    ap.add_argument("--limite", type=int, default=0,
                    help="[--pecas] baixar no maximo N pecas (0 = todas)")
    ap.add_argument("--espera", type=float, default=300.0,
                    help="segundos max p/ o servidor empacotar cada processo (integral)")
    ap.add_argument("--pausa", type=float, default=2.0,
                    help="segundos entre processos (rate limit; padrao 2.0)")
    ap.add_argument("--instancia", default="tjpa",
                    help="instancia PJe: " + ", ".join(i.chave for i in instancias.listar()))
    args = ap.parse_args()

    try:
        inst = instancias.definir(args.instancia)
    except KeyError as e:
        print("[baixar]", e)
        sys.exit(1)
    print(f"[baixar] instancia: {inst.nome} ({inst.host})"
          + ("" if inst.verificado else f" — NAO verificado: {inst.nota}"))

    reuso = sessao.sessao_viva_logada()
    ok, faltas = sessao.ambiente_ok(reuso=reuso)
    print("[ambiente]", "pronto" if ok else "INCOMPLETO",
          "(sessao viva detectada)" if reuso else "")
    for f in faltas:
        print("  -", f)
    if not ok:
        sys.exit(1)

    with sessao.SessaoEfemera() as s:
        if not s.esperar_login_humano():
            return
        if args.pecas:                       # fallback: peca a peca (REST)
            coletar(s, args.cnj, args.limite, args.pausa)
        elif args.todos or args.cnj:         # integral (padrao)
            coletar_integral(s, args.cnj, args.todos, args.espera, args.pausa)
        else:
            print("[baixar] diga --todos (acervo inteiro) ou --cnj <numero>.")
            print("         (--pecas usa o metodo antigo, peca a peca.)")


if __name__ == "__main__":
    main()
