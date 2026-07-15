# -*- coding: utf-8 -*-
"""
Valida o comportamento do script quando o DJEN falha.

O DJEN devolve HTTP 500 de forma intermitente (observado em 2 de 3 consultas
identicas). Estes testes simulam a falha em vez de esperar ela acontecer.
"""
import sys
import urllib.error
from datetime import date
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import monitor_prazos as mp

falhas_teste = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado}")
        print(f"          obtido  : {obtido}")
        falhas_teste.append(nome)

mp.time.sleep = lambda s: None  # nao esperar de verdade nos testes


class RespostaFake:
    def __init__(self, payload):
        self._b = BytesIO(payload.encode("utf-8"))
    def read(self):
        return self._b.read()
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def erro(code):
    return urllib.error.HTTPError("http://x", code, "Erro", {}, None)


VAZIO = '{"status":"success","count":0,"items":[]}'
UM = ('{"status":"success","count":1,"items":[{"id":1,'
      '"data_disponibilizacao":"2026-07-06","siglaTribunal":"TJPA",'
      '"tipoComunicacao":"Intimação","texto":"prazo de 15 dias",'
      '"numeroprocessocommascara":"0001","nomeOrgao":"Vara","nomeClasse":"ACAO",'
      '"link":"http://a","destinatarios":[],"destinatarioadvogados":[]}]}')


def com_respostas(seq):
    """Instala um urlopen falso que devolve/levanta cada item de `seq`."""
    it = iter(seq)
    def fake(req, timeout=None):
        r = next(it)
        if isinstance(r, Exception):
            raise r
        return RespostaFake(r)
    mp.urllib.request.urlopen = fake


print("\n=== 1. Retry: 500 duas vezes e depois responde ===")
com_respostas([erro(500), erro(500), UM])
itens = mp._consultar_bloco("39261", "PA", date(2026, 7, 1), date(2026, 7, 14), 10)
check("insiste e devolve o item", len(itens), 1)

print("\n=== 2. Retry: 500 sempre -> FalhaConsulta ===")
com_respostas([erro(500)] * 4)
try:
    mp._consultar_bloco("39261", "PA", date(2026, 7, 1), date(2026, 7, 14), 10)
    check("levanta FalhaConsulta", False, True)
except mp.FalhaConsulta as ex:
    check("levanta FalhaConsulta", True, True)
    check("mensagem cita as tentativas", "tentativas" in str(ex), True)

print("\n=== 3. Erro 4xx nao e repetido (consulta errada, insistir nao adianta) ===")
chamadas = []
def fake_400(req, timeout=None):
    chamadas.append(1)
    raise erro(400)
mp.urllib.request.urlopen = fake_400
try:
    mp._consultar_bloco("39261", "PA", date(2026, 7, 1), date(2026, 7, 14), 10)
except mp.FalhaConsulta:
    pass
check("400 tentado uma unica vez", len(chamadas), 1)

print("\n=== 4. Timeout tambem e repetido ===")
com_respostas([TimeoutError(), TimeoutError(), UM])
itens = mp._consultar_bloco("39261", "PA", date(2026, 7, 1), date(2026, 7, 14), 10)
check("timeout nao mata a consulta", len(itens), 1)

print("\n=== 5. Fatiamento da janela ===")
b = mp.fatiar(date(2026, 1, 1), date(2026, 1, 10), 45)
check("janela menor que o bloco = 1 bloco", len(b), 1)
check("bloco unico cobre a janela toda", b[0], (date(2026, 1, 1), date(2026, 1, 10)))

b = mp.fatiar(date(2026, 1, 1), date(2026, 12, 31), 45)
check("ano inteiro em blocos de 45 dias", len(b), 9)
check("primeiro bloco comeca no inicio", b[0][0], date(2026, 1, 1))
check("ultimo bloco termina no fim", b[-1][1], date(2026, 12, 31))
check("blocos nao se sobrepoem nem deixam buraco",
      all(b[i][1] + mp.timedelta(days=1) == b[i + 1][0] for i in range(len(b) - 1)), True)

b = mp.fatiar(date(2026, 3, 5), date(2026, 3, 5), 45)
check("janela de 1 dia", b, [(date(2026, 3, 5), date(2026, 3, 5))])

print("\n=== 6. Bloco que cai vira aviso, nao relatorio silenciosamente incompleto ===")
# 3 blocos: o do meio falha em todas as tentativas
com_respostas([UM] + [erro(500)] * 4 + [VAZIO])
itens, falhados = mp.consultar_djen("39261", "PA", date(2026, 1, 1), date(2026, 4, 10), 10)
check("aproveita os blocos que responderam", len(itens), 1)
check("reporta exatamente 1 periodo faltando", len(falhados), 1)
check("informa QUAL periodo faltou", falhados[0], (date(2026, 2, 15), date(2026, 3, 31)))

print("\n=== 7. Tudo respondendo = nenhuma falha reportada ===")
com_respostas([UM, VAZIO, VAZIO])
itens, falhados = mp.consultar_djen("39261", "PA", date(2026, 1, 1), date(2026, 4, 10), 10)
check("sem falhas", falhados, [])

print("\n=== 8. O aviso de incompleto aparece no HTML ===")
cal = mp.Calendario()
linhas = mp.processar([], cal, 15, date(2026, 7, 14))
html_ok = mp.gerar_html(linhas, date(2026, 7, 14), "39261", "PA",
                        date(2026, 7, 1), date(2026, 7, 14), [])
html_ruim = mp.gerar_html(linhas, date(2026, 7, 14), "39261", "PA",
                          date(2026, 7, 1), date(2026, 7, 14),
                          [(date(2026, 7, 2), date(2026, 7, 5))])
check("sem falha, nenhum alerta no HTML", "está incompleto" in html_ok, False)
check("com falha, o HTML alerta", "está incompleto" in html_ruim, True)
check("o HTML mostra o periodo que faltou", "02/07/2026 a 05/07/2026" in html_ruim, True)

print("\n" + "=" * 60)
if falhas_teste:
    print(f"  {len(falhas_teste)} FALHA(S): " + ", ".join(falhas_teste))
    sys.exit(1)
print("  Todos os casos passaram.")
print("=" * 60)
