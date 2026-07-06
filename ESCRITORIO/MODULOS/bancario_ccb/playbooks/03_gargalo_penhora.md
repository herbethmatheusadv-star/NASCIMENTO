# Playbook 03 — Gargalo da Penhora [MÓDULO CENTRAL]

Este é o módulo mais acionado e o mais crítico da skill. Bloqueio, penhora, teimosinha, desbloqueio — o front diário do advogado de defesa. Aqui cada dia importa, cada prazo é fatal, cada argumento mal colocado custa o dinheiro do cliente.

## Regra de ouro: o jogo mudou em 2024/2025

**Tema 1.235/STJ (Corte Especial, Min. Nancy Andrighi)** — a impenhorabilidade de até 40 salários mínimos do art. 833, X do CPC **deixou de ser matéria de ordem pública**. Passou a ser direito disponível do executado, que precisa alegar no prazo de 5 dias do art. 854, §3º, I do CPC. Silêncio vira preclusão; juiz não protege mais de ofício.

Consequência prática: **monitoramento ativo** de SISBAJUD é agora obrigação do advogado. Bloqueio caiu, tem 5 dias — contando sábados e domingos não, só dias úteis — para impugnar com prova. Passou do prazo, o valor migra ao credor no dia seguinte.

**Tema 1.230/STJ** (em julgamento, suspenso em todo país) — alcance do art. 833, §2º sobre impenhorabilidade salarial em dívidas não alimentares, mesmo para rendas inferiores a 50 SM. Abre janela tática: em casos pertinentes, pedir **suspensão da execução** aguardando o julgamento.

## Cenário 1 — Bloqueio SISBAJUD em conta do cliente

### Passo 1: Diagnóstico rápido em 5 perguntas

1. **Quando caiu o bloqueio?** Apurar data exata do comando + da intimação/ciência para calcular prazo de 5 dias úteis. Se a intimação foi eletrônica, o prazo começa no dia útil seguinte à ciência (art. 231 CPC).
2. **Onde caiu?** Conta corrente, poupança, aplicação, conta PJ, conta salário formal, conta investimento? Cada tipo tem defesa específica.
3. **Quanto foi bloqueado?** Todo o saldo ou valor parcial? Valor inferior ou superior a 40 SM (em 2026, 40×R$1.518 ≈ R$60.720, conferir valor vigente)?
4. **Qual a origem do dinheiro?** Salário, pró-labore, faturamento da empresa, venda de bem, poupança acumulada, indenização, benefício?
5. **É conta única do cliente, conjunta ou de terceiro?** Bloqueios em conta conjunta ou de terceiro têm defesa adicional.

### Passo 2: Escolher a peça imediata

**Prazo correndo (menos de 5 dias da ciência):** Impugnação do art. 854, §3º do CPC protocolada nos próprios autos da execução. Não é exceção, não é embargos — é petição de impugnação específica do bloqueio. Ver `templates/impugnacao_bloqueio_sisbajud.md`.

**Prazo perdido (mais de 5 dias):** Situação difícil, mas não perdida. Tentar:
- Arguir matéria de ordem pública que sobrevive à preclusão (salário é inciso IV, não inciso X — salário segue protegido mesmo fora do prazo conforme jurisprudência do STJ sobre proteção à verba alimentar; já os 40 SM em poupança do inciso X caíram no Tema 1.235).
- Exceção de pré-executividade se a matéria é de ordem pública aferível.
- Agravo de instrumento se houve decisão formalizando a penhora.

**Indeferimento da impugnação:** Agravo de instrumento com pedido de **efeito suspensivo ativo** (art. 1.019, I CPC) — prazo de 15 dias. Peça em `templates/agravo_instrumento_desbloqueio.md`.

### Passo 3: Arsenal de defesa por tipo de verba

#### Poupança até 40 SM (art. 833, X)
- Regra clássica: impenhorável até 40 SM (valor-base vigente).
- Tema 1.235 exige alegação tempestiva.
- Se alegado e juiz indeferir: ainda cabível agravo, com fundamento no texto legal e jurisprudência do STJ que **estende a proteção** a conta corrente, fundos e papel-moeda (AgInt no AREsp 2680710; AgInt nos EDcl no AREsp 2467972).
- **Ônus de prova:** ao executado comprovar que o valor é reserva (estabilidade do saldo). Ao credor comprovar abuso, má-fé ou fraude se quiser afastar a impenhorabilidade.

#### Conta corrente onde cai salário (art. 833, IV + X)
Tese combinada e poderosa:
- Até o valor do salário do mês: impenhorável integralmente pelo art. 833, IV (verba alimentar). O simples depósito em CC não desfigura a natureza alimentar (jurisprudência pacífica STJ e TJs).
- Sobras salariais acumuladas: protegidas até 40 SM pelo art. 833, X combinado com entendimento STJ de extensão a CC.
- **Prova necessária:** holerite/folha de pagamento ou comprovante de transferência da fonte pagadora + extratos de 3 a 6 meses mostrando o padrão.

#### Conta salário formal (conta corrente destinada ao depósito salarial)
- Proteção mais forte. Banco identifica como conta-salário e existe jurisprudência reforçada de impenhorabilidade integral enquanto ali mantido o valor do salário.
- Prova: documento do banco confirmando categoria "conta-salário" + comprovante de fonte pagadora.

#### Conta PJ / faturamento da empresa
Terreno diferente, defesa mais técnica:
- Art. 833, VII protege móveis, utensílios e livros necessários ao exercício de qualquer profissão.
- Art. 833, IX protege a quantia depositada em caderneta de poupança até 40 SM (aplicável a PJ? Jurisprudência divergente; TRF3 recente estendeu às PJs em execução fiscal).
- Art. 866 CPC permite penhora de faturamento em **caráter subsidiário** e **proporcional** (10-30% tipicamente), mediante nomeação de administrador, quando não há outro bem.
- Bloqueio total de conta empresarial que inviabilize folha de salários, fornecedores críticos, tributos — é desproporcional e agride o princípio da menor onerosidade (art. 805 CPC).
- **Prova necessária:** folha de salários do mês, contas a pagar essenciais, faturamento do mês, demonstração de ativo/passivo circulante.

#### Aposentadoria / benefício previdenciário
- Impenhorabilidade absoluta (art. 833, IV e Lei 8.213/91 art. 114, I).
- Exceção do §2º: pensão alimentícia ou valor mensal acima de 50 SM — o bloqueio só seria legítimo na parte excedente de 50 SM, e apenas para pagamento de dívida alimentar.

#### Indenização trabalhista, seguro de vida, verbas rescisórias
- Mantêm natureza alimentar enquanto recentes e não consumidas. STJ aceita que **sobras** (depositadas e mantidas por longo período em fundo) podem perder proteção se acima de 40 SM.
- Jurisprudência TJDFT: indenização por seguro equiparada a reserva, protegida até 40 SM (TJDFT Acórdão 1854021, 2024).

#### Verba de liberalidade (pensão alimentícia recebida, doação mensal)
- Art. 833, IV inclui "quantias recebidas por liberalidade de terceiro e destinadas ao sustento do devedor e de sua família". Impenhorável.

### Passo 4: Produzir a prova (diferencial competitivo)

A falha mais comum do advogado no Gargalo da Penhora não é jurídica — é probatória. O juiz não desbloqueia sem prova clara de que o valor é protegido. Checklist de prova:

- **Extratos completos** da conta bloqueada dos últimos 6 a 12 meses, não seletivos.
- **Holerite** ou comprovante da fonte pagadora do mês da penhora e dos 2 anteriores.
- **Comprovante de movimentação da conta-salário** (se houver).
- **Para PJ:** folha de pagamento, contas a pagar do mês, balancete recente, comprovação de despesas essenciais (aluguel, fornecedores, impostos).
- **Declaração do próprio cliente** narrando a natureza dos depósitos (útil para comprovar reserva).
- **Documentos específicos do tipo de verba** (carta de aposentadoria INSS, ofício rescisório, etc.).

Sem esses documentos, **não protocolar a peça**. Pedir ao advogado primeiro.

## Cenário 2 — Teimosinha (reiteração automática)

### O que é
O SISBAJUD permite programar reiterações automáticas da ordem de bloqueio por prazo determinado (tipicamente 30 dias). Cada novo depósito na conta do executado é bloqueado automaticamente até atingir o valor devido.

### Panorama jurisprudencial 2025/2026
- **Legalidade confirmada** pelo TRF-3 (dez/2025) e TRT-15 2ª SDI (abr/2026). Ataque frontal à ferramenta não funciona mais.
- O caminho é outro: **demonstrar que o efeito prático da teimosinha inviabiliza atividade empresarial ou viola impenhorabilidade**.

### Defesa em camadas
1. **Imediata:** pedido de levantamento da teimosinha por comprometimento grave da atividade. Prova: balanços, extratos, folha de pagamentos, demonstração de que cada nova reiteração atinge verba alimentar/essencial.
2. **Alternativa:** pedido de substituição da teimosinha por penhora de bem determinado (imóvel, veículo, direito creditório) com base no art. 847 CPC.
3. **Tática:** pedido de limitação temporal (ex.: suspender a reiteração por 30 dias para que a empresa pague fornecedores essenciais), com compromisso de indicar bem substituto.
4. **Recurso:** se indeferido, agravo de instrumento com efeito suspensivo ativo, alegando violação ao princípio da menor onerosidade (art. 805) e ao livre exercício da atividade econômica (art. 170, CF).

## Cenário 3 — Juiz já indeferiu desbloqueio

Situação real e comum. Advogado impugnou tempestivamente, provou o que podia, e o juiz indeferiu. O caminho:

### Passo 1: Ler a decisão com lupa (radar de lacunas)
- O juiz enfrentou todos os argumentos? (omissão → embargos de declaração)
- Justificou por que rejeitou a prova? (falta de fundamentação art. 489, §1º CPC)
- Citou jurisprudência superada? (recurso com distinguishing)
- Confundiu natureza da verba? (erro material + embargos)
- Invocou abuso/má-fé sem prova do credor? (violação ao ônus da prova — art. 373 CPC)

### Passo 2: Embargos de declaração estratégicos (se couber)
Prazo de 5 dias. Com pretensão modificativa quando a omissão/contradição muda o resultado. Interrompe o prazo do agravo. Útil quando:
- O juiz não enfrentou prova juntada.
- Não analisou tese específica alegada.
- Citou jurisprudência em contradição com a decisão.

### Passo 3: Agravo de instrumento
Se a decisão é consolidada, ir direto ao agravo. Peça em `templates/agravo_instrumento_desbloqueio.md`. Componentes essenciais:
- Pedido de **efeito suspensivo ativo** (art. 1.019, I) com fundamentos em relevância e risco.
- Exposição precisa do fato: quando bloqueou, quanto, natureza do valor.
- Violação a dispositivo legal específico (art. 833, IV ou X; art. 805; art. 854 §3º).
- Jurisprudência-âncora do STJ e do próprio tribunal.
- Prova documental pertinente.

### Passo 4: Estratégia combinada
Paralelamente ao agravo, em primeiro grau:
- **Petição de substituição de penhora** (art. 847 CPC) oferecendo bem menos oneroso.
- **Pedido de levantamento parcial** de valor específico para despesa essencial comprovada (medicamento, pagamento de salários, escola dos filhos) — STJ admite em casos excepcionais, com prova robusta.

## Cenário 4 — Impugnação de RENAJUD / INFOJUD / BACENCCS

### RENAJUD (veículos)
- Bloqueio em veículo utilizado como instrumento de trabalho (taxi, Uber, transporte escolar, representante comercial, caminhão de carga) — art. 833, V protege os instrumentos necessários ao exercício de profissão (com limite — o STJ admite proteção de 1 veículo essencial).
- Impugnação no próprio processo + comprovação documental do uso profissional.
- Se indeferida, agravo de instrumento.

### INFOJUD (sigilo fiscal)
- Requisição de dados fiscais do executado só se legítima após esgotamento de outras diligências (STJ firmou entendimento mitigando o esgotamento após Lei 11.382/06, mas ainda há parâmetros).
- Impugnação cabível em caso de uso abusivo/invasivo.

### BACENCCS (cadastro de clientes do SFN)
- Consulta com ofício ao BACEN — revela contas do executado em toda rede bancária. Não é penhora, é pesquisa de bens. Impugnação é mais limitada, mas cabe se o pedido for excessivo ou lesivo à privacidade.

## Cenário 5 — Penhora no rosto dos autos

Cooperativa pede penhora no rosto dos autos de ações em que o executado é parte autora (trabalhista, previdenciária, civil). O bloqueio de crédito trabalhista merece defesa forte — natureza alimentar (art. 833, IV) + Súmula 498/STJ antiga sobre preservação trabalhista.

Impugnação no rosto dos autos:
- No processo onde a penhora é lançada: ação trabalhista ou previdenciária — arguir impenhorabilidade perante aquele juízo também.
- Na execução: pedir reconsideração ou substituir por bem distinto.
- Se trabalhista e a cooperativa cobra dívida não alimentar: Tema 1.230 STJ (suspensão nacional aguardada).

## Cenário 6 — Protesto, SPC/Serasa, restrições

Não é exatamente penhora, mas muitas vezes vem junto. Cooperativa protocola CCB em cartório de protesto e/ou registra em SPC/Serasa. Defesas:
- Sustação de protesto mediante caução (ação cautelar ou tutela antecipada).
- Ação declaratória de inexistência de débito cumulada com cancelamento de inscrição + danos morais (STJ Súmula 385: inscrição indevida gera dano moral in re ipsa desde que não haja outras inscrições legítimas anteriores).
- Se bloqueio SISBAJUD + protesto + inscrição: pacote de cobrança abusiva, avaliar responsabilidade civil agregada.

## Outputs esperados neste módulo

Ao responder qualquer consulta deste cenário, entregar:

1. **Diagnóstico em minutos** — cenário, prazo remanescente, peça cabível.
2. **Lista de documentos necessários** — o que pedir ao advogado agora.
3. **Minuta da peça** — pronta para protocolo após ajustes finais.
4. **Jurisprudência citada** — lista com número, órgão, data.
5. **Plano B e C** — se a peça primária falhar.
6. **Alerta de riscos** — o que a cooperativa pode contra-atacar.

Este módulo trabalha em velocidade. O advogado que está com bloqueio na conta do cliente precisa de resposta hoje, não amanhã.
