#!/usr/bin/env python3
"""
teste_regras.py — o teste que QUEBRA O BUILD se o robo ganhar poder de agir.

Rode antes de qualquer login. Se falhar, NAO EXISTE conector: o pacote esta com
uma capacidade que o titular proibiu em 15/07/2026.

    python CONECTOR/teste_regras.py     # exit 0 = pode logar; exit 1 = nao pode
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import regras
from regras import (CONDUTA, OPERACOES_MNI_PERMITIDAS, Processo, Quarentena,
                    ViolacaoR7, Watchdog, guarda_de_clique, guarda_de_operacao_mni,
                    guarda_de_url)

FALHAS: list[str] = []
PASSOU = 0

# Arquivos que PRECISAM nomear o proibido para poder proibi-lo.
ISENTOS = {"regras.py", "teste_regras.py"}


def check(nome: str, obtido, esperado) -> None:
    global PASSOU
    if obtido == esperado:
        PASSOU += 1
        print(f"  [ok ] {nome}")
    else:
        FALHAS.append(nome)
        print(f"  [FALHA] {nome}\n         esperado {esperado!r}, veio {obtido!r}")


def check_levanta(nome: str, fn, *args) -> None:
    global PASSOU
    try:
        fn(*args)
    except ViolacaoR7:
        PASSOU += 1
        print(f"  [ok ] {nome}")
        return
    FALHAS.append(nome)
    print(f"  [FALHA] {nome} — NAO levantou ViolacaoR7. O robo pode agir!")


print("=" * 74)
print("  R7 — teste de AUSENCIA de poder de agir")
print("=" * 74)

print("\n=== 1. O fonte do CONECTOR nao contem capacidade de agir ===")
# Esta e a assercao central. Nao testa comportamento: testa que o CODIGO nao
# sabe assinar, peticionar nem tomar ciencia. Ausencia, nao bloqueio.
pacote = Path(__file__).parent
arquivos = [p for p in pacote.glob("*.py") if p.name not in ISENTOS]
print(f"  varrendo {len(arquivos)} arquivo(s): "
      f"{', '.join(p.name for p in arquivos) or '(nenhum ainda)'}")

achados: list[str] = []
for arq in arquivos:
    fonte = arq.read_text(encoding="utf-8", errors="ignore")
    # comentario e docstring podem citar o proibido para explicar a proibicao;
    # o que nao pode e CODIGO. Removemos comentarios de linha antes de varrer.
    codigo = "\n".join(l.split("#")[0] for l in fonte.splitlines())
    for padrao in regras.VOCABULARIO_PROIBIDO:
        for m in re.finditer(padrao, codigo, re.IGNORECASE):
            linha = codigo[:m.start()].count("\n") + 1
            achados.append(f"{arq.name}:{linha} -> {m.group(0)!r} "
                           f"(padrao {padrao!r})")

check("nenhuma capacidade proibida no fonte do pacote", achados, [])
if achados:
    print("\n  *** O BUILD ESTA QUEBRADO. Encontrado no codigo: ***")
    for a in achados:
        print(f"      {a}")
    print("  R7 e ausencia, nao bloqueio. Remova a capacidade — nao a esconda"
          "\n  atras de um if.\n")

print("\n=== 2. Allowlist do MNI ===")
check("consultarAvisosPendentes e permitida",
      "consultarAvisosPendentes" in OPERACOES_MNI_PERMITIDAS, True)
check("consultarProcesso e permitida",
      "consultarProcesso" in OPERACOES_MNI_PERMITIDAS, True)
check("consultarAlteracao e permitida",
      "consultarAlteracao" in OPERACOES_MNI_PERMITIDAS, True)
check("allowlist tem EXATAMENTE 3 operacoes (nada entrou de carona)",
      len(OPERACOES_MNI_PERMITIDAS), 3)
# as duas que tomam ciencia e peticionam nao podem estar la, nunca
for proibida in ("confirmar" + "Recebimento",
                 "entregar" + "ManifestacaoProcessual"):
    check(f"{proibida} NAO esta na allowlist",
          proibida in OPERACOES_MNI_PERMITIDAS, False)
    check_levanta(f"chamar {proibida} levanta ViolacaoR7",
                  guarda_de_operacao_mni, proibida)
check_levanta("consultarTeorComunicacao (em estudo) e barrada",
              guarda_de_operacao_mni, "consultarTeorComunicacao")
check_levanta("operacao inventada e barrada",
              guarda_de_operacao_mni, "assinarDocumento")

print("\n=== 3. Guarda de clique (o botao ao lado do link) ===")
for rotulo in ["Tomar Ciência", "TOMAR CIENCIA", "tomar ciência do expediente",
               "Responder", "Peticionar", "Protocolar", "Assinar",
               "Enviar", "Confirmar Recebimento", "Declarar ciência",
               "Manifestar-se nos autos", "Juntar documento"]:
    check_levanta(f"recusa clicar em {rotulo!r}", guarda_de_clique, rotulo)

# leitura continua possivel — a guarda nao pode travar o trabalho legitimo
for rotulo in ["Abrir processo", "Ver detalhes", "Consultar", "Download",
               "Baixar documento", "Próxima página", "Acervo"]:
    guarda_de_clique(rotulo)   # nao pode levantar
    PASSOU += 1
    print(f"  [ok ] permite clicar em {rotulo!r} (leitura)")

print("\n=== 4. Guarda de URL ===")
for url in ["https://pje.tjpa.jus.br/pje/Peticionamento/listView.seam",
            "https://pje.tjpa.jus.br/pje/expediente/responder?id=1",
            "https://pje.tjpa.jus.br/pje/tomarCiencia?id=9",
            "https://pje.tjpa.jus.br/pje/assinatura/assinar"]:
    check_levanta(f"recusa navegar para {url[-38:]!r}", guarda_de_url, url)

# URLs REAIS do painel TJPA, colhidas na sessao de mapeamento de 16/07/2026.
# Elas provaram que os padroes CHUTADOS nao pegavam a realidade: "peticion"
# nao casa com "peticaoavulsa" (petiCAO != petiCION) e "assinatur" nao casa
# com "naoAssinado". As tres passavam batido. Este bloco existe para que nunca
# mais passem — teste vem do dado real, nao da adivinhacao.
for rot, url in [
    ("Peticionar (peticao avulsa)",
     "https://pje.tjpa.jus.br/pje/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam"),
    ("Assinar documentos (nao assinado)",
     "https://pje.tjpa.jus.br/pje/Painel/advogado/consultaDocnaoAssinado.seam"),
    ("Novo processo (cadastrar/ajuizar)",
     "https://pje.tjpa.jus.br/pje/Processo/cadastrar.seam?newInstance=true"),
    ("Solicitar habilitacao (peticao avulsa)",
     "https://pje.tjpa.jus.br/pje/Processo/CadastroPeticaoAvulsa/listView.seam"),
]:
    check_levanta(f"[REAL] recusa navegar para {rot}", guarda_de_url, url)

# As de LEITURA, tambem reais, NAO podem ser bloqueadas — a guarda protege,
# nao atrapalha o trabalho legitimo.
for rot, url in [
    ("Consulta de processo",
     "https://pje.tjpa.jus.br/pje/Processo/ConsultaProcesso/listView.seam"),
    ("Area de download (onde cai o download integral)",
     "https://pje.tjpa.jus.br/pje/AreaDownload/listView.seam"),
    ("Pauta de audiencia",
     "https://pje.tjpa.jus.br/pje/ProcessoAudiencia/PautaAudiencia/listView.seam"),
    ("Painel do advogado",
     "https://pje.tjpa.jus.br/pje/Painel/painel_usuario/advogado.seam"),
]:
    guarda_de_url(url)   # nao pode levantar
    PASSOU += 1
    print(f"  [ok ] [REAL] permite leitura: {rot}")

print("\n=== 5. Quarentena: ciencia pendente = nao toca (nem os autos) ===")
q = Quarentena()
pend = Processo("0808637-09.2026.8.14.0040", ciencia_pendente=True,
                origem="painel TJPA/expedientes")
livre = Processo("0817105-93.2025.8.14.0040", ciencia_pendente=False,
                 origem="painel TJPA/acervo")
check("processo com ciencia pendente e quarentenado", q.avaliar(pend), True)
check("processo sem ciencia pendente segue o fluxo", q.avaliar(livre), False)
check("quarentena guardou so o pendente", [p.numero for p in q.itens],
      ["0808637-09.2026.8.14.0040"])
check("quarentena vira linha vermelha no briefing",
      len(q.para_briefing()), 1)
check("a linha do briefing diz que os autos tambem nao foram baixados",
      "nem os autos" in q.para_briefing()[0], True)

print("\n=== 6. Watchdog: silencio nao e 'tudo bem' ===")
w = Watchdog()
w.registrar_execucao("TJPA/expedientes", itens=0)
w.registrar_execucao("TJPA/acervo", itens=19, esperado_minimo=15)
w.registrar_execucao("TJMA/expedientes", itens=0, erro="timeout apos 3 tentativas")
w.registrar_execucao("TRT8/acervo", itens=2, esperado_minimo=5)
al = w.alertas()
check("fonte que nao rodou vira alerta vermelho",
      any("NAO RODOU" in a for a in al), True)
check("fonte que voltou vazia vira alerta vermelho",
      any("VAZIA" in a for a in al), True)
check("fonte abaixo do minimo esperado vira alerta amarelo",
      any("abaixo do minimo" in a for a in al), True)
check("fonte saudavel nao gera alerta", len(al), 3)

print("\n=== 7. Conduta declarada ===")
check("modo e somente leitura", CONDUTA["modo"], "SOMENTE LEITURA")
check("perfil do navegador e EFEMERO", CONDUTA["perfil_navegador"], "EFEMERO")
check("execucao e sequencial", CONDUTA["execucao"], "sequencial")
check("so processos proprios", CONDUTA["somente_processos_proprios"], True)
check("credencial nunca e salva",
      "nunca salva" in CONDUTA["credencial"], True)

print("\n" + "=" * 74)
if FALHAS:
    print(f"  {len(FALHAS)} FALHA(S) — R7 VIOLADA. NAO LOGAR NO PJe.")
    for f in FALHAS:
        print(f"    - {f}")
    print("=" * 74)
    sys.exit(1)
print(f"  {PASSOU} casos OK — R7 integra. O conector so sabe ler.")
print("=" * 74)
