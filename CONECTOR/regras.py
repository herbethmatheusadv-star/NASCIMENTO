#!/usr/bin/env python3
"""
regras.py — as REGRAS DE FERRO do Conector PJe (SOJ, 15/07/2026).

Lido antes de qualquer coisa. Nada neste pacote toca o PJe sem passar por aqui.

  R7 NAO E UM `if`. R7 E AUSENCIA.

O codigo do CONECTOR nao contem — e nunca pode conter — funcao que assine,
peticione, tome ciencia ou responda expediente. Nao existe um bloqueio que
alguem possa remover num dia apressado: a capacidade simplesmente nao esta
escrita. `teste_regras.py` varre o fonte deste pacote inteiro e QUEBRA O BUILD
se qualquer uma dessas capacidades aparecer.

Por que tanto rigor (achado do spike de 15/07/2026): no MNI, a porta oficial de
leitura E a porta de escrita. O mesmo webservice que lista expedientes tem
`confirmarRecebimento` (dispara a ciencia e o prazo) e
`entregarManifestacaoProcessual` (protocola peca). Em codigo, um deles e UMA
LINHA — indistinguivel de uma consulta para quem le rapido. No painel e a mesma
coisa: o botao "Tomar ciencia" fica ao lado do link que abre o processo.

As tres camadas, em ordem de confianca:
  1. AUSENCIA no fonte  (nao da para chamar o que nao existe)
  2. GUARDA de clique/URL (o robo se recusa a tocar no que e perigoso)
  3. QUARENTENA          (processo com ciencia pendente nao e nem aberto)

Autoria da decisao: titular, 15/07/2026 (revogacao parcial e explicita —
ver _SISTEMA/emendas.md, Emenda 02).
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
LOG_QUARENTENA = RAIZ / "_SISTEMA" / "logs" / "quarentena.md"
LOG_WATCHDOG = RAIZ / "_SISTEMA" / "logs" / "watchdog.md"


def _sem_acento(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn").lower()


# ---------------------------------------------------------------------------
# CAMADA 1 — o que este pacote pode fazer (allowlist) e o que nao pode existir
# ---------------------------------------------------------------------------

# Unicas operacoes MNI chamaveis. Qualquer outra e ausencia proposital.
# `confirmarRecebimento` e `entregarManifestacaoProcessual` NAO estao aqui e
# nao podem ser adicionadas: sao, respectivamente, tomar ciencia e peticionar.
OPERACOES_MNI_PERMITIDAS = frozenset({
    "consultarAvisosPendentes",   # lista os expedientes — SEM abrir nenhum
    "consultarProcesso",          # dados e documentos do processo
    "consultarAlteracao",         # o que mudou desde uma data
})

# `consultarTeorComunicacao` fica FORA de proposito: ler o teor de um aviso
# pendente pode ser o proprio ato de ciencia (e o que o botao do painel faz).
# So entra se um dia for provado empiricamente que nao dispara ciencia — e a
# prova tem de ser feita pelo titular, num aviso JA ciente.
OPERACOES_MNI_EM_ESTUDO = frozenset({"consultarTeorComunicacao"})

# Vocabulario que NAO PODE APARECER no fonte do CONECTOR. O teste varre todos
# os .py do pacote (menos este arquivo e o teste, que precisam nomea-los para
# proibi-los) e falha se encontrar qualquer um.
VOCABULARIO_PROIBIDO = (
    # MNI — escrita
    r"confirmarRecebimento",
    r"entregarManifestacaoProcessual",
    # atos processuais
    r"\bassinar\b", r"\bassinatura_digital\b", r"\bpeticionar\b",
    r"\bprotocolar\b", r"\btomar_ciencia\b", r"\bdar_ciencia\b",
    r"\bresponder_expediente\b", r"\benviar_peticao\b", r"\bjuntar_peticao\b",
    # o certificado nunca e usado para assinar por este pacote
    r"\bsign\(", r"\bsign_pdf\b", r"\bpkcs11\b", r"\bpkcs12\b",
    # credencial em codigo — o titular digita, o robo nunca ve
    r"\bsenha\s*=\s*[\"']", r"\bpin\s*=\s*[\"']", r"\bpassword\s*=\s*[\"']",
    r"\bkeyring\b", r"\bCredentialManager\b",
    # persistencia de sessao — perfil e EFEMERO por decisao do titular
    r"user_data_dir", r"storage_state", r"\bsave_cookies\b",
    r"\bpersist(ent)?_context\b",
)

# Texto de elemento que o robo JAMAIS clica. Comparado sem acento, minusculo.
ACOES_PROIBIDAS_UI = (
    "tomar ciencia", "tomar conhecimento", "dar ciencia", "ciente",
    "responder", "resposta", "manifestar", "peticionar", "peticionamento",
    "protocolar", "protocolo", "assinar", "assinatura", "enviar",
    "anexar", "juntar", "excluir", "remover", "cancelar audiencia",
    "confirmar recebimento", "declarar ciencia", "registrar ciencia",
)

# URL que o robo jamais navega.
#
# Os quatro primeiros grupos vieram da SESSAO DE MAPEAMENTO REAL (16/07/2026):
# os padroes antigos ("peticion", "assinatur") foram CHUTADOS e NAO pegavam as
# URLs verdadeiras do TJPA — "peticaoavulsa" nao contem "peticion" (petiCAO !=
# petiCION), "consultaDocnaoAssinado" nao contem "assinatur". Regra da casa:
# padrao vem do dado real, nao da adivinhacao. Ver teste_regras.py §4 [REAL].
URLS_PROIBIDAS = (
    # escrita/peticao — reais do painel TJPA
    r"peticaoavulsa", r"cadastropeticao", r"peticion",
    # assinatura — real: consultaDocnaoAssinado.seam
    r"naoassinado", r"assinatur", r"assinado",
    # ajuizar / criar processo — cadastrar.seam ("Novo processo")
    r"cadastrar\.seam", r"processoincidente",
    # ciencia / resposta / protocolo — o robo nunca age
    r"protocol", r"expediente/responder", r"tomarciencia",
    r"confirmarrecebimento", r"manifestacao",
)


class ViolacaoR7(RuntimeError):
    """O robo tentou fazer algo que nao lhe cabe. Sempre fatal, nunca engolida."""


def guarda_de_clique(rotulo: str) -> None:
    """Chame ANTES de qualquer clique. Levanta ViolacaoR7 se o alvo for ato."""
    alvo = _sem_acento(rotulo)
    for proibido in ACOES_PROIBIDAS_UI:
        if proibido in alvo:
            raise ViolacaoR7(
                f"R7: recusado clicar em {rotulo!r} — casa com {proibido!r}. "
                f"O robo le; quem age e o advogado.")


def guarda_de_url(url: str) -> None:
    """Chame ANTES de qualquer navegacao."""
    alvo = _sem_acento(url)
    for padrao in URLS_PROIBIDAS:
        if re.search(padrao, alvo, re.IGNORECASE):
            raise ViolacaoR7(
                f"R7: recusada navegacao para {url!r} — casa com {padrao!r}.")


def guarda_de_operacao_mni(nome: str) -> None:
    """Chame ANTES de qualquer chamada SOAP."""
    if nome in OPERACOES_MNI_PERMITIDAS:
        return
    if nome in OPERACOES_MNI_EM_ESTUDO:
        raise ViolacaoR7(
            f"R7: {nome!r} esta EM ESTUDO — pode ser o proprio ato de ciencia. "
            f"So o titular libera, e so depois de provar num aviso ja ciente.")
    raise ViolacaoR7(
        f"R7: operacao {nome!r} fora da allowlist "
        f"{sorted(OPERACOES_MNI_PERMITIDAS)}.")


# ---------------------------------------------------------------------------
# CAMADA 3 — QUARENTENA
# ---------------------------------------------------------------------------

@dataclass
class Processo:
    """O minimo que o conector sabe de um processo antes de decidir toca-lo."""
    numero: str
    ciencia_pendente: bool
    origem: str = ""
    observacao: str = ""


@dataclass
class Quarentena:
    """
    Processo com ciencia pendente nao e lido — NEM OS AUTOS DELE.

    Por que os autos tambem (decisao do titular, 15/07/2026): no PJe a fronteira
    entre "abrir o processo" e "tomar ciencia do expediente" e um clique de
    distancia, e em alguns fluxos a propria abertura registra a ciencia. Prazo
    disparado por engano do robo e o dano exato que este sistema existe para
    evitar. Diante da duvida: nao toca, e chama o humano.
    """
    itens: list[Processo] = field(default_factory=list)

    def avaliar(self, p: Processo) -> bool:
        """True = quarentenado (nao tocar). Registra o motivo."""
        if p.ciencia_pendente:
            self.itens.append(p)
            return True
        return False

    def registrar(self) -> None:
        if not self.itens:
            return
        LOG_QUARENTENA.parent.mkdir(parents=True, exist_ok=True)
        novo = not LOG_QUARENTENA.exists()
        with LOG_QUARENTENA.open("a", encoding="utf-8") as f:
            if novo:
                f.write("# Quarentena — processos com ciencia pendente\n\n"
                        "> O robo NAO abre estes processos (nem os autos). Fila\n"
                        "> humana: o advogado toma ciencia no PJe, no momento em\n"
                        "> que decidir, e o processo volta ao fluxo normal.\n\n")
            f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M}\n\n")
            for p in self.itens:
                f.write(f"- **{p.numero}** — ciencia pendente ({p.origem})"
                        f"{' · ' + p.observacao if p.observacao else ''}\n")

    def para_briefing(self) -> list[str]:
        return [f"🔴 {p.numero} — expediente pendente de ciência: o robô não "
                f"abriu (nem os autos). Ciência é ato seu."
                for p in self.itens]


# ---------------------------------------------------------------------------
# WATCHDOG
# ---------------------------------------------------------------------------

@dataclass
class Watchdog:
    """
    Fonte que nao rodou, ou que voltou vazia sem explicacao, e ALERTA VERMELHO.

    A licao vem do proprio radar (15/07/2026): um bloco do DJEN em HTTP 500
    escondeu um processo inteiro por 8 meses. O aviso apareceu uma vez e se
    perdeu. Silencio nunca e "esta tudo bem": e "nao sabemos".
    """
    fontes: dict[str, dict] = field(default_factory=dict)

    def registrar_execucao(self, fonte: str, itens: int,
                           esperado_minimo: int | None = None,
                           erro: str = "") -> None:
        self.fontes[fonte] = {"itens": itens, "erro": erro,
                              "esperado_minimo": esperado_minimo,
                              "quando": datetime.now()}

    def alertas(self) -> list[str]:
        out = []
        for fonte, d in self.fontes.items():
            if d["erro"]:
                out.append(f"🔴 {fonte}: NAO RODOU — {d['erro']}. O silencio "
                           f"desta fonte nao significa 'sem novidade'.")
            elif d["itens"] == 0:
                out.append(f"🔴 {fonte}: voltou VAZIA. Pode ser dia sem "
                           f"movimento — ou a fonte quebrou calada. Conferir.")
            elif (d["esperado_minimo"] is not None
                  and d["itens"] < d["esperado_minimo"]):
                out.append(f"🟡 {fonte}: {d['itens']} itens, abaixo do minimo "
                           f"esperado ({d['esperado_minimo']}).")
        return out

    def registrar(self) -> None:
        LOG_WATCHDOG.parent.mkdir(parents=True, exist_ok=True)
        novo = not LOG_WATCHDOG.exists()
        with LOG_WATCHDOG.open("a", encoding="utf-8") as f:
            if novo:
                f.write("# Watchdog do Conector — execucoes e alertas\n\n")
            f.write(f"\n## {datetime.now():%Y-%m-%d %H:%M}\n\n")
            for fonte, d in self.fontes.items():
                estado = f"ERRO: {d['erro']}" if d["erro"] else f"{d['itens']} itens"
                f.write(f"- {fonte}: {estado}\n")
            for a in self.alertas():
                f.write(f"  - {a}\n")


# ---------------------------------------------------------------------------
# CONDUTA
# ---------------------------------------------------------------------------

CONDUTA = {
    "somente_processos_proprios": True,   # so onde a OAB 39261/PA esta habilitada
    "execucao": "sequencial",             # nunca paralelo: e um humano com pressa
    "pausa_entre_requisicoes_seg": 2.0,   # nao castigar o tribunal
    "frequencia": "1x/dia as 07h + sob demanda",
    "perfil_navegador": "EFEMERO",        # descartado ao fim da sessao
    "credencial": "digitada pelo titular a cada sessao; nunca vista, nunca salva",
    "modo": "SOMENTE LEITURA",
}
