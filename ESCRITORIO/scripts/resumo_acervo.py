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

import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("[ERRO] falta pyyaml: pip install pyyaml")

RAIZ = Path(__file__).resolve().parents[2]
AUTOS = RAIZ / "AUTOS"
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


def status_autos(numero: str) -> dict | None:
    """Le AUTOS/{cnj}/ (manifesto + linha do tempo) para o briefing: quantas
    paginas/pecas, a ultima peca relevante e se ha novidade. None = nao baixados."""
    if not numero or numero == "?":
        return None
    base = AUTOS / str(numero)
    manif = base / "texto" / "manifesto.json"
    if not manif.exists():
        return None
    try:
        m = json.loads(manif.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    info = {"paginas": m.get("paginas", 0), "pecas": m.get("documentos", 0),
            "novidades": m.get("novidades"), "alta": 0, "ultima_alta": None}
    intel = base / "inteligencia" / "linha_do_tempo.json"
    if intel.exists():
        try:
            j = json.loads(intel.read_text(encoding="utf-8"))
            info["alta"] = j.get("alta", 0)
            altas = [it for it in j.get("itens", []) if it.get("relevancia") == "alta"]
            info["ultima_alta"] = altas[-1] if altas else None
        except Exception:  # noqa: BLE001
            pass
    return info


def main() -> None:
    grupos: dict[int, list[str]] = {0: [], 1: [], 2: [], 9: []}
    total, sem_destilacao, com_autos, com_novidades = 0, 0, 0, 0

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

        # AUTOS (Fase 3): estado real dos autos indexados, para o dia a dia.
        sa = status_autos(num)
        if sa:
            com_autos += 1
            autos_l = f"📂 **Autos indexados:** {sa['paginas']} pgs · {sa['pecas']} peças"
            if sa.get("alta"):
                autos_l += f" ({sa['alta']} p/ leitura prioritária)"
            ua = sa.get("ultima_alta")
            if ua:
                fls = (str(ua["p_ini"]) if ua["p_ini"] == ua["p_fim"]
                       else f"{ua['p_ini']}–{ua['p_fim']}")
                autos_l += (f" · última relevante: {ua['tipo']} "
                            f"({ua.get('data') or '?'}, fls. {fls})")
            bloco += ["", autos_l]
            nv = sa.get("novidades")
            if nv:
                com_novidades += 1
                bloco.append(f"🆕 **{len(nv['novos_nums'])} nova(s) peça(s)** nos "
                             f"autos desde {nv['data']} "
                             f"({nv['paginas_antes']}→{nv['paginas_agora']} pgs).")
            bloco.append(f"↳ linha do tempo: `AUTOS/{num}/inteligencia/linha_do_tempo.md`")

        bloco += ["", f"**Próxima ação:** {acao}", f"**Até:** {quando}", ""]
        grupos[urgencia(fm)].append("\n".join(bloco))

    linhas = [
        f"# ACERVO EM UMA PÁGINA — {HOJE}",
        "",
        f"**{total} processos** · {total - sem_destilacao} com análise real · "
        f"{sem_destilacao} aguardando destilação · "
        f"**{com_autos} com autos indexados**"
        + (f" · 🆕 {com_novidades} com novidade nos autos" if com_novidades else ""),
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
        f"**Autos:** {com_autos}/{total} indexados (`soj_autos.py`). Resumo "
        "executivo de um processo: `soj_resumo.py --cnj <n>` + geração pela IA "
        "(rascunho até você conferir). Linha do tempo por processo em "
        "`AUTOS/<n>/inteligencia/`.",
    ]

    destino = RAIZ / "BRIEFINGS" / f"ACERVO_{HOJE}.md"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[ACERVO] {total} processos ({sem_destilacao} sem destilação) -> "
          f"{destino.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
