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
    """Host da instancia + o Bearer. Existe so enquanto o processo roda; nao ha
    salvar() nem carregar() — se um dia alguem quiser persistir, escreve do zero
    e o teste_regras barra."""
    host: str          # ex.: "https://pje.trt8.jus.br"
    _token: str

    def __repr__(self) -> str:
        return f"Sessao(host={self.host}, token=<oculto>)"

    __str__ = __repr__


def base_host(inst: "instancias.Instancia | None" = None) -> str:
    inst = inst or instancias.atual()
    if not getattr(inst, "api_pdpj", False):
        raise RuntimeError(
            f"{inst.nome} nao e PJe novo (PDPJ): nao tem a API /pje-comum-api. "
            f"Este cliente e para instancias com api_pdpj=True (ex.: trt8).")
    return f"https://{inst.host}"


def pedir_token() -> str:
    """Pergunta o Bearer ao titular. getpass nao ecoa nem vai ao historico."""
    print("\n  Token PDPJ (access_token) — colado agora, nunca gravado. Ele morre")
    print("  com este processo. No navegador ja logado no painel do TRT-8:")
    print("  DevTools -> Application -> Cookies -> valor de 'access_token'")
    print("  (ou Network -> chamada /pje-comum-api -> Authorization: Bearer).\n")
    tok = getpass.getpass("  Bearer (nao aparece na tela): ").strip()
    tok = re.sub(r"^Bearer\s+", "", tok, flags=re.IGNORECASE).strip()
    if not tok:
        sys.exit("  Sem token, sem consulta.")
    # Sanidade de FORMA (nao de conteudo, nada gravado): um JWT tem 3 partes
    # nao-vazias separadas por ponto. Se vier cortado (copia parcial do cookie),
    # o servidor responde HTTP 500 cru — melhor avisar aqui, na hora.
    partes = tok.split(".")
    if len(partes) != 3 or not all(partes):
        print("\n  [!] ESSE TOKEN PARECE INCOMPLETO (cortado).")
        print("      Um token bom tem 3 partes separadas por ponto; a ultima (a")
        print("      validacao) veio vazia. A copia do cookie costuma cortar.")
        print("      >> Pegue o token INTEIRO assim: DevTools (F12) -> aba Network")
        print("         -> clique numa chamada 'pje-comum-api' -> Headers -> em")
        print("         'Request Headers' copie o valor apos 'Authorization: Bearer'.")
        resp = input("\n      Seguir mesmo assim? (s/N): ").strip().lower()
        if resp not in ("s", "sim"):
            sys.exit("      Ok — pegue o token inteiro e rode de novo.")
    return tok


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
    # A sessao logada autentica o GET pelo cookie access_token (comprovado na
    # sessao de 20/07/2026); mandamos tambem como Bearer por robustez. So GET,
    # entao o Xsrf-Token (anti-CSRF de escrita) nao entra.
    req.add_header("Cookie", f"access_token={sessao._token}")
    req.add_header("Authorization", f"Bearer {sessao._token}")
    req.add_header("Accept", "application/json")
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
