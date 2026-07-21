# -*- coding: utf-8 -*-
"""Testes da ponte v1→v2 — quem entra na fila de protocolo e quem NÃO entra."""
import soj_casos_v1 as ponte

ponte.soj.console_utf8()
ok = falhas = 0


def checa(nome, obtido, esperado):
    global ok, falhas
    if obtido == esperado:
        ok += 1
        print(f"  ok  {nome}")
    else:
        falhas += 1
        print(f"  XX  {nome}: obtido {obtido!r}, esperado {esperado!r}")


print("— detecção de fixture de teste —")
checa("TESTE_FICTICIO é teste", ponte._eh_teste("TESTE_FICTICIO", "Maria Ficticia"), True)
checa("TESTE_IMPORTACAO é teste", ponte._eh_teste("TESTE_IMPORTACAO", "Lab"), True)
checa("TANIA não é teste", ponte._eh_teste("TANIA", "Tania x Cicero"), False)
checa("DAIANE não é teste", ponte._eh_teste("DAIANE", "Nascimento x perfil"), False)

print("\n— leitura dos casos de v1 —")
casos = ponte.casos_v1()
dirs = {c["dir"]: c for c in casos}
checa("casos_v1 é lista não-vazia", len(casos) > 0, True)
checa("TANIA presente", "TANIA" in dirs, True)
checa("GETULIO presente", "GETULIO" in dirs, True)
if "TANIA" in dirs:
    checa("TANIA tem peça final", bool(dirs["TANIA"]["peca_final"]), True)
    checa("TANIA é segredo", dirs["TANIA"]["segredo"], True)
if "GETULIO" in dirs:
    checa("GETULIO já é decisória", dirs["GETULIO"]["fase_processual"], "decisoria")

print("\n— quem entra na fila de protocolo —")
pend = ponte.pendentes_de_protocolo()
refs = {p["ref"] for p in pend}
checa("TANIA entra (pronta)", "TANIA" in refs, True)
checa("DAIANE entra (pronta)", "DAIANE" in refs, True)
checa("GETULIO NÃO entra (decisória)", "GETULIO" not in refs, True)
checa("TESTE_FICTICIO NÃO entra", "TESTE_FICTICIO" not in refs, True)
checa("TESTE_IMPORTACAO NÃO entra", "TESTE_IMPORTACAO" not in refs, True)

print("\n— formato da pendência (casa com soj_pendencias) —")
if pend:
    p = pend[0]
    for campo in ("tipo", "ref", "titulo", "o_que", "quem", "status"):
        checa(f"tem campo '{campo}'", campo in p, True)
    checa("tipo é 'protocolo'", p["tipo"], "protocolo")
    checa("quem é 'advogado' (R7: você assina)", p["quem"], "advogado")

print(f"\n{ok} ok, {falhas} falha(s).")
raise SystemExit(1 if falhas else 0)
