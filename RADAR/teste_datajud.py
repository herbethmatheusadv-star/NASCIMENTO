# -*- coding: utf-8 -*-
"""
Testa o cruzamento com o DataJud sem depender da rede (fixtures) e, no fim,
uma checagem opcional contra a API real.
"""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import datajud as dj

falhas = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado}")
        print(f"          obtido  : {obtido}")
        falhas.append(nome)


def proc(movs):
    return dj.Processo(numero="1", tribunal="TJPA", classe="X", orgao="Y",
                       assuntos=[], ajuizamento=date(2026, 1, 1),
                       atualizado=date(2026, 7, 10),
                       movimentos=[dj.Movimento(d, c, n, []) for d, c, n in movs])


print("\n=== 1. Indice do tribunal ===")
check("TJPA -> tjpa", dj.indice_do_tribunal("TJPA"), "tjpa")
check("TRT8 -> trt8", dj.indice_do_tribunal("TRT8"), "trt8")
check("vazio -> None", dj.indice_do_tribunal(""), None)

print("\n=== 2. Datas em formatos variados ===")
check("ISO com timezone", dj._parse_data("2026-07-05T08:01:10.359000Z"), date(2026, 7, 5))
check("ISO simples", dj._parse_data("2026-06-30T00:00:00"), date(2026, 6, 30))
check("so data", dj._parse_data("2026-06-30"), date(2026, 6, 30))
check("compacto do ajuizamento", dj._parse_data("2026062512"), date(2026, 6, 25))
check("nulo", dj._parse_data(None), None)

print("\n=== 3. O CASO REAL: agravo com decurso de prazo ===")
# publicado 22/06, prazo de 5 dias uteis venceu 29/06,
# decurso certificado em 30/06 e concluso para julgamento em 01/07
agravo = proc([
    (date(2026, 6, 18), 334, "Gratuidade da Justiça"),
    (date(2026, 6, 20), 1061, "Disponibilização no DJE"),
    (date(2026, 6, 22), 92, "Publicação"),
    (date(2026, 6, 30), 1051, "Decurso de Prazo"),
    (date(2026, 7, 1), 51, "Conclusão"),
])
sit, det = dj.conferir_cumprimento(agravo, date(2026, 6, 22), date(2026, 6, 29))
check("detecta o decurso", sit, dj.DECURSO_REGISTRADO)
print(f"        -> {det}")

print("\n=== 4. Peticao dentro do prazo = sinal de cumprido ===")
cumprido = proc([
    (date(2026, 6, 22), 92, "Publicação"),
    (date(2026, 6, 25), 85, "Petição"),
])
sit, det = dj.conferir_cumprimento(cumprido, date(2026, 6, 22), date(2026, 6, 29))
check("detecta a peticao", sit, dj.PETICAO_NO_PRAZO)
print(f"        -> {det}")

print("\n=== 5. Peticao E decurso: avisa, nao decide sozinho ===")
ambos = proc([
    (date(2026, 6, 22), 92, "Publicação"),
    (date(2026, 6, 25), 85, "Petição"),
    (date(2026, 6, 30), 1051, "Decurso de Prazo"),
])
sit, det = dj.conferir_cumprimento(ambos, date(2026, 6, 22), date(2026, 6, 29))
check("prioriza a peticao mas menciona o decurso", sit, dj.PETICAO_NO_PRAZO)
check("o detalhe pede conferencia", "confira" in det, True)
print(f"        -> {det}")

print("\n=== 6. Decurso de OUTRO prazo nao conta ===")
outro = proc([
    (date(2026, 6, 22), 92, "Publicação"),
    (date(2026, 4, 29), 1051, "Decurso de Prazo"),   # muito antes
])
sit, _ = dj.conferir_cumprimento(outro, date(2026, 6, 22), date(2026, 6, 29))
check("decurso antigo nao vira alarme", sit, dj.INDEFINIDO)

print("\n=== 7. Base defasada e admitida, nao mascarada ===")
defasado = dj.Processo(numero="1", tribunal="TJPA", classe="X", orgao="Y",
                       assuntos=[], ajuizamento=date(2026, 1, 1),
                       atualizado=date(2026, 7, 1),
                       movimentos=[dj.Movimento(date(2026, 6, 22), 92, "Publicação", [])])
sit, det = dj.conferir_cumprimento(defasado, date(2026, 6, 22), date(2026, 7, 10))
check("avisa que a base e mais antiga que o vencimento", sit, dj.INDEFINIDO)
check("o detalhe explica a defasagem", "atualizada até" in det, True)
print(f"        -> {det}")

print("\n=== 8. Processo ausente do DataJud ===")
sit, det = dj.conferir_cumprimento(None, date(2026, 6, 22), date(2026, 6, 29))
check("sem dados", sit, dj.SEM_DADOS)

print("\n=== 9. Rede: o agravo de verdade (opcional) ===")
try:
    p = dj.consultar("08078847520268140000", "TJPA", usar_cache=True)
    if p is None:
        print("  [pulado] DataJud não devolveu o processo agora")
    else:
        check("achou o agravo", p.numero, "08078847520268140000")
        check("classe correta", "Agravo" in (p.classe or ""), True)
        tem_decurso = any(m.codigo == dj.COD_DECURSO_PRAZO
                          and m.data == date(2026, 6, 30) for m in p.movimentos)
        check("o decurso de 30/06 esta la (dado real)", tem_decurso, True)
        sit, det = dj.conferir_cumprimento(p, date(2026, 6, 22), date(2026, 6, 29))
        check("cruzamento real acusa decurso", sit, dj.DECURSO_REGISTRADO)
        print(f"        -> {det}")
except Exception as ex:
    print(f"  [pulado] rede indisponível: {type(ex).__name__}")

print("\n" + "=" * 62)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Todos os casos passaram.")
print("=" * 62)
