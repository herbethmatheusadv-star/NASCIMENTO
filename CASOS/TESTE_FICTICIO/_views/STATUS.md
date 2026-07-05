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
atualizado: 2026-07-04 21:35
---

# STATUS — Maria Ficticia x Joao Ficticio — Alimentos c/c Guarda (CASO DE TESTE)

**Cliente/pasta:** TESTE_FICTICIO · **Caso:** 2026-0001 · **Área:** familia · **Módulo:** familia/alimentos_guarda_convivencia
**Fase:** E2_estrategia · **Complexidade:** simples · **Segredo de justiça:** sim
**Gates:** G1 aprovado (2026-07-04) · G2 reprovado (2026-07-04) · G3 pendente

## Próximos prazos
- PZ02 — **2026-06-30** (alta): TESTE DO VIGIA: prazo vencido de mentira
- PZ03 — **2026-07-09** (media): TESTE DO VIGIA: prazo a 5 dias de mentira
- PZ01 — **2026-07-31** (media): Meta interna: protocolar a inicial (FICTICIO)

## Pendências críticas abertas
- PEN01 (cliente): Comprovantes de despesas da menor e da inadimplencia (F02) — bloqueia G3
- PEN02 (advogado): Confirmar endereco atual do reu — bloqueia G3

## Números do caso
- Partes: 3 · Fatos: 2 (provados 1 / alegados 1 / controversos 0) · Provas: 1 · Pedidos: 1 · Pendências abertas: 2

## Últimas entradas do diário
- #013 | 2026-07-04 21:35 | GATE — G2 executado: REPROVADO. 3/6 itens. Relatorio: _views/gate_G2_2026-07-04.md
- #012 | 2026-07-04 21:35 | GATE — G1 executado: APROVADO. 7/7 itens. Relatorio: _views/gate_G1_2026-07-04.md
- #011 | 2026-07-04 21:34 | ALERTA — VIGIA-PRAZO PZ03 [PROXIMO]: 'TESTE DO VIGIA: prazo a 5 dias de mentira' vence em 2026-07-09 (em 5 dia(s), criticidade media).
- #010 | 2026-07-04 21:34 | ALERTA — VIGIA-PRAZO PZ02 [VENCIDO]: 'TESTE DO VIGIA: prazo vencido de mentira' VENCEU em 2026-06-30 (ha 4 dia(s)). Providenciar imediatamente ou registrar no CASO.yaml o status cumprido/prejudicado com justificativa.
- #009 | 2026-07-04 17:57 | GATE — G2 executado: REPROVADO. 3/6 itens. Relatorio: _views/gate_G2_2026-07-04.md

_Gerado por gerar_views.py — não editar._
