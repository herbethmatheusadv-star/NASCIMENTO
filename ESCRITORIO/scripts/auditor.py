#!/usr/bin/env python3
"""
auditor.py — o Auditor do SOJ (prompt-mestre, §6): varre os frontmatters e o
modelo v1, aplica as Seis Regras (R1-R6) e a auditoria ESTRUTURAL da dupla
arquitetura (v1 CASO.yaml x v2 fichas markdown).

Saida: console + _SISTEMA/logs/AUDITORIA_<data>.md. Exit 1 se houver VERMELHO.

Nao corrige nada: auditor aponta, humano (ou migracao aprovada) resolve.
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

VERMELHO, AMARELO, INFO = "VERMELHO", "AMARELO", "INFO"
LAB = {"TESTE_FICTICIO", "TESTE_IMPORTACAO"}

achados: list[tuple[str, str, str]] = []   # (nivel, regra, texto)


def add(nivel: str, regra: str, texto: str) -> None:
    achados.append((nivel, regra, texto))


def frontmatter(p: Path) -> dict | None:
    txt = p.read_text(encoding="utf-8", errors="ignore")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", txt, re.S)
    if not m:
        return None
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        add(VERMELHO, "PARSE", f"{p.name}: frontmatter invalido ({e})")
        return None


def vazio(v) -> bool:
    return v is None or (isinstance(v, str) and not v.strip())


# ---------------------------------------------------------------- PROCESSOS
def auditar_processos() -> dict[str, dict]:
    fichas: dict[str, dict] = {}
    sem_caso = []
    for p in sorted((RAIZ / "PROCESSOS").glob("PROC-*.md")):
        fm = frontmatter(p)
        if fm is None:
            continue
        fichas[p.stem] = fm
        situacao = str(fm.get("situacao") or "")
        # R1: status + proxima_acao + data_interna (arquivado dispensa data)
        if vazio(fm.get("proxima_acao")):
            add(VERMELHO, "R1", f"{p.stem}: sem proxima_acao")
        if situacao == "ativo" and vazio(fm.get("data_interna")):
            add(VERMELHO, "R1", f"{p.stem}: ativo sem data_interna")
        if vazio(fm.get("situacao")):
            add(VERMELHO, "R1", f"{p.stem}: sem situacao")
        caso = str(fm.get("caso") or "")
        if "pendente" in caso or vazio(caso):
            sem_caso.append(p.stem)
        # R6: encerrado exige fechamento
        corpo = p.read_text(encoding="utf-8", errors="ignore")
        if situacao == "encerrado" and "CONCLUÍDO" not in corpo:
            add(AMARELO, "R6",
                f"{p.stem}: encerrado sem R6 concluido (financeiro/resultado/"
                f"aprendizado/comunicacao/arquivo)")
    if sem_caso:
        add(VERMELHO, "R1",
            f"{len(sem_caso)}/{len(fichas)} processos SEM CASO vinculado: "
            f"{', '.join(sem_caso)} — 'um processo sem caso nao existe' "
            f"(modelo de dados, §3)")
    return fichas


# ----------------------------------------------------------------- CLIENTES
def auditar_clientes() -> int:
    n = 0
    for p in sorted((RAIZ / "CLIENTES").glob("CLI-*.md")):
        fm = frontmatter(p)
        if fm is None:
            continue
        n += 1
        if str(fm.get("status")) != "ativo":
            continue
        faltas = []
        if str(fm.get("contrato")) in ("pendente", "None", ""):
            faltas.append("contrato")
        if str(fm.get("procuracao")) == "pendente":
            faltas.append("procuracao")
        if vazio(fm.get("cpf_cnpj")):
            faltas.append("cpf/cnpj")
        if vazio(fm.get("telefone")):
            faltas.append("telefone")
        if vazio(fm.get("forma_pagamento")):
            faltas.append("forma_pagamento")
        if faltas:
            add(AMARELO, "R3", f"{p.stem} ({fm.get('nome','?')}): faltam "
                               f"{', '.join(faltas)}")
    return n


# ----------------------------------------------------------------- CASOS v1
def auditar_casos_v1() -> dict[str, dict]:
    casos: dict[str, dict] = {}
    for cy in sorted((RAIZ / "CASOS").glob("*/CASO.yaml")):
        nome = cy.parent.name
        try:
            dados = yaml.safe_load(cy.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            add(VERMELHO, "PARSE", f"CASOS/{nome}/CASO.yaml invalido: {e}")
            continue
        cid = str((dados.get("caso") or {}).get("id") or nome)
        casos[cid] = {"nome": nome, "dados": dados}
        nivel = AMARELO if nome in LAB else VERMELHO
        tag = " [LAB]" if nome in LAB else ""
        caso_meta = dados.get("caso") or {}
        # R1 no modelo v1: o prompt-mestre exige proxima_acao/data_interna no
        # caso — o CASO.yaml v1 NAO TEM esses campos (nunca foram adicionados)
        if "proxima_acao" not in caso_meta:
            add(nivel, "R1", f"caso {cid} ({nome}){tag}: CASO.yaml sem campo "
                             f"proxima_acao")
        if "data_interna" not in caso_meta:
            add(nivel, "R1", f"caso {cid} ({nome}){tag}: CASO.yaml sem campo "
                             f"data_interna")
        # R2: prazos
        for pz in (dados.get("prazos") or []):
            pid = pz.get("id", "PZ?")
            estado = pz.get("estado")
            status = pz.get("status")
            if status in ("cumprido",) or estado in ("cancelado",):
                continue
            if estado is None and status is None:
                add(AMARELO, "R2", f"caso {cid}: {pid} sem estado nem status "
                                   f"(modelo v1 legado — motor v2 exige estado)")
            elif estado == "sugerido":
                add(AMARELO, "R2", f"caso {cid}: {pid} SUGERIDO aguardando "
                                   f"confirmacao humana")
            if "processo" not in pz and (dados.get("caso") or {}).get(
                    "fase_processual") not in (None, "pre_protocolo"):
                add(AMARELO, "R2", f"caso {cid}: {pid} sem campo processo "
                                   f"(condicao (a) da fonte_da_verdade)")
    return casos


# -------------------------------------------------------------- ESTRUTURAIS
def auditar_estrutura(fichas: dict, casos_v1: dict) -> None:
    # dupla morada: ficha nova apontando para caso v1 (duas fontes de verdade)
    for pid, fm in fichas.items():
        caso = str(fm.get("caso") or "")
        cid = caso.strip('"')
        if cid in casos_v1:
            nome = casos_v1[cid]["nome"]
            add(AMARELO, "ESTRUTURA",
                f"{pid} aponta para caso v1 {cid} (CASOS/{nome}) — DUPLA "
                f"ARQUITETURA no mesmo processo")
            # R2 espelho: prazo vivo no CASO.yaml precisa aparecer na ficha
            corpo = (RAIZ / "PROCESSOS" / f"{pid}.md").read_text(
                encoding="utf-8", errors="ignore")
            for pz in (casos_v1[cid]["dados"].get("prazos") or []):
                vivo = (pz.get("estado") in ("sugerido", "confirmado")
                        and pz.get("status") != "cumprido")
                if vivo and pz.get("id", "") not in corpo:
                    add(VERMELHO, "R2",
                        f"{pid}: prazo VIVO {pz.get('id')} existe no CASO.yaml "
                        f"de {cid} mas NAO aparece na ficha do processo — a "
                        f"dualidade ja esta escondendo prazo")
    # orfaos e pendencias de etapa
    if (RAIZ / "CASO_TESTE_001").exists():
        add(AMARELO, "ESTRUTURA", "CASO_TESTE_001/ na raiz: resquicio do "
                                  "sistema pre-v1, fora de qualquer modelo")
    inbox = [p for p in (RAIZ / "INBOX").iterdir()
             if p.name != ".gitkeep"] if (RAIZ / "INBOX").exists() else []
    if not inbox:
        add(INFO, "ETAPA2", "INBOX/ vazio — fluxo DJEN->INBOX ainda nao liga "
                            "radar ao sistema (Etapa 2)")
    briefs = [p for p in (RAIZ / "BRIEFINGS").iterdir()
              if p.name != ".gitkeep"] if (RAIZ / "BRIEFINGS").exists() else []
    if not briefs:
        add(INFO, "ETAPA4", "BRIEFINGS/ vazio — briefing diario 07h ainda nao "
                            "existe (Etapa 4)")
    # R5: conhecimento nao ratificado
    for a in sorted((RAIZ / "ESCRITORIO" / "APRENDIZADOS").glob("*.md")):
        fm = frontmatter(a)
        if fm and str(fm.get("status")) not in ("aprovado", "institucional"):
            add(AMARELO, "R5", f"{a.name}: status={fm.get('status')} — "
                               f"aguarda ratificacao do titular")


# -------------------------------------------------------------------- MAIN
def main() -> None:
    fichas = auditar_processos()
    n_cli = auditar_clientes()
    casos = auditar_casos_v1()
    auditar_estrutura(fichas, casos)

    vermelhos = [a for a in achados if a[0] == VERMELHO]
    amarelos = [a for a in achados if a[0] == AMARELO]
    infos = [a for a in achados if a[0] == INFO]

    linhas = [
        f"# AUDITORIA SOJ — {HOJE}",
        "",
        f"Universo: **{len(fichas)} processos** (fichas) · **{len(casos)} "
        f"casos v1** (CASO.yaml, {len(LAB & {c['nome'] for c in casos.values()})} "
        f"de laboratório) · **{n_cli} clientes**.",
        "",
        f"**{len(vermelhos)} VERMELHOS · {len(amarelos)} amarelos · "
        f"{len(infos)} informativos**",
        "",
        "## 🔴 VERMELHOS (violacao de regra — briefing)",
        "",
        *[f"- **[{r}]** {t}" for _, r, t in vermelhos],
        "",
        "## 🟡 Amarelos",
        "",
        *[f"- [{r}] {t}" for _, r, t in amarelos],
        "",
        "## ℹ️ Informativos",
        "",
        *[f"- [{r}] {t}" for _, r, t in infos],
        "",
        "---",
        "R4 (protocolo) ainda nao e verificavel mecanicamente neste modelo — "
        "entra com a migracao v2 (checklist de protocolo como campos).",
    ]
    rel = RAIZ / "_SISTEMA" / "logs" / f"AUDITORIA_{HOJE}.md"
    rel.write_text("\n".join(linhas), encoding="utf-8")

    print(f"[AUDITOR] {len(vermelhos)} VERMELHOS, {len(amarelos)} amarelos, "
          f"{len(infos)} infos -> {rel.relative_to(RAIZ)}")
    for _, r, t in vermelhos:
        print(f"  🔴 [{r}] {t}")
    sys.exit(1 if vermelhos else 0)


if __name__ == "__main__":
    main()
