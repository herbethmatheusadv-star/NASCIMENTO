#!/usr/bin/env python3
"""
baixar_autos.py — baixa os autos de UM processo pela API REST do PJe/TJPA.

LEITURA, e so leitura. Roda DENTRO da sessao que o titular autenticou
(`sessao.py`, certificado + 2FA). Fecha a Fase de coleta do PLANO_SOJ: entrega
os PDFs em AUTOS/{cnj}/ para o importador (Fase 3) transformar em texto com
marcador de pagina.

  COMO FUNCIONA (desenho fechado em 16/07/2026 — ver CONECTOR/MAPA_PJE.md §11)

  1. O titular loga (o robo para no portao; ele digita cert + 2FA).
  2. O titular ABRE os autos de UM processo pela Acervo (nova janela). Isso e
     leitura; e ele quem clica.
  3. O robo detecta a pagina `listProcessoCompletoAdvogado`, LE o HTML e extrai:
       - o numero CNJ (do cabecalho);
       - todos os `idProcessoDocumento` (cada peca dos autos).
  4. Para cada peca, GET no UNICO endpoint de leitura:
         /pje/seam/resource/rest/pje-legacy/documento/download/{id}
     autenticado pelo COOKIE da sessao (JSESSIONID) que o navegador do titular
     ja tem — o robo NUNCA extrai nem guarda esse cookie.
  5. Salva em AUTOS/{cnj}/, com sha256, dedup e indice.

  R7 — POR QUE ISTO SO SABE LER

  Existe UMA rota construida aqui: `documento/download/{id}` (GET). Qualquer
  outra rota do `rest/pje-legacy/` — inclusive as de escrita — simplesmente NAO
  tem funcao neste arquivo. E allowlist, como no MNI, nao blocklist. Toda URL
  passa por `regras.guarda_de_url`. Nao ha clique em botao de acao: o robo so
  faz GET de documento. `teste_regras.py` varre este arquivo e quebra o build se
  aparecer capacidade de agir.

Uso:
    python CONECTOR/baixar_autos.py        # abre a sessao; voce loga e abre 1 processo
    python CONECTOR/baixar_autos.py --limite 5 --pausa 2
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

import regras
import sessao

RAIZ = Path(__file__).resolve().parents[1]
BASE = "https://pje.tjpa.jus.br/pje"

# A UNICA rota de leitura que este arquivo constroi e chama. Allowlist.
REST_DOWNLOAD = BASE + "/seam/resource/rest/pje-legacy/documento/download/{id}"

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


def _url_download(iddoc: str) -> str:
    url = REST_DOWNLOAD.format(id=iddoc)
    # allowlist + guarda: so passa o que comeca pelo prefixo de leitura, e a
    # guarda ainda barra qualquer verbo de acao que porventura aparecesse.
    if not url.startswith(BASE + "/seam/resource/rest/pje-legacy/documento/download/"):
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


# URL dos autos por processo, lida da aba Acervo do painel. Cada linha traz o
# CNJ junto do link listProcessoCompletoAdvogado.seam?id=..&ca=.. — o `ca` e um
# token por processo, valido so na sessao viva.
RE_ACERVO = re.compile(
    r'((?:/pje/[^"\']*)?listProcessoCompletoAdvogado\.seam\?id=\d+&(?:amp;)?ca=[a-f0-9]+)')


def extrair_acervo(html: str) -> dict[str, str]:
    """{cnj: url_dos_autos} a partir do HTML do painel (aba Acervo aberta)."""
    out: dict[str, str] = {}
    html = html or ""
    for m in RE_ACERVO.finditer(html):
        caminho = htmlmod.unescape(m.group(1))
        if caminho.startswith("http"):
            url = caminho
        elif caminho.startswith("/pje"):
            url = "https://pje.tjpa.jus.br" + caminho
        else:
            url = BASE + "/Processo/ConsultaProcesso/Detalhe/" + caminho
        # o CNJ vem DEPOIS do link, no texto da linha, ~600 chars a frente
        # (medido no HTML real 16/07/2026; 400 nao alcancava). Janela de 1200
        # cobre com folga sem invadir a proxima linha (~1700 a frente).
        cm = RE_CNJ.search(html[m.start():m.start() + 1200])
        if cm:
            out.setdefault(cm.group(0), url)
    return out


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
    ap = argparse.ArgumentParser(description="Baixa os autos de um processo (leitura).")
    ap.add_argument("--cnj", default="",
                    help="numero CNJ do processo (deixe a comarca dele aberta no Acervo)")
    ap.add_argument("--limite", type=int, default=0,
                    help="baixar no maximo N pecas (0 = todas)")
    ap.add_argument("--pausa", type=float, default=1.5,
                    help="segundos entre downloads (rate limit; padrao 1.5)")
    args = ap.parse_args()

    ok, faltas = sessao.ambiente_ok()
    print("[ambiente]", "pronto" if ok else "INCOMPLETO")
    for f in faltas:
        print("  -", f)
    if not ok:
        sys.exit(1)

    with sessao.SessaoEfemera() as s:
        if not s.esperar_login_humano():
            return
        coletar(s, args.cnj, args.limite, args.pausa)


if __name__ == "__main__":
    main()
