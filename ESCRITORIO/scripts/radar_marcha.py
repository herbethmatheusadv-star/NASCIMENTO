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


def cnjs_ativos() -> list[str]:
    """CNJs dos processos com situacao=ativo nas fichas (os encerrados ficam
    de fora do radar — regra do titular)."""
    out = []
    proc_dir = RAIZ / "PROCESSOS"
    if not proc_dir.exists():
        return out
    for p in sorted(proc_dir.glob("PROC-*.md")):
        if not re.match(r"PROC-\d+\.md$", p.name):
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"^---\s*\n(.*?)\n---", t, re.S)
        if not m:
            continue
        fm = m.group(1)
        sit = re.search(r"^situacao:\s*(.+)$", fm, re.M)
        num = re.search(r"^numero:\s*(.+)$", fm, re.M)
        if sit and num and sit.group(1).strip().strip('"') == "ativo":
            out.append(num.group(1).strip().strip('"'))
    return out


def motivo_sem_cobertura(cnj: str) -> str:
    """Por que o DataJud publico ainda nao devolve este ATIVO — p/ a lista
    SEM_COBERTURA. Nao e cegueira: o radar DJEN cobre a PUBLICACAO; isto so
    explica a lacuna. Medido em 21/07/2026: os dois ausentes (PROC-0007 TJMA 1o
    grau; PROC-0028 TJPA origem 0000) sao processos NOVOS ainda nao indexados — a
    base tem ~4 dias de defasagem, as vezes mais. NAO e regra de 2o grau: outro
    processo origem 0000 do TJPA (0807884-…-0000) esta na base normalmente."""
    if sigla_do_cnj(cnj) is None:
        return "tribunal fora do DataJud (sem indice publico)"
    return "ainda nao indexado no DataJud (processo novo; a base atrasa) — retry diario"


def ativos_sem_baseline() -> list[str]:
    """ATIVOS (fichas) que NAO tem regua/baseline — os que o DataJud nao indexou.
    Se um deles aparecer no DataJud num dia, o --init cria a regua e ele sai
    daqui sozinho (auto-cura)."""
    com = {cnj for cnj, _ in ativos_com_baseline()}
    return [c for c in cnjs_ativos() if c not in com]


def init_baselines(usar_rede: bool = True) -> list[tuple[str, str]]:
    """Cria a regua (baseline) via DataJud para cada ATIVO que ainda nao tem.
    Nao mexe em quem ja tem baseline (ex.: a Beatryz, com a timeline rica do Kz).
    O DataJud se paca sozinho (pausa + backoff 429 + cache 12h)."""
    import datajud
    rel = []
    for cnj in cnjs_ativos():
        bl = RAIZ / "AUTOS" / cnj / "timeline_baseline.json"
        if bl.exists():
            rel.append((cnj, "ja_tinha")); continue
        sigla = sigla_do_cnj(cnj)
        if not sigla:
            rel.append((cnj, "sem_sigla")); continue
        if not usar_rede:
            rel.append((cnj, "offline")); continue
        import time as _t
        try:
            proc = datajud.consultar(so_digitos(cnj), sigla)
        except Exception as e:  # o DataJud RESETA a conexao em rajada (WinError 10054)
            rel.append((cnj, f"erro_rede: {type(e).__name__} (tentar de novo depois)"))
            _t.sleep(5); continue
        _t.sleep(1.5)  # gentileza extra: nao provocar novo reset
        movs = sorted([m for m in (proc.movimentos if proc else []) if m.data],
                      key=lambda m: m.data)
        if not movs:
            rel.append((cnj, "sem_datajud")); continue
        pecas = [{"id": f"mov-{i}", "id_unico": f"mov-{i}", "tipo": m.nome,
                  "titulo": m.nome, "data": m.data.isoformat() + "T00:00:00",
                  "responsavel": "", "sigiloso": False} for i, m in enumerate(movs)]
        bl.parent.mkdir(parents=True, exist_ok=True)
        bl.write_text(json.dumps(
            {"cnj": cnj, "fonte": "datajud",
             "capturado_em": datetime.now().isoformat(timespec="seconds"),
             "total_pecas": len(pecas), "pecas": pecas},
            ensure_ascii=False, indent=1), encoding="utf-8")
        rel.append((cnj, f"regua {movs[-1].data.isoformat()} ({len(movs)} movs)"))
    return rel


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
    ap.add_argument("--init", action="store_true",
                    help="cria a regua (baseline) via DataJud p/ os ATIVOS sem baseline")
    args = ap.parse_args()

    if args.init:
        print("=" * 74)
        print("  MARCHA VIVA — criando regua (baseline) dos ATIVOS via DataJud")
        print("  (o DataJud se paca sozinho: pausa + backoff 429 + cache 12h)")
        print("=" * 74)
        for cnj, st in init_baselines(usar_rede=not args.sem_rede):
            print(f"  {st:36} {cnj}")
        print("")

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

    # Fase C — o elo DETECTAR->CAPTURAR: grava a FILA de capturas pendentes (o
    # que o proximo login vai buscar) e a lista dos que o DataJud nao ve — que NAO
    # ficam cegos: o radar DJEN cobre a publicacao deles. Tudo local, sem rede.
    import marcha_fila
    marcha_fila.registrar(novidades)
    sem_cob = [{"cnj": c, "sigla": sigla_do_cnj(c), "motivo": motivo_sem_cobertura(c)}
               for c in ativos_sem_baseline()]
    marcha_fila.registrar_sem_cobertura(sem_cob)
    fila = marcha_fila.pendentes()
    if fila:
        print("-" * 74)
        print(f"  [!] fila de captura: {len(fila)} processo(s) esperando o proximo login")
        print("      (rode a captura logada; o orquestrador aplica so o delta).")
    if sem_cob:
        print("-" * 74)
        print(f"  [i] {len(sem_cob)} ativo(s) SEM regua DataJud — cobertos pelo radar DJEN:")
        for i in sem_cob:
            print(f"      {i['cnj']}  ({i['motivo']})")
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
                f"{len(novidades)} novidade(s), fila {len(fila)}\n")
        for r in novidades:
            f.write(f"- [!] {r['cnj']} mexeu (ult.mov {r.get('ultimo_movimento')} "
                    f"· {r.get('ultimo_nome')}) — capturar no Kz\n")
        if not novidades and rel:
            f.write("- (nada novo)\n")
        if sem_cob:
            f.write(f"- [i] {len(sem_cob)} sem regua DataJud (DJEN cobre a publicacao): "
                    + ", ".join(i["cnj"] for i in sem_cob) + "\n")
        f.write("\n")


if __name__ == "__main__":
    main()
