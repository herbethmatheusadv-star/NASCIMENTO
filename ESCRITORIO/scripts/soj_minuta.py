# -*- coding: utf-8 -*-
"""
soj_minuta.py — MATERIAL + ESQUELETO de minuta (Fase 3; camada de ACAO — a que o
R7 mantem fora do robo).

  A LINHA QUE NAO SE CRUZA

  Este script (e a IA) PREPARAM um RASCUNHO de peca. NAO assinam, NAO protocolam,
  NAO peticionam. Isso e trabalho de escritorio (drafting), nao ato no PJe — o
  CONECTOR continua so sabendo ler (R7). Quem revisa, assina e protocola e o
  advogado, sempre. Por isso a minuta nasce `status: rascunho` e com este aviso.

  O QUE FAZ

  Junta o material GROUNDED para uma minuta de um processo: o resumo executivo, a
  peca-alvo (a ultima sentenca/decisao, no caso do recurso) e a peticao inicial —
  textos integrais, com citacao fls./Num. — e escreve um esqueleto da peca com
  cabecalho de proveniencia. A IA redige a partir do material; cada afirmacao
  cita a fonte, para o soj_verificar_citacoes conferir.

Uso:
  python soj_minuta.py --cnj 0808637-09.2026.8.14.0040 --tipo recurso
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import soj_lib as soj
import soj_reindex as rdx

AUTOS = soj.ROOT / "AUTOS"

TIPOS = ("recurso", "manifestacao")   # extensivel; hoje o recurso e o alvo


def _norm(s: str) -> str:
    return soj.normaliza(s or "")


def _texto_peca(paginas: dict, p_ini: int, p_fim: int) -> str:
    corpo = "\n".join(paginas.get(p, "") for p in range(p_ini, p_fim + 1))
    # tira os rodapes do PJe (assinatura/URL/Num-Pag) — poluem a leitura
    corpo = re.sub(r"Assinado eletronicamente por:.*?N[uú]m\.\s*\d+\s*-\s*P[aá]g\.\s*\d+",
                   "", corpo, flags=re.S)
    corpo = re.sub(r"https?://\S+", "", corpo)
    corpo = re.sub(r"\n{3,}", "\n\n", corpo).strip()
    return corpo


def _cita(it: dict) -> str:
    fls = (str(it["p_ini"]) if it["p_ini"] == it["p_fim"]
           else f"{it['p_ini']}–{it['p_fim']}")
    return f"fls. {fls} · Num. {it['num']} · {it.get('data') or 's/data'}"


def coletar_pecas(cnj: str) -> dict:
    intel = AUTOS / cnj / "inteligencia"
    tl_f = intel / "linha_do_tempo.json"
    texto_f = AUTOS / cnj / "texto" / "autos_integral.txt"
    if not (tl_f.exists() and texto_f.exists()):
        return {}
    tl = json.loads(tl_f.read_text(encoding="utf-8"))
    paginas = rdx.paginas_do_texto(texto_f.read_text(encoding="utf-8"))
    itens = tl.get("itens", [])
    decisoes = [it for it in itens
                if "senten" in _norm(it["tipo"]) or "decis" in _norm(it["tipo"])]
    inicial = next((it for it in itens if "inicial" in _norm(it["tipo"])), None)
    alvo = decisoes[-1] if decisoes else None      # a ultima decisao = a recorrida
    resumo = intel / "resumo_executivo.md"
    return {"tl": tl, "paginas": paginas, "alvo": alvo, "inicial": inicial,
            "resumo": resumo if resumo.exists() else None}


def escrever_material(cnj: str, tipo: str, d: dict) -> Path:
    intel = AUTOS / cnj / "inteligencia" / "minutas"
    intel.mkdir(parents=True, exist_ok=True)
    L = [f"# Material para minuta ({tipo}) — {cnj}", "",
         "> GROUNDED (peca-alvo + inicial + resumo). A IA redige a minuta a partir",
         "> daqui, citando fls./Num. NAO e a minuta — e a materia-prima dela.", ""]
    if d.get("resumo"):
        L += ["## Resumo executivo (rascunho)", "",
              d["resumo"].read_text(encoding="utf-8"), "", "---", ""]
    if d.get("alvo"):
        L += [f"## PECA RECORRIDA — {d['alvo']['tipo']} [{_cita(d['alvo'])}]", "",
              _texto_peca(d["paginas"], d["alvo"]["p_ini"], d["alvo"]["p_fim"]),
              "", "---", ""]
    if d.get("inicial"):
        L += [f"## PETICAO INICIAL [{_cita(d['inicial'])}]", "",
              _texto_peca(d["paginas"], d["inicial"]["p_ini"], d["inicial"]["p_fim"]),
              ""]
    p = intel / f"_material_{tipo}.md"
    p.write_text("\n".join(L), encoding="utf-8")
    return p


ESQUELETO_RECURSO = """---
gerado_por: soj_minuta.py + IA (Claude)
gerado_em: {ts}
baseado_em:
  - autos_integral.pdf (sha {sha})
  - peca recorrida: {alvo}
status: rascunho
tipo: minuta_recurso_inominado
processo: {cnj}
proc_id: {proc_id}
---

# RASCUNHO — Recurso Inominado — {cnj}

> **RASCUNHO gerado por IA** a partir de `_material_recurso.md`. O sistema
> PREPARA; **quem revisa, assina e protocola é o advogado** (R7 — o robô nunca
> age no PJe). Cada afirmação cita **fls./Num.**; confira com
> `soj_verificar_citacoes.py`. Vire `status: conferido` só após sua revisão.

## I. Interposição (ao Juízo de origem)
<!-- PREENCHER: tempestividade (10 dias), preparo/gratuidade, pedido de
     recebimento e remessa à Turma Recursal -->

## II. Razões recursais (à Turma Recursal)

### 1. Síntese
<!-- PREENCHER -->

### 2. Da tempestividade e do preparo
<!-- PREENCHER -->

### 3. Do mérito recursal — da competência do Juizado
<!-- PREENCHER: por que a sentença errou ao extinguir -->

### 4. Do pedido
<!-- PREENCHER -->
"""


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Material + esqueleto de minuta (rascunho).")
    ap.add_argument("--cnj", required=True, help="CNJ do processo")
    ap.add_argument("--tipo", default="recurso", choices=TIPOS, help="tipo de peca")
    ap.add_argument("--refazer", action="store_true",
                    help="recria o esqueleto da minuta (perde o preenchido)")
    args = ap.parse_args()

    alvo = re.sub(r"\D", "", args.cnj)
    cnj = next((p.name for p in (AUTOS.iterdir() if AUTOS.exists() else [])
                if p.is_dir() and re.sub(r"\D", "", p.name) == alvo), None)
    if not cnj:
        print(f"[minuta] {args.cnj} nao esta em AUTOS/. Rode soj_import.py antes.")
        sys.exit(1)

    d = coletar_pecas(cnj)
    if not d:
        print(f"[minuta] faltam texto/linha do tempo de {cnj}. Rode "
              f"soj_import.py e soj_inteligencia.py antes.")
        sys.exit(1)

    mat = escrever_material(cnj, args.tipo, d)
    intel = AUTOS / cnj / "inteligencia" / "minutas"
    minuta = intel / f"{args.tipo}_RASCUNHO.md"
    if minuta.exists() and not args.refazer:
        print(f"[minuta] material atualizado. {minuta.name} JA existe "
              f"(--refazer p/ recomecar).")
    elif args.tipo == "recurso":
        minuta.write_text(ESQUELETO_RECURSO.format(
            ts=datetime.now().strftime("%Y-%m-%d %H:%M"),
            sha=(d["tl"].get("pdf_sha256") or "")[:8],
            alvo=(_cita(d["alvo"]) if d.get("alvo") else "—"),
            cnj=cnj, proc_id=d["tl"].get("proc_id", "")), encoding="utf-8")
        print(f"[minuta] esqueleto criado: {minuta}")
    else:
        print(f"[minuta] esqueleto do tipo {args.tipo!r} ainda nao modelado.")

    print(f"[minuta] material: {mat}")
    if d.get("alvo"):
        print(f"[minuta] peca recorrida: {d['alvo']['tipo']} ({_cita(d['alvo'])})")
    print("[minuta] a IA redige a minuta a partir do material; depois: "
          "soj_verificar_citacoes.py. O advogado revisa, assina e protocola.")


if __name__ == "__main__":
    main()
