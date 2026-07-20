# -*- coding: utf-8 -*-
"""teste_soj_resumo.py — prioridade das pecas + recorte head/tail (sem PDF/IA)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import soj_resumo as r

falhas = []


def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"        esperado: {esperado!r}\n        obtido  : {obtido!r}")
        falhas.append(nome)


print("=" * 60)
print("  soj_resumo — prioridade + recorte")
print("=" * 60)

check("peticao inicial = prioridade 0", r.prioridade("Petição Inicial", ""), 0)
check("sentenca = 0", r.prioridade("Sentença", ""), 0)
check("contestacao = 1", r.prioridade("Contestação", ""), 1)
check("certidao = 2 (fora da lista)", r.prioridade("Certidão", "de intimação"), 2)

# _trecho: texto curto volta inteiro; longo vira head + [...] + tail
paginas_curto = {1: "linha A", 2: "linha B"}
check("trecho curto volta inteiro (sem corte)",
      "[...]" not in r._trecho(paginas_curto, 1, 2), True)

grande = {1: "A" * 4000, 2: "B" * 4000}
tr = r._trecho(grande, 1, 2)
check("trecho longo tem marcador de corte", "[...]" in tr, True)
check("trecho longo comeca com o head (A)", tr.startswith("A"), True)
check("trecho longo termina com o tail (B)", tr.rstrip().endswith("B"), True)
check("trecho longo respeita o orcamento (< head+tail+folga)",
      len(tr) <= r.HEAD + r.TAIL + 40, True)

print("=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas)); sys.exit(1)
print("  Tudo verde. Selecao e recorte do dossie OK.")
print("=" * 60)
