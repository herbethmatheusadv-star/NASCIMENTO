#!/usr/bin/env python3
"""
trt8_api.py — cliente da API REST do PJe NOVO (PDPJ). LEITURA, e so leitura.

O PJe novo (PDPJ / "Meu Painel", ex.: TRT-8) NAO fala o MNI SOAP (ver mni.py e
MAPA_PJE.md §13.8-13.9). Ele expoe uma API REST sob `/pje-comum-api/api/`. Este
modulo le o acervo do advogado por ela — apenas consultas GET.

  R7 e a MESMA do mni.py, nas mesmas camadas:
    1. AUSENCIA — nao existe neste arquivo funcao que faca escrita no tribunal.
       Nao ha o que chamar; chamar seria um AttributeError, nao um if a remover.
    2. ALLOWLIST — `ROTAS_PERMITIDAS` deixa passar so um punhado de rotas de
       leitura. A rota de avisos/expedientes fica DE FORA de proposito: e a
       candidata a gatilho de ato (como o consultarTeorComunicacao no MNI); so
       entra depois de o titular provar que so le.
    3. GUARDA DE URL — regras.guarda_de_url em toda chamada.

  CREDENCIAL (Emenda 05): o token (access_token) e do titular, colado A CADA
  EXECUCAO. Nao vai para disco, env, codigo nem log — vive na memoria e morre com
  o processo. Como obter (no navegador ja logado no painel do TRT-8): DevTools ->
  Application -> Cookies -> valor de `access_token` (a API aceita esse cookie no
  GET; comprovado 20/07/2026). Alternativa: Network -> Authorization: Bearer.

Uso:
  python CONECTOR/trt8_api.py --instancia trt8 --advogado 837986
  python CONECTOR/trt8_api.py --instancia trt8 --advogado 837986 --enum 5
"""
from __future__ import annotations

import argparse
import getpass
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass

import instancias
import regras

TIMEOUT = 60

# `idPainelAdvogadoEnum` (confirmado na sessao logada de 20/07/2026).
ENUM_PAINEL = {1: "Acervo Geral", 5: "Arquivados"}

# Allowlist de rotas de LEITURA. Qualquer outra e recusada. A rota
# `/pje-comum-api/api/quadroavisos/…` (avisos/expedientes) fica FORA de
# proposito — potencial gatilho de ato; so entra apos prova do titular.
ROTAS_PERMITIDAS = (
    r"^/pje-comum-api/api/paineladvogado/\d+/totalizadores\b",
    r"^/pje-comum-api/api/paineladvogado/\d+/processos\b",
    r"^/pje-comum-api/api/paineladvogado/\d+/orgaojulgadores\b",
    r"^/pje-comum-api/api/parametros/",
)


@dataclass
class Sessao:
    """Host da instancia + o COOKIE de sessao, do jeito que o navegador manda:
    'access_token=...; access_token_footer=...'. O PDPJ parte o JWT em dois
    cookies (o footer e a assinatura). Existe so enquanto o processo roda; nao ha
    salvar() nem carregar() — se um dia alguem quiser persistir, escreve do zero
    e o teste_regras barra."""
    host: str          # ex.: "https://pje.trt8.jus.br"
    _cookie: str       # "access_token=<hdr.payload>; access_token_footer=<assin>"

    def __repr__(self) -> str:
        return f"Sessao(host={self.host}, cookie=<oculto>)"

    __str__ = __repr__


def base_host(inst: "instancias.Instancia | None" = None) -> str:
    inst = inst or instancias.atual()
    if not getattr(inst, "api_pdpj", False):
        raise RuntimeError(
            f"{inst.nome} nao e PJe novo (PDPJ): nao tem a API /pje-comum-api. "
            f"Este cliente e para instancias com api_pdpj=True (ex.: trt8).")
    return f"https://{inst.host}"


def pedir_token() -> str:
    """Pergunta os DOIS cookies de sessao ao titular e monta o header Cookie.
    getpass nao ecoa nem vai ao historico; nada e gravado, morre com o processo.

    Descoberta 21/07/2026: o PDPJ NAO usa cabecalho Authorization — autentica por
    COOKIE, e parte o JWT em dois: `access_token` (cabecalho.dados, 2 partes) e
    `access_token_footer` (a assinatura). O navegador manda os dois; o servidor
    remonta. Copiar so o access_token vinha 'cortado' (sem assinatura) e dava 500.
    Por isso pedimos OS DOIS. Ver MAPA_PJE.md §13.11."""
    print("\n  Sessao PDPJ — os DOIS cookies, colados agora, NUNCA gravados.")
    print("  DevTools (F12) -> Application -> Cookies -> https://pje.trt8.jus.br .")
    print("  Copie o VALOR de cada um (aceito tambem no formato 'nome=valor'):\n")

    def _limpa(s: str) -> str:
        s = s.strip()
        # se colou 'access_token=...' ou 'Bearer ...', tira o prefixo
        s = re.sub(r"^\s*access_token(_footer)?\s*=\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"^Bearer\s+", "", s, flags=re.IGNORECASE)
        return s.rstrip(";").strip()

    at = _limpa(getpass.getpass("  1) access_token  (~1019 chars, TEM 1 ponto): "))
    print(f"     -> li {len(at)} chars, {at.count('.') + 1} parte(s)"
          + ("  ok" if at.count(".") == 1 else "  <== esperado: 2 partes / ~1019 chars"))
    ft = _limpa(getpass.getpass("  2) access_token_footer  (curto, SEM ponto): "))
    print(f"     -> li {len(ft)} chars, {ft.count('.') + 1} parte(s)"
          + ("  ok" if ft.count(".") == 0 and ft else "  <== esperado: 1 parte, sem ponto"))

    if not at or not ft:
        sys.exit("  Faltou um dos dois cookies — sem sessao, sem consulta.")
    # Sanidade de FORMA (nada gravado): access_token = cabecalho.dados (2 partes,
    # 1 ponto); footer = assinatura (1 parte, sem ponto). Se nao bate, provavel
    # troca dos dois ou cookie errado. Juntos fecham um JWT de 3 partes.
    if at.count(".") != 1 or ft.count(".") != 0:
        print("\n  [!] Nao bate: parece que os dois se trocaram ou veio o cookie errado.")
        print("      access_token = 2 partes (1 ponto), ~1019 chars; footer = sem ponto.")
        if input("      Seguir assim mesmo? (s/N): ").strip().lower() not in ("s", "sim"):
            sys.exit("      Ok — confira os DOIS cookies e rode de novo.")
    return f"access_token={at}; access_token_footer={ft}"


def _rota_permitida(rota: str) -> bool:
    return any(re.search(p, rota) for p in ROTAS_PERMITIDAS)


def _get(sessao: Sessao, rota: str, params: dict | None = None):
    """GET numa rota da allowlist. Devolve (ok, obj_json, erro)."""
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
    # O PDPJ autentica por COOKIE (access_token + access_token_footer), NAO por
    # cabecalho Authorization — confirmado na rede real 21/07/2026. So GET, entao
    # o Xsrf-Token (anti-CSRF de escrita) nao entra: e a linha R7 na porta.
    req.add_header("Cookie", sessao._cookie)
    req.add_header("Accept", "application/json, text/plain, */*")
    req.add_header("User-Agent", "SOJ-Conector/1.0 (leitura; OAB 39261/PA)")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return True, json.loads(r.read().decode("utf-8", "ignore")), ""
    except urllib.error.HTTPError as e:
        corpo = e.read()[:300].decode("utf-8", "ignore")
        if e.code in (401, 403):
            dica = " (token expirado? pegue um novo no navegador)"
        elif e.code == 500:
            dica = (" (token pode ter vindo CORTADO — copie o valor INTEIRO;"
                    " veja Network -> Authorization: Bearer)")
        else:
            dica = ""
        return False, None, f"HTTP {e.code}{dica} — {corpo}"
    except Exception as e:  # noqa: BLE001
        return False, None, f"{type(e).__name__}: {e}"


# ---------------------------------------------------------------------------
# As UNICAS consultas que existem neste arquivo
# ---------------------------------------------------------------------------

def totalizadores(sessao: Sessao, id_advogado: int):
    return _get(sessao, f"/pje-comum-api/api/paineladvogado/{id_advogado}/totalizadores",
                {"tipoPainelAdvogado": 0})


def _pagina_processos(sessao: Sessao, id_advogado: int, enum: int, pagina: int):
    # NB (21/07/2026): NAO enviar o cache-buster `data=<ms>` — o servidor devolve
    # HTTP 500 com ele (provado na sessao logada; sem ele, a lista vem certa). Era
    # ruido copiado do XHR do SPA. Ver MAPA_PJE.md §13.9.
    return _get(sessao, f"/pje-comum-api/api/paineladvogado/{id_advogado}/processos",
                {"pagina": pagina, "tamanhoPagina": 20, "tipoPainelAdvogado": enum,
                 "ordenacaoCrescente": "false", "idPainelAdvogadoEnum": enum})


def processos(sessao: Sessao, id_advogado: int, enum: int = 1) -> list:
    """Lista normalizada do painel `enum` (1=acervo, 5=arquivados), paginando."""
    out, pagina = [], 1
    while True:
        ok, obj, err = _pagina_processos(sessao, id_advogado, enum, pagina)
        if not ok:
            raise RuntimeError(err)
        for p in (obj.get("resultado") or []):
            out.append(_normalizar(p))
        if pagina >= (obj.get("qtdPaginas") or 1):
            break
        pagina += 1
    return out


def orgaos(sessao: Sessao, id_advogado: int, enum: int = 1):
    return _get(sessao, f"/pje-comum-api/api/paineladvogado/{id_advogado}/orgaojulgadores",
                {"tipoPainelAdvogado": enum})


def _normalizar(p: dict) -> dict:
    """Do JSON da API para os campos que a ficha PROC entende."""
    return {
        "numero": p.get("numeroProcesso"),
        "classe": p.get("classeJudicial"),
        "orgao": p.get("descricaoOrgaoJulgador"),
        "autora": p.get("nomeParteAutora"),
        "re": p.get("nomeParteRe"),
        "autuacao": (p.get("dataAutuacao") or "")[:10],
        "arquivamento": (p.get("dataArquivamento") or "")[:10] or None,
        "segredo": bool(p.get("segredoDeJustica")),
        "status": p.get("codigoStatusProcesso"),
        "id_pje": p.get("id"),
    }


# NAO existe funcao de escrita neste arquivo (peticao, ciencia, resposta). E R7:
# a API tem as duas faces na mesma porta; a unica defesa que nao depende de
# disciplina e a operacao nao estar escrita. Ver regras.py e MAPA_PJE.md §13.9.


def main() -> None:
    ap = argparse.ArgumentParser(description="Cliente REST do PJe novo (PDPJ) — leitura.")
    ap.add_argument("--instancia", default="trt8", help="instancia PDPJ (ex.: trt8)")
    ap.add_argument("--advogado", type=int, required=True,
                    help="id do advogado no painel (ex.: 837986)")
    ap.add_argument("--enum", type=int, default=1, choices=sorted(ENUM_PAINEL),
                    help="1=Acervo Geral, 5=Arquivados")
    args = ap.parse_args()

    try:
        inst = instancias.definir(args.instancia)
        host = base_host(inst)
    except (KeyError, RuntimeError) as e:
        sys.exit(f"  {e}")

    print("=" * 74)
    print("  PJe REST (PDPJ) — CONECTOR SOJ (somente leitura)")
    print(f"  instancia: {inst.nome}")
    print(f"  painel   : {ENUM_PAINEL[args.enum]}  (advogado {args.advogado})")
    print(f"  base     : {host}/pje-comum-api/api")
    print("=" * 74)

    sessao = Sessao(host, pedir_token())
    try:
        lista = processos(sessao, args.advogado, args.enum)
    except RuntimeError as e:
        sys.exit(f"    FALHOU: {e}")

    print(f"\n  {len(lista)} processo(s):\n")
    for p in lista:
        seg = " · SEGREDO" if p["segredo"] else ""
        print(f"    {p['numero']}  {p['classe']:6}  {(p['autora'] or '')[:26]:26} "
              f"x {(p['re'] or '')[:26]:26}{seg}")
        print(f"        {p['orgao']} · autuado {p['autuacao']}"
              f"{' · arquivado ' + p['arquivamento'] if p['arquivamento'] else ''}")
    print("\n" + "=" * 74)
    print("  R7: o cliente so LE (GET de consulta). As operacoes de escrita nao")
    print("  existem neste arquivo — agir no PJe segue sendo so do titular.")
    print("=" * 74)


if __name__ == "__main__":
    main()
