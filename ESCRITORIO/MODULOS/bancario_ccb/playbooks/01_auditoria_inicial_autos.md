# Playbook 01 — Auditoria inicial dos autos

Este é o primeiro ato obrigatório toda vez que o advogado entrega documentos. Sem auditoria, não há estratégia válida. O objetivo é produzir um **diagnóstico estruturado** que oriente as decisões seguintes.

## Passo 1 — Inventariar o que foi entregue

Listar explicitamente cada documento recebido:
- CCB? Com todos os aditivos?
- Petição inicial da execução?
- Memória de cálculo da cooperativa?
- Extratos?
- Decisões já proferidas?
- Se houve bloqueio: extratos do período do bloqueio?
- Procuração e documentos pessoais?

Se faltar material essencial para a tese pretendida, **avisar o advogado e pedir** antes de avançar. Diagnóstico incompleto é diagnóstico errado.

## Passo 2 — Auditar a CCB contra o art. 29 da Lei 10.931/2004

Aplicar `checklists/auditoria_ccb_cooperativa.md` item por item. Os pontos críticos:

**Requisitos do art. 29 (requisitos do título):**
- Denominação "Cédula de Crédito Bancário" expressa
- Promessa do emitente de pagar em dinheiro
- Data e lugar do pagamento
- Nome da instituição credora
- Data e lugar da emissão
- Assinatura do emitente
- Se cooperativa: verificar se a singular que emitiu tem poderes (muitas CCBs vêm em nome do Banco Cooperativo Sicredi ou do SICOOB Confederação, mas a operação é da singular — cuidado com ilegitimidade ativa)

**Discriminação do crédito (art. 28, §2º):**
- Se crédito fixo: identificação do valor líquido disponibilizado na conta, das amortizações, dos encargos incidentes
- Se crédito rotativo (conta corrente, cheque especial, capital de giro rotativo): obrigatoriedade de ANEXAR extratos discriminando cada utilização, amortização e encargo por período. **Sem essa discriminação, a CCB rotativa perde a liquidez e não é título executivo** (STJ REsp 1291575; TJSP 17ª Câmara de Direito Privado 2025)

**Via original:**
- A cooperativa anexou o original ou só cópia?
- Se só cópia: o pedido foi inicial ou houve alegação concreta de circulação/duplicidade? O STJ (AgInt no EREsp 2117579/SP) exige original quando há alegação motivada de duplicidade, sob risco de extinção.

**Testemunhas:**
- A ausência de testemunhas **não** é nulidade na CCB (jurisprudência consolidada — Lei 10.931/04 não exige). Não perder tempo com essa tese.

**Aval, fiança, garantia real:**
- Identificar quem mais firmou. Aval dado por cônjuge sem outorga em regime diverso de separação absoluta é atacável (art. 1.647, III, CC).
- Se há garantia fiduciária ou hipotecária, a ação correta seria busca e apreensão ou execução de título extrajudicial com garantia real — confirmar se a cooperativa usou o rito correto.

## Passo 3 — Auditar a relação material (abusividades)

Consultar `references/abusividades_contratuais.md` e percorrer:

**Juros remuneratórios:**
- Taxa pactuada mensal e anual — bate com a taxa efetiva real?
- Comparar com a taxa média de mercado BACEN da modalidade (conta corrente, capital de giro, crédito pessoal) no mês da contratação — consultar https://www.bcb.gov.br/estatisticas/txjuros
- Súmula 382/STJ: estipulação de juros acima de 12% a.a. **não é por si só abusiva**; só abusividade demonstrada caso a caso (divergência substancial em relação à taxa média).
- Súmula 530/STJ: nos contratos bancários não regidos por legislação específica, quando ausente cláusula ou ela for abusiva, aplica-se a taxa média de mercado.

**Capitalização:**
- Só é lícita se expressamente pactuada (Súmula 539/STJ) e desde que a taxa anual seja superior ao duodécuplo da mensal (Súmula 541/STJ).
- Capitalização diária sem destaque específico e sem taxa diária informada: abusiva (viola dever de informação, art. 46 e 54, §4º do CDC).

**Multa moratória:**
- Máximo de 2% após a Lei 9.298/96 (art. 52, §1º do CDC). Se CCB estabeleceu 10% como era comum antes, isso é excesso.

**Juros moratórios:**
- 1% a.m. em regra (art. 406 CC combinado com art. 161, §1º CTN) ou o pactuado se razoável.

**Comissão de permanência:**
- Súmula 472/STJ: impossibilidade de cumulação com correção monetária, juros remuneratórios, juros moratórios e multa. Se houver cumulação na memória de cálculo, a comissão deve ser afastada.

**Tarifas:**
- Registro de contrato e avaliação de bem: STJ aceita se demonstrado o serviço efetivamente prestado (Tema 958). Sem comprovação documental: abusivas.
- Seguro prestamista: só lícito com livre escolha da seguradora pelo consumidor (Tema 972 STJ). Se a cooperativa impôs a seguradora, é venda casada e abusividade.
- Tarifa de cadastro: admitida em início de relacionamento (Tema 618), apenas uma vez.
- Outras tarifas "soltas" (abertura de crédito, elaboração de contrato, etc.): avaliar caso a caso.

**IOF:**
- Lícita se calculada na alíquota legal. Se a cooperativa embutiu IOF no capital financiado gerando juros sobre IOF, atacar a capitalização indevida do tributo.

## Passo 4 — Auditar a memória de cálculo

Comparar:
- Data de início do cálculo = data de vencimento inadimplida da CCB? Deve ser.
- Valor inicial = saldo devedor na data de vencimento? Deve ser.
- Taxa aplicada = taxa da CCB? Deve ser, não mais.
- Capitalização aplicada = capitalização pactuada? Só se expressamente clausulada.
- Índice de correção = TR? IPCA? Confere com o pactuado?
- Há incidência de multa, juros de mora e comissão de permanência cumulativamente? Se sim, problema.
- Honorários contratuais cobrados na execução? Em regra, não são devidos (não se confundem com honorários sucumbenciais).

**Art. 917, §3º CPC** — para embargar por excesso de execução, o advogado precisa apresentar a memória correta. Sem isso, embargos por excesso são inadmissíveis. Então se a análise detectar excesso, **produzir a memória alternativa** já no diagnóstico (ver seção Calculador Forense no SKILL.md principal).

## Passo 5 — Identificar impenhorabilidades aplicáveis

Consultar `references/impenhorabilidades_arsenal.md` mesmo quando ainda não há bloqueio, porque isso orienta:
- Advertência preventiva ao cliente sobre onde guardar recursos.
- Antecipação de argumentos defensivos.
- Identificação de bens que a cooperativa poderia atacar.

## Passo 6 — Identificar teses de cooperativa aplicáveis

Consultar `references/teses_exclusivas_cooperativas.md`. Pontos a verificar:
- O executado é cooperado? Quando aderiu? Quais documentos de adesão?
- A operação foi ato cooperativo puro ou operação bancária típica? (Quase sempre é operação bancária.)
- Há cobrança de rateio de prejuízo? Foi válida a assembleia? Houve notificação?
- CDC aplicável? (Em regra sim, conforme Súmula 297 e jurisprudência consolidada.)

## Passo 7 — Verificar prescrição e decadência

- Prescrição da pretensão executiva: 5 anos (art. 206, §5º, I, CC) para títulos de crédito em geral; CCB segue mesma regra conforme jurisprudência.
- Contagem a partir do vencimento da obrigação exequenda.
- Checar datas: emissão da CCB, vencimento, ajuizamento, citação — interrupções aplicáveis.

## Passo 8 — Entregar diagnóstico estruturado

Formato de saída obrigatório:

```
=== DIAGNÓSTICO DO CASO ===

1. PARTES E TÍTULO
   - Exequente: [nome completo da cooperativa / número CNPJ / natureza]
   - Executado: [nome / qualidade — principal/avalista/fiador]
   - Título: CCB nº ___, emitida em ___, vencimento ___, valor emitido R$ ___
   - Natureza da CCB: fixa | rotativa | crédito em conta corrente | capital de giro

2. ATAQUES FORTES IDENTIFICADOS (Plano A)
   - [Nulidade 1 com fundamento legal e jurisprudência]
   - [Abusividade 1 com fundamento]
   - [Excesso apurado: R$ ___ menor que o cobrado, se houver]

3. ATAQUES SECUNDÁRIOS (Plano B, cartas na manga)
   - [Tese 1]
   - [Tese 2]

4. IMPENHORABILIDADES APLICÁVEIS
   - [Lista]

5. PEÇA RECOMENDADA
   - [Peça principal + justificativa]
   - [Peças auxiliares a considerar]

6. DOCUMENTOS ADICIONAIS QUE PRECISO
   - [Se algo faltou]

7. RISCOS
   - [Pontos fracos da defesa]
   - [Jurisprudência desfavorável que pode ser invocada pela cooperativa]
```

Só depois desse diagnóstico, avançar para `playbooks/02_escolha_peca_arvore_decisoria.md`.
