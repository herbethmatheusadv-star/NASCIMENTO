# Playbook 02 — Escolha da peça processual

Após o diagnóstico, decidir **qual peça** usar, **quando** e **em que ordem**. Peça errada perde prazo, preclusão ou enfraquece a tese. Escolha certa multiplica as chances.

## Árvore de decisão principal

### A — Antes de embargos, há matéria arguível de plano?

Nulidade formal da CCB, ilegitimidade manifesta, impenhorabilidade absoluta, prescrição, litispendência, coisa julgada — **qualquer matéria de ordem pública ou aferível sem dilação probatória** pode ir em **exceção de pré-executividade**. Vantagens:
- Não exige garantia do juízo (art. 919 CPC só vale para embargos).
- Não tem prazo específico — pode ser apresentada a qualquer tempo (STJ Súmula 393 — aferível de ofício e sem preclusão para matérias aferíveis de plano).
- Se acolhida, extingue a execução sem custo para o executado.
- Se rejeitada, cabe agravo de instrumento (art. 1.015, parágrafo único, CPC) e o prazo dos embargos só começa com a citação/penhora, regularmente.

Então: **use exceção sempre que houver matéria aferível de plano.** Pode ser apresentada cumulativamente com embargos ou separadamente.

### B — O prazo de embargos está correndo?

Embargos à execução têm prazo de **15 dias úteis** contados da juntada do mandado de citação aos autos (art. 915 CPC). Não depende de penhora.

- Dentro do prazo + juízo seguro com bens suficientes: **embargos à execução com pedido de efeito suspensivo** (art. 919, §1º — requisitos: relevância dos fundamentos, risco de dano grave, garantia do juízo).
- Dentro do prazo + sem garantia: embargos sem efeito suspensivo (tramitam, mas não param a execução).
- Fora do prazo: **exceção de pré-executividade** para matérias aferíveis; para o resto, ação autônoma (revisional, reparação).

### C — Já houve bloqueio ou penhora?

Ativar `playbooks/03_gargalo_penhora.md`. Aqui, prazo de **5 dias** do art. 854, §3º, I CPC é fatal — uma vez perdido, presume-se aceita a penhora e os valores migram ao exequente. Nesse cenário:
- Impugnação do bloqueio (art. 854, §3º) é a peça primária se o prazo está correndo.
- Agravo de instrumento se a decisão de indeferimento já saiu.
- Pedido de substituição de penhora paralelamente (art. 847 CPC).

### D — Houve decisão interlocutória desfavorável?

Identificar qual. Em execução, o **parágrafo único do art. 1.015 CPC** permite agravo de instrumento contra **qualquer decisão interlocutória** (regra mais ampla que no processo de conhecimento). Recursos possíveis:

- **Embargos de declaração** (5 dias, art. 1.023 CPC) — usar antes do agravo se há omissão, contradição, obscuridade ou erro material. Com pretensão modificativa quando a correção muda o resultado. Atenção: interrompe o prazo do agravo (art. 1.026, §1º CPC).
- **Agravo de instrumento** (15 dias, art. 1.003) — decisões em execução. Efeito suspensivo em pedido (art. 1.019, I) quando houver risco e relevância. Peça na fase de penhora, na decisão de rejeição da exceção, no indeferimento de impugnação de bloqueio.
- **Agravo interno** — contra decisão monocrática do relator no tribunal.

### E — Houve sentença nos embargos?

- Procedente: cooperativa recorre por apelação.
- Improcedente: executado recorre por **apelação** (15 dias úteis, art. 1.009). A apelação nos embargos segue para o tribunal e geralmente **não tem efeito suspensivo automático** (depende do caso e da matéria), então a execução pode seguir mesmo com a apelação.
- Parcialmente procedente: apelação da parte sucumbente em cada ponto.

### F — Houve acórdão desfavorável em TJ/TRF?

- Se há questão constitucional federal e prequestionamento: **recurso especial** (15 dias, art. 1.029). Requisitos severos: prequestionamento (súmulas 282 e 356 STF), dissídio jurisprudencial ou violação a lei federal, indicação clara do dispositivo violado. Altíssima taxa de inadmissão — exige trabalho técnico exemplar.
- Se há violação constitucional direta: **recurso extraordinário**.
- Antes do REsp/RE: **embargos de declaração** se houver vício no acórdão, para fins de prequestionamento (Súmula 98/STJ).

### G — Há ação paralela possível?

- **Ação revisional do contrato** (autônoma) — discute abusividade, revisa taxas, pede recalculação da dívida. Pode ser ajuizada paralelamente à execução. Pedido de tutela de urgência para suspender os efeitos da execução enquanto se revisa (STJ REsp 1110925, apesar de restritiva, admite em casos excepcionais).
- **Ação de repetição do indébito** — para cobrar em dobro o que foi pago indevidamente (art. 42, parágrafo único do CDC).
- **Ação declaratória de inexistência de débito** — quando o título é nulo integralmente.
- **Ação de responsabilidade civil** — danos morais e materiais por cobrança abusiva, inscrição indevida em cadastros, bloqueio injustificado.

## Tabela-resumo de peças por situação

| Situação | Peça principal | Prazo | Garantia exigida |
|---|---|---|---|
| Nulidade formal do título ou matéria de ordem pública | Exceção de pré-executividade | Sem prazo | Não |
| Citação recente, quer discutir mérito amplo | Embargos à execução | 15 dias úteis da juntada do mandado | Não obrigatória, mas sim p/ efeito suspensivo |
| Bloqueio SISBAJUD caiu | Impugnação art. 854 §3º | 5 dias | Não |
| Decisão interlocutória desfavorável | Agravo de instrumento | 15 dias úteis | Não |
| Decisão com omissão/contradição/erro | Embargos de declaração | 5 dias úteis | Não |
| Sentença nos embargos desfavorável | Apelação | 15 dias úteis | Não |
| Acórdão TJ desfavorável com dissídio | Recurso especial | 15 dias úteis | Não |
| Quer revisar contrato antes de execução | Ação revisional | Enquanto vigente | Não |
| Quer cobrar valores pagos a mais | Ação de repetição | Prescricional 3 ou 10 anos | Não |

## Combinações mais eficazes

**Estratégia "pinça" (padrão-ouro):**
1. Exceção de pré-executividade para nulidades aferíveis de plano (imediata).
2. Em paralelo, protocolar embargos à execução dentro do prazo legal, cobrindo o mérito amplo.
3. Ação revisional autônoma com tutela de urgência para suspender provisoriamente.
4. Se cair bloqueio, impugnação imediata (art. 854) e/ou agravo.

**Estratégia "escudo" (sem garantia do juízo):**
1. Exceção de pré-executividade com matéria forte.
2. Aguardar penhora para impugnar pontos adicionais.
3. Embargos só se necessário e com garantia.

**Estratégia "recuperação" (depois de bloqueio):**
1. Ativar `playbooks/03_gargalo_penhora.md` imediatamente.
2. Impugnação SISBAJUD no prazo de 5 dias.
3. Se indeferida, agravo de instrumento com efeito suspensivo.
4. Paralelamente, substituição de penhora (art. 847).

## Erros comuns a evitar

- **Não usar exceção quando cabível** por achar que só embargos servem. Perde tempo e custo.
- **Embargar sem memória de cálculo** quando o fundamento é excesso (viola art. 917, §3º — inadmissibilidade).
- **Ignorar o prazo de 5 dias** do art. 854, §3º — perde o bloqueio.
- **Agravar sem pedido de efeito suspensivo** quando o tempo importa.
- **Não prequestionar** em recurso para tribunal, inviabilizando REsp posterior.
- **Apresentar embargos de declaração meramente protelatórios** — pode gerar multa do art. 1.026, §2º CPC.

## Confirmação obrigatória com o advogado

Após identificar a peça recomendada, **sempre confirmar com o advogado** antes de redigir. Formato da confirmação:

> "Com base no diagnóstico, minha recomendação é: [peça principal] com fundamento em [teses centrais], e em paralelo [peça secundária, se cabível]. O prazo é até [data]. Se concorda, começo a redação. Quer ajustar alguma tese ou prefere estratégia diferente?"
