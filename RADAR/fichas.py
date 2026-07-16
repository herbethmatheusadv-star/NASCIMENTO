# -*- coding: utf-8 -*-
"""
Le o polo do cliente das fichas de PROCESSOS/ — para o radar parar de adivinhar.

Por que existe (BUG-04): o DJEN manda uma comunicacao por destinatario, e quando
ela lista as duas partes o radar nao tem como saber qual delas e do nosso cliente.
Resultado: INCERTO em processo que e do escritorio ha meses. O dado sempre esteve
na ficha (`polo_cliente`) — o radar e que nao a lia.

DUAS REGRAS QUE NAO PODEM SER AFROUXADAS:

1. **So conta ficha conferida por humano** (`ultima_revisao_humana` preenchida).
   O censo de 15/07/2026 inferiu polo a partir da LISTA do painel, que traz as
   partes e nao quem contratou — a propria ficha do PROC-0014 avisa "confianca
   MEDIA, confirmar antes de agir". Tratar palpite do censo como autoridade seria
   trocar um erro visivel (INCERTO) por um invisivel (MEU/DA_OUTRA_PARTE errado),
   e errar para "nao e seu" faz perder prazo.

2. **A ficha so MELHORA o veredito, nunca piora.** Sem PROCESSOS/, sem ficha, sem
   revisao ou sem polo, tudo devolve None e o radar volta a adivinhar — que e o
   comportamento de hoje. Este modulo nao pode ser motivo de o radar parar.

NAO e um parser YAML: le so pares `chave: valor` planos do frontmatter, que e o
que estes campos usam. O radar e stdlib pura por decisao de projeto (roda em
tarefa agendada, sem venv), e nao vale importar PyYAML para ler seis linhas.
"""
from __future__ import annotations

import re
from pathlib import Path

# ativo/passivo da ficha -> A/P do classificador. "terceiro" fica de fora de
# proposito: nao e um dos polos que o classificador sabe opor.
POLOS = {"ativo": "A", "passivo": "P"}

RE_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
RE_CAMPO = re.compile(r"^([a-z_]+)\s*:\s*(.*?)\s*$")


def _frontmatter_plano(txt: str) -> dict[str, str]:
    """Pares `chave: valor` do topo do arquivo. Ignora listas e campos aninhados."""
    m = RE_FRONTMATTER.match(txt)
    if not m:
        return {}
    out: dict[str, str] = {}
    for linha in m.group(1).splitlines():
        if not linha or linha[0] in " \t-":     # aninhado ou item de lista
            continue
        mm = RE_CAMPO.match(linha)
        if not mm:
            continue
        chave, valor = mm.group(1), mm.group(2)
        if len(valor) >= 2 and valor[0] == valor[-1] and valor[0] in "\"'":
            valor = valor[1:-1]
        out[chave] = valor
    return out


def carregar(raiz: Path | None = None) -> dict[str, dict]:
    """
    Indice CNJ (so digitos) -> {id, polo, confirmado_em}.

    Devolve {} se PROCESSOS/ nao existir — o radar tem de rodar em qualquer lugar.
    """
    raiz = raiz or Path(__file__).resolve().parent.parent
    pasta = raiz / "PROCESSOS"
    idx: dict[str, dict] = {}
    if not pasta.is_dir():
        return idx
    for p in sorted(pasta.glob("PROC-*.md")):
        try:
            fm = _frontmatter_plano(p.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
        # o glob acha o nome; o frontmatter diz o que o arquivo E. Em PROCESSOS/
        # tambem moram roteiros de audiencia e analises com nome PROC-*.
        if fm.get("tipo") != "processo":
            continue
        num = re.sub(r"\D", "", fm.get("numero", ""))
        if not num:
            continue
        idx[num] = {
            "id": fm.get("id") or p.stem,
            "polo": POLOS.get(fm.get("polo_cliente", "")),
            "confirmado_em": fm.get("ultima_revisao_humana") or None,
        }
    return idx


def polo_confirmado(idx: dict[str, dict], numero_limpo: str) -> str | None:
    """
    'A'/'P' so quando a ficha existe, tem polo E foi conferida por um humano.
    Qualquer outra situacao: None, e o radar adivinha como antes.
    """
    f = idx.get(numero_limpo or "")
    if not f:
        return None
    if not f.get("confirmado_em"):
        return None
    return f.get("polo")


def id_do_processo(idx: dict[str, dict], numero_limpo: str) -> str | None:
    """PROC-#### do processo, para o relatorio apontar a ficha. Independe de revisao."""
    f = idx.get(numero_limpo or "")
    return f.get("id") if f else None
