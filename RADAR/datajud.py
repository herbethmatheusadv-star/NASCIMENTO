# -*- coding: utf-8 -*-
"""
Cliente da API Publica do DataJud (CNJ).

Para que serve: o DJEN conta o que foi PUBLICADO ("ha intimacao mandando
recolher o preparo"). O DataJud conta o que ACONTECEU no processo ("decurso de
prazo em 30/06, concluso para julgamento em 01/07"). Cruzando os dois da para
responder a unica pergunta que importa: o prazo foi cumprido ou nao?

Limites medidos na pratica (14/07/2026):
  - NAO indexa advogado/OAB: nao da para perguntar "quais sao meus processos".
    A lista de processos tem que vir do DJEN. Aqui so se consulta um a um.
  - Defasagem de ~4 dias em relacao ao andamento real.
  - Rate limit agressivo: HTTP 429 ja na terceira consulta seguida.

A chave abaixo e a chave PUBLICA que o CNJ divulga na documentacao da API. Nao
e credencial pessoal, nao identifica ninguem e nao da acesso a nada sigiloso.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

CHAVE_PUBLICA_CNJ = "cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="
BASE = "https://api-publica.datajud.cnj.jus.br/api_publica_{indice}/_search"

CACHE = Path(__file__).resolve().parent / ".cache_datajud.json"
CACHE_HORAS = 12          # a base so atualiza de tempos em tempos; nao adianta insistir
PAUSA_ENTRE_CONSULTAS = 1.5
TENTATIVAS_429 = 5

# Codigos da Tabela Processual Unificada do CNJ que interessam aqui
COD_DECURSO_PRAZO = 1051
COD_PETICAO = 85
COD_PUBLICACAO = 92
COD_DISPONIBILIZACAO = 1061
COD_CONCLUSAO = 51
COD_JULGAMENTO = {193, 196, 198, 199, 219, 220, 221, 237, 242, 246}


class Movimento:
    __slots__ = ("data", "codigo", "nome", "complementos")

    def __init__(self, data: date | None, codigo: int, nome: str, complementos: list[str]):
        self.data = data
        self.codigo = codigo
        self.nome = nome
        self.complementos = complementos

    def __repr__(self):
        d = self.data.strftime("%d/%m/%Y") if self.data else "??"
        return f"<{d} [{self.codigo}] {self.nome}>"


class Processo:
    __slots__ = ("numero", "tribunal", "classe", "orgao", "assuntos",
                 "ajuizamento", "atualizado", "movimentos")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def ultimos(self, n: int = 10) -> list[Movimento]:
        return sorted([m for m in self.movimentos if m.data],
                      key=lambda m: m.data, reverse=True)[:n]


# --------------------------------------------------------------------------

def indice_do_tribunal(sigla: str) -> str | None:
    """
    Sigla do DJEN -> indice do DataJud.

    O padrao e a sigla em minusculas (TJPA -> tjpa, TRT8 -> trt8). Tribunais
    fora desse padrao entram aqui conforme aparecerem.
    """
    if not sigla:
        return None
    s = sigla.strip().lower()
    return s or None


def _carregar_cache() -> dict:
    if not CACHE.exists():
        return {}
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _gravar_cache(c: dict) -> None:
    try:
        CACHE.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def _consultar_api(indice: str, numero: str, timeout: int = 60) -> dict | None:
    url = BASE.format(indice=indice)
    corpo = json.dumps({"query": {"match": {"numeroProcesso": numero}}}).encode("utf-8")

    for n in range(TENTATIVAS_429):
        req = urllib.request.Request(url, data=corpo, method="POST", headers={
            "Authorization": f"APIKey {CHAVE_PUBLICA_CNJ}",
            "Content-Type": "application/json",
            "User-Agent": "monitor-prazos/1.0",
        })
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                espera = 3 * (n + 1)
                print(f"      [DataJud rate limit] aguardando {espera}s...")
                time.sleep(espera)
                continue
            if e.code == 404:
                return None  # indice inexistente para esse tribunal
            print(f"      [DataJud HTTP {e.code}] {numero}")
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"      [DataJud falhou] {type(e).__name__}")
            return None
    print(f"      [DataJud] desisti de {numero} apos {TENTATIVAS_429} tentativas (429)")
    return None


def _parse_data(v) -> date | None:
    if not v:
        return None
    s = str(v)
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s.replace("Z", "+0000"), fmt).date()
        except ValueError:
            continue
    try:  # formato compacto que aparece em dataAjuizamento: 2026062512
        return datetime.strptime(s[:8], "%Y%m%d").date()
    except ValueError:
        return None


def consultar(numero_sem_mascara: str, sigla_tribunal: str,
              usar_cache: bool = True) -> Processo | None:
    """Busca um processo. Devolve None se o DataJud nao tiver."""
    indice = indice_do_tribunal(sigla_tribunal)
    if not indice:
        return None

    chave = f"{indice}:{numero_sem_mascara}"
    cache = _carregar_cache()
    if usar_cache and chave in cache:
        reg = cache[chave]
        quando = _parse_data(reg.get("_lido_em"))
        if quando and (date.today() - quando) < timedelta(hours=CACHE_HORAS / 24 + 1):
            if reg.get("_vazio"):
                return None
            return _montar(reg["dados"])

    d = _consultar_api(indice, numero_sem_mascara)
    time.sleep(PAUSA_ENTRE_CONSULTAS)

    hits = (d or {}).get("hits", {}).get("hits", [])
    if not hits:
        cache[chave] = {"_lido_em": date.today().isoformat(), "_vazio": True}
        _gravar_cache(cache)
        return None

    src = hits[0]["_source"]
    cache[chave] = {"_lido_em": date.today().isoformat(), "dados": src}
    _gravar_cache(cache)
    return _montar(src)


def _montar(src: dict) -> Processo:
    movs = []
    for m in (src.get("movimentos") or []):
        compl = [f"{c.get('nome')}: {c.get('descricao')}"
                 for c in (m.get("complementosTabelados") or [])]
        movs.append(Movimento(_parse_data(m.get("dataHora")),
                              int(m.get("codigo") or 0),
                              str(m.get("nome") or ""), compl))
    return Processo(
        numero=src.get("numeroProcesso"),
        tribunal=src.get("tribunal"),
        classe=(src.get("classe") or {}).get("nome"),
        orgao=(src.get("orgaoJulgador") or {}).get("nome"),
        assuntos=[a.get("nome") for a in (src.get("assuntos") or [])],
        ajuizamento=_parse_data(src.get("dataAjuizamento")),
        atualizado=_parse_data(src.get("dataHoraUltimaAtualizacao")),
        movimentos=movs,
    )


# --------------------------------------------------------------------------
# Cruzamento: o prazo foi cumprido?
# --------------------------------------------------------------------------

SEM_DADOS = "SEM_DADOS"
PETICAO_NO_PRAZO = "PETICAO_NO_PRAZO"
DECURSO_REGISTRADO = "DECURSO_REGISTRADO"
INDEFINIDO = "INDEFINIDO"

ROTULO_CUMPRIMENTO = {
    SEM_DADOS: "sem dados no DataJud",
    PETICAO_NO_PRAZO: "houve petição dentro do prazo",
    DECURSO_REGISTRADO: "o tribunal certificou DECURSO DE PRAZO",
    INDEFINIDO: "sem sinal claro",
}


def conferir_cumprimento(proc: Processo | None, publicacao: date,
                         vencimento: date, folga: int = 5) -> tuple[str, str]:
    """
    Cruza o prazo calculado com o andamento real. Devolve (situacao, detalhe).

    IMPORTANTE - isto e um SINAL, nao uma certeza. Um processo tem varios
    prazos correndo ao mesmo tempo; o "Decurso de Prazo" registrado pode ser de
    outro deles, e uma peticao no periodo pode tratar de outra coisa. Serve para
    dizer "olha isto aqui", nunca para dar baixa em prazo.
    """
    if proc is None:
        return SEM_DADOS, "processo não encontrado na base do CNJ"

    janela_ini = publicacao
    janela_fim = vencimento + timedelta(days=folga)

    decursos = [m for m in proc.movimentos
                if m.codigo == COD_DECURSO_PRAZO and m.data
                and vencimento - timedelta(days=2) <= m.data <= janela_fim]
    peticoes = [m for m in proc.movimentos
                if m.codigo == COD_PETICAO and m.data
                and janela_ini <= m.data <= vencimento + timedelta(days=1)]

    if decursos and not peticoes:
        d = sorted(decursos, key=lambda m: m.data)[0]
        return DECURSO_REGISTRADO, (f"decurso de prazo certificado em "
                                    f"{d.data.strftime('%d/%m/%Y')}, sem petição sua "
                                    f"no período")
    if peticoes:
        p = sorted(peticoes, key=lambda m: m.data)[-1]
        extra = f" (e há decurso em {decursos[0].data.strftime('%d/%m/%Y')} — confira)" \
                if decursos else ""
        return PETICAO_NO_PRAZO, (f"petição em {p.data.strftime('%d/%m/%Y')}, "
                                  f"dentro do prazo{extra}")
    if proc.atualizado and proc.atualizado < vencimento:
        return INDEFINIDO, (f"a base do CNJ só está atualizada até "
                            f"{proc.atualizado.strftime('%d/%m/%Y')}, antes do "
                            f"vencimento")
    return INDEFINIDO, "nenhuma petição nem decurso registrado no período"
