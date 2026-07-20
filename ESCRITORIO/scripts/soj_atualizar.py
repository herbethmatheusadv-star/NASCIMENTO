# -*- coding: utf-8 -*-
"""
soj_atualizar.py — a ATUALIZAÇÃO SILENCIOSA do dia (o que o agendador roda).

Regenera, com a data de HOJE e SEM abrir o navegador:
  - index/painel.html      (o cockpit, já com prazos + pendências)
  - index/prazos.json       (vencimentos calculados)
  - index/pendencias.json   (fila de ações humanas)
  - index/briefing_do_dia.md (resumo curto para leitura rápida / log)

NÃO baixa autos — o download exige o seu login no PJe. Isto só atualiza as
VISTAS para refletirem o dia de hoje. Rode à mão a qualquer momento:

  python soj_atualizar.py
"""
import json
from datetime import date

import soj_lib as soj
import soj_prazos
import soj_pendencias
import soj_painel


def _quando(it) -> str:
    q = it.get("quando")
    try:
        return f" ({q:%d/%m})" if q else ""
    except (ValueError, TypeError):
        return ""


def main() -> None:
    soj.console_utf8()
    idx = soj.ROOT / "index"
    idx.mkdir(parents=True, exist_ok=True)

    prazos = soj_prazos.prazos_do_acervo()
    (idx / "prazos.json").write_text(
        json.dumps(prazos, ensure_ascii=False, indent=1), encoding="utf-8")

    pend = soj_pendencias.pendencias_do_acervo()
    (idx / "pendencias.json").write_text(
        json.dumps(pend, ensure_ascii=False, indent=1), encoding="utf-8")

    dados = soj_painel.carregar()
    soj_painel.SAIDA.write_text(soj_painel.render(dados), encoding="utf-8")

    # briefing do dia — curto, para bater o olho (e servir de log do agendador)
    hoje = dados["hoje"]
    L = [f"# Briefing do dia — {date.today():%d/%m/%Y}  (gerado {soj.agora()})", ""]
    L.append(f"## Precisa de você hoje — {len(hoje)} item(ns)")
    for it in hoje[:8]:
        L.append(f"- [{it.get('proc','')}] {it['tipo']}{_quando(it)}: "
                 f"{(it.get('obs') or '')[:100]}")
    r = soj_pendencias.resumo(pend)
    L += ["", f"## Pendências — {len(pend)} aberta(s)",
          "  " + " · ".join(f"{v} {k}" for k, v in r.items())]
    if prazos:
        L += ["", f"## Prazos em curso — {len(prazos)}"]
        for p in prazos[:6]:
            L.append(f"- {p['vencimento']} · {p['tipo']} · {p['proc']} "
                     f"({'a conferir' if not p['conferido'] else 'conferido'})")
    (idx / "briefing_do_dia.md").write_text("\n".join(L), encoding="utf-8")

    print(f"[atualizar] {soj.agora()} — painel + {len(prazos)} prazo(s) + "
          f"{len(pend)} pendência(s). Briefing: index/briefing_do_dia.md")


if __name__ == "__main__":
    main()
