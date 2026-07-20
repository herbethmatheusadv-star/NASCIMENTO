# -*- coding: utf-8 -*-
"""
soj_resumo.py — DOSSIE para o resumo executivo (Fase 3; camada de narrativa).

A narrativa e IA SOB DEMANDA: o script prepara o material GROUNDED (o texto das
pecas de alta relevancia, com citacao fls./Num., dentro de um orcamento) e um
esqueleto com cabecalho de proveniencia + status: rascunho. Depois, a IA (Claude)
preenche o resumo a partir do dossie — CADA afirmacao citando a fonte, para o
soj_verificar_citacoes poder conferir. Vira `conferido` so apos revisao humana.

Por que assim (ethos do SOJ): o script e deterministico e barato; a IA nao
"inventa" — le um material fechado e citavel; e o humano assina embaixo. Fecha o
ciclo: resumo -> citacoes -> verificacao contra os proprios autos.

Uso:
  python soj_resumo.py --cnj 0808548-83.2026.8.14.0040     # monta dossie+esqueleto
  python soj_resumo.py --cnj <n> --refazer                  # refaz o esqueleto
  (depois: a IA preenche inteligencia/resumo_executivo.md; confira com
   soj_verificar_citacoes.py e vire status: conferido)
"""
import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import soj_lib as soj
import soj_reindex as rdx

AUTOS = soj.ROOT / "AUTOS"
PROCESSOS = soj.ROOT / "PROCESSOS"
DOSSIE_MAX = 55_000      # teto de caracteres do dossie (foco, nao despejo)
HEAD, TAIL = 2600, 1300  # trecho de cada peca: abertura + fecho (dispositivo)

PRIOR = (("peticao inicial", 0), ("sentenca", 0), ("decisao", 0),
         ("acordao", 0), ("despacho saneador", 0),
         ("contestacao", 1), ("replica", 1), ("impugnacao", 1),
         ("embargos", 1), ("apelacao", 1), ("recurso", 1), ("agravo", 1),
         ("contrarrazoes", 1), ("laudo", 1), ("parecer", 1))


def prioridade(tipo: str, nome: str) -> int:
    t = soj.normaliza(f"{tipo} {nome}")
    for chave, p in PRIOR:
        if chave in t:
            return p
    return 2


def _trecho(paginas: dict, p_ini: int, p_fim: int) -> str:
    corpo = "\n".join(paginas.get(p, "") for p in range(p_ini, p_fim + 1)).strip()
    corpo = re.sub(r"\n{3,}", "\n\n", corpo)
    if len(corpo) <= HEAD + TAIL + 40:
        return corpo
    return corpo[:HEAD].rstrip() + "\n\n[...]\n\n" + corpo[-TAIL:].lstrip()


def montar_dossie(cnj: str) -> tuple[str, list, dict]:
    intel = AUTOS / cnj / "inteligencia"
    tl_json = intel / "linha_do_tempo.json"
    texto_f = AUTOS / cnj / "texto" / "autos_integral.txt"
    if not (tl_json.exists() and texto_f.exists()):
        return "", [], {}
    tl = json.loads(tl_json.read_text(encoding="utf-8"))
    paginas = rdx.paginas_do_texto(texto_f.read_text(encoding="utf-8"))

    altas = [it for it in tl.get("itens", []) if it.get("relevancia") == "alta"]
    # ordena por prioridade (inicial/decisoes primeiro) e vai enchendo ate o teto
    ordenadas = sorted(altas, key=lambda it: (prioridade(it["tipo"], it["nome"]),
                                              it["p_ini"]))
    escolhidas, orc = [], 0
    for it in ordenadas:
        tr = _trecho(paginas, it["p_ini"], it["p_fim"])
        if orc + len(tr) > DOSSIE_MAX and escolhidas:
            continue
        it = dict(it, trecho=tr)
        escolhidas.append(it)
        orc += len(tr)
    escolhidas.sort(key=lambda it: it["p_ini"])   # apresenta em ordem de folha

    partes = [
        f"# Dossie para resumo — {cnj} ({tl.get('proc_id', '')})",
        "",
        f"> Material GROUNDED: {len(escolhidas)} peca(s) de alta relevancia "
        f"(de {tl.get('alta', 0)}), trechos (abertura + fecho). Periodo "
        f"{tl.get('periodo', '-')}. Gerado por soj_resumo.py — NAO editar.",
        "> A IA escreve o resumo a partir DAQUI; cada afirmacao cita fls./Num.",
        "",
    ]
    for it in escolhidas:
        fls = (str(it["p_ini"]) if it["p_ini"] == it["p_fim"]
               else f"{it['p_ini']}–{it['p_fim']}")
        nome = re.sub(r"\s+", " ", it["nome"]).strip()[:80]
        data = it.get("data") or "s/data"
        partes += [
            f"## [fls. {fls} · Num. {it['num']} · {data}] {it['tipo']} — {nome}",
            "", it["trecho"], "",
        ]
    return "\n".join(partes), escolhidas, tl


ESQUELETO = """---
gerado_por: soj_resumo.py + IA (Claude)
gerado_em: {ts}
baseado_em:
  - {pdf} (sha {sha})
  - dossie: {n} peca(s) de alta relevancia
status: rascunho
tipo: resumo_executivo
processo: {cnj}
proc_id: {proc_id}
---

# Resumo executivo — {cnj}

> **RASCUNHO gerado por IA** a partir do dossie (`_dossie.md`). Cada afirmacao
> deve citar **fls./Num.**; confira com `soj_verificar_citacoes.py` antes de usar.
> Vire `status: conferido` só após a sua revisao.

## Do que se trata
<!-- PREENCHER a partir do _dossie.md -->

## Partes e representacao
<!-- PREENCHER -->

## Pedido e causa de pedir
<!-- PREENCHER -->

## Fase atual e ultimas decisoes
<!-- PREENCHER -->

## Pontos de atencao
<!-- PREENCHER -->

## Proximos passos sugeridos (a confirmar pelo advogado)
<!-- PREENCHER -->
"""


def cnj_em_autos(entrada: str) -> str | None:
    """Resolve o CNJ (com/sem pontuacao) para o nome da pasta em AUTOS/."""
    alvo = re.sub(r"\D", "", entrada or "")
    for d in (AUTOS.iterdir() if AUTOS.exists() else []):
        if d.is_dir() and re.sub(r"\D", "", d.name) == alvo:
            return d.name
    return None


def preparar(cnj: str, refazer: bool = False) -> dict | None:
    """Monta o dossie e (re)cria o esqueleto do resumo. None se faltar texto."""
    dossie, pecas, tl = montar_dossie(cnj)
    if not dossie:
        return None
    intel = AUTOS / cnj / "inteligencia"
    intel.mkdir(parents=True, exist_ok=True)
    (intel / "_dossie.md").write_text(dossie, encoding="utf-8")
    resumo = intel / "resumo_executivo.md"
    novo = refazer or not resumo.exists()
    if novo:
        resumo.write_text(ESQUELETO.format(
            ts=datetime.now().strftime("%Y-%m-%d %H:%M"),
            pdf=(tl.get("pdf") or "autos_integral.pdf"),
            sha=(tl.get("pdf_sha256") or "")[:8],
            n=len(pecas), cnj=cnj, proc_id=tl.get("proc_id", "")),
            encoding="utf-8")
    return {"cnj": cnj, "chars": len(dossie), "pecas": len(pecas),
            "novo": novo, "resumo": resumo}


def _frontmatter(txt: str) -> dict:
    try:
        import yaml
    except ImportError:
        return {}
    if not txt.startswith("---"):
        return {}
    fim = txt.find("\n---", 3)
    if fim < 0:
        return {}
    try:
        return yaml.safe_load(txt[3:fim]) or {}
    except Exception:  # noqa: BLE001
        return {}


def iminentes(dias: int = 14) -> list[dict]:
    """Processos com AUDIENCIA (sub-ficha) ou PRAZO EM CURSO na janela. Fonte: as
    fichas humanas de PROCESSOS/ — nao o HTML do monitor_prazos. data_interna
    sozinha (data de revisao) NAO conta: so prazo_em_curso=true e audiencia."""
    hoje = date.today()
    limite = hoje + timedelta(days=dias)
    achados: dict[str, dict] = {}
    for f in sorted(PROCESSOS.glob("PROC-*.md")):
        fm = _frontmatter(f.read_text(encoding="utf-8", errors="ignore"))
        numero = str(fm.get("numero") or "").strip().strip('"')
        if not numero or numero.startswith("("):
            continue
        sinais = []
        m = re.search(r"_audiencia_(\d{4}-\d{2}-\d{2})", f.stem)
        if m:
            try:
                sinais.append(("audiência", date.fromisoformat(m.group(1))))
            except ValueError:
                pass
        if str(fm.get("prazo_em_curso")).lower() in ("true", "1"):
            try:
                sinais.append(("prazo", date.fromisoformat(str(fm.get("data_interna")))))
            except (ValueError, TypeError):
                pass
        for motivo, d in sinais:
            if hoje <= d <= limite:
                key = re.sub(r"\D", "", numero)
                if key not in achados or d < achados[key]["data"]:
                    achados[key] = {"proc_id": fm.get("id") or f.stem,
                                    "cnj": numero, "motivo": motivo, "data": d}
    return sorted(achados.values(), key=lambda x: x["data"])


def _um(cnj_pedido: str, refazer: bool) -> None:
    cnj = cnj_em_autos(cnj_pedido)
    if not cnj:
        print(f"[resumo] {cnj_pedido} nao esta em AUTOS/. Rode soj_import.py antes.")
        sys.exit(1)
    r = preparar(cnj, refazer)
    if not r:
        print(f"[resumo] faltam texto/linha do tempo de {cnj}. Rode "
              f"soj_import.py e soj_inteligencia.py antes.")
        sys.exit(1)
    estado = "esqueleto criado" if r["novo"] else "resumo JA existe (--refazer recomeca)"
    print(f"[resumo] {cnj}: dossie {r['chars']} chars, {r['pecas']} pecas · {estado}")
    print(f"[resumo] a IA preenche {r['resumo']} a partir do _dossie.md; "
          f"depois: soj_verificar_citacoes.py.")


def _iminentes(dias: int, refazer: bool) -> None:
    lst = iminentes(dias)
    if not lst:
        print(f"[resumo] nada iminente ate {dias}d (audiencia ou prazo em curso).")
        return
    print(f"[resumo] {len(lst)} processo(s) iminente(s) ate {dias}d:")
    pend = 0
    for it in lst:
        cnj = cnj_em_autos(it["cnj"])
        rotulo = f"{it['proc_id']} · {it['cnj']} · {it['motivo']} {it['data']}"
        if not cnj:
            print(f"  - {rotulo} · autos NAO indexados — pulado")
            continue
        r = preparar(cnj, refazer)
        if not r:
            print(f"  - {rotulo} · sem texto — rode soj_import/soj_inteligencia")
            continue
        if r["novo"]:
            pend += 1
            print(f"  - {rotulo} · dossie pronto · ESQUELETO NOVO (IA preenche)")
        else:
            print(f"  - {rotulo} · dossie atualizado · resumo ja existe")
    if pend:
        print(f"[resumo] {pend} esqueleto(s) novo(s) — a IA preenche o resumo de "
              f"cada um a partir do _dossie.md; depois soj_verificar_citacoes.py.")


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Dossie/esqueleto do resumo executivo.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--cnj", help="um processo")
    g.add_argument("--iminentes", action="store_true",
                   help="todos com audiencia/prazo em curso na janela (--dias)")
    ap.add_argument("--dias", type=int, default=14, help="janela p/ --iminentes (14)")
    ap.add_argument("--refazer", action="store_true",
                    help="recria o esqueleto do resumo (perde o preenchido)")
    args = ap.parse_args()
    if args.iminentes:
        _iminentes(args.dias, args.refazer)
    else:
        _um(args.cnj, args.refazer)


if __name__ == "__main__":
    main()
