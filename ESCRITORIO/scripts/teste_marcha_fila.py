#!/usr/bin/env python3
"""teste_marcha_fila.py — a Fase C (fila detectar->capturar) inteira, OFFLINE.

Prova, sem login e sem tocar em caso real (usa um AUTOS temporario e um duble de
captura), o ciclo: registrar novidade -> nao capturou (segue na fila) -> capturou
a peca nova -> delta aplicado -> fila limpa -> idempotente. Tambem o roundtrip da
lista SEM_COBERTURA (os que o DataJud nao enxerga)."""
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import marcha_fila as mf
import radar_delta as rd
import estruturar_autos as ea  # noqa: F401  (rd o usa; garante import limpo)

falhas = []


def check(nome, cond):
    print(f"  [{'ok ' if cond else 'FALHA'}] {nome}")
    if not cond:
        falhas.append(nome)


def peca(id_, data, tipo="Peticao", titulo=""):
    return {"id": id_, "id_unico": id_, "tipo": tipo, "titulo": titulo or tipo,
            "data": data, "responsavel": "", "sigiloso": False}


print("=" * 74)
print("  marcha_fila — Fase C: detectar -> capturar (offline, duble)")
print("=" * 74)

CNJ = "0000483-10.2025.5.08.0130"

with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    # redireciona TODOS os caminhos para o temporario (nao suja _SISTEMA/AUTOS reais)
    mf.PASTA = tmp / "_SISTEMA" / "marcha"
    mf.FILA = mf.PASTA / "capturas_pendentes.json"
    mf.SEM_COBERTURA = mf.PASTA / "sem_cobertura.json"
    rd.RAIZ = tmp                      # radar_delta grava em tmp/AUTOS/<cnj>

    # baseline (Fase A): 2 pecas, regua = 2026-03-03
    base = [peca("A1", "2025-11-11T09:00:00", "Peticao Inicial"),
            peca("A2", "2026-03-03T17:42:00", "Contestacao")]
    bl = tmp / "AUTOS" / CNJ / "timeline_baseline.json"
    bl.parent.mkdir(parents=True, exist_ok=True)
    bl.write_text(json.dumps(
        {"cnj": CNJ, "capturado_em": datetime.now().isoformat(timespec="seconds"),
         "total_pecas": 2, "pecas": base}, ensure_ascii=False), encoding="utf-8")

    print("\n=== 1. registrar novidade -> entra na fila ===")
    mf.registrar([{"cnj": CNJ, "sigla": "TRT8", "regua": "2026-03-03",
                   "ultimo_movimento": "2026-03-10", "ultimo_nome": "Conclusos"}])
    check("fila tem 1 pendencia", len(mf.pendentes()) == 1)
    check("a pendencia e o CNJ certo", mf.pendentes()[0]["cnj"] == CNJ)

    print("\n=== 2. registrar de novo o MESMO -> nao duplica ===")
    fila = mf.registrar([{"cnj": CNJ, "sigla": "TRT8", "regua": "2026-03-03",
                          "ultimo_movimento": "2026-03-10", "ultimo_nome": "Conclusos"}])
    check("continua com 1 (merge por CNJ)", len(fila) == 1)
    check("preservou o detectado_em", "detectado_em" in fila[0])

    print("\n=== 3. processar mas a captura falha (None) -> segue na fila ===")
    r = mf.processar(CNJ, lambda c: None)
    check("status nao_capturou", r["status"] == "nao_capturou")
    check("continua na fila (1)", len(mf.pendentes()) == 1)

    print("\n=== 4. captura traz a peca NOVA -> delta aplicado, sai da fila ===")
    atual = base + [peca("A3", "2026-03-10T11:00:00", "Decisao", "Conclusao/Decisao")]
    r = mf.processar(CNJ, lambda c: atual)
    check("status atualizado", r["status"] == "atualizado")
    check("1 peca nova no delta", len(r.get("novas", [])) == 1)
    check("baseline avancou p/ 3 pecas", rd.carregar_baseline(CNJ)["total_pecas"] == 3)
    check("fila esvaziou", len(mf.pendentes()) == 0)
    check("gerou a estrutura cronologica",
          (tmp / "AUTOS" / CNJ / "estrutura_cronologica.md").exists())

    print("\n=== 5. idempotente: reprocessar a MESMA timeline nao muda nada ===")
    mf.registrar([{"cnj": CNJ, "sigla": "TRT8", "regua": "2026-03-10"}])
    r = mf.processar(CNJ, lambda c: atual)
    check("status sem_novidade", r["status"] == "sem_novidade")
    check("baseline segue com 3", rd.carregar_baseline(CNJ)["total_pecas"] == 3)
    check("fila limpa de novo", len(mf.pendentes()) == 0)

    print("\n=== 6. remover explicito ===")
    mf.registrar([{"cnj": CNJ}])
    mf.remover(CNJ)
    check("remover tira da fila", len(mf.pendentes()) == 0)

    print("\n=== 7. sem_cobertura: roundtrip (os que o DataJud nao ve) ===")
    mf.registrar_sem_cobertura([
        {"cnj": "0813960-18.2026.8.14.0000", "sigla": "TJPA",
         "motivo": "ainda nao indexado no DataJud (processo novo) — retry diario"},
        {"cnj": "0805885-75.2026.8.10.0040", "sigla": "TJMA",
         "motivo": "ainda nao indexado no DataJud (processo novo) — retry diario"}])
    sc = mf.sem_cobertura()
    check("guardou os 2 sem cobertura", len(sc) == 2)
    check("motivo preservado (roundtrip)", "indexado" in sc[0]["motivo"])

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Fase C confere: a fila liga 'detectei' a 'capturei', e so o delta entra.")
print("=" * 74)
