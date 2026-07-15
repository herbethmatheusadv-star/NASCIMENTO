# -*- coding: utf-8 -*-
"""
Testa o classificador contra trechos REAIS das intimacoes da OAB 39261/PA.

Os dois casos que motivaram este modulo:
  - o agravo com preparo sob pena de desercao (era grave, foi enterrado)
  - as contrarrazoes do Municipio (nao era dele, virou "VENCE HOJE")
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from classificador import (DA_OUTRA_PARTE, INCERTO, MEU, analisar,
                           de_quem_e_o_prazo, gravidade, providencias,
                           sancoes, tipo_de_ato, trechos_de_ordem)

falhas = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado}")
        print(f"          obtido  : {obtido}")
        falhas.append(nome)

A = [{"nome": "KATIA APARECIDA MENDES VIANA", "polo": "A"}]
P = [{"nome": "PERFIL COMERCIO E ENGENHARIA LTDA", "polo": "P"}]
AMBOS = [{"nome": "BANCO SANTANDER", "polo": "P"},
         {"nome": "DANIEL AUGUSTO", "polo": "A"}]
SEM_POLO = [{"nome": "FULANO"}]

# ---------------------------------------------------------------- textos reais
AGRAVO = (
    "Ante o exposto, INDEFIRO o pedido de concessão da gratuidade da justiça. "
    "Intime-se o agravante para, no prazo de 05 (cinco) dias, efetuar o "
    "recolhimento do preparo recursal, comprovando-o nos autos, sob pena de "
    "não conhecimento do recurso por deserção, nos termos dos arts. 99, § 7º, "
    "e 1.007 do Código de Processo Civil. Cumpra-se."
)
CONTRARRAZOES_MUNICIPIO = (
    "ATO ORDINATÓRIO - 19 de junho de 2026. Nos termos do provimento n.º "
    "006/2006-CJRM c/c Portaria 054/2008-GJ, fica a parte requerida INTIMADA "
    "para apresentar contrarrazões ao recurso de apelação interposto pelo "
    "autor. Prazo da Lei."
)
CUSTAS_AUTOR = (
    "DECISÃO Da análise dos autos, DETERMINO: 1- CERTIFIQUE-SE quanto a "
    "oposição de embargos à execução. INTIME-SE o autor para EFETUAR o "
    "pagamento/recolhimento das custas processuais pendentes. CUMPRA-SE e "
    "EXPEÇA-SE o necessário."
)
DECISAO_AGUAS = (
    "DECISÃO Trata-se de ação declaratória de inexigibilidade de débito "
    "cumulada com repetição de indébito e indenização por danos morais. "
    "Intime-se a parte autora para se manifestar, no prazo de 15 dias."
)
SENTENCA = (
    "SENTENÇA Trata-se de ação de cobrança ajuizada por COOPERATIVA. "
    "Ante o exposto, JULGO PROCEDENTE o pedido. Publique-se. Cumpra-se."
)
TERMO_AUDIENCIA = (
    "TERMO DE AUDIÊNCIA DE CONCILIAÇÃO. Conciliador: Carlos. "
    "CONCILIAÇÃO (X) SEM ACORDO: a tentativa de conciliação foi infrutífera. "
    "O autor manifesta que não tem interesse na produção de outras provas e "
    "requer o julgamento antecipado da lide."
)
SIGILOSO = "Processo sigiloso. Para visualização do documento consulte os autos digitais"
DISTRIBUICAO = ("Processo 0000987-62.2024.5.08.0126 distribuído para 4ª Turma "
                "na data 08/07/2026")
REVELIA = ("Cite-se o réu para, no prazo de 15 dias, apresentar contestação, "
           "sob pena de revelia e confissão quanto à matéria de fato.")

print("\n=== 1. Tipo do ato ===")
check("agravo -> decisao", tipo_de_ato(AGRAVO), "decisao")
check("ato ordinatorio", tipo_de_ato(CONTRARRAZOES_MUNICIPIO), "ato_ordinatorio")
check("sentenca", tipo_de_ato(SENTENCA), "sentenca")
check("termo de audiencia", tipo_de_ato(TERMO_AUDIENCIA), "audiencia")
check("sigiloso", tipo_de_ato(SIGILOSO), "sigiloso")
check("distribuicao", tipo_de_ato(DISTRIBUICAO), "distribuicao")

print("\n=== 2. Providencia exigida ===")
check("agravo pede preparo", "preparo" in providencias(AGRAVO), True)
check("ato ordinatorio pede contrarrazoes",
      "contrarrazoes" in providencias(CONTRARRAZOES_MUNICIPIO), True)
check("decisao pede custas", "custas" in providencias(CUSTAS_AUTOR), True)
check("citacao pede contestacao", "contestacao" in providencias(REVELIA), True)
check("generico 'manifestar' so aparece se nao houver especifica",
      providencias(DECISAO_AGUAS), ["manifestacao"])

print("\n=== 3. Gravidade (sob pena de) ===")
check("desercao = peso 3", gravidade(AGRAVO), 3)
check("revelia = peso 3", gravidade(REVELIA), 3)
check("sem sancao = 0", gravidade(TERMO_AUDIENCIA), 0)
check("sancao principal do agravo", analisar(AGRAVO, A)["sancao_principal"], "deserção")

print("\n=== 4. O PRAZO E MEU?  (o caso que gerou falso positivo) ===")
v, motivo = de_quem_e_o_prazo(CONTRARRAZOES_MUNICIPIO, A)
check("contrarrazoes: intima o REU, cliente e AUTOR -> nao e dele",
      v, DA_OUTRA_PARTE)
print(f"        motivo: {motivo}")

v, motivo = de_quem_e_o_prazo(CUSTAS_AUTOR, P)
check("custas: intima o AUTOR, cliente e REU -> nao e dele", v, DA_OUTRA_PARTE)
print(f"        motivo: {motivo}")

v, motivo = de_quem_e_o_prazo(DECISAO_AGUAS, A)
check("intima a AUTORA e o cliente e AUTOR -> e dele", v, MEU)
print(f"        motivo: {motivo}")

v, _ = de_quem_e_o_prazo(CONTRARRAZOES_MUNICIPIO, P)
check("mesmas contrarrazoes, mas cliente REU -> e dele", v, MEU)

print("\n=== 5. Na duvida, MOSTRAR (nunca esconder) ===")
v, motivo = de_quem_e_o_prazo(TERMO_AUDIENCIA, AMBOS)
check("duas partes na comunicacao -> INCERTO, nao 'nao e seu'", v, INCERTO)
print(f"        motivo: {motivo}")

v, motivo = de_quem_e_o_prazo(DECISAO_AGUAS, SEM_POLO)
check("sem polo informado -> INCERTO", v, INCERTO)

v, motivo = de_quem_e_o_prazo(SENTENCA, A)
check("texto nao diz quem age -> INCERTO", v, INCERTO)
print(f"        motivo: {motivo}")

v, _ = de_quem_e_o_prazo(SIGILOSO, A)
check("sigiloso -> INCERTO (nao da para ler o teor)", v, INCERTO)

print("\n=== 6. O agravo, de ponta a ponta ===")
r = analisar(AGRAVO, [{"nome": "CARLOS EDUARDO", "polo": "A"}])
check("e do cliente dele", r["de_quem"], MEU)
check("classificado como decisao", r["ato"], "decisao")
check("providencia: preparo", "preparo" in r["providencias"], True)
check("gravidade maxima", r["gravidade"], 3)
check("sancao nomeada", r["sancao_principal"], "deserção")
print(f"        -> {r['ato_rotulo']} | {', '.join(r['providencias_rotulo'])} "
      f"| sob pena de {r['sancao_principal']} | {r['de_quem']}")

print("\n=== 7. Narrativa NAO vira ordem (o ruido do acordao) ===")
# Este e o texto real do agravo: 10 mil chars em que o relatorio CITA
# contrarrazoes, embargos, custas e apelacao ao contar o historico. Nenhum
# deles e ordem. So o preparo e.
ACORDAO_LONGO = (
    "AGRAVO DE INSTRUMENTO. GRATUIDADE DA JUSTIÇA. IMPUGNAÇÃO PELA PARTE "
    "AGRAVADA. A SICOOB apresentou contrarrazões, sustentando, preliminarmente, "
    "o não conhecimento do recurso por deserção, uma vez que o agravante não "
    "recolheu o preparo recursal no ato da interposição. A cooperativa destaca "
    "que os embargos à execução anteriormente opostos pelo agravante tiveram a "
    "distribuição cancelada justamente pela ausência de recolhimento das custas "
    "processuais. Apresentou tempestivamente embargos à execução. Argumenta que "
    "a decisão é nula. Requer a concessão da justiça gratuita e a atribuição de "
    "efeito suspensivo ao recurso. É O RELATÓRIO. "
    "Ante o exposto, INDEFIRO o pedido de concessão da gratuidade da justiça. "
    "Intime-se o agravante para, no prazo de 05 (cinco) dias, efetuar o "
    "recolhimento do preparo recursal, comprovando-o nos autos, sob pena de "
    "não conhecimento do recurso por deserção. Cumpra-se."
)
p = providencias(ACORDAO_LONGO)
check("a ordem real (preparo) e detectada", "preparo" in p, True)
check("'contrarrazoes' do relatorio NAO vira ordem", "contrarrazoes" in p, False)
check("'embargos' do relatorio NAO vira ordem", "embargos" in p, False)
check("'custas' do relatorio NAO vira ordem", "custas" in p, False)
check("'recurso' do relatorio NAO vira ordem", "recurso" in p, False)
print(f"        -> providencias: {p}")
check("gravidade continua maxima", gravidade(ACORDAO_LONGO), 3)

print("\n=== 8. Sentenca que julga extinto NAO e ameaca de extincao ===")
SENT_EXTINTA = (
    "SENTENÇA. Ante o exposto, JULGO EXTINTO o processo sem resolução do "
    "mérito, nos termos do art. 485, VI, do CPC. Sem custas. "
    "Publique-se. Registre-se. Intimem-se."
)
check("nao inventa sancao de extincao", gravidade(SENT_EXTINTA), 0)
check("sem providencia inventada", providencias(SENT_EXTINTA), [])

SENT_PROCEDENTE = (
    "SENTENÇA Trata-se de ação de cobrança. A requerida suscitou nulidade da "
    "citação e apresentou contestação. Ante o exposto, JULGO PROCEDENTE o "
    "pedido para condenar a ré ao pagamento. Publique-se."
)
check("sentenca procedente: sem sancao", gravidade(SENT_PROCEDENTE), 0)
check("'contestacao' narrada nao vira ordem",
      "contestacao" in providencias(SENT_PROCEDENTE), False)

print("\n=== 9. 'sob pena de' continua pegando as ameacas de verdade ===")
casos = [
    ("sob pena de deserção", "sob pena de deserção", 3, "deserção"),
    ("sob pena de revelia", "cite-se o réu, sob pena de revelia", 3, "revelia"),
    ("sob pena de extinção", "emende a inicial, sob pena de extinção do feito", 3, "extinção"),
    ("sob pena de arquivamento", "manifeste-se, sob pena de arquivamento", 3, "arquivamento"),
    ("sob pena de preclusão", "especifique provas, sob pena de preclusão", 3, "preclusão"),
    ("sob pena de multa", "cumpra, sob pena de multa diária", 2, "multa"),
    ("julgado deserto (sem a formula)", "o recurso será julgado deserto", 3, "deserção"),
]
for nome, txt, peso, rotulo in casos:
    s = sancoes(txt)
    check(f"{nome} -> peso {peso}", (s[0] if s else None), (peso, rotulo))

print("\n=== 10. Termo de audiencia nao vira ordem falsa ===")
check("termo sem comando: sem providencia", providencias(TERMO_AUDIENCIA), [])
check("termo sem comando: sem sancao", gravidade(TERMO_AUDIENCIA), 0)

print("\n" + "=" * 62)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Todos os casos passaram.")
print("=" * 62)
