# MÓDULO BANCÁRIO / CCB × COOPERATIVAS — contrato do módulo (Onda 3/F6, 2026-07-06)

> Adaptação da skill `advogado-bancario-cooperativas` ao kernel (D10/Fase 5).
> **100% do conteúdo validado preservado por cópia byte a byte** em
> `referencias/`, `checklists/`, `playbooks/` e `templates/` (integridade
> conferida). `SKILL_original.md` = a skill como era. Este arquivo e os
> demais do contrato são a CAMADA DE ADAPTAÇÃO — apontam, não reescrevem.

## ⚔️ MODO DEFESA NATIVO

Esta área nasce do lado do EXECUTADO/devedor — a skill "não serve a credor".
**Todo caso novo desta área: `novo_caso.py ... --polo passivo`** (salvo ordem
expressa em contrário). Consequências do kernel: ITEM ZERO do G1 (prazo de
resposta/embargos no vigia ANTES de tudo — ex.: 5 dias do art. 854 §3º em
bloqueio SISBAJUD), alegações da cooperativa como `alegado_pelo_adversario`,
simulação adversária INVERTIDA (simular a réplica/impugnação da cooperativa).

## Tipos de ação cobertos (cenários da skill → rotas do kernel)

| Cenário (SKILL_original §árvore) | Entrada no kernel | Peça típica (templates/) |
|---|---|---|
| 1. Citado em execução de CCB | novo caso (polo passivo) + inicial deles pela porta única (`--tipo peca_adversaria`) | excecao_pre_executividade.md · embargos_execucao_ccb.md |
| 2. Bloqueio SISBAJUD/teimosinha **[URGÊNCIA]** | porta única `--tipo decisao` (prazo de 5 dias ANTES de tudo) → playbooks/03_gargalo_penhora.md | impugnacao_bloqueio_sisbajud.md · agravo_instrumento_desbloqueio.md |
| 3. Decisão contra o cliente | porta única `--tipo decisao/sentenca` (gatilho de fase propõe embargos de declaração/agravo/apelação — recurso = Tier B) | (radar de decisões — SKILL_original §radar) |
| 4. Segunda opinião / auditoria | modo revisão de peça + playbooks/01 | — |
| 5. Cálculo de excesso | SKILL_original §calculador forense + referencias/abusividades_contratuais.md | (memória do art. 917 §3º CPC — obrigatória nos embargos por excesso) |

## Rito e particularidades

- Execução de título extrajudicial (CCB — Lei 10.931/2004); defesa em
  camadas (SKILL_original §estrategista multicamada): revisional c/ tutela →
  exceção de pré-executividade → embargos c/ efeito suspensivo → incidentais
  → recursal → autônoma.
- Conceitos-chave de cooperativas (CDC aplicável — Súmula 297/STJ; ato
  cooperativo × operação bancária; rateio): SKILL_original §conceitos.
- Saída padrão de toda peça: **Plano A + Plano B** (carta na manga) — regra
  da skill preservada como regra do módulo.

## Correspondências com o kernel

- Auditoria inicial dos autos (playbooks/01 + checklists/auditoria) → roteiro
  do INTAKE (E1) da área; documentos → `checklist_documental.md`.
- Escolha da peça (playbooks/02) → é a base da `praxe_decisoria.md`.
- Auto-revisão (playbooks/04 + checklists/revisao_peticao_pre_protocolo) →
  absorvida pelo `anti_erro_fatal.md` + G3.
- "Quando pesquisar web" (playbooks/05) → subordinado à BASE_LEGAL/D6: o que
  se pesquisa vira VERBETE com data; nunca citar sem verbete válido.
- Jurisprudência da skill (referencias/jurisprudencia_chave/) → conteúdo
  validado em uso; para citar em peça NOVA: reverificar na fonte e verbetar
  em `BASE_LEGAL/bancario.md` (regra de ferro do Acervo vale aqui).

## Estado do contrato (seção 9)

| Arquivo | Estado |
|---|---|
| MODULO.md · praxe_decisoria.md · decisoes_reservadas.md · checklist_documental.md · teses.md · anti_erro_fatal.md | ✅ (Onda 3) |
| templates/ (4 peças) · referencias/ · checklists/ · playbooks/ | ✅ copiados íntegros da skill |
| Tabelas de quantum | cálculo de excesso = método do §calculador (paramétrico) |
