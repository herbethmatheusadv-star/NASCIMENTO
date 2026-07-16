#!/usr/bin/env python3
"""
resumo_acervo.py — O ACERVO EM UMA PAGINA (SOJ).

Compila as fichas de PROCESSOS/ num relatorio unico: para cada processo, o
resumo executivo, a situacao, a proxima acao e o que falta saber. E o
"me traga um resumo de todos os processos" do titular — gerado das FICHAS,
nunca dos autos: quem le autos e o Analista, uma vez; o resumo e mecanico.

Saida: BRIEFINGS/ACERVO_<data>.md (+ console). Honesto por construcao: ficha
que so tem cadastro aparece marcada como "SEM DESTILACAO — o Analista ainda
nao leu os autos", em vez de fingir resumo.
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("[ERRO] falta pyyaml: pip install pyyaml")

RAIZ = Path(__file__).resolve().parents[2]
HOJE = date.today()


def frontmatter_e_corpo(p: Path) -> tuple[dict, str]:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", txt, re.S)
    if not m:
        return {}, txt
    try:
        return (yaml.safe_load(m.group(1)) or {}), m.group(2)
    except yaml.YAMLError:
        return {}, m.group(2)


def secao(corpo: str, titulo: str) -> str:
    m = re.search(rf"^## \d+\.\s*{titulo}.*?\n(.*?)(?=^## |\Z)",
                  corpo, re.S | re.M)
    return m.group(1).strip() if m else ""


def primeiro_paragrafo(texto: str) -> str:
    for bloco in re.split(r"\n\s*\n", texto):
        limpo = " ".join(l.strip() for l in bloco.splitlines()).strip()
        if limpo and not limpo.startswith((">", "#", "|", "<!--")):
            return limpo
    return ""


def destilada(corpo: str) -> bool:
    """Ficha do censo declara que ninguem leu os autos; as curadas nao."""
    return "ninguém leu este processo ainda" not in corpo.lower()


def urgencia(fm: dict) -> int:
    acao = str(fm.get("proxima_acao") or "")
    if "🔴" in acao or "URGENTE" in acao.upper():
        return 0
    if str(fm.get("situacao")) == "ativo" and str(fm.get("risco")) == "alto":
        return 1
    if str(fm.get("situacao")) == "ativo":
        return 2
    return 9


ROTULO = {0: "🔴 AGIR AGORA", 1: "🟠 ATIVOS DE RISCO ALTO",
          2: "🟢 ATIVOS EM DIA", 9: "✅ ENCERRADOS (R6/arquivo)"}


def main() -> None:
    grupos: dict[int, list[str]] = {0: [], 1: [], 2: [], 9: []}
    total, sem_destilacao = 0, 0

    for p in sorted((RAIZ / "PROCESSOS").glob("PROC-*.md")):
        fm, corpo = frontmatter_e_corpo(p)
        if not fm:
            continue
        # O glob acha o nome; o frontmatter diz o que o arquivo E. Em PROCESSOS/
        # tambem moram roteiros de audiencia e analises com nome PROC-*, e sem
        # isto eles entram na conta como se fossem processos (em 15/07/2026 o
        # acervo anunciou "27 processos" quando sao 25). Mesma correcao do
        # auditor.py.
        if str(fm.get("tipo") or "") != "processo":
            continue
        total += 1
        tem_analise = destilada(corpo)
        if not tem_analise:
            sem_destilacao += 1

        resumo = primeiro_paragrafo(secao(corpo, "Resumo executivo"))
        situacao_txt = primeiro_paragrafo(secao(corpo, "SITUAÇÃO ATUAL"))
        num = fm.get("numero", "?")
        adverso = str(fm.get("parte_adversa") or "?")[:60]
        cliente = str(fm.get("cliente") or "?").strip('"')
        orgao = str(fm.get("orgao") or "?")
        acao = str(fm.get("proxima_acao") or "—")
        quando = fm.get("data_interna") or "—"
        sig = " · 🔒 segredo" if fm.get("sigiloso") else ""

        bloco = [f"### {p.stem} · `{num}`{sig}",
                 f"**{cliente}** × {adverso} — {orgao}", ""]
        if resumo:
            bloco.append(resumo)
        if tem_analise and situacao_txt and situacao_txt != resumo:
            bloco += ["", f"**Situação:** {situacao_txt[:400]}"]
        if not tem_analise:
            bloco += ["", "⚪ **SEM DESTILAÇÃO** — cadastro do censo; o "
                          "Analista ainda não leu os autos. O resumo de "
                          "verdade nasce do backfill (ver rodapé)."]
        bloco += ["", f"**Próxima ação:** {acao}", f"**Até:** {quando}", ""]
        grupos[urgencia(fm)].append("\n".join(bloco))

    linhas = [
        f"# ACERVO EM UMA PÁGINA — {HOJE}",
        "",
        f"**{total} processos** · {total - sem_destilacao} com análise real · "
        f"{sem_destilacao} aguardando destilação dos autos",
        "",
        "> Gerado das FICHAS (mecânico, custo zero de leitura). A qualidade de",
        "> cada resumo é a qualidade da destilação que o alimentou — ficha sem",
        "> destilação aparece marcada, nunca inventada (§1.4).",
        "",
    ]
    for nivel in (0, 1, 2, 9):
        if grupos[nivel]:
            linhas += [f"## {ROTULO[nivel]} ({len(grupos[nivel])})", ""]
            linhas += grupos[nivel]

    linhas += [
        "---",
        "**Backfill pendente:** processos ⚪ precisam dos autos em "
        "`AUTOS/<numero>/` (upload seu ou Conector Parte 2) + passada do "
        "Analista (12 saídas, §5). Prioridade sugerida: os 🔴, depois 🟠.",
    ]

    destino = RAIZ / "BRIEFINGS" / f"ACERVO_{HOJE}.md"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[ACERVO] {total} processos ({sem_destilacao} sem destilação) -> "
          f"{destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
