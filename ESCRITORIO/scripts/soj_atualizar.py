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
import os
import time
from datetime import date

import soj_lib as soj
import soj_prazos
import soj_pendencias
import soj_financeiro
import soj_painel


def _escrever(caminho, conteudo: str) -> None:
    """Escrita atômica com retry — o OneDrive/antivírus às vezes segura o
    arquivo (o run agendado cai em cima da sincronização). Grava num .tmp e
    troca; tenta de novo se estiver travado."""
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    for tent in range(6):
        try:
            tmp.write_text(conteudo, encoding="utf-8")
            os.replace(tmp, caminho)
            return
        except OSError:
            if tent == 5:
                raise
            time.sleep(0.7)


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
    _escrever(idx / "prazos.json",
              json.dumps(prazos, ensure_ascii=False, indent=1))

    pend = soj_pendencias.pendencias_do_acervo()
    _escrever(idx / "pendencias.json",
              json.dumps(pend, ensure_ascii=False, indent=1))

    fin = soj_financeiro.resumo()
    _escrever(idx / "financeiro.json",
              json.dumps(fin, ensure_ascii=False, indent=1))

    dados = soj_painel.carregar()
    _escrever(soj_painel.SAIDA, soj_painel.render(dados))

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
    caf = fin.get("contratos_a_formalizar", [])
    L += ["", "## Financeiro",
          f"  A receber {soj_financeiro._r(fin.get('a_receber', 0))} · "
          f"recebido {soj_financeiro._r(fin.get('recebido', 0))} · "
          f"{len(caf)} contrato(s) a formalizar"]
    if prazos:
        L += ["", f"## Prazos em curso — {len(prazos)}"]
        for p in prazos[:6]:
            L.append(f"- {p['vencimento']} · {p['tipo']} · {p['proc']} "
                     f"({'a conferir' if not p['conferido'] else 'conferido'})")
    _escrever(idx / "briefing_do_dia.md", "\n".join(L))

    print(f"[atualizar] {soj.agora()} — painel + {len(prazos)} prazo(s) + "
          f"{len(pend)} pendência(s). Briefing: index/briefing_do_dia.md")


if __name__ == "__main__":
    import traceback
    try:
        main()
    except Exception:
        # daemon nao pode falhar em silencio: registra o traceback no TEMP
        # (fora do OneDrive, para nao depender do que pode estar travado).
        alvo = os.path.join(os.environ.get("TEMP", "."), "soj_agendador_erro.log")
        try:
            with open(alvo, "a", encoding="utf-8") as fh:
                fh.write(f"\n=== {soj.agora()} ===\n{traceback.format_exc()}")
        except Exception:
            pass
        raise
