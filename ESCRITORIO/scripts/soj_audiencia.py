# -*- coding: utf-8 -*-
"""
soj_audiencia.py — PREPARA O ROTEIRO da audiência (o esqueleto; o especialista
preenche a estratégia).

Monta um `PROC-XXXX_audiencia_DATA.md` a partir do que já está estruturado — o
ato (data/hora/órgão, do campo `prazos:`), o caso (do resumo executivo), as
provas de alta relevância (da linha do tempo dos autos, com fls./Num.) e o
checklist logístico — e deixa a ESTRATÉGIA e as PERGUNTAS marcadas para o
advogado especialista completar (peça: "prepare o roteiro da audiência do
PROC-XXXX como advogado de <área>"). É o padrão do soj_resumo: esqueleto +
preenchimento pela IA.

  python soj_audiencia.py --cnj 0808548-83.2025.8.14.0040
  python soj_audiencia.py --iminentes          # todas as audiências futuras
  python soj_audiencia.py --cnj <n> --forcar   # sobrescreve um roteiro existente

R7: o robô prepara o roteiro; conduzir a audiência e decidir acordo são seus.
"""
import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import soj_lib as soj

try:
    import yaml
except ImportError:
    sys.exit("[audiencia] falta pyyaml: pip install pyyaml")

PROCESSOS = soj.ROOT / "PROCESSOS"
AUTOS = soj.ROOT / "AUTOS"
HOJE = date.today()


def _fm(caminho: Path) -> tuple[dict, str]:
    txt = caminho.read_text(encoding="utf-8", errors="ignore")
    if not txt.startswith("---"):
        return {}, txt
    fim = txt.find("\n---", 3)
    if fim < 0:
        return {}, txt
    try:
        return (yaml.safe_load(txt[3:fim]) or {}), txt[fim + 4:]
    except Exception:  # noqa: BLE001
        return {}, txt


def _data(v):
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


def _audiencia_da_ficha(fm: dict):
    """Acha a próxima audiência no campo `prazos:` (tipo 'audiência', com data)."""
    melhor = None
    for pz in (fm.get("prazos") or []):
        if not isinstance(pz, dict):
            continue
        if "audi" in str(pz.get("tipo") or "").lower() and pz.get("data"):
            d = _data(pz["data"])
            if d and d >= HOJE and (melhor is None or d < melhor[0]):
                melhor = (d, pz)
    return melhor


def _provas(cnj: str) -> list:
    """Peças de ALTA relevância da linha do tempo (com fls./Num.)."""
    tl = AUTOS / cnj / "inteligencia" / "linha_do_tempo.json"
    if not tl.exists():
        return []
    try:
        j = json.loads(tl.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    out = []
    for it in j.get("itens", []):
        if it.get("relevancia") == "alta" and it.get("tipo") not in (None, "(capa/índice)"):
            out.append(f"**{it.get('tipo','?')}** ({it.get('data') or 's/data'}) — "
                       f"fls. {it.get('fls','?')}"
                       + (f", Num. {it['num']}" if it.get("num") else ""))
    return out[:12]


def _do_que_se_trata(cnj: str) -> str:
    res = AUTOS / cnj / "inteligencia" / "resumo_executivo.md"
    if not res.exists():
        return "_(sem resumo executivo — gerar com `soj_resumo.py --cnj <n>`.)_"
    _, corpo = _fm(res)
    m = re.search(r"## Do que se trata\s*(.+?)(?:\n##|\Z)", corpo, re.S)
    return m.group(1).strip() if m else "_(ver `resumo_executivo.md`.)_"


def _risco_comparecimento(fm: dict) -> str:
    polo = str(fm.get("polo_cliente") or "").lower()
    orgao = str(fm.get("orgao") or "").lower()
    jec = "juizado" in orgao or "jec" in orgao
    if jec and polo == "ativo":
        return ("**O cliente é autor em JEC. Se faltar, o processo é EXTINTO** "
                "(art. 51, I, Lei 9.099/95) — e eventual liminar cai junto. "
                "Confirmar presença é a prioridade zero.")
    if polo == "ativo":
        return ("Cliente autor: a ausência pode gerar extinção/arquivamento — "
                "confirmar presença.")
    extra = " No JEC, contestação e provas são no ato." if jec else ""
    return ("Cliente réu/requerido: a ausência pode gerar confissão/revelia quanto "
            "à matéria de fato — confirmar presença e preparar a defesa." + extra)


def gerar(cnj: str, forcar: bool) -> bool:
    ficha = next((f for f in PROCESSOS.glob("PROC-*.md")
                  if "_audiencia" not in f.stem and _fm(f)[0].get("numero") == cnj), None)
    if not ficha:
        ficha = next((f for f in PROCESSOS.glob("PROC-*.md")
                      if "_audiencia" not in f.stem and cnj in str(_fm(f)[0].get("numero") or "")), None)
    if not ficha:
        print(f"[audiencia] processo {cnj} não encontrado em PROCESSOS/.")
        return False
    fm, _ = _fm(ficha)
    pid = fm.get("id") or ficha.stem
    numero = str(fm.get("numero") or "").strip().strip('"')
    aud = _audiencia_da_ficha(fm)
    if not aud:
        print(f"[audiencia] {pid}: nenhuma audiência futura no campo `prazos:`. "
              f"Adicione uma (tipo: audiência, data: AAAA-MM-DD) e rode de novo.")
        return False
    d, pz = aud
    saida = PROCESSOS / f"{pid}_audiencia_{d.isoformat()}.md"
    if saida.exists() and not forcar:
        print(f"[audiencia] {saida.name} JÁ existe (roteiro feito). Use --forcar "
              f"para sobrescrever.")
        return False

    cliente = str(fm.get("cliente") or "?")
    m = re.search(r"CLI-\d+", cliente)
    cliente = m.group(0) if m else cliente
    adverso = str(fm.get("parte_adversa") or "?")[:60]
    area = str(fm.get("modulo") or fm.get("area") or "geral")
    hora = str(pz.get("hora") or "")
    provas = _provas(numero)
    provas_txt = ("\n".join(f"- {p}" for p in provas) if provas
                  else "_(autos não indexados — rodar `soj_autos.py`.)_")

    conteudo = f"""---
tipo: roteiro_audiencia
processo: {pid}
numero: {numero}
audiencia_em: {d.isoformat()} {hora}
audiencia_tipo: {pz.get('tipo')}
status: rascunho (esqueleto — o especialista preenche a estratégia)
gerado_por: soj_audiencia.py
gerado_em: {HOJE.isoformat()}
modulo: {area}
ultima_revisao_humana:
---

# Roteiro — audiência · {cliente} × {adverso}

> **ESQUELETO gerado.** O ato, as provas e o checklist vêm das fichas/autos; a
> **ESTRATÉGIA** e as **PERGUNTAS** são do especialista — peça: *"prepare o roteiro
> da audiência do {pid} como advogado de {area}"*. Cada fato cita fls./Num.; o
> robô prepara, conduzir a audiência e fechar acordo são seus (R7).

## 1. O ato

| | |
|---|---|
| **Quando** | **{d:%d/%m/%Y} {hora}** — chegar/entrar 15 min antes |
| **Onde** | {fm.get('orgao','?')} |
| **Formato/Tipo** | {pz.get('obs','')} · {pz.get('tipo','')} |

## 2. Risco nº 1 — comparecimento

{_risco_comparecimento(fm)}

- [ ] Confirmar presença do cliente (e formato, se híbrido).
- [ ] Documento com foto; **procuração** conferida.
- [ ] Provas à mão (§4); se instrução, testemunhas intimadas/arroladas.

## 3. O caso (do resumo executivo)

{_do_que_se_trata(numero)}

## 4. Provas a ter em mãos (alta relevância nos autos)

{provas_txt}

## 5. Estratégia e o que fazer na mesa

> **[ESPECIALISTA PREENCHE — módulo `{area}`.]** Objetivos; pontos de ataque/defesa;
> parâmetros de acordo (decisão reservada — o número é do cliente, ouvido por você);
> o que recusar; a ordem da conversa.

## 6. Perguntas (se audiência de instrução)

> **[ESPECIALISTA PREENCHE.]** Perguntas por testemunha e o ponto que cada uma prova.

## 7. Depois

- [ ] Registrar o resultado na ficha ({pid}.md §7); havendo acordo: termo, prazo, baixa, `situacao`.
- [ ] Alimentar a camada LOCAL do módulo `{area}` (como o juízo conduz).
"""
    saida.write_text(conteudo, encoding="utf-8")
    print(f"[audiencia] {saida.name} — esqueleto do roteiro para {d:%d/%m/%Y}. "
          f"Peça ao especialista de `{area}` para preencher a estratégia (§5/§6).")
    return True


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Prepara o roteiro da audiência.")
    ap.add_argument("--cnj", default="", help="um processo")
    ap.add_argument("--iminentes", action="store_true",
                    help="todas as audiências futuras (campo prazos:)")
    ap.add_argument("--forcar", action="store_true", help="sobrescreve roteiro existente")
    args = ap.parse_args()

    if args.cnj:
        gerar(args.cnj, args.forcar)
        return
    if args.iminentes:
        n = 0
        for f in sorted(PROCESSOS.glob("PROC-*.md")):
            if "_audiencia" in f.stem:
                continue
            fm, _ = _fm(f)
            if _audiencia_da_ficha(fm):
                if gerar(str(fm.get("numero") or "").strip().strip('"'), args.forcar):
                    n += 1
        print(f"[audiencia] {n} roteiro(s) gerado(s).")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
