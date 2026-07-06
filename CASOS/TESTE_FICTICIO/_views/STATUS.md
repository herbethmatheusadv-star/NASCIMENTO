---
caso_id: 2026-0001
cliente: TESTE_FICTICIO
titulo: "Maria Ficticia x Joao Ficticio — Alimentos c/c Guarda (CASO DE TESTE)"
area: familia
fase: E2_estrategia
complexidade: simples
g1: aprovado
g2: reprovado
g3: pendente
proximo_prazo: "2026-06-30 — TESTE DO VIGIA: prazo vencido de mentira"
pendencias_criticas_abertas: 2
atualizado: 2026-07-06 10:26
---

# STATUS — Maria Ficticia x Joao Ficticio — Alimentos c/c Guarda (CASO DE TESTE)

**Cliente/pasta:** TESTE_FICTICIO · **Caso:** 2026-0001 · **Área:** familia · **Módulo:** familia/alimentos_guarda_convivencia
**Fase:** E2_estrategia · **Complexidade:** simples · **Segredo de justiça:** sim
**Gates:** G1 aprovado (2026-07-06) · G2 reprovado (2026-07-06) · G3 pendente

## Próximos prazos
- PZ02 — **2026-06-30** (alta): TESTE DO VIGIA: prazo vencido de mentira
- PZ03 — **2026-07-09** (media): TESTE DO VIGIA: prazo a 5 dias de mentira
- PZ04 — **2026-07-10** (alta): PRAZO DE RESPOSTA (contestacao) a inicial adversaria ficticia — 15 dias uteis simulados (TESTE MODO DEFESA)

## Pendências críticas abertas
- PEN01 (cliente): Comprovantes de despesas da menor e da inadimplencia (F02) — bloqueia G3
- PEN02 (advogado): Confirmar endereco atual do reu — bloqueia G3

## Números do caso
- Partes: 3 · Fatos: 3 (provados 1 / alegados 1 / controversos 0) · Provas: 2 · Pedidos: 1 · Pendências abertas: 2

## Últimas entradas do diário
- #035 | 2026-07-06 10:26 | GATE — G1 executado: APROVADO. 8/8 itens. Relatorio: _views/gate_G1_2026-07-06.md
- #034 | 2026-07-06 10:26 | ALERTA — VIGIA-PRAZO PZ04 [PROXIMO]: 'PRAZO DE RESPOSTA (contestacao) a inicial adversaria ficticia — 15 dias uteis simulados (TESTE MODO DEFESA)' vence em 2026-07-10 (em 4 dia(s), criticidade alta).
- #033 | 2026-07-06 10:26 | DOC_RECEBIDO — Recebido INICIAL ADVERSARIA COBRANCA FICTICIA [rota: peca_adversaria] -> 00_originais/inicial_adversaria_falsa.md -> DOC-02_INICIAL_ADVERSARIA_COBRANCA_FICTICIA.md.
- #032 | 2026-07-06 10:26 | GATE — G1 executado: REPROVADO. 7/8 itens. Relatorio: _views/gate_G1_2026-07-06.md
- #031 | 2026-07-06 09:25 | NOTA — CICLO DE COLHEITA executado (gatilho: teste do acervo): proposta de aprendizado gerada em _views/PROPOSTA_DE_APRENDIZADO.md com 12 candidato(s). Nenhum arquivo de modulo alterado — aguarda RATIFICACAO em bloco do advogado.

_Gerado por gerar_views.py — não editar._
