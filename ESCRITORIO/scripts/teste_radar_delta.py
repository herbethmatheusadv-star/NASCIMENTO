#!/usr/bin/env python3
"""teste_radar_delta.py — o motor do delta (Fase B), sem rede e sem dados reais.

Prova que diff() acha SO o que e novo (por id) e que aplicar_delta e idempotente
(rodar de novo sem novidade nao muda nada). Usa um CNJ de laboratorio e limpa
tudo no fim — nao toca em caso real (regra do laboratorio)."""
import json
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import radar_delta as rd

RAIZ = Path(__file__).resolve().parents[2]
TCNJ = "0000000-00.0000.0.00.0000"   # CNJ de laboratorio, descartavel
falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado {esperado!r}, veio {obtido!r}")
        falhas.append(nome)


def peca(i, tipo, data, tit=None):
    return {"id": i, "id_unico": f"u{i}", "tipo": tipo, "titulo": tit or tipo,
            "data": data, "responsavel": "X", "sigiloso": False}


print("=" * 74)
print("  radar_delta — o elo do delta (offline, laboratorio)")
print("=" * 74)

base = [peca(1, "Petição Inicial", "2025-01-10T09:00:00"),
        peca(2, "Contestação", "2025-02-01T10:00:00"),
        peca(3, "Despacho", "2025-02-10T11:00:00")]

print("\n=== 1. diff() acha so o que e novo ===")
# atual = baseline + 1 peca nova
atual_mais = base + [peca(4, "Manifestação", "2025-03-01T12:00:00")]
novas, sumidas = rd.diff(base, atual_mais)
check("1 peca nova detectada", [p["id"] for p in novas], [4])
check("nenhuma sumida", sumidas, [])
# atual == baseline -> nada novo
novas, sumidas = rd.diff(base, base)
check("sem mudanca: 0 novas", len(novas), 0)
check("sem mudanca: 0 sumidas", len(sumidas), 0)
# atual sem uma peca -> 1 sumida (alerta)
novas, sumidas = rd.diff(base, base[:2])
check("peca que sumiu vira alerta", [p["id"] for p in sumidas], [3])

print("\n=== 2. novas saem em ordem cronologica ===")
atual_2 = base + [peca(5, "Despacho", "2025-04-01"), peca(4, "Manifestação", "2025-03-01")]
novas, _ = rd.diff(base, atual_2)
check("2 novas, da mais antiga p/ a mais nova", [p["id"] for p in novas], [4, 5])

print("\n=== 3. aplicar_delta grava e e IDEMPOTENTE (lab) ===")
dlab = RAIZ / "AUTOS" / TCNJ
try:
    dlab.mkdir(parents=True, exist_ok=True)
    (dlab / "timeline_baseline.json").write_text(json.dumps(
        {"cnj": TCNJ, "total_pecas": len(base), "pecas": base}), encoding="utf-8")

    r1 = rd.aplicar_delta(TCNJ, atual_mais)
    check("1a passada: atualizado", r1["status"], "atualizado")
    check("1a passada: +1 peca nova", len(r1["novas"]), 1)
    check("baseline cresceu p/ 4", r1["total_agora"], 4)
    check("estrutura foi (re)gerada", (dlab / "estrutura_cronologica.md").exists(), True)

    # 2a passada com o MESMO atual -> nada novo (idempotente)
    r2 = rd.aplicar_delta(TCNJ, atual_mais)
    check("2a passada: sem novidade", r2["status"], "sem_novidade")

    # baseline sem existir -> avisa, nao quebra
    r3 = rd.aplicar_delta("9999999-99.9999.9.99.9999", atual_mais)
    check("sem baseline: avisa", r3["status"], "sem_baseline")
finally:
    shutil.rmtree(dlab, ignore_errors=True)   # limpa o laboratorio

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Motor do delta confere. Baseline 1x + delta diario, so o que e novo.")
print("=" * 74)
