#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Prazos — DJEN / Nascimento Advocacia

Consulta as comunicacoes processuais publicadas no Diario de Justica Eletronico
Nacional (DJEN/CNJ) para uma OAB e monta um relatorio de prazos estimados.

Uso:
    python monitor_prazos.py                    # usa o config.json
    python monitor_prazos.py --dias 30          # janela de busca (padrao 15)
    python monitor_prazos.py --oab 12345 --uf PA
    python monitor_prazos.py --sem-navegador    # nao abre o HTML no final

Sem dependencias externas: so a biblioteca padrao do Python.
"""
from __future__ import annotations

import argparse
import html as html_mod
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date, datetime, timedelta
from pathlib import Path

import classificador
import datajud

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
BASE = Path(__file__).resolve().parent
ARQ_CONFIG = BASE / "config.json"
ARQ_FERIADOS = BASE / "feriados_locais.txt"
ARQ_RESOLVIDOS = BASE / "resolvidos.txt"
DIR_RELATORIOS = BASE / "relatorios"

PRAZO_PADRAO = 15
ITENS_POR_PAGINA = 100
MAX_PAGINAS = 50
DIAS_POR_BLOCO = 45  # janelas grandes viram varias consultas: o DJEN cai menos

# A janela de busca filtra por DATA DE DISPONIBILIZACAO, mas o prazo vive muito
# depois dela: 15 dias uteis sao ~23 dias corridos, e passam de 50 se
# atravessarem o recesso. Por isso a janela e calculada, nao chutada.
JANELA_PISO = 45          # nunca olhar menos que isso para tras
JANELA_TETO = 200         # limite de sanidade
PRAZO_REFERENCIA = 30     # dias uteis usados para dimensionar a janela:
                          # cobre um prazo de 15 contado em dobro
MARGEM_JANELA = 7         # folga em dias corridos


# --------------------------------------------------------------------------
# Calendario forense
# --------------------------------------------------------------------------

def calcular_pascoa(ano: int) -> date:
    """Domingo de Pascoa pelo algoritmo anonimo gregoriano (Meeus/Butcher)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes, dia = divmod(h + l - 7 * m + 114, 31)
    return date(ano, mes, dia + 1)


def feriados_nacionais(ano: int) -> dict[date, str]:
    """Feriados nacionais com efeito forense em todo o pais."""
    p = calcular_pascoa(ano)
    fer = {
        date(ano, 1, 1): "Confraternizacao Universal",
        date(ano, 4, 21): "Tiradentes",
        date(ano, 5, 1): "Dia do Trabalho",
        date(ano, 9, 7): "Independencia",
        date(ano, 10, 12): "Nossa Senhora Aparecida",
        date(ano, 11, 2): "Finados",
        date(ano, 11, 15): "Proclamacao da Republica",
        date(ano, 12, 25): "Natal",
        p - timedelta(days=48): "Carnaval (segunda)",
        p - timedelta(days=47): "Carnaval (terca)",
        p - timedelta(days=46): "Quarta-feira de Cinzas",
        p - timedelta(days=2): "Sexta-feira Santa",
        p + timedelta(days=60): "Corpus Christi",
    }
    if ano >= 2024:
        # Lei 14.759/2023
        fer[date(ano, 11, 20)] = "Consciencia Negra"
    return fer


RE_ESCOPO = re.compile(r"^(?:\*|[A-Z]{2,5}\d{0,2})$")


def ler_feriados_locais(caminho: Path) -> list[tuple[date, str, str]]:
    """
    Le o arquivo de feriados locais.

    Formato:  YYYY-MM-DD  [ESCOPO]  Descricao
    ESCOPO e a sigla do tribunal (TJPA, TJMA, TRT8...) ou * para todos.
    Omitir o escopo equivale a *.

    O escopo existe porque feriado estadual nao e nacional: 28/07 e feriado no
    Maranhao e dia util no Para. Quem atua em mais de um estado nao pode ter um
    calendario so.
    """
    if not caminho.exists():
        return []
    extra: list[tuple[date, str, str]] = []
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        partes = linha.split()
        try:
            d = datetime.strptime(partes[0], "%Y-%m-%d").date()
        except (ValueError, IndexError):
            print(f"  [aviso] feriados_locais.txt linha {n} ignorada: {linha!r}")
            continue
        resto = partes[1:]
        escopo = "*"
        if resto and RE_ESCOPO.match(resto[0]):
            escopo = resto[0].upper()
            resto = resto[1:]
        extra.append((d, escopo, " ".join(resto) or "feriado local"))
    return extra


def ler_resolvidos(caminho: Path) -> dict[tuple[str, str], str]:
    """
    Le o que o advogado ja marcou como tratado.

    Chave: (numero do processo so com digitos, data de disponibilizacao ISO).
    Valor: a nota que ele escreveu.
    """
    if not caminho.exists():
        return {}
    marcados: dict[tuple[str, str], str] = {}
    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        linha = linha.strip()
        if not linha or linha.startswith("#"):
            continue
        nota = ""
        if "#" in linha:
            linha, nota = linha.split("#", 1)
            nota = nota.strip()
        partes = linha.split()
        if len(partes) < 2:
            print(f"  [aviso] resolvidos.txt linha {n} ignorada: falta a data")
            continue
        num = re.sub(r"\D", "", partes[0])
        try:
            d = datetime.strptime(partes[1], "%Y-%m-%d").date()
        except ValueError:
            print(f"  [aviso] resolvidos.txt linha {n}: data invalida {partes[1]!r}")
            continue
        if num:
            marcados[(num, d.isoformat())] = nota or "marcado como resolvido"
    return marcados


class Calendario:
    """
    Dias uteis forenses: exclui fins de semana, feriados e recesso.

    Todo metodo recebe `tribunal` (a sigla que vem do DJEN, ex. TJPA) para
    resolver os feriados de escopo estadual. Sem tribunal, valem so os
    feriados nacionais e os locais marcados com *.
    """

    def __init__(self, feriados_extra: list[tuple[date, str, str]] | None = None):
        self.extra = feriados_extra or []
        self._cache: dict[tuple[int, str], dict[date, str]] = {}

    def feriados(self, ano: int, tribunal: str | None = None) -> dict[date, str]:
        alvo = (tribunal or "*").upper()
        chave = (ano, alvo)
        if chave not in self._cache:
            f = feriados_nacionais(ano)
            for d, escopo, desc in self.extra:
                if d.year == ano and (escopo == "*" or escopo == alvo):
                    f[d] = desc
            self._cache[chave] = f
        return self._cache[chave]

    @staticmethod
    def em_recesso(d: date) -> bool:
        """Art. 220 do CPC e art. 775-A da CLT: 20/12 a 20/01, inclusive."""
        return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)

    def motivo_nao_util(self, d: date, tribunal: str | None = None) -> str | None:
        if d.weekday() >= 5:
            return "sabado/domingo"
        f = self.feriados(d.year, tribunal)
        if d in f:
            return f[d]
        if self.em_recesso(d):
            return "recesso forense (art. 220 CPC / 775-A CLT)"
        return None

    def eh_util(self, d: date, tribunal: str | None = None) -> bool:
        return self.motivo_nao_util(d, tribunal) is None

    def proximo_util(self, d: date, tribunal: str | None = None) -> date:
        """Primeiro dia util seguinte a `d` (nunca o proprio `d`)."""
        x = d + timedelta(days=1)
        while not self.eh_util(x, tribunal):
            x += timedelta(days=1)
        return x

    def contar(self, inicio: date, dias_uteis: int, tribunal: str | None = None) -> date:
        """N-esimo dia util a partir de `inicio`, contando `inicio` como dia 1."""
        d = inicio
        restantes = dias_uteis - 1
        while restantes > 0:
            d += timedelta(days=1)
            if self.eh_util(d, tribunal):
                restantes -= 1
        return d

    def uteis_entre(self, inicio: date, fim: date, tribunal: str | None = None) -> int:
        """Dias uteis de `inicio` (exclusive) ate `fim` (inclusive)."""
        if fim < inicio:
            return -self.uteis_entre(fim, inicio, tribunal)
        n, d = 0, inicio
        while d < fim:
            d += timedelta(days=1)
            if self.eh_util(d, tribunal):
                n += 1
        return n


def calcular_prazo(disponibilizacao: date, dias: int, cal: Calendario,
                   tribunal: str | None = None):
    """
    Art. 224, §2o CPC : publicacao = 1o dia util seguinte a disponibilizacao.
    Art. 224, §3o CPC : contagem inicia no 1o dia util seguinte a publicacao.
    Art. 219 CPC / 775 CLT : contagem em dias uteis.

    Como so dias uteis sao contados, o vencimento ja cai em dia util - a
    prorrogacao do art. 224, §1o fica implicita.
    """
    publicacao = cal.proximo_util(disponibilizacao, tribunal)
    inicio = cal.proximo_util(publicacao, tribunal)
    vencimento = cal.contar(inicio, dias, tribunal)
    return publicacao, inicio, vencimento


def janela_necessaria(hoje: date, cal: Calendario,
                      dias_uteis: int = PRAZO_REFERENCIA) -> int:
    """
    Quantos dias corridos olhar para tras para nao perder prazo ainda vivo.

    O DJEN filtra por data de disponibilizacao, mas o prazo so morre bem
    depois: 15 dias uteis viram ~23 corridos, e mais de 50 se cair no recesso.
    Uma janela fixa curta esconde prazo vigente - foi o que aconteceu aqui:
    a janela de 15 dias omitia um prazo que vencia no proprio dia.

    Entao a gente anda para tras ate achar a disponibilizacao mais antiga cujo
    prazo ainda estaria correndo hoje. Como disponibilizar antes significa
    vencer antes, basta parar no primeiro dia ja vencido. Em janeiro isso
    devolve uma janela naturalmente maior, por causa do recesso.
    """
    d = hoje
    piso = hoje - timedelta(days=JANELA_TETO)
    while d > piso:
        _, _, venc = calcular_prazo(d, dias_uteis, cal)
        if venc < hoje:
            return max(JANELA_PISO, min(JANELA_TETO, (hoje - d).days + MARGEM_JANELA))
        d -= timedelta(days=1)
    return JANELA_TETO


# --------------------------------------------------------------------------
# API do DJEN
# --------------------------------------------------------------------------

class FalhaConsulta(Exception):
    """A consulta a um bloco falhou mesmo depois das tentativas."""


def _requisitar(params: dict, timeout: int, tentativas: int = 4) -> dict:
    """
    GET com retry e backoff.

    O DJEN devolve HTTP 500 de forma intermitente - a mesma consulta que falha
    agora responde daqui a alguns segundos. Nao adianta repetir erro 4xx (a
    consulta e que esta errada), mas 5xx, timeout e queda de conexao merecem
    nova tentativa.
    """
    url = f"{API}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "monitor-prazos/1.0"})

    ultimo = ""
    for n in range(tentativas):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500:
                raise FalhaConsulta(f"HTTP {e.code} ({e.reason}) - consulta rejeitada")
            ultimo = f"HTTP {e.code} ({e.reason})"
        except urllib.error.URLError as e:
            ultimo = f"conexao: {e.reason}"
        except TimeoutError:
            ultimo = "timeout"
        except json.JSONDecodeError:
            ultimo = "resposta nao e JSON"

        if n < tentativas - 1:
            espera = 2 ** n
            print(f"    [instabilidade do DJEN: {ultimo}] nova tentativa em {espera}s...")
            time.sleep(espera)

    raise FalhaConsulta(f"{ultimo} apos {tentativas} tentativas")


def _consultar_bloco(oab: str, uf: str, inicio: date, fim: date,
                     timeout: int) -> list[dict]:
    itens: list[dict] = []
    pagina = 1
    while pagina <= MAX_PAGINAS:
        dados = _requisitar({
            "numeroOab": oab,
            "ufOab": uf.upper(),
            "dataDisponibilizacaoInicio": inicio.isoformat(),
            "dataDisponibilizacaoFim": fim.isoformat(),
            "itensPorPagina": ITENS_POR_PAGINA,
            "pagina": pagina,
        }, timeout)
        lote = dados.get("items") or []
        itens.extend(lote)
        total = dados.get("count") or 0
        if not lote or len(itens) >= total:
            break
        pagina += 1
    return itens


def fatiar(inicio: date, fim: date, tamanho: int) -> list[tuple[date, date]]:
    """Quebra o periodo em blocos de no maximo `tamanho` dias."""
    blocos = []
    a = inicio
    while a <= fim:
        b = min(a + timedelta(days=tamanho - 1), fim)
        blocos.append((a, b))
        a = b + timedelta(days=1)
    return blocos


def consultar_djen(oab: str, uf: str, inicio: date, fim: date,
                   timeout: int = 60) -> tuple[list[dict], list[tuple[date, date]]]:
    """
    Consulta o periodo em blocos e devolve (itens, periodos_que_falharam).

    Fatiar tem dois motivos: janelas menores sao consultas mais leves (menos
    500), e se um bloco cair mesmo assim, a gente sabe EXATAMENTE qual pedaco
    ficou faltando em vez de perder o relatorio inteiro. Quem chama e obrigado
    a olhar a segunda lista: um relatorio de prazos incompleto que se apresenta
    como completo e pior do que relatorio nenhum.
    """
    itens: list[dict] = []
    falhas: list[tuple[date, date]] = []
    blocos = fatiar(inicio, fim, DIAS_POR_BLOCO)
    for i, (a, b) in enumerate(blocos, 1):
        if len(blocos) > 1:
            print(f"  bloco {i}/{len(blocos)}: {a.strftime('%d/%m/%Y')} a "
                  f"{b.strftime('%d/%m/%Y')}...")
        try:
            itens.extend(_consultar_bloco(oab, uf, a, b, timeout))
        except FalhaConsulta as ex:
            print(f"    [FALHOU] {a.strftime('%d/%m/%Y')} a {b.strftime('%d/%m/%Y')}: {ex}")
            falhas.append((a, b))
    return itens, falhas


# --------------------------------------------------------------------------
# Texto
# --------------------------------------------------------------------------

# Pega "prazo de 15 dias", "prazo de 05 (cinco) dias", "prazo comum de 15 dias"
# e tambem "prazo legal (10 dias)" - esta ultima forma, sem o "de", e como as
# sentencas de JEC anunciam o prazo do recurso. Ela escapava e custou caro:
# ver BUG-01 em _SISTEMA/logs/bugs_radar.md.
RE_PRAZO = re.compile(
    r"prazo\s+(?:\w+\s+){0,3}?(?:de\s+)?\(?\s*(\d{1,3})\s*\)?\s*"
    r"(?:\([^)]{0,40}\)\s*)?dias?\b",
    re.IGNORECASE,
)

# Contextos onde um prazo NAO e do cliente: sao prazos que a decisao apenas
# menciona (arquivamento, cumprimento voluntario do adversario, decurso).
# Confundi-los com o prazo da parte foi o BUG-01: numa sentenca de JEC, o
# "prazo de 15 dias ... arquive-se" virou o prazo do recurso, que era de 10 -
# sete dias a MAIS do que o advogado tinha.
#
# ATENCAO: estes padroes rodam sobre classificador.normalizar() - texto SEM
# acento. Escreva-os sem acento. Na primeira versao desta correcao o padrao
# dizia "voluntario" e o texto real trazia "voluntario" com acento agudo: dois
# prazos alheios passaram batido. E o mesmo motivo pelo qual todo o resto do
# classificador normaliza antes de casar.
RE_CONTEXTO_ALHEIO = re.compile(
    r"arquive-se|arquivamento|"
    r"cumprimento\s+voluntario|"
    r"sem\s+manifesta\w+\s+d[ao]s?\s+partes?|"
    r"decorrid[oa]\s+o\s+prazo|"
    r"sobrestamento|suspens\w+\s+do\s+processo",
    re.IGNORECASE,
)

# Contextos que confirmam: este prazo e uma providencia da parte.
RE_CONTEXTO_PROPRIO = re.compile(
    r"interpos\w+|interpor|recorrer|recurso|contrarraz\w+|"
    r"contestar|contesta\w+|impugna\w+|embargos|"
    r"emend\w+|especific\w+\s+(?:as\s+)?provas|"
    r"apresent\w+|junt\w+|comprov\w+|recolh\w+|"
    r"sob\s+pena\s+de|manifestar-se|manifestem-se",
    re.IGNORECASE,
)

# Um termo/ata de audiencia se anuncia no proprio texto. Nao da para usar o
# tipo_de_ato() aqui: o termo real de 22/06/2026 traz "conclusos para decisao"
# no fim e e classificado como "decisao", porque essa entrada vem antes na lista
# de prioridade do classificador.
RE_TERMO_AUDIENCIA = re.compile(
    r"\btermo\s+de\s+audiencia\b|\bata\s+de\s+audiencia\b", re.IGNORECASE)

LIMITE_CLAUSULA = 400  # teto de seguranca para a busca de fronteira


def _clausula(texto: str, ini: int, fim: int) -> str:
    """
    Devolve a clausula (frase) que contem o trecho [ini:fim].

    Por que nao uma janela de N caracteres: numa sentenca densa, o "arquive-se"
    de uma frase fica a poucos caracteres do prazo da frase SEGUINTE e
    contamina o julgamento. A unidade de sentido e a frase, delimitada por
    ponto, ponto-e-virgula ou quebra de linha.
    """
    piso = max(0, ini - LIMITE_CLAUSULA)
    inicio = max(texto.rfind(". ", piso, ini), texto.rfind("; ", piso, ini),
                 texto.rfind("\n", piso, ini))
    inicio = piso if inicio < 0 else inicio + 1

    teto = min(len(texto), fim + LIMITE_CLAUSULA)
    cortes = [c for c in (texto.find(". ", fim, teto), texto.find("; ", fim, teto),
                          texto.find("\n", fim, teto)) if c >= 0]
    final = min(cortes) if cortes else teto
    return texto[inicio:final]


def limpar_html(texto: str) -> str:
    if not texto:
        return ""
    t = re.sub(r"<br\s*/?>", "\n", texto, flags=re.IGNORECASE)
    t = re.sub(r"</p\s*>", "\n", t, flags=re.IGNORECASE)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html_mod.unescape(t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n", t)
    return t.strip()


def detectar_prazos(texto: str) -> dict:
    """
    Acha os prazos do texto e diz QUAIS sao do cliente.

    Devolve {"escolhido": int|None, "candidatos": [int], "descartados": [int],
             "ambiguo": bool}.

    Por que nao basta pegar o primeiro "prazo de N dias" (BUG-01, 15/07/2026):
    uma sentenca de JEC diz, em clausulas diferentes, "recurso inominado no
    prazo legal (10 dias)" - o prazo do cliente - e tambem "decorrido o prazo
    de 15 dias sem manifestacao das partes, arquive-se" e "aguarde-se o prazo
    de 15 (quinze) dias para cumprimento voluntario" - que nao sao dele. O
    primeiro match era o 15, e o relatorio anunciava vencimento SETE DIAS
    depois do real, com o rotulo "detectado no texto" (confianca alta).

    Regras, na ordem:
      1. prazo em contexto alheio (arquivamento, cumprimento voluntario,
         decurso) e DESCARTADO;
      2. sobra mais de um valor distinto -> escolhe o MENOR e marca ambiguo:
         errar para menos antecipa a data (chato); errar para mais perde o
         prazo (fatal). Ambiguo vai para a fila vermelha do briefing.
    """
    candidatos: list[int] = []
    descartados: list[int] = []
    t = texto or ""
    for m in RE_PRAZO.finditer(t):
        n = int(m.group(1))
        if not (1 <= n <= 60):
            continue
        clausula = classificador.normalizar(_clausula(t, m.start(), m.end()))
        if RE_CONTEXTO_ALHEIO.search(clausula):
            descartados.append(n)
        else:
            candidatos.append(n)

    unicos = sorted(set(candidatos))
    return {
        "escolhido": unicos[0] if unicos else None,
        "candidatos": unicos,
        "descartados": sorted(set(descartados)),
        "ambiguo": len(unicos) > 1,
    }


def detectar_prazo(texto: str) -> int | None:
    """Compatibilidade: so o prazo escolhido. Ver detectar_prazos()."""
    return detectar_prazos(texto)["escolhido"]


# Atos que so comunicam: nao abrem prazo por si. "Termo/ata de audiencia" entrou
# aqui no BUG-02 (15/07/2026): um termo de conciliacao SEM ACORDO virou alerta
# [ATENCAO] de 15 dias "padrao assumido" - prazo que nao existe - competindo com
# o prazo verdadeiro do mesmo processo. Alerta falso e o comeco do fim: quem
# recebe alarme sem motivo para de ler o relatorio.
def eh_meramente_informativo(tipo: str, texto: str = "") -> bool:
    """
    Comunicacoes que normalmente nao abrem prazo para a parte.

    `texto` e opcional so por compatibilidade com chamadas antigas; passe-o
    sempre que tiver, porque o tipo do DJEN diz "Intimacao" ate para um termo
    de audiencia.
    """
    t = (tipo or "").lower()
    if "distribui" in t or "pauta" in t:
        return True
    # INTIMACAO PARA audiencia tambem nao abre prazo: convoca. Sem isto, o
    # padrao assumido de 15 dias transforma a convocacao num prazo ficticio que
    # "vence" e desce para o rodape - foi o que escondeu a audiencia do EDIO
    # (BUG-05). Nao vira informativo se o texto trouxer ordem com prazo junto.
    if texto and classificador.tipo_de_ato(texto) == "intimacao_audiencia":
        ordem = classificador.trechos_de_ordem(texto)
        return detectar_prazos(ordem)["escolhido"] is None
    if texto and RE_TERMO_AUDIENCIA.search(classificador.normalizar(texto)):
        # ... a menos que o proprio termo traga ORDEM COM PRAZO a parte.
        # O gatilho e o prazo, nao o "sob pena de": o termo real de 22/06/2026
        # transcreve um pedido do advogado ADVERSO ("intimacao exclusiva ...
        # sob pena de nulidade") - pedido de terceiro nao e ordem ao cliente.
        ordem = classificador.trechos_de_ordem(texto)
        return detectar_prazos(ordem)["escolhido"] is None
    return False


# --------------------------------------------------------------------------
# Processamento
# --------------------------------------------------------------------------

def processar(itens: list[dict], cal: Calendario, prazo_padrao: int, hoje: date,
              resolvidos: dict[tuple[str, str], str] | None = None) -> list[dict]:
    resolvidos = resolvidos or {}
    linhas = []
    for it in itens:
        try:
            disp = datetime.strptime(it["data_disponibilizacao"], "%Y-%m-%d").date()
        except (KeyError, TypeError, ValueError):
            continue

        texto = limpar_html(it.get("texto") or "")
        tipo = it.get("tipoComunicacao") or "-"
        tribunal = it.get("siglaTribunal") or ""
        # o DJEN manda o numero nos dois formatos; qualquer um serve, porque a
        # chave e so os digitos
        num_digitos = re.sub(r"\D", "", it.get("numero_processo")
                             or it.get("numeroprocessocommascara") or "")
        deteccao = detectar_prazos(texto)
        detectado = deteccao["escolhido"]
        informativo = eh_meramente_informativo(tipo, texto)
        dias = detectado or prazo_padrao

        # o tribunal entra na conta: feriado estadual vale so no seu estado
        publicacao, inicio, vencimento = calcular_prazo(disp, dias, cal, tribunal)
        restantes = cal.uteis_entre(hoje, vencimento, tribunal)

        if vencimento < hoje:
            nivel, rotulo = 0, "VENCIDO"
        elif vencimento == hoje:
            nivel, rotulo = 1, "VENCE HOJE"
        elif restantes <= 2:
            nivel, rotulo = 2, "CRITICO"
        elif restantes <= 5:
            nivel, rotulo = 3, "ATENCAO"
        else:
            nivel, rotulo = 4, "NO PRAZO"

        analise = classificador.analisar(texto, it.get("destinatarios") or [])
        # vencido + sancao grave nao pode ser tratado como agua passada: e
        # justamente o caso do agravo que virou desercao enquanto o relatorio
        # o listava como "provavelmente ja cumprido"
        if nivel == 0 and analise["gravidade"] >= 3:
            rotulo = "VENCIDO GRAVE"

        # Audiencia: dia do compromisso, nao de vencimento de prazo. Guardado
        # como date (e nao datetime) para poder ordenar junto com vencimento.
        aud_dt = analise.get("audiencia_em")
        aud_data = aud_dt.date() if aud_dt else None
        aud_dias = (aud_data - hoje).days if aud_data else None
        if aud_data and aud_dias is not None and aud_dias >= 0:
            if aud_dias == 0:
                rotulo = "AUDIENCIA HOJE"
            elif aud_dias == 1:
                rotulo = "AUDIENCIA AMANHA"
            else:
                rotulo = f"AUDIENCIA EM {aud_dias} DIAS"

        advs = [
            (a.get("advogado") or {}).get("nome", "")
            for a in (it.get("destinatarioadvogados") or [])
        ]
        partes = [
            d.get("nome", "") for d in (it.get("destinatarios") or [])
        ]

        linhas.append({
            **analise,
            "processo": it.get("numeroprocessocommascara") or it.get("numero_processo") or "-",
            "tribunal": tribunal or "-",
            "orgao": it.get("nomeOrgao") or "-",
            "classe": (it.get("nomeClasse") or "-").title(),
            "tipo": tipo,
            "disponibilizacao": disp,
            "publicacao": publicacao,
            "inicio": inicio,
            "vencimento": vencimento,
            "dias": dias,
            "prazo_detectado": detectado is not None,
            "prazo_ambiguo": deteccao["ambiguo"],
            "prazo_candidatos": deteccao["candidatos"],
            "informativo": informativo,
            "audiencia_data": aud_data,
            "audiencia_dias": aud_dias,
            "restantes": restantes,
            "nivel": nivel,
            "rotulo": rotulo,
            "texto": texto,
            "link": it.get("link") or "",
            "advogados": [a for a in advs if a],
            "partes": [p for p in partes if p],
            "destinatarios_raw": it.get("destinatarios") or [],
            "numero_limpo": num_digitos,
            "cumprimento": None,
            "cumprimento_detalhe": "",
            "resolvido": resolvidos.get((num_digitos, disp.isoformat())),
        })

    linhas = agrupar(linhas)
    linhas.sort(key=prioridade)
    return linhas


def cruzar_com_datajud(linhas: list[dict]) -> None:
    """
    Pergunta ao CNJ se cada prazo foi cumprido, e escreve o resultado nas linhas.

    So consulta o que muda decisao: prazo vivo, ou vencido com sancao grave.
    O DataJud tem rate limit agressivo e a lista pode ser longa - varrer tudo
    so gastaria 429. O que e da parte contraria tambem fica de fora.
    """
    alvos = [l for l in linhas
             if not l["resolvido"]
             and l["de_quem"] != classificador.DA_OUTRA_PARTE
             and not l["informativo"]
             and (l["nivel"] > 0 or l["gravidade"] >= 3)]
    if not alvos:
        return

    # um processo pode ter varias intimacoes: consulta uma vez, aproveita em todas
    por_processo: dict[tuple[str, str], list[dict]] = {}
    for l in alvos:
        num = re.sub(r"\D", "", l["numero_limpo"] or l["processo"])
        if num:
            por_processo.setdefault((num, l["tribunal"]), []).append(l)

    print(f"\n  Cruzando {len(por_processo)} processo(s) com o andamento no CNJ"
          f" (DataJud)...")
    for i, ((num, trib), grupo) in enumerate(por_processo.items(), 1):
        print(f"    {i}/{len(por_processo)}: {grupo[0]['processo']} ({trib})")
        try:
            proc = datajud.consultar(num, trib)
        except Exception as ex:
            print(f"      [erro] {type(ex).__name__}: {ex}")
            continue
        for l in grupo:
            sit, det = datajud.conferir_cumprimento(proc, l["publicacao"],
                                                    l["vencimento"])
            l["cumprimento"], l["cumprimento_detalhe"] = sit, det
            if sit == datajud.DECURSO_REGISTRADO:
                print(f"      >> DECURSO DE PRAZO: {det}")


def tem_audiencia_futura(l: dict) -> bool:
    """Audiencia marcada e ainda nao realizada (hoje conta: a hora pode nao ter
    chegado). Passada, ja nao ha o que avisar - o termo virá depois."""
    ad = l.get("audiencia_dias")
    return ad is not None and ad >= 0


def prioridade(l: dict) -> tuple:
    """
    Ordem de leitura do relatorio. Menor = mais acima.

    A regra que nao pode ser quebrada: prazo VENCIDO com sancao grave sobe ao
    topo, junto dos criticos. Foi o erro que deixou passar uma desercao - o
    relatorio presumia que prazo vencido e assunto encerrado. Nao e: enquanto
    nao houver julgamento, ainda pode haver o que fazer.

    A unica coisa que rebaixa um vencido grave e o advogado dizer, no
    resolvidos.txt, que ja tratou. So ele sabe disso - nem o DJEN nem o CNJ
    contam.
    """
    if l["resolvido"]:
        return (10, l["vencimento"])

    # Audiencia designada e COMPROMISSO, nao prazo: nao se cumpre antes, nao se
    # perde por decurso - ou voce esta la, ou o processo do autor e extinto
    # (art. 51, I, Lei 9.099/95). Por isso tem faixa propria e sobe sozinha
    # conforme a data chega, ANTES de qualquer regra que rebaixe:
    #   - "de_quem" nao vale aqui: a intimacao convoca quem foi intimado, ainda
    #     que o mesmo ato mande a outra parte fazer algo;
    #   - "informativo" tambem nao: nao abre prazo, mas nao e dispensavel.
    # BUG-05 (15/07/2026): a audiencia do EDIO era no dia seguinte e o
    # relatorio a listava no rodape, como "Nao identificado" e prazo vencido.
    if tem_audiencia_futura(l):
        return (0, l["audiencia_data"])

    if l["de_quem"] == classificador.DA_OUTRA_PARTE:
        return (9, l["vencimento"])
    if l["informativo"]:
        return (8, l["vencimento"])
    if l["nivel"] == 0:
        if l["gravidade"] >= 3:
            return (0, l["vencimento"])      # vencido E grave: topo
        return (7, l["vencimento"])          # vencido comum: rodape
    # vivos: mais grave primeiro, depois mais proximo do vencimento
    return (1 + l["nivel"], -l["gravidade"], l["vencimento"])


def agrupar(linhas: list[dict]) -> list[dict]:
    """
    O DJEN emite uma comunicacao por destinatario do mesmo ato: o mesmo
    processo aparece 2, 3, 4 vezes na mesma data, com textos ligeiramente
    diferentes (cada um nomeia o seu destinatario). Juridicamente sao atos
    distintos, mas o PRAZO e um so. Aqui a gente junta o que gera o mesmo
    prazo, sem jogar nada fora: guarda a contagem, todos os links e o texto
    mais completo do grupo.
    """
    grupos: dict[tuple, dict] = {}
    for l in linhas:
        chave = (l["processo"], l["disponibilizacao"], l["tipo"], l["dias"])
        g = grupos.get(chave)
        if g is None:
            l["ocorrencias"] = 1
            l["links"] = [l["link"]] if l["link"] else []
            grupos[chave] = l
            continue
        g["ocorrencias"] += 1
        if l["link"] and l["link"] not in g["links"]:
            g["links"].append(l["link"])
        if len(l["texto"]) > len(g["texto"]):
            # o texto mais completo manda: reclassifica o grupo por ele.
            # Os campos de audiencia entram aqui junto com "ato": esquecer um
            # deles deixa o grupo dizendo "Intimacao para audiencia" com a data
            # do texto curto (ou sem data nenhuma) - rotulo certo, agenda errada.
            g["texto"] = l["texto"]
            for campo in ("ato", "ato_rotulo", "providencias", "providencias_rotulo",
                          "sancoes", "gravidade", "sancao_principal",
                          "audiencia_em", "audiencia_data", "audiencia_dias",
                          "rotulo"):
                g[campo] = l[campo]
        for nome in l["partes"]:
            if nome not in g["partes"]:
                g["partes"].append(nome)
        # juntar as partes das varias comunicacoes pode revelar o polo que
        # faltava - vale reavaliar de quem e o prazo com o quadro completo
        vistos = {(d.get("nome"), d.get("polo")) for d in g["destinatarios_raw"]}
        for d in l["destinatarios_raw"]:
            if (d.get("nome"), d.get("polo")) not in vistos:
                g["destinatarios_raw"].append(d)
        g["de_quem"], g["de_quem_motivo"] = classificador.de_quem_e_o_prazo(
            g["texto"], g["destinatarios_raw"])
    return list(grupos.values())


# --------------------------------------------------------------------------
# Saida: console
# --------------------------------------------------------------------------

def imprimir_console(linhas: list[dict], hoje: date, oab: str, uf: str,
                     ini: date, fim: date,
                     falhas: list[tuple[date, date]] | None = None) -> None:
    br = lambda d: d.strftime("%d/%m/%Y")
    falhas = falhas or []
    print()
    print("=" * 78)
    print(f"  MONITOR DE PRAZOS - DJEN   |   OAB {oab}/{uf.upper()}")
    print(f"  Janela consultada: {br(ini)} a {br(fim)}   |   Hoje: {br(hoje)}")
    print("=" * 78)

    if falhas:
        print()
        print("  " + "!" * 74)
        print("  !!  RELATORIO INCOMPLETO")
        print("  !!")
        print("  !!  O DJEN nao respondeu para o(s) periodo(s) abaixo. Pode haver")
        print("  !!  intimacao sua nessas datas que NAO esta neste relatorio:")
        for a, b in falhas:
            print(f"  !!      {br(a)} a {br(b)}")
        print("  !!")
        print("  !!  Rode de novo daqui a pouco (costuma ser instabilidade passageira)")
        print("  !!  ou confira esse periodo direto no sistema do tribunal.")
        print("  " + "!" * 74)

    if not linhas:
        if falhas:
            print("\n  Nenhuma comunicacao nos periodos que responderam"
                  " - mas veja o aviso acima.\n")
        else:
            print("\n  Nenhuma comunicacao encontrada nesta janela.\n")
        return

    resolvidos_l = [l for l in linhas if l["resolvido"]]
    abertos = [l for l in linhas if not l["resolvido"]]
    # A audiencia sai da fila ANTES de tudo: nao e prazo (nao entra em vivos/
    # vencidos) e nao e informativa (nao pode ir para a lista silenciosa). Era
    # exatamente esse o buraco do BUG-05 - a convocacao do EDIO nao tinha
    # secao onde caber e foi parar no rodape, na vespera do ato.
    audiencias = [l for l in abertos if tem_audiencia_futura(l)]
    demais = [l for l in abertos if not tem_audiencia_futura(l)]
    outra_parte = [l for l in demais if l["de_quem"] == classificador.DA_OUTRA_PARTE]
    restantes_l = [l for l in demais if l["de_quem"] != classificador.DA_OUTRA_PARTE]
    informativos = [l for l in restantes_l if l["informativo"]]
    acionaveis = [l for l in restantes_l if not l["informativo"]]
    graves = [l for l in acionaveis if l["nivel"] == 0 and l["gravidade"] >= 3]
    vivos = [l for l in acionaveis if l["nivel"] > 0]
    vencidos = [l for l in acionaveis if l["nivel"] == 0 and l["gravidade"] < 3]

    resumo: dict[str, int] = {}
    for l in vivos:
        resumo[l["rotulo"]] = resumo.get(l["rotulo"], 0) + 1
    print("\n  EM ABERTO: " + ("   ".join(f"{k}: {v}" for k, v in resumo.items())
                               if resumo else "nenhum prazo correndo"))
    if audiencias:
        prox = min(l["audiencia_dias"] for l in audiencias)
        quando = ("HOJE" if prox == 0 else "AMANHA" if prox == 1
                  else f"em {prox} dias")
        print(f"  ** {len(audiencias)} AUDIENCIA(S) MARCADA(S) - a proxima e "
              f"{quando} - veja no topo **")
    if graves:
        print(f"  ** {len(graves)} VENCIDO(S) COM SANCAO GRAVE - veja no topo **")
    if vencidos:
        print(f"  (+ {len(vencidos)} vencido(s) sem sancao grave - listados no fim)")
    if outra_parte:
        print(f"  (+ {len(outra_parte)} prazo(s) da PARTE CONTRARIA - nao sao seus)")
    if informativos:
        print(f"  (+ {len(informativos)} informativa(s), sem prazo aparente)")
    if resolvidos_l:
        print(f"  (+ {len(resolvidos_l)} marcado(s) por voce como resolvido(s))")

    def detalhar(l, marca):
        print("\n" + "-" * 78)
        print(f"{marca} [{l['rotulo']}]  {l['processo']}  ({l['tribunal']})")
        print(f"    {l['ato_rotulo']} - {l['classe']}")
        if l["providencias_rotulo"]:
            print(f"    O QUE PEDE    : {', '.join(l['providencias_rotulo'])}")
        if l["sancao_principal"]:
            print(f"    SOB PENA DE   : {l['sancao_principal'].upper()}")
        print(f"    De quem e     : {l['de_quem']} ({l['de_quem_motivo']})")
        print(f"    Orgao         : {l['orgao']}")
        print(f"    Disponibilizado {br(l['disponibilizacao'])}"
              f"  ->  Publicado {br(l['publicacao'])}"
              f"  ->  Inicio {br(l['inicio'])}")
        origem = "detectado no texto" if l["prazo_detectado"] else "padrao assumido"
        print(f"    VENCIMENTO    : {br(l['vencimento'])}"
              f"   ({l['dias']} dias uteis, {origem})")
        if l.get("prazo_ambiguo"):
            outros = ", ".join(f"{n}" for n in l["prazo_candidatos"])
            print(f"    !! PRAZO AMBIGUO: o texto traz {outros} dias. Assumi o "
                  f"MENOR ({l['dias']}). CONFIRA NOS AUTOS qual e o seu.")
        if l["nivel"] == 0:
            print(f"    Situacao      : VENCIDO ha {abs(l['restantes'])} dia(s) util(eis)")
        elif l["nivel"] == 1:
            print(f"    Situacao      : VENCE HOJE")
        else:
            print(f"    Situacao      : faltam {l['restantes']} dia(s) util(eis)")
        if l["cumprimento"]:
            print(f"    ANDAMENTO CNJ : {datajud.ROTULO_CUMPRIMENTO[l['cumprimento']]}"
                  f" - {l['cumprimento_detalhe']}")
        if l["ocorrencias"] > 1:
            print(f"    Obs           : {l['ocorrencias']} comunicacoes deste ato "
                  f"(uma por destinatario) - mesmo prazo")
        trecho = l["texto"][:220].replace("\n", " ")
        if trecho:
            print(f"    Trecho        : {trecho}{'...' if len(l['texto']) > 220 else ''}")
        for i, link in enumerate(l["links"]):
            print(f"    {'Autos         :' if i == 0 else '                '} {link}")

    if audiencias:
        print("\n" + "!" * 78)
        print("  AUDIENCIAS MARCADAS - compromisso com dia e hora, nao prazo.")
        print("  Nao se cumpre antes nem se compensa depois: ou voce esta la,")
        print("  ou o processo do seu cliente autor e extinto (art. 51, I, da")
        print("  Lei 9.099/95 no JEC; no rito comum, arquiva ou segue a revelia).")
        print("!" * 78)
        for l in audiencias:
            quando = l["audiencia_data"]
            hora = l["audiencia_em"].strftime("%H:%M") if l.get("audiencia_em") else ""
            marca = "!!!" if l["audiencia_dias"] <= 2 else "   "
            print("\n" + "-" * 78)
            print(f"{marca} [{l['rotulo']}]  {l['processo']}  ({l['tribunal']})")
            print(f"    {l['ato_rotulo']} - {l['classe']}")
            print(f"    QUANDO        : {br(quando)}"
                  f"{' as ' + hora if hora and hora != '00:00' else ' (hora nao informada no texto)'}"
                  f"   -> faltam {l['audiencia_dias']} dia(s) corrido(s)")
            print(f"    Orgao         : {l['orgao']}")
            if l["partes"]:
                print(f"    Partes        : {', '.join(l['partes'][:3])}")
            print(f"    Disponibilizado {br(l['disponibilizacao'])}")
            trecho = l["texto"][:220].replace("\n", " ")
            if trecho:
                print(f"    Trecho        : {trecho}"
                      f"{'...' if len(l['texto']) > 220 else ''}")
            for i, link in enumerate(l["links"]):
                print(f"    {'Autos         :' if i == 0 else '                '} {link}")

    if graves:
        print("\n" + "!" * 78)
        print("  VENCIDOS COM SANCAO GRAVE - o prazo passou, mas a consequencia")
        print("  ainda pode estar em curso. Confira se ha o que fazer.")
        print("!" * 78)
        for l in graves:
            detalhar(l, "!!!")

    for l in vivos:
        detalhar(l, "!!!" if l["nivel"] <= 2 or l["gravidade"] >= 3 else "   ")

    if vencidos:
        print("\n" + "-" * 78)
        print("  JA VENCIDOS, sem sancao grave no texto (conferencia):")
        for l in vencidos:
            cump = ""
            if l["cumprimento"] == datajud.DECURSO_REGISTRADO:
                cump = "  << DECURSO DE PRAZO no CNJ"
            print(f"    . venceu {br(l['vencimento'])}  {l['processo']} "
                  f"({l['tribunal']})  {l['ato_rotulo']}{cump}")

    if outra_parte:
        print("\n" + "-" * 78)
        print("  PRAZOS DA PARTE CONTRARIA (voce aparece por ser advogado nos autos):")
        for l in outra_parte:
            print(f"    . {br(l['disponibilizacao'])}  {l['processo']} "
                  f"({l['tribunal']})  {l['ato_rotulo']}")
            print(f"        {l['de_quem_motivo']}")

    if informativos:
        print("\n" + "-" * 78)
        print("  INFORMATIVAS (conferir se abrem prazo):")
        for l in informativos:
            print(f"    . {br(l['disponibilizacao'])}  {l['processo']}  {l['tipo']}")

    if resolvidos_l:
        print("\n" + "-" * 78)
        print("  MARCADOS POR VOCE COMO RESOLVIDOS (resolvidos.txt):")
        for l in resolvidos_l:
            print(f"    . {br(l['disponibilizacao'])}  {l['processo']} "
                  f"({l['tribunal']})  {l['ato_rotulo']}")
            print(f"        \"{l['resolvido']}\"")

    print("\n" + "=" * 78)
    print("  ATENCAO: datas ESTIMADAS. Confira no sistema do tribunal antes de agir.")
    print("  Feriados locais e suspensoes por portaria nao entram automaticamente.")
    print("=" * 78 + "\n")


# --------------------------------------------------------------------------
# Saida: HTML
# --------------------------------------------------------------------------

CORES = {
    0: ("#5c1a2b", "#e06a6a"),   # vencido
    1: ("#7d2637", "#e06a6a"),   # vence hoje
    2: ("#8d5b1d", "#e2b256"),   # critico
    3: ("#0c1e33", "#e2b256"),   # atencao
    4: ("#0c1e33", "#a6b2be"),   # no prazo
}


def gerar_html(linhas: list[dict], hoje: date, oab: str, uf: str,
               ini: date, fim: date,
               falhas: list[tuple[date, date]] | None = None) -> str:
    br = lambda d: d.strftime("%d/%m/%Y")
    e = html_mod.escape
    falhas = falhas or []

    resolvidos_l = [l for l in linhas if l["resolvido"]]
    abertos = [l for l in linhas if not l["resolvido"]]
    # mesma regra do console: a audiencia sai da fila antes de "de_quem" e de
    # "informativo" (BUG-05)
    audiencias = [l for l in abertos if tem_audiencia_futura(l)]
    demais = [l for l in abertos if not tem_audiencia_futura(l)]
    outra_parte = [l for l in demais if l["de_quem"] == classificador.DA_OUTRA_PARTE]
    meus = [l for l in demais if l["de_quem"] != classificador.DA_OUTRA_PARTE]
    informativos = [l for l in meus if l["informativo"]]
    acionaveis = [l for l in meus if not l["informativo"]]
    graves = [l for l in acionaveis if l["nivel"] == 0 and l["gravidade"] >= 3]
    vivos = [l for l in acionaveis if l["nivel"] > 0]
    vencidos = [l for l in acionaveis if l["nivel"] == 0 and l["gravidade"] < 3]

    alerta = ""
    if falhas:
        periodos = "".join(f"<li>{br(a)} a {br(b)}</li>" for a, b in falhas)
        alerta = f"""
      <section class="alerta">
        <h2>Este relatório está incompleto</h2>
        <p>O DJEN não respondeu para o(s) período(s) abaixo. <strong>Pode haver
        intimação sua nessas datas que não aparece aqui.</strong></p>
        <ul>{periodos}</ul>
        <p>Costuma ser instabilidade passageira: rode de novo daqui a pouco. Se
        insistir, confira esse período direto no sistema do tribunal.</p>
      </section>"""

    def montar_card(l):
        fundo, borda = CORES[l["nivel"]]
        if l["nivel"] == 0:
            sit = f"vencido há {abs(l['restantes'])} dia(s) útil(eis)"
        elif l["nivel"] == 1:
            sit = "vence hoje"
        else:
            sit = f"faltam {l['restantes']} dia(s) útil(eis)"
        origem = "detectado no texto" if l["prazo_detectado"] else "padrão assumido"
        if len(l["links"]) == 1:
            link = (f'<a class="autos" href="{e(l["links"][0])}" target="_blank" '
                    f'rel="noopener">abrir os autos &rarr;</a>')
        else:
            link = "".join(
                f'<a class="autos" href="{e(u)}" target="_blank" rel="noopener">'
                f'abrir os autos ({i}) &rarr;</a>'
                for i, u in enumerate(l["links"], 1))
        multi = (f'<p class="multi">{l["ocorrencias"]} comunicações deste mesmo ato '
                 f'(uma por destinatário) &mdash; o prazo é o mesmo</p>'
                 if l["ocorrencias"] > 1 else "")
        pena = (f'<p class="pena">sob pena de <b>{e(l["sancao_principal"])}</b></p>'
                if l["sancao_principal"] else "")
        pede = ""
        if l["providencias_rotulo"]:
            pede = (f'<div class="pede"><span class="pede-label">O que pede</span>'
                    f'<strong>{e(", ".join(l["providencias_rotulo"]))}</strong></div>')
        dono = ""
        if l["de_quem"] == classificador.INCERTO:
            dono = (f'<p class="incerto">Não deu para confirmar se o prazo é seu: '
                    f'{e(l["de_quem_motivo"])}. <b>Confira nos autos.</b></p>')
        ambiguo = ""
        if l.get("prazo_ambiguo"):
            outros = ", ".join(str(n) for n in l["prazo_candidatos"])
            ambiguo = (f'<p class="incerto"><b>Prazo ambíguo:</b> o texto traz '
                       f'{outros} dias. Assumi o <b>menor ({l["dias"]})</b> — '
                       f'errar para menos antecipa a data; errar para mais perde '
                       f'o prazo. <b>Confira nos autos qual é o seu.</b></p>')
        cnj = ""
        if l["cumprimento"]:
            classe_cnj = ("cnj-alerta" if l["cumprimento"] == datajud.DECURSO_REGISTRADO
                          else "cnj")
            cnj = (f'<div class="{classe_cnj}"><span class="pede-label">Andamento no CNJ'
                   f'</span><strong>{e(datajud.ROTULO_CUMPRIMENTO[l["cumprimento"]])}'
                   f'</strong><em>{e(l["cumprimento_detalhe"])}</em></div>')
        return f"""
      <article class="card" style="--fundo:{fundo};--borda:{borda}">
        <header>
          <span class="tag">{e(l['rotulo'])}</span>
          <h2>{e(l['processo'])}</h2>
          <p class="sub">{e(l['ato_rotulo'])} &middot; {e(l['tribunal'])}
             &middot; {e(l['classe'])}</p>
          {multi}
        </header>
        {pede}
        {pena}
        <div class="venc">
          <span class="venc-label">Vencimento estimado</span>
          <strong>{br(l['vencimento'])}</strong>
          <span class="venc-sit">{e(sit)}</span>
        </div>
        {cnj}
        {dono}
        {ambiguo}
        <dl>
          <div><dt>Órgão</dt><dd>{e(l['orgao'])}</dd></div>
          <div><dt>Disponibilizado</dt><dd>{br(l['disponibilizacao'])}</dd></div>
          <div><dt>Publicado</dt><dd>{br(l['publicacao'])}</dd></div>
          <div><dt>Início da contagem</dt><dd>{br(l['inicio'])}</dd></div>
          <div><dt>Prazo</dt><dd>{l['dias']} dias úteis <em>({e(origem)})</em></dd></div>
        </dl>
        <details><summary>Ver a intimação na íntegra</summary>
          <pre>{e(l['texto'])}</pre></details>
        {link}
      </article>"""

    def montar_card_audiencia(l):
        # card proprio: o de prazo mostraria "vencimento estimado" e "vencido ha
        # N dias" para uma audiencia que ainda vai acontecer.
        d = l["audiencia_dias"]
        fundo, borda = (CORES[0] if d <= 2 else CORES[2] if d <= 7 else CORES[3])
        hora = l["audiencia_em"].strftime("%H:%M") if l.get("audiencia_em") else ""
        quando = (f"{br(l['audiencia_data'])}"
                  + (f" às {hora}" if hora and hora != "00:00" else ""))
        falta = ("é hoje" if d == 0 else "é amanhã" if d == 1
                 else f"faltam {d} dias corridos")
        sem_hora = ("" if hora and hora != "00:00" else
                    '<p class="ambiguo">O texto não trouxe o horário &mdash; '
                    'confira nos autos antes de se programar.</p>')
        link = "".join(
            f'<a class="autos" href="{e(u)}" target="_blank" rel="noopener">'
            f'abrir os autos &rarr;</a>' for u in l["links"])
        partes = (f'<div><dt>Partes</dt><dd>{e(", ".join(l["partes"][:3]))}</dd></div>'
                  if l["partes"] else "")
        return f"""
      <article class="card" style="--fundo:{fundo};--borda:{borda}">
        <header>
          <span class="tag">{e(l['rotulo'])}</span>
          <h2>{e(l['processo'])}</h2>
          <p class="sub">{e(l['ato_rotulo'])} &middot; {e(l['tribunal'])}
             &middot; {e(l['classe'])}</p>
        </header>
        <div class="venc">
          <span class="venc-label">Audiência</span>
          <strong>{quando}</strong>
          <span class="venc-sit">{falta}</span>
        </div>
        {sem_hora}
        <dl>
          <div><dt>Órgão</dt><dd>{e(l['orgao'])}</dd></div>
          {partes}
          <div><dt>Disponibilizado</dt><dd>{br(l['disponibilizacao'])}</dd></div>
        </dl>
        <details><summary>Ver a intimação na íntegra</summary>
          <pre>{e(l['texto'])}</pre></details>
        {link}
      </article>"""

    bloco_audiencias = ""
    if audiencias:
        bloco_audiencias = f"""
      <section class="graves">
        <h2>Audiências marcadas &mdash; dia e hora, não prazo</h2>
        <p>Audiência não se cumpre antes nem se compensa depois: <strong>ou você
        está lá, ou o processo do seu cliente autor é extinto</strong> (art. 51,
        I, da Lei 9.099/95, no JEC). Por isso fica no topo e sobe conforme a data
        chega &mdash; nenhum &ldquo;prazo&rdquo; avisa sobre isto.</p>
      </section>{''.join(montar_card_audiencia(l) for l in audiencias)}"""

    bloco_graves = ""
    if graves:
        bloco_graves = f"""
      <section class="graves">
        <h2>Venceu, mas ainda pode haver o que fazer</h2>
        <p>O prazo passou <strong>e o texto prevê sanção grave</strong>. Enquanto
        não houver julgamento, a consequência ainda pode estar em curso &mdash;
        por isso isto está no topo, e não enterrado na lista de vencidos.</p>
      </section>{''.join(montar_card(l) for l in graves)}"""

    cards = [montar_card(l) for l in vivos]

    bloco_venc = ""
    if vencidos:
        itens_venc = "".join(
            f"<li><strong>venceu {br(l['vencimento'])}</strong> &middot; "
            f"{e(l['processo'])} ({e(l['tribunal'])}) &middot; {e(l['ato_rotulo'])}"
            + ('<span class="flag-cnj">DECURSO DE PRAZO no CNJ</span>'
               if l["cumprimento"] == datajud.DECURSO_REGISTRADO else "")
            + "</li>"
            for l in vencidos
        )
        bloco_venc = f"""
      <section class="info">
        <h3>Já vencidos, sem sanção grave no texto &mdash; conferência</h3>
        <ul>{itens_venc}</ul>
      </section>"""

    bloco_resolvidos = ""
    if resolvidos_l:
        itens_res = "".join(
            f"<li><strong>{br(l['disponibilizacao'])}</strong> &middot; "
            f"{e(l['processo'])} ({e(l['tribunal'])}) &middot; {e(l['ato_rotulo'])}"
            f"<em>&ldquo;{e(l['resolvido'])}&rdquo;</em></li>"
            for l in resolvidos_l
        )
        bloco_resolvidos = f"""
      <section class="info outra">
        <h3>Marcados por você como resolvidos <code>resolvidos.txt</code></h3>
        <ul>{itens_res}</ul>
      </section>"""

    bloco_outra = ""
    if outra_parte:
        itens_outra = "".join(
            f"<li><strong>{br(l['disponibilizacao'])}</strong> &middot; "
            f"{e(l['processo'])} ({e(l['tribunal'])}) &middot; {e(l['ato_rotulo'])}"
            f"<em>{e(l['de_quem_motivo'])}</em></li>"
            for l in outra_parte
        )
        bloco_outra = f"""
      <section class="info outra">
        <h3>Prazos da parte contrária &mdash; você aparece por ser advogado nos autos</h3>
        <ul>{itens_outra}</ul>
      </section>"""

    bloco_info = ""
    if informativos:
        itens_info = "".join(
            f"<li><strong>{br(l['disponibilizacao'])}</strong> &middot; "
            f"{e(l['processo'])} &middot; {e(l['tipo'])}</li>"
            for l in informativos
        )
        bloco_info = f"""
      <section class="info">
        <h3>Informativas &mdash; conferir se abrem prazo</h3>
        <ul>{itens_info}</ul>
      </section>"""

    resumo: dict[str, int] = {}
    for l in vivos:
        resumo[l["rotulo"]] = resumo.get(l["rotulo"], 0) + 1
    chips = "".join(f'<span class="chip">{e(k)}: <b>{v}</b></span>'
                    for k, v in resumo.items())
    # a audiencia tem chip proprio, e vem primeiro: sem isto o cabecalho dizia
    # "nenhum prazo correndo" no dia anterior a uma audiencia (BUG-05) - e,
    # tecnicamente, estava certo. Prazo nao era o que faltava.
    if audiencias:
        prox = min(l["audiencia_dias"] for l in audiencias)
        quando = ("HOJE" if prox == 0 else "AMANHÃ" if prox == 1
                  else f"em {prox} dias")
        chips = (f'<span class="chip chip-aud">AUDIÊNCIA {quando}'
                 + (f' (+{len(audiencias) - 1})' if len(audiencias) > 1 else "")
                 + '</span>') + chips
    if not chips:
        chips = '<span class="chip">nenhum prazo correndo</span>'

    corpo = "".join(cards) or '<p class="vazio">Nenhum prazo em aberto nesta janela.</p>'

    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prazos DJEN &middot; OAB {e(oab)}/{e(uf.upper())}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#071120;color:#f5f1e8;
       font-family:'Segoe UI',system-ui,-apple-system,sans-serif;
       line-height:1.6;padding:32px 20px 64px}}
  .wrap{{max-width:920px;margin:0 auto}}
  .topo{{border-bottom:2px solid #c8922e;padding-bottom:20px;margin-bottom:28px}}
  .topo h1{{font-size:1.5rem;font-weight:600;letter-spacing:.06em;
           text-transform:uppercase;color:#f6e2ad}}
  .topo p{{color:#a6b2be;font-size:.9rem;margin-top:6px}}
  .chips{{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}}
  .chip{{background:#0c1e33;border:1px solid #102743;border-radius:99px;
        padding:5px 14px;font-size:.78rem;color:#a6b2be;letter-spacing:.04em}}
  .chip b{{color:#e2b256}}
  .chip-aud{{background:#e06a6a;border-color:#e06a6a;color:#071120;font-weight:700}}
  .card{{background:var(--fundo);border-left:4px solid var(--borda);
        border-radius:8px;padding:22px;margin-bottom:18px}}
  .tag{{display:inline-block;background:var(--borda);color:#071120;
       font-size:.68rem;font-weight:700;letter-spacing:.1em;
       padding:3px 10px;border-radius:4px;margin-bottom:10px}}
  .card h2{{font-size:1.12rem;font-weight:600;color:#f5f1e8;
          font-variant-numeric:tabular-nums}}
  .sub{{color:#a6b2be;font-size:.82rem;margin-top:2px}}
  .multi{{margin-top:8px;font-size:.74rem;color:#e2b256;
         background:rgba(226,178,86,.1);border-radius:4px;padding:4px 9px;
         display:inline-block}}
  .venc{{background:rgba(7,17,32,.5);border-radius:6px;padding:14px 16px;
        margin:16px 0;display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}}
  .venc-label{{font-size:.7rem;letter-spacing:.1em;text-transform:uppercase;
             color:#6c7a88}}
  .venc strong{{font-size:1.45rem;color:#f6e2ad;font-variant-numeric:tabular-nums}}
  .venc-sit{{font-size:.82rem;color:var(--borda);font-weight:600}}
  dl{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}}
  dt{{font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:#6c7a88}}
  dd{{font-size:.88rem;color:#dfe6ee}}
  dd em{{color:#6c7a88;font-style:normal;font-size:.78rem}}
  details{{margin-top:16px;border-top:1px solid rgba(166,178,190,.15);padding-top:12px}}
  summary{{cursor:pointer;font-size:.8rem;color:#e2b256;letter-spacing:.03em}}
  pre{{white-space:pre-wrap;word-wrap:break-word;font-size:.78rem;color:#a6b2be;
      background:rgba(7,17,32,.6);padding:14px;border-radius:6px;margin-top:10px;
      font-family:ui-monospace,Consolas,monospace;max-height:340px;overflow:auto}}
  .autos{{display:inline-block;margin-top:14px;margin-right:16px;color:#e2b256;
         font-size:.82rem;text-decoration:none;
         border-bottom:1px solid rgba(226,178,86,.4)}}
  .autos:hover{{color:#f6e2ad}}
  .info{{background:#0c1e33;border-radius:8px;padding:20px;margin-top:26px}}
  .info h3{{font-size:.78rem;letter-spacing:.1em;text-transform:uppercase;
          color:#6c7a88;margin-bottom:10px}}
  .info ul{{list-style:none;font-size:.84rem;color:#a6b2be}}
  .info li{{padding:5px 0;border-bottom:1px solid rgba(166,178,190,.08)}}
  .info b,.info strong{{color:#dfe6ee;font-weight:600}}
  .vazio{{color:#6c7a88;text-align:center;padding:50px}}
  .alerta{{background:#5c1a2b;border:2px solid #e06a6a;border-radius:8px;
          padding:22px;margin-bottom:24px}}
  .alerta h2{{color:#e06a6a;font-size:1rem;letter-spacing:.06em;
             text-transform:uppercase;margin-bottom:10px}}
  .alerta p{{color:#e0928f;font-size:.86rem;margin-bottom:8px}}
  .alerta strong{{color:#f5f1e8}}
  .alerta ul{{list-style:none;margin:10px 0;font-variant-numeric:tabular-nums}}
  .alerta li{{color:#f5f1e8;font-size:.9rem;font-weight:600;padding:3px 0 3px 14px;
             border-left:3px solid #e06a6a;margin-bottom:4px}}
  .graves{{background:rgba(224,106,106,.1);border:1px solid #e06a6a;
          border-radius:8px;padding:18px 20px;margin-bottom:14px}}
  .graves h2{{color:#e06a6a;font-size:.9rem;letter-spacing:.08em;
             text-transform:uppercase;margin-bottom:8px}}
  .graves p{{color:#e0928f;font-size:.84rem}}
  .graves strong{{color:#f5f1e8}}
  .pede{{margin:14px 0 0;padding:12px 14px;background:rgba(7,17,32,.35);
        border-radius:6px}}
  .pede-label{{display:block;font-size:.66rem;letter-spacing:.1em;
             text-transform:uppercase;color:#6c7a88;margin-bottom:3px}}
  .pede strong{{color:#f5f1e8;font-size:.95rem}}
  .pena{{margin-top:8px;font-size:.82rem;color:#e06a6a;letter-spacing:.04em}}
  .pena b{{text-transform:uppercase;letter-spacing:.08em}}
  .cnj,.cnj-alerta{{margin:12px 0;padding:12px 14px;border-radius:6px;
                   background:rgba(7,17,32,.35)}}
  .cnj-alerta{{background:rgba(224,106,106,.14);border:1px solid #e06a6a}}
  .cnj strong,.cnj-alerta strong{{display:block;font-size:.88rem;color:#f5f1e8}}
  .cnj-alerta strong{{color:#e06a6a}}
  .cnj em,.cnj-alerta em{{font-style:normal;font-size:.78rem;color:#a6b2be}}
  .incerto{{margin:10px 0;font-size:.8rem;color:#e2b256;
           background:rgba(226,178,86,.08);border-radius:5px;padding:8px 12px}}
  .incerto b{{color:#f6e2ad}}
  .flag-cnj{{display:inline-block;margin-left:8px;background:#5c1a2b;
            color:#e06a6a;font-size:.66rem;font-weight:700;letter-spacing:.06em;
            padding:2px 8px;border-radius:4px}}
  .outra li em{{display:block;font-style:normal;font-size:.76rem;color:#6c7a88;
               margin-top:2px}}
  .rodape{{margin-top:34px;padding:18px;border:1px solid #5c1a2b;border-radius:8px;
         background:rgba(92,26,43,.18);color:#e0928f;font-size:.8rem}}
  .rodape b{{color:#e06a6a}}
  @media print{{body{{background:#fff;color:#000}}.card{{border:1px solid #ccc}}}}
</style></head><body><div class="wrap">
  <header class="topo">
    <h1>Monitor de Prazos &middot; DJEN</h1>
    <p>OAB {e(oab)}/{e(uf.upper())} &nbsp;&middot;&nbsp;
       janela de {br(ini)} a {br(fim)} &nbsp;&middot;&nbsp;
       gerado em {hoje.strftime('%d/%m/%Y')}</p>
    <div class="chips">{chips}</div>
  </header>
  {alerta}
  {bloco_audiencias}
  {bloco_graves}
  {corpo}
  {bloco_venc}
  {bloco_outra}
  {bloco_info}
  {bloco_resolvidos}
  <p class="rodape"><b>Confira antes de agir.</b> As datas sao estimadas a partir
  da data de disponibilizacao no DJEN, aplicando os arts. 219 e 224 do CPC com
  feriados nacionais e o recesso de 20/12 a 20/01. Feriados locais, suspensoes de
  expediente por portaria e prazos em dobro ou proprios de cada rito
  <b>nao</b> entram nesta conta. Quando o prazo nao vem escrito na intimacao, o
  relatorio assume o padrao configurado. Este relatorio organiza, nao substitui a
  conferencia nos autos.</p>
</div></body></html>"""


# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

MODELO_FERIADOS = """# Feriados locais e suspensoes de expediente
#
# Formato:  YYYY-MM-DD  [ESCOPO]  Descricao
#
# ESCOPO e a sigla do tribunal como vem do DJEN (TJPA, TJMA, TRT8, TRF1...)
# ou * para valer em todos. Se voce omitir, vale para todos.
#
#   2026-07-28  TJMA  Adesao do Maranhao      -> so nos processos do TJMA
#   2026-08-15  TJPA  Adesao do Para          -> so nos processos do TJPA
#   2026-03-02  *     Suspensao geral         -> em todos
#
# Por que o escopo existe: feriado estadual nao e nacional. 28/07 e feriado no
# Maranhao e dia util no Para. Sem escopo, um feriado do MA empurraria errado
# os prazos dos seus processos paraenses.
#
# Os feriados NACIONAIS ja estao no script (incluindo Carnaval, Sexta-feira
# Santa e Corpus Christi, calculados pela Pascoa de cada ano) e o recesso de
# 20/12 a 20/01. Nao precisa cadastrar.
#
# ATENCAO A DIRECAO DO ERRO: um feriado a MAIS aqui empurra o vencimento para
# frente e te da a impressao de ter MAIS tempo do que voce tem. Um feriado a
# MENOS antecipa a data, o que e chato mas seguro. So cadastre o que voce
# confirmou no calendario oficial do tribunal.
"""


def carregar_config(args) -> dict:
    cfg = {"oab": "", "uf": "", "prazo_padrao": PRAZO_PADRAO, "janela_dias": "auto"}
    if ARQ_CONFIG.exists():
        try:
            cfg.update(json.loads(ARQ_CONFIG.read_text(encoding="utf-8")))
        except json.JSONDecodeError as ex:
            raise SystemExit(f"config.json invalido: {ex}")

    if args.oab:
        cfg["oab"] = args.oab
    if args.uf:
        cfg["uf"] = args.uf
    if args.prazo:
        cfg["prazo_padrao"] = args.prazo
    if args.dias:
        cfg["janela_dias"] = args.dias

    cfg["oab"] = re.sub(r"\D", "", str(cfg.get("oab") or ""))
    cfg["uf"] = str(cfg.get("uf") or "").strip().upper()

    if not cfg["oab"] or not cfg["uf"]:
        raise SystemExit(
            "\nFalta a OAB. Preencha o config.json:\n"
            f"  {ARQ_CONFIG}\n"
            '  {"oab": "12345", "uf": "PA", "prazo_padrao": 15, "janela_dias": 15}\n'
            "\nOu passe na linha de comando:\n"
            "  python monitor_prazos.py --oab 12345 --uf PA\n"
        )
    return cfg


def garantir_arquivos(cfg: dict) -> None:
    if not ARQ_CONFIG.exists():
        ARQ_CONFIG.write_text(
            json.dumps({k: cfg[k] for k in ("oab", "uf", "prazo_padrao", "janela_dias")},
                       indent=2, ensure_ascii=False),
            encoding="utf-8")
        print(f"  [criado] {ARQ_CONFIG.name}")
    if not ARQ_FERIADOS.exists():
        ARQ_FERIADOS.write_text(MODELO_FERIADOS, encoding="utf-8")
        print(f"  [criado] {ARQ_FERIADOS.name}")


# --------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Consulta o DJEN por OAB e monta o relatorio de prazos.")
    ap.add_argument("--oab", help="numero da OAB (so digitos)")
    ap.add_argument("--uf", help="UF da OAB, ex: PA")
    ap.add_argument("--dias", type=int,
                    help="janela de busca em dias corridos (padrao: calculada)")
    ap.add_argument("--prazo", type=int, help=f"prazo assumido quando nao vem no texto (padrao {PRAZO_PADRAO})")
    ap.add_argument("--datajud", action="store_true",
                    help="cruzar com o andamento do CNJ (mais lento; diz se o "
                         "prazo foi cumprido)")
    ap.add_argument("--sem-navegador", action="store_true", help="nao abrir o HTML ao final")
    args = ap.parse_args()

    cfg = carregar_config(args)
    garantir_arquivos(cfg)

    hoje = date.today()
    fim = hoje

    feriados_extra = ler_feriados_locais(ARQ_FERIADOS)
    cal = Calendario(feriados_extra)

    janela = cfg["janela_dias"]
    if str(janela).lower() == "auto":
        janela = janela_necessaria(hoje, cal)
        print(f"\n  Janela calculada: {janela} dias corridos para tras.")
        print(f"  (o bastante para nao perder um prazo de {PRAZO_REFERENCIA} dias"
              f" uteis ainda correndo)")
    janela = int(janela)
    ini = hoje - timedelta(days=janela)

    vigentes = [f for f in feriados_extra if f[0] >= ini]
    if vigentes:
        print(f"\n  Feriados locais em vigor ({ARQ_FERIADOS.name}) - confira se procedem:")
        for d, escopo, desc in sorted(vigentes):
            onde = "todos os tribunais" if escopo == "*" else escopo
            print(f"    {d.strftime('%d/%m/%Y')}  {onde:<20} {desc}")

    print(f"\n  Consultando o DJEN para a OAB {cfg['oab']}/{cfg['uf']}...")
    itens, falhas = consultar_djen(cfg["oab"], cfg["uf"], ini, fim)
    print(f"  {len(itens)} comunicacao(oes) recebida(s).")

    resolvidos = ler_resolvidos(ARQ_RESOLVIDOS)
    linhas = processar(itens, cal, int(cfg["prazo_padrao"]), hoje, resolvidos)

    if args.datajud:
        cruzar_com_datajud(linhas)

    imprimir_console(linhas, hoje, cfg["oab"], cfg["uf"], ini, fim, falhas)

    DIR_RELATORIOS.mkdir(exist_ok=True)
    destino = DIR_RELATORIOS / f"prazos_{hoje.isoformat()}.html"
    destino.write_text(
        gerar_html(linhas, hoje, cfg["oab"], cfg["uf"], ini, fim, falhas),
        encoding="utf-8")
    print(f"  Relatorio salvo em: {destino}\n")

    if not args.sem_navegador:
        webbrowser.open(destino.resolve().as_uri())

    # sai != 0 quando faltou periodo: quem agenda a tarefa consegue perceber
    if falhas:
        sys.exit(2)


if __name__ == "__main__":
    main()
