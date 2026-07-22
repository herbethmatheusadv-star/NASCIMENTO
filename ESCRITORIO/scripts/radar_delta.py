#!/usr/bin/env python3
"""
radar_delta.py — Fase B da MARCHA PROCESSUAL VIVA: o ELO DO DELTA.

Baseline 1x + delta diario. Compara a timeline ATUAL de um processo com o
BASELINE guardado (`AUTOS/{cnj}/timeline_baseline.json`, gerado pela Fase A) e
acha as pecas NOVAS — por id. So o que entrou depois da regua e capturado;
nunca se rebaixa os autos inteiros (a ideia do titular, 21/07/2026).

Aqui nao se baixa nem se toca no tribunal: recebe a timeline atual (ja
capturada — token-free, pela leitura do /detalhe do Kz) e faz a comparacao e a
atualizacao da estrutura. LEITURA/escrita local apenas.

Fluxo da Fase B completa (quando ligado ao RADAR das 07h):
  1. RADAR acusa movimento (DJEN/DataJud) OU releitura periodica da timeline Kz.
  2. radar_delta.diff(baseline, atual) -> pecas novas.
  3. (fora daqui) baixa SO as pecas novas (front-end, por documento) e junta.
  4. aplicar_delta -> avanca a regua, regenera a estrutura, devolve o que mudou
     para o cockpit sinalizar ficha/prazo.

  ARQUIVADO nao entra aqui: so processo ATIVO tem baseline e e vigiado.

Uso:
  python ESCRITORIO/scripts/radar_delta.py --cnj <CNJ> --atual <timeline_atual.json> [--aplicar]
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

import estruturar_autos as ea  # reaproveita normalizacao + render do indice


def _chave(p: dict) -> str:
    return str(p.get("id") or p.get("id_unico") or "")


def carregar_baseline(cnj: str) -> dict | None:
    f = RAIZ / "AUTOS" / cnj / "timeline_baseline.json"
    if not f.exists():
        return None
    return json.loads(f.read_text(encoding="utf-8"))


def diff(baseline_pecas: list[dict], atuais_pecas: list[dict]) -> tuple[list[dict], list[dict]]:
    """(novas, sumidas). novas = estao no ATUAL e nao no baseline (o delta que
    interessa). sumidas = estavam no baseline e nao no atual (raro; alerta)."""
    b = {_chave(p) for p in baseline_pecas}
    a = {_chave(p) for p in atuais_pecas}
    novas = [p for p in atuais_pecas if _chave(p) not in b]
    sumidas = [p for p in baseline_pecas if _chave(p) not in a]
    novas.sort(key=lambda x: x.get("data", ""))
    return novas, sumidas


def aplicar_delta(cnj: str, atuais_pecas: list[dict]) -> dict:
    """Une atual ao baseline (uniao por id, cronologico), regenera a estrutura e
    avanca a regua. Idempotente: sem novidade, nada muda. Devolve o relatorio."""
    base = carregar_baseline(cnj)
    if base is None:
        return {"status": "sem_baseline", "cnj": cnj,
                "obs": "rode estruturar_autos.py primeiro (Fase A)"}
    novas, sumidas = diff(base.get("pecas", []), atuais_pecas)
    if not novas:
        return {"status": "sem_novidade", "cnj": cnj, "sumidas": len(sumidas)}

    # uniao por id: mantem tudo, com o metadado mais recente (o atual manda)
    por_id = {_chave(p): p for p in base.get("pecas", [])}
    for p in atuais_pecas:
        por_id[_chave(p)] = p
    unidas = sorted(por_id.values(), key=lambda x: x.get("data", ""))

    destino = RAIZ / "AUTOS" / cnj
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "estrutura_cronologica.md").write_text(
        ea.render_md(cnj, unidas), encoding="utf-8")
    (destino / "timeline_baseline.json").write_text(json.dumps(
        {"cnj": cnj, "capturado_em": datetime.now().isoformat(timespec="seconds"),
         "total_pecas": len(unidas), "pecas": unidas},
        ensure_ascii=False, indent=1), encoding="utf-8")

    return {"status": "atualizado", "cnj": cnj,
            "novas": [{"data": p.get("data", "")[:10], "tipo": p.get("tipo"),
                       "titulo": p.get("titulo"), "id": _chave(p)} for p in novas],
            "sumidas": len(sumidas), "total_agora": len(unidas)}


def main() -> None:
    ap = argparse.ArgumentParser(description="Delta diario da marcha viva (Fase B).")
    ap.add_argument("--cnj", required=True)
    ap.add_argument("--atual", required=True, help="timeline atual (JSON do Kz)")
    ap.add_argument("--aplicar", action="store_true",
                    help="grava a atualizacao (senao so mostra o delta)")
    args = ap.parse_args()

    atuais = ea.carregar_timeline(Path(args.atual))
    base = carregar_baseline(args.cnj)
    if base is None:
        raise SystemExit(f"  Sem baseline para {args.cnj} — rode estruturar_autos.py (Fase A).")

    novas, sumidas = diff(base.get("pecas", []), atuais)
    print(f"  {args.cnj}: baseline {base.get('total_pecas')} pecas | "
          f"atual {len(atuais)} | NOVAS {len(novas)} | sumidas {len(sumidas)}")
    for p in novas:
        print(f"    + {p.get('data','')[:10]}  {p.get('tipo')}  {p.get('titulo')}  ({_chave(p)})")
    if not novas:
        print("    (nada novo — o processo nao andou desde a ultima regua; nao estamos cegos)")

    if args.aplicar:
        r = aplicar_delta(args.cnj, atuais)
        print(f"  -> {r['status']}"
              + (f": +{len(r['novas'])} peca(s), total {r['total_agora']}"
                 if r.get("status") == "atualizado" else ""))


if __name__ == "__main__":
    main()
