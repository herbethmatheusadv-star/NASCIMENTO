#!/usr/bin/env python3
"""
gerar_fichas.py — transforma o censo em fichas de PROCESSOS/ (SOJ, Etapa 1).

Trabalho MECANICO (prompt-mestre, §1.3: economia maxima). Le
`_SISTEMA/config/censo_tjpa.yaml` e cria as fichas que faltam.

REGRAS:
  * NUNCA sobrescreve ficha existente. A ficha e curada a mao (bloco SITUACAO
    ATUAL, tese, analises) — o gerador so CRIA o que falta.
  * Toda ficha nasce com `proxima_acao` e `data_interna` preenchidas: sem elas
    o processo violaria a R1 no minuto seguinte ao cadastro.
  * Polo com confianca < alta entra com aviso visivel na ficha. Nao se inventa
    polo (§1.4).

Uso:
    python CONECTOR/gerar_fichas.py --dry-run    # so mostra o que faria
    python CONECTOR/gerar_fichas.py              # cria
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CENSO = RAIZ / "_SISTEMA" / "config" / "censo_tjpa.yaml"
DESTINO = RAIZ / "PROCESSOS"

MODULOS_PLENOS = {"bancario_ccb", "consumidor_aguas", "familia", "civel"}


def carregar_censo() -> dict:
    try:
        import yaml
    except ImportError:
        sys.exit("[ERRO] falta o pyyaml: pip install pyyaml")
    return yaml.safe_load(CENSO.read_text(encoding="utf-8"))


def proximo_id() -> int:
    """Maior PROC-#### existente + 1. Ids nunca se reutilizam."""
    usados = [int(m.group(1))
              for p in DESTINO.glob("PROC-*.md")
              if (m := re.match(r"PROC-(\d{4})\.md$", p.name))]
    return (max(usados) + 1) if usados else 1


def fichas_por_numero() -> dict[str, str]:
    """numero-do-processo -> PROC-id, lendo o que ja existe."""
    mapa = {}
    for p in DESTINO.glob("PROC-*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        if m := re.search(r"^numero:\s*(\S+)", txt, re.M):
            mapa[m.group(1).strip()] = p.stem
    return mapa


def proxima_acao_de(pr: dict) -> tuple[str, date]:
    """
    Toda ficha nasce acionavel (R1). A acao sai do estado real do processo.
    """
    hoje = date(2026, 7, 15)
    mov = (pr.get("ultimo_movimento") or "").lower()
    cliente = pr.get("cliente_nome", "o cliente")

    if pr.get("situacao") == "encerrado":
        return ("R6: conferir resultado e honorários, comunicar o cliente, "
                "extrair 1 aprendizado e arquivar", hoje + timedelta(days=5))

    # prazo do PROPRIO cliente decorrido = o mais urgente que existe
    nome_curto = cliente.split(" e outros")[0].strip().lower()
    if "decorrido prazo" in mov and nome_curto[:15] in mov:
        return (f"🔴 URGENTE: o PJe registra prazo de {cliente} DECORRIDO. "
                f"Descobrir no PJe o que era e o que se perdeu — antes de "
                f"qualquer outra coisa neste processo", hoje)

    if "decorrido prazo" in mov:
        return ("Prazo decorrido registrado (aparentemente da parte adversa) — "
                "conferir de quem era e se abre oportunidade",
                hoje + timedelta(days=3))
    if "conclusos" in mov:
        return ("Conclusos — aguardar decisão; conferir no PJe se há algo "
                "pendente nossa parte", hoje + timedelta(days=15))
    if "grau de recurso" in mov or "instância superior" in mov:
        return ("Em 2º grau — localizar o processo na Turma, conferir se há "
                "prazo para contrarrazões/manifestação", hoje + timedelta(days=7))
    if "baixa definitiva" in mov or "arquiv" in mov:
        return ("R6: conferir resultado e honorários, comunicar o cliente, "
                "extrair 1 aprendizado e arquivar", hoje + timedelta(days=5))
    return ("Triagem: abrir os autos no PJe, definir tese e próxima ação real",
            hoje + timedelta(days=7))


def montar_ficha(pid: str, pr: dict) -> str:
    numero = pr["numero"]
    acao, quando = proxima_acao_de(pr)
    conf = pr.get("confianca_polo", "media")
    modulo = pr.get("modulo") or ""
    cliente_link = (f'"[[{pr["cliente_id"]}]]"' if pr.get("cliente_id")
                    else '"(a cadastrar — cadastro assistido)"')

    avisos = []
    if conf != "alta":
        avisos.append(
            f"> ⚠️ **Polo do cliente inferido com confiança {conf.upper()}** — "
            f"o censo traz as partes, não quem contratou. Confirmar antes de "
            f"agir. (§1.4: não se inventa polo.)")
    if pr.get("nota", "").startswith("🔴") or "URGENTE" in acao:
        avisos.append(f"> 🔴 **{pr['nota']}**")
    elif pr.get("nota"):
        avisos.append(f"> **Nota do censo:** {pr['nota']}")
    if modulo in MODULOS_PLENOS:
        avisos.append(
            f"> 📚 **Módulo `{modulo}` é PLENO no SOJ v1** — tem praxe "
            f"decisória, decisões reservadas, checklist documental, anti-erro "
            f"fatal, teses/antíteses e templates. Usar, não reinventar.")

    bloco_avisos = "\n>\n".join(avisos) if avisos else ""

    return f"""---
tipo: processo
id: {pid}
numero: {numero}
caso: "{pr.get('caso_v1', '(pendente — cadastro assistido)')}"
cliente: {cliente_link}
polo_cliente: {pr.get('polo_cliente', 'a-confirmar')}
parte_adversa: {pr.get('partes_adversas', '')}
tribunal: TJPA
sistema: PJe
grau: {pr.get('grau', 1)}
orgao: {pr.get('orgao', '')}
classe: {pr.get('classe', '')}
valor_causa:
fase: {pr.get('fase', 'conhecimento')}
situacao: {pr.get('situacao', 'ativo')}
risco: {pr.get('risco', 'medio')}
sigiloso: {str(pr.get('sigiloso', False)).lower()}
prazo_em_curso: false
proxima_acao: "{acao}"
data_interna: {quando}
ultima_movimentacao: {pr.get('ultimo_movimento', '')[:10]}
ultima_revisao_humana:
---

# {pid} · {numero}

{bloco_avisos}

## 1. Resumo executivo

{pr.get('cliente_nome', '(cliente)')} × {pr.get('partes_adversas', '(adversa)')}
— {pr.get('classe', '')}, {pr.get('orgao', '')}. Distribuído em
{pr.get('distribuido', '?')}. Último movimento conhecido:
{pr.get('ultimo_movimento', '?')}.

## 2. SITUAÇÃO ATUAL

**Ficha criada pelo censo do acervo PJe/TJPA em 15/07/2026** — os dados aqui
vêm da **lista** do painel, não dos autos. Ninguém leu este processo ainda.

- Fonte: `_SISTEMA/logs/CENSO_TJPA_2026-07-15.md` (sessão autenticada pelo
  titular; o robô não abriu expediente nenhum).
- **O que se sabe:** partes, classe, vara, data de distribuição e último
  movimento.
- **O que NÃO se sabe:** tese, pedidos, provas, prazos em curso, valor,
  contrato e honorários. Isso só sai dos autos e da entrevista.
- Confiança geral: **baixa** — é cadastro, não análise.

## 3. Cronologia

- {pr.get('distribuido', '?')} — distribuído.
- {pr.get('ultimo_movimento', '?')} — último movimento no acervo (15/07/2026).

## 4. Tese e estratégia

(a definir — {'usar o módulo `' + modulo + '`' if modulo in MODULOS_PLENOS else 'sem módulo pleno para esta área'})

## 5. Provas

(a levantar)

## 6. Prazos

Nenhum confirmado. **O acervo não mostra prazos em curso** — só o último
movimento. Prazo só nasce do DJEN (radar) ou dos autos, e só vira `confirmado`
por decisão humana.

## 7. Histórico de análises

- 2026-07-15 — ficha criada pelo censo (mecânico, sem leitura de autos).
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    censo = carregar_censo()
    ja_existem = fichas_por_numero()
    prox = proximo_id()
    criadas, puladas = [], []

    for pr in censo["processos"]:
        numero = pr["numero"]
        if pr.get("ficha_existente") or numero in ja_existem:
            puladas.append(f"{numero} -> {pr.get('ficha_existente') or ja_existem[numero]}")
            continue
        pid = f"PROC-{prox:04d}"
        prox += 1
        destino = DESTINO / f"{pid}.md"
        if not args.dry_run:
            destino.write_text(montar_ficha(pid, pr), encoding="utf-8")
        criadas.append(f"{pid}  {numero}  {pr.get('cliente_nome','')[:38]}")

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}"
          f"{len(criadas)} ficha(s) {'seriam criadas' if args.dry_run else 'criadas'}, "
          f"{len(puladas)} pulada(s) (ja existiam):\n")
    for c in criadas:
        print("  +", c)
    for p in puladas:
        print("  =", p)


if __name__ == "__main__":
    main()
