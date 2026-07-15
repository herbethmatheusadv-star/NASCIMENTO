# -*- coding: utf-8 -*-
"""Valida o calendario forense e a contagem de prazos contra casos conferiveis."""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from monitor_prazos import (Calendario, calcular_pascoa, calcular_prazo,
                            detectar_prazo, prioridade)

falhas = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado}")
        print(f"          obtido  : {obtido}")
        falhas.append(nome)

DIAS = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]

print("\n=== 1. Pascoa (datas historicas conhecidas) ===")
check("Pascoa 2024", calcular_pascoa(2024), date(2024, 3, 31))
check("Pascoa 2025", calcular_pascoa(2025), date(2025, 4, 20))
check("Pascoa 2026", calcular_pascoa(2026), date(2026, 4, 5))
check("Pascoa 2027", calcular_pascoa(2027), date(2027, 3, 28))

print("\n=== 2. Feriados moveis 2026 (derivados da Pascoa 05/04) ===")
cal = Calendario()
f26 = cal.feriados(2026)
check("Carnaval terca = 17/02/2026", date(2026, 2, 17) in f26, True)
check("Sexta-feira Santa = 03/04/2026", date(2026, 4, 3) in f26, True)
check("Corpus Christi = 04/06/2026", date(2026, 6, 4) in f26, True)
check("Consciencia Negra = 20/11/2026", date(2026, 11, 20) in f26, True)

print("\n=== 3. Dias uteis ===")
check("10/07/2026 eh sexta", DIAS[date(2026, 7, 10).weekday()], "sexta")
check("sabado 11/07 nao eh util", cal.eh_util(date(2026, 7, 11)), False)
check("domingo 12/07 nao eh util", cal.eh_util(date(2026, 7, 12)), False)
check("segunda 13/07 eh util", cal.eh_util(date(2026, 7, 13)), True)
check("07/09/2026 (Independencia) nao eh util", cal.eh_util(date(2026, 9, 7)), False)
check("26/12/2026 (recesso) nao eh util", cal.eh_util(date(2026, 12, 26)), False)
check("15/01/2027 (recesso) nao eh util", cal.eh_util(date(2027, 1, 15)), False)
check("21/01/2027 (fim recesso) eh util", cal.eh_util(date(2027, 1, 21)), True)

print("\n=== 4. Prazo: disponibilizado sexta 10/07/2026, 15 dias uteis ===")
# Conferencia manual:
#   publicacao = segunda 13/07 ; inicio = terca 14/07 (dia 1)
#   14,15,16,17 (4) | 20,21,22,23,24 (9) | 27,28,29,30,31 (14) | 03/08 (15)
pub, ini, venc = calcular_prazo(date(2026, 7, 10), 15, cal)
check("publicacao = 13/07/2026", pub, date(2026, 7, 13))
check("inicio contagem = 14/07/2026", ini, date(2026, 7, 14))
check("vencimento = 03/08/2026", venc, date(2026, 8, 3))

print("\n=== 5. Prazo cruzando feriado: disponibilizado 01/09/2026, 5 dias uteis ===")
# 01/09 terca -> publicacao quarta 02/09 -> inicio quinta 03/09 (dia 1)
# 03 (1), 04 (2), [05-06 fds], 07 = Independencia (feriado), 08 (3), 09 (4), 10 (5)
pub, ini, venc = calcular_prazo(date(2026, 9, 1), 5, cal)
check("publicacao = 02/09/2026", pub, date(2026, 9, 2))
check("inicio = 03/09/2026", ini, date(2026, 9, 3))
check("vencimento pula 07/09 = 10/09/2026", venc, date(2026, 9, 10))

print("\n=== 6. Prazo caindo no recesso: disponibilizado 15/12/2026, 15 dias uteis ===")
# 15/12 terca -> publicacao 16/12 -> inicio 17/12 (dia 1)
# 17 (1), 18 (2), [19-20 fds/recesso], recesso ate 20/01/2027
# volta 21/01/2027 (3), 22 (4), 25 (5), 26 (6), 27 (7), 28 (8), 29 (9),
# 01/02 (10), 02 (11), 03 (12), 04 (13), 05 (14) sexta,
# 08 e 09/02 = Carnaval, 10/02 = Cinzas  ->  dia 15 = quinta 11/02/2027
pub, ini, venc = calcular_prazo(date(2026, 12, 15), 15, cal)
check("publicacao = 16/12/2026", pub, date(2026, 12, 16))
check("inicio = 17/12/2026", ini, date(2026, 12, 17))
check("vencimento atravessa recesso E Carnaval = 11/02/2027", venc, date(2027, 2, 11))

print("\n=== 6b. Carnaval 2027 (Pascoa 28/03) cai em 08-10/02 ===")
check("08/02/2027 (Carnaval seg) nao eh util", cal.eh_util(date(2027, 2, 8)), False)
check("09/02/2027 (Carnaval ter) nao eh util", cal.eh_util(date(2027, 2, 9)), False)
check("10/02/2027 (Cinzas) nao eh util", cal.eh_util(date(2027, 2, 10)), False)
check("11/02/2027 eh util", cal.eh_util(date(2027, 2, 11)), True)

print("\n=== 7. Disponibilizado na vespera do recesso (18/12/2026) ===")
# 18/12 sexta -> proximo util: 19-20 fds/recesso, recesso ate 20/01
# publicacao = 21/01/2027 (quinta) -> inicio = 22/01/2027 (sexta)
pub, ini, venc = calcular_prazo(date(2026, 12, 18), 15, cal)
check("publicacao pula p/ 21/01/2027", pub, date(2027, 1, 21))
check("inicio = 22/01/2027", ini, date(2027, 1, 22))

print("\n=== 8. Feriado local desloca o vencimento ===")
cal_loc = Calendario([(date(2026, 7, 16), "*", "feriado teste")])
_, _, venc_loc = calcular_prazo(date(2026, 7, 10), 15, cal_loc)
check("com 1 feriado local, vence 1 dia util depois (04/08)", venc_loc, date(2026, 8, 4))

print("\n=== 9. uteis_entre ===")
check("14/07 -> 03/08 = 14 dias uteis apos o inicio",
      cal.uteis_entre(date(2026, 7, 14), date(2026, 8, 3)), 14)
check("data passada devolve negativo",
      cal.uteis_entre(date(2026, 7, 20), date(2026, 7, 17)), -1)
check("mesmo dia = 0", cal.uteis_entre(date(2026, 7, 14), date(2026, 7, 14)), 0)

print("\n=== 10. Deteccao de prazo no texto ===")
check("'no prazo de 15 (quinze) dias'",
      detectar_prazo("Fica intimado para, no prazo de 15 (quinze) dias, manifestar-se."), 15)
check("'prazo de 5 dias uteis'",
      detectar_prazo("Apresente os documentos no prazo de 5 dias uteis."), 5)
check("'prazo legal de 8 (oito) dias'",
      detectar_prazo("Contrarrazoes no prazo legal de 8 (oito) dias."), 8)
check("'prazo comum de 15 dias'",
      detectar_prazo("Manifestem-se as partes no prazo comum de 15 dias."), 15)
check("texto sem prazo devolve None",
      detectar_prazo("Processo distribuido para a 4a Turma."), None)
check("numero absurdo (999 dias) e ignorado",
      detectar_prazo("prazo de 999 dias"), None)

print("\n=== 11. Agrupamento das comunicacoes do mesmo ato ===")
from monitor_prazos import processar

def com(proc, data, texto, tipo="Intimação", link="", parte="FULANO"):
    return {
        "numeroprocessocommascara": proc, "data_disponibilizacao": data,
        "tipoComunicacao": tipo, "texto": texto, "link": link,
        "siglaTribunal": "TRT8", "nomeOrgao": "1a Vara", "nomeClasse": "ACAO",
        "destinatarios": [{"nome": parte}], "destinatarioadvogados": [],
    }

hoje_t = date(2026, 7, 14)
# mesmo ato, dois destinatarios: textos diferentes, links diferentes
itens = [
    com("0001", "2026-07-10", "Intime-se no prazo de 15 dias. Destinatario: AUTOR",
        link="http://autos/1", parte="AUTOR"),
    com("0001", "2026-07-10", "Intime-se no prazo de 15 dias. Destinatario: REU aqui",
        link="http://autos/2", parte="REU"),
]
r = processar(itens, cal, 15, hoje_t)
check("2 comunicacoes do mesmo ato viram 1 linha", len(r), 1)
check("a linha registra 2 ocorrencias", r[0]["ocorrencias"], 2)
check("guarda os dois links", sorted(r[0]["links"]), ["http://autos/1", "http://autos/2"])
check("guarda as duas partes", sorted(r[0]["partes"]), ["AUTOR", "REU"])
check("mantem o texto mais completo", "REU aqui" in r[0]["texto"], True)

# datas diferentes = prazos diferentes, NAO agrupa
itens = [
    com("0002", "2026-07-03", "prazo de 15 dias"),
    com("0002", "2026-07-10", "prazo de 15 dias"),
]
check("mesmo processo em datas diferentes = 2 linhas",
      len(processar(itens, cal, 15, hoje_t)), 2)

# prazos diferentes no mesmo dia = NAO agrupa
itens = [
    com("0003", "2026-07-10", "prazo de 5 dias"),
    com("0003", "2026-07-10", "prazo de 15 dias"),
]
check("mesmo processo/data com prazos diferentes = 2 linhas",
      len(processar(itens, cal, 15, hoje_t)), 2)

# informativas vao para o fim da lista
itens = [
    com("0004", "2026-07-10", "distribuido", tipo="Lista de distribuição"),
    com("0005", "2026-07-10", "prazo de 5 dias"),
]
r = processar(itens, cal, 15, hoje_t)
check("informativa fica por ultimo", r[-1]["informativo"], True)
check("acionavel vem primeiro", r[0]["informativo"], False)

print("\n=== 12. Feriado estadual so vale no seu estado ===")
# 28/07 e feriado no MA e dia util no PA. O mesmo calendario tem que dar
# respostas diferentes conforme o tribunal do processo.
cal_uf = Calendario([
    (date(2026, 7, 28), "TJMA", "Adesao do Maranhao"),
    (date(2026, 8, 15), "TJPA", "Adesao do Para"),
    (date(2026, 3, 2), "*", "suspensao geral"),
])
check("28/07/2026 NAO eh util no TJMA", cal_uf.eh_util(date(2026, 7, 28), "TJMA"), False)
check("28/07/2026 EH util no TJPA", cal_uf.eh_util(date(2026, 7, 28), "TJPA"), True)
check("15/08/2026 eh sabado (nao util em qualquer lugar)",
      cal_uf.eh_util(date(2026, 8, 15), "TJMA"), False)
check("feriado com escopo * vale no TJMA", cal_uf.eh_util(date(2026, 3, 2), "TJMA"), False)
check("feriado com escopo * vale no TJPA", cal_uf.eh_util(date(2026, 3, 2), "TJPA"), False)
check("sem tribunal, feriado estadual nao se aplica",
      cal_uf.eh_util(date(2026, 7, 28), None), True)

print("\n=== 12b. O escopo muda o vencimento (caso real 39261/PA) ===")
# Disponibilizado 06/07/2026 em ambos, prazo 15 dias uteis.
# Sem feriado: os dois venceriam em 28/07. Com o feriado do MA, so o TJMA anda.
_, _, v_pa = calcular_prazo(date(2026, 7, 6), 15, cal_uf, "TJPA")
_, _, v_ma = calcular_prazo(date(2026, 7, 6), 15, cal_uf, "TJMA")
check("TJPA vence 28/07/2026", v_pa, date(2026, 7, 28))
check("TJMA pula o feriado e vence 29/07/2026", v_ma, date(2026, 7, 29))
check("as duas datas sao mesmo diferentes", v_pa != v_ma, True)

print("\n=== 13. Parser do feriados_locais.txt ===")
import tempfile
from monitor_prazos import ler_feriados_locais

with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False,
                                 encoding="utf-8") as fh:
    fh.write(
        "# comentario\n"
        "\n"
        "2026-07-28  TJMA  Adesao do Maranhao\n"
        "2026-08-15  TJPA  Adesao do Para\n"
        "2026-03-02  *  Suspensao geral\n"
        "2026-04-10  Sem escopo vale pra todos\n"
        "linha-invalida-aqui\n"
        "2026-05-01\n"
    )
    tmp = Path(fh.name)

lidos = ler_feriados_locais(tmp)
por_data = {d: (esc, desc) for d, esc, desc in lidos}
check("le 5 linhas validas", len(lidos), 5)
check("escopo TJMA reconhecido", por_data[date(2026, 7, 28)][0], "TJMA")
check("escopo * reconhecido", por_data[date(2026, 3, 2)][0], "*")
check("sem escopo vira *", por_data[date(2026, 4, 10)][0], "*")
check("descricao sem escopo preservada",
      por_data[date(2026, 4, 10)][1], "Sem escopo vale pra todos")
check("data solta ganha descricao padrao",
      por_data[date(2026, 5, 1)][1], "feriado local")
check("linha invalida e ignorada", date(2026, 1, 1) in por_data, False)
tmp.unlink()

print("\n=== 14. Arquivo de feriados do escritorio carrega sem erro ===")
real = Path(__file__).resolve().parent / "feriados_locais.txt"
if real.exists():
    reais = ler_feriados_locais(real)
    check("feriados_locais.txt do escritorio parseia", isinstance(reais, list), True)
    escopos = {e for _, e, _ in reais}
    check("todo feriado cadastrado tem escopo de tribunal (nenhum global solto)",
          escopos <= {"TJPA", "TJMA", "TRT8", "TRF1", "*"}, True)
    # O TRT8 concentra o maior volume (varas de Parauapebas/PA): tem que ter os
    # feriados paraenses, senao o tribunal mais movimentado fica descoberto.
    # Aqui olhamos o registro, nao eh_util(), porque 15/08 cai em fim de semana
    # em 2026 (sabado) e 2027 (domingo) - o feriado so passa a ter efeito
    # pratico em 2028. O cadastro tem que estar certo mesmo assim.
    cal_real = Calendario(reais)
    for ano in (2026, 2027):
        check(f"15/08/{ano} registrado como feriado no TRT8",
              date(ano, 8, 15) in cal_real.feriados(ano, "TRT8"), True)
        check(f"15/08/{ano} registrado como feriado no TJPA",
              date(ano, 8, 15) in cal_real.feriados(ano, "TJPA"), True)
        check(f"15/08/{ano} NAO registrado no TJMA (feriado paraense)",
              date(ano, 8, 15) in cal_real.feriados(ano, "TJMA"), False)
        check(f"28/07/{ano} registrado como feriado no TJMA",
              date(ano, 7, 28) in cal_real.feriados(ano, "TJMA"), True)
        check(f"28/07/{ano} NAO registrado no TRT8 (feriado maranhense)",
              date(ano, 7, 28) in cal_real.feriados(ano, "TRT8"), False)
    # efeito pratico, onde a data cai em dia de semana
    check("28/07/2027 nao eh util no TJMA", cal_real.eh_util(date(2027, 7, 28), "TJMA"), False)
    check("28/07/2027 EH util no TRT8", cal_real.eh_util(date(2027, 7, 28), "TRT8"), True)
    check("15/08/2026 cai em fim de semana de todo jeito",
          date(2026, 8, 15).weekday() >= 5, True)
    print(f"        -> {len(reais)} feriado(s) cadastrado(s): "
          + ", ".join(f"{d.strftime('%d/%m/%y')}/{e}" for d, e, _ in sorted(reais)))

print("\n=== 15. Janela de busca calculada ===")
# O bug original: janela fixa de 15 dias escondia um prazo que vencia HOJE,
# porque o filtro do DJEN e por disponibilizacao e o prazo vive ~23 dias
# corridos. A janela tem que sair da conta, nao do chute.
from monitor_prazos import janela_necessaria, JANELA_PISO, PRAZO_REFERENCIA

j = janela_necessaria(date(2026, 7, 14), cal)
check("janela em julho respeita o piso", j >= JANELA_PISO, True)
check("janela em julho cobre o prazo real de 22 dias que escapou", j >= 22, True)

# Em janeiro o recesso (20/12-20/01) estica muito a vida do prazo:
# a janela tem que crescer sozinha.
j_jan = janela_necessaria(date(2027, 1, 25), cal)
j_jul = janela_necessaria(date(2026, 7, 14), cal)
check("janela pos-recesso e maior que a de julho", j_jan > j_jul, True)
print(f"        -> julho: {j_jul} dias | pos-recesso (25/01): {j_jan} dias")

# A garantia que importa: nenhum prazo vivo pode cair fora da janela.
def escapa_algum(hoje, dias_uteis):
    """Existe disponibilizacao dentro da vida do prazo que a janela nao pega?"""
    jan = janela_necessaria(hoje, cal, dias_uteis)
    limite = hoje - timedelta(days=jan)
    d = hoje
    for _ in range(JANELA_TETO_TESTE := 220):
        _, _, venc = calcular_prazo(d, dias_uteis, cal)
        if venc >= hoje and d < limite:
            return d  # prazo vivo fora da janela = furo
        d -= timedelta(days=1)
    return None

for hoje_t in (date(2026, 7, 14), date(2026, 3, 2), date(2027, 1, 25),
               date(2026, 12, 18), date(2026, 9, 8), date(2027, 2, 12)):
    furo = escapa_algum(hoje_t, PRAZO_REFERENCIA)
    check(f"nenhum prazo vivo escapa da janela em {hoje_t.strftime('%d/%m/%Y')}",
          furo, None)

# O caso concreto que motivou tudo isto
j = janela_necessaria(date(2026, 7, 14), cal)
disp_fazenda = date(2026, 6, 22)  # vencia 14/07, sumia na janela de 15 dias
check("a janela calculada alcanca a intimacao da Fazenda (22/06)",
      date(2026, 7, 14) - timedelta(days=j) <= disp_fazenda, True)

print("\n=== 16. Vivos e vencidos sao separados ===")
itens = [
    com("0010", "2026-05-04", "prazo de 5 dias"),    # ja vencido
    com("0011", "2026-07-10", "prazo de 15 dias"),   # vivo
]
r = processar(itens, cal, 15, date(2026, 7, 14))
vivos_t = [l for l in r if l["nivel"] > 0]
vencidos_t = [l for l in r if l["nivel"] == 0]
check("1 vivo", len(vivos_t), 1)
check("1 vencido", len(vencidos_t), 1)
check("o vivo e o de julho", vivos_t[0]["processo"], "0011")

html_t = gerar_html_teste = __import__("monitor_prazos").gerar_html(
    r, date(2026, 7, 14), "39261", "PA", date(2026, 5, 1), date(2026, 7, 14))
check("o vencido nao vira card de destaque", html_t.count('class="card"'), 1)
check("mas aparece na secao de conferencia", "Já vencidos" in html_t, True)

# vencido COM sancao grave e a excecao: tem que virar card, no topo
itens_g = [
    com("0012", "2026-05-04",
        "Intime-se o agravante para recolher o preparo no prazo de 5 dias, "
        "sob pena de deserção."),
]
rg = processar(itens_g, cal, 15, date(2026, 7, 14))
check("vencido grave e rotulado", rg[0]["rotulo"], "VENCIDO GRAVE")
check("vencido grave vai para o topo da ordem", prioridade_teste := rg[0]["nivel"], 0)
html_g = __import__("monitor_prazos").gerar_html(
    rg, date(2026, 7, 14), "39261", "PA", date(2026, 5, 1), date(2026, 7, 14))
check("vencido grave VIRA card (nao fica enterrado)",
      html_g.count('class="card"'), 1)
check("e ganha o bloco de destaque", "ainda pode haver o que fazer" in html_g, True)

print("\n=== 17. resolvidos.txt: rebaixa, mas nao some ===")
from monitor_prazos import ler_resolvidos, ARQ_RESOLVIDOS
import tempfile as _tf

GRAVE = ("Intime-se o agravante para recolher o preparo no prazo de 5 dias, "
         "sob pena de deserção.")
itens_r = [com("0807884-75.2026.8.14.0000", "2026-06-19", GRAVE)]

# sem marcar: grita no topo
r = processar(itens_r, cal, 15, date(2026, 7, 14))
check("sem marcar, e VENCIDO GRAVE", r[0]["rotulo"], "VENCIDO GRAVE")
check("sem marcar, nao esta resolvido", r[0]["resolvido"], None)

# marcando
marcados = {("08078847520268140000", "2026-06-19"): "preparo resolvido"}
r = processar(itens_r, cal, 15, date(2026, 7, 14), marcados)
check("marcado carrega a nota", r[0]["resolvido"], "preparo resolvido")
check("marcado continua sendo VENCIDO GRAVE (o fato nao muda)",
      r[0]["rotulo"], "VENCIDO GRAVE")
check("mas sai do topo da ordem", prioridade(r[0])[0], 10)

html_r = __import__("monitor_prazos").gerar_html(
    r, date(2026, 7, 14), "39261", "PA", date(2026, 5, 1), date(2026, 7, 14))
check("resolvido NAO vira card de alarme", html_r.count('class="card"'), 0)
check("mas continua visivel no relatorio", "0807884-75.2026.8.14.0000" in html_r, True)
check("com a nota do advogado", "preparo resolvido" in html_r, True)
check("sem o bloco de panico", "ainda pode haver o que fazer" in html_r, False)

print("\n=== 17b. Parser do resolvidos.txt ===")
with _tf.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as fh:
    fh.write(
        "# comentario\n"
        "0807884-75.2026.8.14.0000  2026-06-19  # preparo ok\n"
        "08086370920268140040  2026-07-06\n"
        "0809362-95.2026.8.14.0040  data-ruim  # invalida\n"
        "so-o-numero\n"
    )
    tmp_r = Path(fh.name)
lidos = ler_resolvidos(tmp_r)
check("le 2 linhas validas", len(lidos), 2)
check("normaliza o numero com mascara",
      ("08078847520268140000", "2026-06-19") in lidos, True)
check("aceita numero sem mascara",
      ("08086370920268140040", "2026-07-06") in lidos, True)
check("guarda a nota", lidos[("08078847520268140000", "2026-06-19")], "preparo ok")
check("sem nota ganha texto padrao",
      lidos[("08086370920268140040", "2026-07-06")], "marcado como resolvido")
tmp_r.unlink()

print("\n=== 17c. O arquivo real do escritorio ===")
if ARQ_RESOLVIDOS.exists():
    reais_r = ler_resolvidos(ARQ_RESOLVIDOS)
    check("resolvidos.txt do escritorio parseia", isinstance(reais_r, dict), True)
    check("o agravo esta marcado como resolvido",
          ("08078847520268140000", "2026-06-19") in reais_r, True)
    print(f"        -> {len(reais_r)} marcado(s)")

print("\n" + "=" * 60)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Todos os casos passaram.")
print("=" * 60)
