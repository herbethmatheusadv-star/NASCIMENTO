#!/usr/bin/env python3
"""
radar_marcha.py — Fase B automatica: o detector DIARIO de novidade (session-free).

O elo que roda no RADAR das 07h, SOZINHO (sem login). Para cada processo ATIVO
da marcha viva (os que tem `AUTOS/{cnj}/timeline_baseline.json`, gerado pela Fase
A), pergunta ao DataJud (publico, CNJ) se o processo MEXEU desde a regua. Se
mexeu, marca 'captura pendente' — a peca nova em si se busca no Kz quando o
titular loga (radar_delta + download; ja provado ao vivo 21/07).

  Divisao (a realidade da R7): a tarefa das 07h NAO tem sessao logada, entao NAO
  le o Kz. Ela usa DataJud/DJEN (publicos) para saber QUE mexeu — e nunca ficar
  cego. A leitura da peca (Kz) depende do login do titular, e e efemera.

  ARQUIVADO nao tem baseline -> nao entra aqui (so ativo e vigiado).

Uso:
  python ESCRITORIO/scripts/radar_marcha.py            # varre os ativos
  python ESCRITORIO/scripts/radar_marcha.py --sem-rede # so a logica (offline)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "RADAR"))

# Justica Estadual (J=8): codigo do tribunal (TR) -> sigla DJEN.
TJ_POR_TR = {"14": "TJPA", "10": "TJMA"}


def sigla_do_cnj(cnj: str) -> str | None:
    """Do numero CNJ (…AAAA.J.TR.OOOO) para a sigla que o DataJud entende.
    J=5 Trabalho -> TRT{TR}; J=8 Estadual -> TJ do estado; senao None."""
    m = re.match(r"\d{7}-?\d{2}\.\d{4}\.(\d)\.(\d{2})\.\d{4}", cnj)
    if not m:
        return None
    segmento, tr = m.group(1), m.group(2)
    if segmento == "5":                       # Justica do Trabalho
        return f"TRT{int(tr)}"
    if segmento == "8":                       # Justica Estadual
        return TJ_POR_TR.get(tr)
    if segmento == "4":                       # Justica Federal
        return f"TRF{int(tr)}"
    return None


def so_digitos(cnj: str) -> str:
    return re.sub(r"\D", "", cnj)


def regua_do_baseline(base: dict) -> date | None:
    """A data da peca mais nova do baseline — a regua do delta."""
    datas = [p.get("data", "")[:10] for p in base.get("pecas", []) if p.get("data")]
    if not datas:
        return None
    try:
        return datetime.strptime(max(datas), "%Y-%m-%d").date()
    except ValueError:
        return None


def precisa_captura(regua: date | None, ultimo_movimento: date | None) -> bool:
    """True se o DataJud mostra movimento MAIS NOVO que a regua (mexeu desde a
    ultima captura). Sem regua ou sem movimento -> nao afirma que mexeu."""
    if regua is None or ultimo_movimento is None:
        return False
    return ultimo_movimento > regua


def ativos_com_baseline() -> list[tuple[str, dict]]:
    """Os processos da marcha viva: pasta em AUTOS/ com timeline_baseline.json."""
    autos = RAIZ / "AUTOS"
    out = []
    if not autos.exists():
        return out
    for d in sorted(autos.iterdir()):
        bl = d / "timeline_baseline.json"
        if bl.is_file():
            out.append((d.name, json.loads(bl.read_text(encoding="utf-8"))))
    return out


def varrer(usar_rede: bool = True) -> list[dict]:
    """Varre os ativos e devolve o relatorio de novidade (captura pendente)."""
    import datajud
    rel = []
    for cnj, base in ativos_com_baseline():
        regua = regua_do_baseline(base)
        sigla = sigla_do_cnj(cnj)
        item = {"cnj": cnj, "sigla": sigla, "regua": regua.isoformat() if regua else None}
        if not usar_rede:
            item["status"] = "offline"; rel.append(item); continue
        if not sigla:
            item["status"] = "tribunal_desconhecido"; rel.append(item); continue
        proc = datajud.consultar(so_digitos(cnj), sigla)
        ult = proc.ultimos(1) if proc else []
        umov = ult[0].data if ult else None
        item["ultimo_movimento"] = umov.isoformat() if umov else None
        item["ultimo_nome"] = ult[0].nome if ult else None
        if proc is None:
            item["status"] = "sem_datajud"
        elif precisa_captura(regua, umov):
            item["status"] = "NOVIDADE"        # mexeu desde a regua -> capturar no Kz
        else:
            item["status"] = "sem_novidade"
        rel.append(item)
    return rel


def main() -> None:
    ap = argparse.ArgumentParser(description="Detector diario de novidade (marcha viva).")
    ap.add_argument("--sem-rede", action="store_true", help="so a logica, sem DataJud")
    args = ap.parse_args()

    rel = varrer(usar_rede=not args.sem_rede)
    print("=" * 74)
    print("  MARCHA VIVA — novidade nos processos ATIVOS (via DataJud, sem login)")
    print("=" * 74)
    if not rel:
        print("  Nenhum processo ativo com baseline ainda (rode estruturar_autos.py).")
        return
    novidades = [r for r in rel if r.get("status") == "NOVIDADE"]
    for r in rel:
        tag = {"NOVIDADE": "[!] MEXEU", "sem_novidade": "[ok] parado",
               "sem_datajud": "[?] sem DataJud", "tribunal_desconhecido": "[?] tribunal?",
               "offline": "[-] offline"}.get(r["status"], r["status"])
        mv = f" | ult.mov {r.get('ultimo_movimento')} ({r.get('ultimo_nome')})" if r.get("ultimo_movimento") else ""
        print(f"  {tag:16} {r['cnj']}  (regua {r['regua']}){mv}")
    print("-" * 74)
    if novidades:
        print(f"  [!] {len(novidades)} processo(s) COM NOVIDADE — capturar a peca nova no")
        print("      Kz no proximo login (radar_delta + baixar a peca). Nao estamos cegos.")
    else:
        print("  [ok] Nenhuma novidade — os ativos nao andaram desde a ultima captura.")
    print("=" * 74)

    # heartbeat persistente: o titular ve a varredura mesmo rodando sozinha (07h)
    log = RAIZ / "_SISTEMA" / "logs" / "marcha_viva.md"
    log.parent.mkdir(parents=True, exist_ok=True)
    novo = not log.exists()
    with log.open("a", encoding="utf-8") as f:
        if novo:
            f.write("# Marcha viva — varredura diaria (radar_marcha)\n\n"
                    "> O que mexeu nos processos ATIVOS, via DataJud (sem login).\n"
                    "> NOVIDADE = capturar a peca nova no Kz no proximo login.\n\n")
        f.write(f"## {datetime.now():%Y-%m-%d %H:%M} — {len(rel)} ativo(s), "
                f"{len(novidades)} novidade(s)\n")
        for r in novidades:
            f.write(f"- [!] {r['cnj']} mexeu (ult.mov {r.get('ultimo_movimento')} "
                    f"· {r.get('ultimo_nome')}) — capturar no Kz\n")
        if not novidades and rel:
            f.write("- (nada novo)\n")
        f.write("\n")


if __name__ == "__main__":
    main()
