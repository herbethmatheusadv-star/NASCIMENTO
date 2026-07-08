# SOJ — Regras de sessão (Claude Code)

Este é o Sistema Operacional Jurídico do escritório NASCIMENTO. A especificação
que manda em tudo é `SOJ_BLUEPRINT_v1.md` (v1.3 + adendos). O dono é advogado
e NÃO programa: explique tudo em português simples e pergunte antes de decisões
importantes.

## Início de TODA sessão (ordem obrigatória)

1. **Vigia de prazos** (blueprint, seção 7): `python ESCRITORIO/scripts/vigia_prazos.py`
   — antes de qualquer outra coisa, sobre qualquer caso. Depois, espelhar
   prazos ativos novos na agenda Google "SOJ — Prazos" (eventos anonimizados:
   "SOJ <id-do-caso> · PZ##" — nunca nomes de partes). Se o vigia lembrar o
   ritual mensal: rodar `revalidar_biblioteca.py` e reverificar NA FONTE os
   verbetes vencidos (casos afetados listados pelo próprio comando).
2. Se for trabalhar um caso: leia `CASOS/<CLIENTE>/CASO.yaml` +
   `_views/STATUS.md` + cauda do `DIARIO.md`. NÃO releia a pasta inteira.

## Doutrina de Análise (kernel — 07/07/2026)

Antes de QUALQUER tarefa analítica (diagnóstico, estratégia, simulação
adversária, juiz rigoroso, Tier B, revisão de peça/colaborador, destilação
de autos, preparação de audiência): **ler `ESCRITORIO/DOUTRINA_ANALISE.md`
e obedecê-la**. Resumo inegociável: mecânico = economia máxima; analítico =
PROFUNDIDADE É O PRODUTO (proibido economizar); quatro passadas
(mapear → aprofundar → adversariar a si mesmo → sintetizar); toda afirmação
ancorada em elemento concreto do caso e com consequência declarada; veredito
só com base e faixa; tarefa analítica LÊ MAIS (ficha + INTAKE integral +
provas + teses do módulo), nunca menos.

## Regras duras (blueprint)

- `00_originais/` é imutável. `DIARIO.md` é append-only (corrigir = nova
  entrada). `_views/` nunca se edita à mão (regenerar com `gerar_views.py`).
- Documento novo entra SÓ pelo `receber_documento.py` (ponto único de entrada).
- Gates G1/G2/G3 pelo `gate_check.py`; gate reprovado bloqueia a etapa.
- Exceções/justificativas são CAMPOS do CASO.yaml com referência ao DIARIO
  (blueprint, seção 6 — robustez); os gates não leem texto livre.
- Nunca citar lei de memória: verbete verificado em `ESCRITORIO/BASE_LEGAL/`
  dentro da validade; diante de lacuna, parar e perguntar — nunca inventar fato.
- Decisões técnico-jurídicas: DECISAO_SISTEMA no DIARIO com fundamento,
  alternativa descartada e confiança (D11); ratificação em bloco nos gates.

## Módulos e kernel

- Comandos padrão do sistema: skill `soj-kernel` (.claude/skills/soj-kernel/).
- Módulos PLENOS: `familia/` · `consumidor_aguas/` (negativação × Águas do
  Pará, JEC) · `bancario_ccb/` (defesa em execução de CCB × cooperativas —
  **modo defesa nativo: novo caso da área nasce --polo passivo**) ·
  `civel/` (honra e reputação digital — nascido do caso 2026-0004). Cada um:
  praxe_decisoria (árvore Tier A/B + camada LOCAL), decisoes_reservadas,
  checklist_documental, anti_erro_fatal, teses (com antiteses) e templates.
  Esqueletos: `trabalhista/`, `previdenciario/` (módulo nasce do caso 1).
- Camada LOCAL da praxe: anotação com contagem (fontes = Acervo); vira
  recomendação só com n≥3 do MESMO juízo; divergiu do nacional = Tier B.

## Regra do laboratório

`CASOS/TESTE_FICTICIO` é o caso-laboratório PERMANENTE. Alterou qualquer
script? Rode tudo nele ANTES de tocar em caso real.

## Dados sensíveis

Casos com `segredo_justica: true` envolvem menores: nunca colar dados
identificados fora deste ambiente; em serviços externos (ex.: Calendar),
usar só o id do caso e o PZ## — nunca nomes de partes.
