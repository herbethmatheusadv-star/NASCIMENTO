# RASTREABILIDADE — fato × prova × pedido × parágrafo × fundamento

Minuta lida: MINUTA_v01.md

| Fato | Status | Provas | Pedidos | Minuta (linhas) |
|---|---|---|---|---|
| F01 | provado | P06, P08, P09, P01 | PED01, PED03, PED04, PED05 | — |
| F02 | alegado | P08, P09 | PED03, PED04 | — |
| F03 | provado | P02, P03, P04, P05 | PED01, PED02 | — |
| F04 | provado | P04, P05 | PED02 | — |
| F05 | provado | P03 | — | — |
| F06 | provado | P06, P07, P08, P09 | PED01, PED03, PED04, PED05 | — |
| F07 | provado | P01 | — | — |
| F08 | alegado | — | — | — |
| F09 | alegado | — | — | — |

## Pedidos

| Pedido | Tipo | Fatos | Fundamentos | Tags na minuta |
|---|---|---|---|---|
| PED01 | tutela_urgencia_remocao | F01, F03, F06 | CPC:art300, MCI:art15, MCI:art22 | 0 |
| PED02 | exibicao_de_dados | F03, F04 | MCI:art22, MCI:art15, STF:tema987 | 0 |
| PED03 | danos_morais_pj | F01, F02, F06 | CC:art186, CC:art927, SUM227:STJ, STJ:teses130 | 0 |
| PED04 | danos_morais_pf | F01, F02, F06 | CC:art186, CC:art927, STJ:teses130 | 0 |
| PED05 | obrigacao_de_fazer_retratacao | F01, F06 | CC:art927 | 0 |

## Alertas de cobertura

- PED01 sem nenhuma tag na minuta.
- PED02 sem nenhuma tag na minuta.
- PED03 sem nenhuma tag na minuta.
- PED04 sem nenhuma tag na minuta.
- PED05 sem nenhuma tag na minuta.

_Gerado por gerar_views.py — não editar._
