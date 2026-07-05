# SOJ — Regras de sessão (Claude Code)

Este é o Sistema Operacional Jurídico do escritório NASCIMENTO. A especificação
que manda em tudo é `SOJ_BLUEPRINT_v1.md` (v1.3 + adendos). O dono é advogado
e NÃO programa: explique tudo em português simples e pergunte antes de decisões
importantes.

## Início de TODA sessão (ordem obrigatória)

1. **Vigia de prazos** (blueprint, seção 7): `python ESCRITORIO/scripts/vigia_prazos.py`
   — antes de qualquer outra coisa, sobre qualquer caso. Depois, espelhar
   prazos ativos novos na agenda Google "SOJ — Prazos" (eventos anonimizados:
   "SOJ <id-do-caso> · PZ##" — nunca nomes de partes).
2. Se for trabalhar um caso: leia `CASOS/<CLIENTE>/CASO.yaml` +
   `_views/STATUS.md` + cauda do `DIARIO.md`. NÃO releia a pasta inteira.

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
- Caso de família: usar `ESCRITORIO/MODULOS/familia/` — praxe_decisoria.md
  (árvore Tier A/B), decisoes_reservadas.md, checklist_documental.md,
  anti_erro_fatal.md, teses.md e templates/ (minuta nasce ~70% pronta).

## Regra do laboratório

`CASOS/TESTE_FICTICIO` é o caso-laboratório PERMANENTE. Alterou qualquer
script? Rode tudo nele ANTES de tocar em caso real.

## Dados sensíveis

Casos com `segredo_justica: true` envolvem menores: nunca colar dados
identificados fora deste ambiente; em serviços externos (ex.: Calendar),
usar só o id do caso e o PZ## — nunca nomes de partes.
