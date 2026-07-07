# DIÁRIO — TESTE_IMPORTACAO (caso 2026-0003)

Ledger append-only (blueprint, seção 4). NUNCA edite ou apague uma entrada:
correção é entrada NOVA referenciando a antiga. Formato e tipos de entrada:
ESCRITORIO/MODELOS/DIARIO.formato.md

---
## #001 | 2026-07-06 22:59 | NOTA
Caso criado pelo novo_caso.py. Id: 2026-0003. Area: familia. Modulo: a_definir. Complexidade: padrao. Fase: E1_intake.
---
## #002 | 2026-07-06 22:59 | IMPORTACAO
Origem: colaborador DR. COLABORADOR FICTICIO (importado pelo sistema).
PORTA DE IMPORTACAO: pasta do colaborador DR. COLABORADOR FICTICIO (6 arquivos, todos lacrados com SHA-256 em 00_originais/importacao_DR_COLABORADOR_FICTICIO/). Roteados: 1 prova(s) [P01], 2 instrumental(is) [INS01, INS02], 1 duplicata(s) fora do roteamento, 1 rascunho(s) em _efemeros. Minuta 'PETICAO INICIAL - ALIMENTOS.md' importada como MINUTA_v01 (confianca zero); relatorio em _views/REVISAO_COLABORADOR.md. Engenharia reversa (F##/PED##/propostas do colaborador) segue na sessao.
---
## #003 | 2026-07-06 23:01 | ENGENHARIA_REVERSA
Origem: sistema.
Engenharia reversa da MINUTA_v01 importada (confianca zero): 3 fatos (F02 provado por P01; F01 e F03 ALEGADOS — F03 e fato orfao, afirmado sem prova), 3 pedidos (PED02 reancorado no CPC:art529 — a minuta citava os REVOGADOS arts. 16-18 da L5478, verbete LEI5478:art16a18), pendencias PEN02-PEN05. Decisoes embutidas do colaborador viraram propostas PC01 (quantum 40 por cento SM/filho) e PC02 (valor da causa) com status aguardando_ratificacao — G2 bloqueia ate o titular ratificar ou vetar. Relatorio completo: _views/REVISAO_COLABORADOR.md.
---
## #004 | 2026-07-06 23:02 | GATE
G1 executado: REPROVADO. 2/7 itens. Relatorio: _views/gate_G1_2026-07-06.md
Itens reprovados: Originais preservados e documentos registrados (P## com original); Toda parte com qualificacao completa OU pendencia aberta; Prazos identificados (PZ##) ou declaracoes.sem_prazos com referencia ao DIARIO; Complexidade classificada (D9) e modulo definido; Checklist do cliente gerado e enviado (declaracoes.checklist_cliente_enviado)
---
