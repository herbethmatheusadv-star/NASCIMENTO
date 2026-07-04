# -*- coding: utf-8 -*-
"""
novo_caso.py — cria a árvore de um caso novo + CASO.yaml esqueleto.
Blueprint: seções 2, 3 e 7 ("a estrutura do caso é SAÍDA do sistema").

Uso:
  python novo_caso.py NOME_DO_CLIENTE [--titulo "..."] [--area familia]
                      [--modulo familia/alimentos_guarda_convivencia]
                      [--comarca "Parauapebas/PA"] [--complexidade padrao]
                      [--segredo]
"""
import argparse
import re
import sys

import soj_lib as soj

ESQUELETO_CASO = '''\
# =====================================================================
# CASO.yaml — FONTE DA VERDADE deste caso (SOJ, blueprint secao 3).
# Modelo comentado completo: ESCRITORIO/MODELOS/CASO.schema.yaml
# Regra de ouro: informacao vive AQUI, uma unica vez. Views sao geradas.
# IDs estaveis: PT=parte, F=fato, P=prova, PED=pedido, PZ=prazo, PEN=pendencia.
# =====================================================================

caso:
  id: __ID__
  titulo: "__TITULO__"
  area: __AREA__                # familia | consumidor | bancario | ...
  modulo: __MODULO__            # ex.: familia/alimentos_guarda_convivencia
  complexidade: __COMPLEXIDADE__  # simples | padrao | complexo (D9)
  fase: E1_intake               # E1_intake | E2_estrategia | E3_minuta | E4_protocolo | ativo | encerrado
  comarca: "__COMARCA__"
  segredo_justica: __SEGREDO__  # true quando ha menores / dados sensiveis
  gates:
    G1: {status: pendente}
    G2: {status: pendente}
    G3: {status: pendente}

partes: []
# - { id: PT01, papel: autora_representante, nome: "...", cpf: "...",
#     renda_mensal: 0.00, qualificacao: completa }
# - { id: PT02, papel: reu, nome: "...",
#     endereco: { status: nao_confirmado, pendencia: PEN01 } }

fatos: []
# status: provado | alegado | controverso. Provado exige prova; sem prova,
# abrir pendencia (ou campo justificativa: "...").
# - { id: F01, descricao: "...", status: alegado, provas: [], pendencias: [PEN01] }

provas: []
# Registradas pelo receber_documento.py — nao preencher a mao sem necessidade.
# - { id: P01, doc: "01_documentos/DOC-01_....pdf", original: "00_originais/...",
#     o_que_prova: "...", forca: plena, fragilidade: null }

pedidos: []
# - { id: PED01, tipo: ..., parametro: "... — DECISAO_SISTEMA #NNN",
#     fundamentos: [CC:art1694], fatos: [F01] }

fundamentos_citados: []
# Espelho local da BASE_LEGAL (D6). validade_dias: 90 padrao / 30 alterada.
# nucleo: true => rechecagem obrigatoria na vespera do protocolo (G3).
# - { ref: "CC:art1694", verificado_em: 2026-01-01, status: vigente,
#     validade_dias: 90, nucleo: true }

prazos: []
# - { id: PZ01, descricao: "...", data: 2026-01-01, criticidade: alta }
# Caso genuinamente sem prazos: registrar NOTA "SEM PRAZOS" no DIARIO.

pendencias: []
# responsavel: cliente | advogado | terceiro; prioridade: critica|alta|media|baixa
# critica DEVE ter bloqueia: [G2] e/ou [G3]. status: aberta (padrao) | resolvida.
# mensagem_cliente: versao leiga p/ checklist WhatsApp (opcional).
# - { id: PEN01, descricao: "...", responsavel: cliente, prioridade: critica,
#     bloqueia: [G3], mensagem_cliente: "..." }
'''

CABECALHO_DIARIO = '''\
# DIÁRIO — __CLIENTE__ (caso __ID__)

Ledger append-only (blueprint, seção 4). NUNCA edite ou apague uma entrada:
correção é entrada NOVA referenciando a antiga. Formato e tipos de entrada:
ESCRITORIO/MODELOS/DIARIO.formato.md

---
'''

ESQUELETO_INTAKE = '''\
# INTAKE — __TITULO__

> Prosa do atendimento (blueprint, seções 2 e 10). Os DADOS (partes, fatos,
> provas, prazos, pendências) vivem no CASO.yaml — aqui vive a narrativa.

## 1. Resumo do atendimento

(a preencher na E1)

## 2. Cronologia narrativa

(a preencher na E1)

## 3. Contradições e lacunas

(a preencher na E1)

## 4. Perguntas complementares ao cliente

(a preencher na E1)
'''

ESQUELETO_ESTRATEGIA = '''\
# ESTRATÉGIA — __TITULO__

> Prosa da Etapa 2 (blueprint, seções 2 e 6/G2). Profundidade conforme a
> complexidade do caso (D9).

## 1. Diagnóstico

(a preencher na E2)

## 2. Estratégia

(a preencher na E2)

## 3. Simulação da defesa adversária

(a preencher na E2)

## 4. Análise do juiz rigoroso

(a preencher na E2)

## 5. Riscos e contramedidas

(a preencher na E2 — todo risco da simulação precisa de contramedida aqui ou
aceitação expressa no DIARIO)
'''


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Cria a arvore de um caso novo (SOJ).")
    ap.add_argument("nome", help="Nome do cliente = nome da pasta em CASOS/ (ex.: TANIA)")
    ap.add_argument("--titulo", default="", help='Ex.: "Tania x Cicero — Alimentos"')
    ap.add_argument("--area", default="a_definir")
    ap.add_argument("--modulo", default="a_definir")
    ap.add_argument("--comarca", default="a_definir")
    ap.add_argument("--complexidade", default="padrao",
                    choices=["simples", "padrao", "complexo"])
    ap.add_argument("--segredo", action="store_true",
                    help="Marca segredo_justica: true (menores, dados sensiveis)")
    args = ap.parse_args()

    nome = args.nome.strip()
    if not re.fullmatch(r"[A-Za-z0-9 _\-]+", nome):
        sys.exit("[ERRO] Nome da pasta deve conter apenas letras, numeros, espaco, _ ou -")

    pasta = soj.CASOS / nome
    if pasta.exists():
        sys.exit(f"[ERRO] A pasta CASOS/{nome} ja existe. Nada foi alterado.")

    caso_id = soj.proximo_id_caso()
    titulo = args.titulo or f"{nome} — (titulo a definir)"

    # 1. arvore de pastas (secao 2 do blueprint)
    for sub in ["00_originais", "01_documentos", "_views", "_efemeros"]:
        (pasta / sub).mkdir(parents=True)

    # 2. CASO.yaml esqueleto comentado
    conteudo = (ESQUELETO_CASO
                .replace("__ID__", caso_id)
                .replace("__TITULO__", titulo)
                .replace("__AREA__", args.area)
                .replace("__MODULO__", args.modulo)
                .replace("__COMARCA__", args.comarca)
                .replace("__COMPLEXIDADE__", args.complexidade)
                .replace("__SEGREDO__", "true" if args.segredo else "false"))
    (pasta / "CASO.yaml").write_text(conteudo, encoding="utf-8", newline="\n")

    # 3. DIARIO com cabecalho + entrada #001
    cab = CABECALHO_DIARIO.replace("__CLIENTE__", nome).replace("__ID__", caso_id)
    (pasta / "DIARIO.md").write_text(cab, encoding="utf-8", newline="\n")
    soj.append_diario(pasta, "NOTA",
                      f"Caso criado pelo novo_caso.py. Id: {caso_id}. "
                      f"Area: {args.area}. Modulo: {args.modulo}. "
                      f"Complexidade: {args.complexidade}. Fase: E1_intake.")

    # 4. esqueletos de prosa
    (pasta / "INTAKE.md").write_text(
        ESQUELETO_INTAKE.replace("__TITULO__", titulo), encoding="utf-8", newline="\n")
    (pasta / "ESTRATEGIA.md").write_text(
        ESQUELETO_ESTRATEGIA.replace("__TITULO__", titulo), encoding="utf-8", newline="\n")

    # 5. views iniciais + painel
    import gerar_views
    gerar_views.gerar_views(nome)

    print(f"[OK] Caso criado: CASOS/{nome}  (id {caso_id})")
    print( "     Proximo passo (E1): povoar 00_originais/ e 01_documentos/ com")
    print( "     receber_documento.py, preencher CASO.yaml + INTAKE.md e rodar o G1.")


if __name__ == "__main__":
    main()
