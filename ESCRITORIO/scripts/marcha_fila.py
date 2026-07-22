#!/usr/bin/env python3
"""
marcha_fila.py — Fase C da MARCHA VIVA: a FILA que liga DETECTAR a CAPTURAR.

O radar das 07h (radar_marcha, SEM login) descobre QUE um processo mexeu, mas
nao pode ler a peca nova — isso exige o login do titular, e e efemero. Faltava o
elo DURAVEL entre os dois momentos: uma fila persistente de "capturas pendentes".
Este modulo e essa fila.

  - radar_marcha, ao achar NOVIDADE, chama `registrar()` — grava o CNJ na fila.
  - quando o titular loga, o orquestrador chama `processar(cnj, capturar_fn)`:
    captura a timeline ATUAL (capturar_fn = o driver do tribunal), calcula o delta
    (radar_delta) e, se aplicou, TIRA o CNJ da fila. Idempotente.

  capturar_fn e INJETADO: no teste, um duble offline; ao vivo, o driver real
  (Kz token-free p/ TRT; acervo p/ TJPA). Assim o CEREBRO (fila + delta) se testa
  sem login; as MAOS (captura logada) se exercem ao vivo com o titular.

  Alem da fila, guarda a lista SEM_COBERTURA: os ATIVOS que o DataJud nao enxerga
  (2o grau TJPA nao e alimentado; processo novo ainda nao indexado). Nao ficam
  cegos — o radar DJEN cobre a PUBLICACAO deles; aqui so tornamos a lacuna VISIVEL.

Uso (linha de comando — inspecao):
  python ESCRITORIO/scripts/marcha_fila.py            # mostra a fila + sem-cobertura
  python ESCRITORIO/scripts/marcha_fila.py --limpar <CNJ>
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "_SISTEMA" / "marcha"
FILA = PASTA / "capturas_pendentes.json"
SEM_COBERTURA = PASTA / "sem_cobertura.json"

import radar_delta as rd   # reaproveita o motor do delta (Fase B)


def _ler(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    try:
        d = json.loads(caminho.read_text(encoding="utf-8"))
        return d if isinstance(d, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _gravar(caminho: Path, dados: list[dict]) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=1),
                       encoding="utf-8")


# --- a fila de capturas pendentes -------------------------------------------

def pendentes() -> list[dict]:
    """A fila: os CNJs que mexeram (DataJud) e ainda faltam capturar no login."""
    return _ler(FILA)


def registrar(novidades: list[dict]) -> list[dict]:
    """Junta as novidades do radar a fila (merge por CNJ; NAO duplica). Cada item
    guarda o que o radar viu: ultimo movimento e a regua atual. Preserva o
    `detectado_em` original (quando entrou na fila) e atualiza `visto_em`.
    Devolve a fila ja ordenada (mais antigo primeiro)."""
    fila = {i["cnj"]: i for i in _ler(FILA) if i.get("cnj")}
    agora = datetime.now().isoformat(timespec="seconds")
    for n in novidades:
        cnj = n.get("cnj")
        if not cnj:
            continue
        prev = fila.get(cnj, {})
        fila[cnj] = {
            "cnj": cnj,
            "sigla": n.get("sigla"),
            "regua": n.get("regua"),
            "ultimo_movimento": n.get("ultimo_movimento"),
            "ultimo_nome": n.get("ultimo_nome"),
            "detectado_em": prev.get("detectado_em") or agora,
            "visto_em": agora,
        }
    ordenada = sorted(fila.values(), key=lambda x: x.get("detectado_em", ""))
    _gravar(FILA, ordenada)
    return ordenada


def remover(cnj: str) -> None:
    """Tira um CNJ da fila (apos a captura ser aplicada com sucesso)."""
    _gravar(FILA, [i for i in _ler(FILA) if i.get("cnj") != cnj])


# --- a lista dos que o DataJud nao enxerga (visivel, nunca cego) -------------

def registrar_sem_cobertura(itens: list[dict]) -> None:
    """Persiste os ATIVOS sem regua DataJud (2o grau TJPA / ainda nao indexado).
    Cada item: {cnj, sigla, motivo}. O radar DJEN cobre a publicacao deles."""
    _gravar(SEM_COBERTURA, itens)


def sem_cobertura() -> list[dict]:
    return _ler(SEM_COBERTURA)


# --- o orquestrador: uma pendencia por vez ----------------------------------

def processar(cnj: str, capturar_fn) -> dict:
    """Processa UMA pendencia da fila.

    capturar_fn(cnj) -> list[peca] (a timeline ATUAL do processo, ja capturada do
    tribunal) ou None se nao deu para capturar agora.

      - None            -> mantem na fila (tenta de novo no proximo login).
      - lista de pecas  -> aplica o delta (radar_delta). Se 'atualizado' ou
                           'sem_novidade', TIRA o CNJ da fila.

    Idempotente: capturar a mesma timeline duas vezes nao muda nada na 2a e limpa
    a fila do mesmo jeito. Nunca rebaixa os autos inteiros — so o delta (a peca
    nova) entra. Devolve o relatorio do radar_delta (+ o cnj)."""
    try:
        atuais = capturar_fn(cnj)
    except Exception as e:  # noqa: BLE001
        return {"cnj": cnj, "status": "erro_captura", "detalhe": str(e)[:160]}
    if atuais is None:
        return {"cnj": cnj, "status": "nao_capturou"}   # segue na fila
    r = rd.aplicar_delta(cnj, atuais)
    r.setdefault("cnj", cnj)
    if r.get("status") in ("atualizado", "sem_novidade"):
        remover(cnj)
    return r


def main() -> None:
    ap = argparse.ArgumentParser(description="Fila de capturas pendentes (marcha viva Fase C).")
    ap.add_argument("--limpar", metavar="CNJ", help="tira um CNJ da fila a mao")
    args = ap.parse_args()

    if args.limpar:
        remover(args.limpar)
        print(f"  removido da fila: {args.limpar}")

    fila = pendentes()
    sc = sem_cobertura()
    print("=" * 74)
    print("  MARCHA VIVA — fila de capturas pendentes (Fase C)")
    print("=" * 74)
    if not fila:
        print("  Fila vazia — nenhum processo esperando captura.")
    for i in fila:
        print(f"  [!] {i['cnj']}  (mexeu {i.get('ultimo_movimento')} · "
              f"{i.get('ultimo_nome')}) — desde {i.get('detectado_em', '')[:10]}")
    if sc:
        print("-" * 74)
        print(f"  Sem cobertura DataJud ({len(sc)}) — cobertos pelo radar DJEN:")
        for i in sc:
            print(f"    {i['cnj']}  ({i.get('motivo', '')})")
    print("=" * 74)


if __name__ == "__main__":
    main()
