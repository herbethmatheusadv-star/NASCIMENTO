<!--
TEMPLATE DE MINUTA — Alimentos c/c Guarda Compartilhada e Convivência
Extraído da MINUTA_v03 do caso 2026-0002 (texto APROVADO em revisão humana
integral, 04/07/2026). Fase 4 do SOJ.

COMO USAR (E3 de um caso novo):
1. Copiar para CASOS/<CLIENTE>/MINUTA_v01.md.
2. Preencher os campos {{...}} com dados do CASO.yaml (nunca digitar de novo
   o que já é dado — Princípio 2).
3. Ajustar as tags SOJ de cada parágrafo para os IDs reais do caso
   (formato: <!-- SOJ: fatos | provas | pedidos | fundamentos -->).
4. As decisões da árvore (praxe_decisoria.md) devem estar TOMADAS e no
   DIARIO antes de preencher (G2). Blocos [SE ...] são condicionais: manter
   ou remover conforme a decisão correspondente.
5. Fundamentos citados: espelhar em fundamentos_citados do CASO.yaml e
   CONFERIR A VALIDADE dos verbetes na BASE_LEGAL (o G3 cobra; ECA:art22
   tem validade de 30 dias; PARAM:SM#### muda todo ano!).
6. Markup compatível com a skill formatacao-peticoes-nascimento
   (#, ##, -, >, **negrito**). Os capítulos são numerados automaticamente
   na formatação final (I, II, ...; 1.1, 2.1, ...).
-->

**EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DE DIREITO DA VARA DE FAMÍLIA DA COMARCA DE {{COMARCA}} — ESTADO DO {{ESTADO}}**
<!-- SOJ: - | - | - | CPC:art53 -->

**PROCESSO EM SEGREDO DE JUSTIÇA** — Tramitação reservada por versar a causa sobre alimentos e guarda de crianças e adolescentes, na forma do art. 189, II, do Código de Processo Civil, restringindo-se a consulta aos autos às partes e a seus procuradores (art. 189, § 1º).
<!-- SOJ: - | - | - | CPC:art189 -->

**{{AUTORA_NOME}}**, {{AUTORA_QUALIFICACAO: nacionalidade, profissão}}, portadora do CPF n.º {{AUTORA_CPF}}, nascida em {{AUTORA_NASCIMENTO}}, residente e domiciliada em {{AUTORA_ENDERECO_COMPLETO}}{{SE ENDERECO_DECLARADO: , endereço declarado sob responsabilidade da parte — a conta de consumo do imóvel encontra-se em nome de co-residente —}}, por seu advogado que esta subscreve, **{{ADVOGADO_NOME (ADVOGADO.md)}}**, {{ADVOGADO_QUALIFICACAO}}, inscrito na OAB/{{UF}} sob o n.º {{OAB}}, com escritório profissional em {{ADVOGADO_ENDERECO}}, e-mail {{ADVOGADO_EMAIL}}, telefone {{ADVOGADO_TELEFONE}}, onde recebe intimações, vem, respeitosamente, à presença de Vossa Excelência, em nome próprio e na qualidade de representante legal de seus filhos menores **{{MENOR1_NOME}}** e **{{MENOR2_NOME}}**, propor a presente
<!-- SOJ: F(endereco) | P(cpf autora) | - | - -->

> AÇÃO DE ALIMENTOS C/C REGULAMENTAÇÃO DE GUARDA COMPARTILHADA E DE CONVIVÊNCIA, COM PEDIDO DE TUTELA DE URGÊNCIA PARA FIXAÇÃO DE ALIMENTOS PROVISÓRIOS

em face de **{{REU_NOME}}**, {{REU_QUALIFICACAO}}, portador do CPF n.º {{REU_CPF}}{{SE RG: e do RG n.º {{REU_RG}}}}, nascido em {{REU_NASCIMENTO}}, {{SE ENDERECO_CONHECIDO: residente e domiciliado em {{REU_ENDERECO}}}}{{SE ENDERECO_DESCONHECIDO: atualmente residente em {{REU_CIDADE_DECLARADA}}, em endereço desconhecido pela Autora — razão pela qual se requer, com fundamento no art. 319, §§ 1º a 3º, do CPC, as diligências necessárias à sua localização, na forma do capítulo dos pedidos}}, pelos fatos e fundamentos a seguir expostos.
<!-- SOJ: F(endereco reu) | P(qualificacao reu) | - | CPC:art319 -->

# Dos fatos

## Da união entre os genitores e da filiação dos menores

A Autora e o Réu mantiveram {{TIPO_UNIAO: união estável/casamento}} por {{PERIODO}}, da qual nasceram {{N}} filhos comuns: **{{MENOR1_NOME}}**, nascida em {{DATA}}, em {{LOCAL}}, portadora do CPF n.º {{CPF}} (DOC-01), e **{{MENOR2_NOME}}**, nascido em {{DATA}}, portador do CPF n.º {{CPF}} (DOC-02).
<!-- SOJ: F(filiacao) | P01,P02 | PED01,PED02,PED03 | - -->

A filiação paterna e materna de ambos os menores encontra-se formalmente reconhecida nas respectivas certidões de nascimento (DOC-01 e DOC-02), documentos públicos dotados de fé.
<!-- SOJ: F(filiacao) | P01,P02 | PED01,PED02,PED03 | - -->

## Da separação e da situação atual dos menores

{{QUANDO: "No ano de {{ANO}}" se a data exata for desconhecida}}, os genitores encerraram a convivência. Desde então, os menores residem exclusivamente com a Autora, em {{CIDADE}}, sob sua guarda de fato, sem que jamais tenha sido formalizado qualquer acordo de guarda ou homologado qualquer ajuste judicial a respeito. {{ROTINA: escola pública/particular; plano de saúde sim/não — conforme CASO.yaml}}.
<!-- SOJ: F(separacao),F(guarda de fato) | - | PED02 | - -->

{{SE REU_EM_OUTRA_CIDADE: O Réu, após a separação, transferiu-se para {{CIDADE_REU}}, mantendo com os filhos contato esporádico e sem periodicidade regular.}}
<!-- SOJ: F(residencia reu),F(convivencia) | - | PED02,PED03 | - -->

## Da contribuição alimentar irregular do Réu

Conforme relata a Autora, desde a separação o Réu tem prestado alimentos de forma irregular, sem periodicidade definida e em valores insuficientes para atender às necessidades dos menores. Segundo a Autora, o valor máximo por ele pago em uma única oportunidade foi de {{VALOR_MAXIMO}}, sem que tenha havido regularidade nos repasses. Não existe acordo formal, extrajudicial ou judicial, que estabeleça obrigação alimentar exigível.
<!-- SOJ: F(inadimplencia),F(sem titulo) | - | PED01 | - -->

{{SE SEM_EXTRATO (exceção de prova ratificada — praxe §citacao/decisão reservada 2): A irregularidade, nesta fase inicial, sustenta-se na declaração da Autora, sujeita a complementação probatória: a Autora diligencia a obtenção do extrato bancário dos últimos doze meses da conta na qual costumava receber os valores enviados pelo Réu, e requer, desde logo, a exibição, pelo Réu, dos comprovantes dos depósitos que alegue haver efetuado.}}
{{SE COM_EXTRATO: O extrato bancário da conta da Autora relativo aos últimos doze meses (DOC-{{NN}}) demonstra {{a ausência/irregularidade}} dos repasses.}}
<!-- SOJ: F(inadimplencia) | P(extrato, se houver) | PED01 | - -->

## Das necessidades dos menores

A Autora declara ser a provedora exclusiva dos {{N}} filhos desde a separação, arcando integralmente com as despesas necessárias à sua manutenção, educação e desenvolvimento. {{DESPESAS: listar categorias COM comprovante (DOC-NN) e narrar como declaração as sem comprovante — NUNCA somar lista informal como valor comprovado; itens pessoais do guardião ficam FORA}}.
<!-- SOJ: F(despesas) | P(comprovantes/lista) | PED01 | - -->

## Da situação econômica da Autora

A Autora exerce a função de {{PROFISSAO}} na empresa {{EMPREGADOR}}, percebendo salário mensal de **{{SALARIO}}**, conforme demonstra {{PROVA_RENDA: CTPS digital (DOC-NN)/holerite}}. {{SE CONTRATO_A_TERMO: O vínculo é por prazo determinado — circunstância que revela renda formal, porém estruturalmente precária e sujeita a interrupções periódicas, tornando imprescindível a constituição de obrigação alimentar estável em favor dos menores.}}
<!-- SOJ: F(renda autora) | P(ctps) | PED01 | - -->

{{PROPORCIONALIDADE: comparar a renda da Autora com o SM vigente e com as necessidades — ver exemplo do caso-fonte: "corresponde exatamente a um salário mínimo (R$ {{SM}} — Decreto n.º {{DECRETO}})"}}
<!-- SOJ: F(renda),F(despesas) | P(ctps) | PED01 | - -->

## Da capacidade contributiva do Réu

{{SE RENDA_CONHECIDA: O Réu percebe {{RENDA_REU}} (DOC-NN), de modo que o percentual pedido atende ao binômio necessidade-possibilidade.}}
{{SE RENDA_DESCONHECIDA (ramo §alimentos-2 da praxe): A renda atual do Réu é desconhecida pela Autora, razão pela qual se requer a expedição de ofícios para sua apuração. Registram-se os indícios objetivos: {{INDICIOS: CNH categoria, cidade, profissão conhecida — SÓ o que tem documento; indício não confirmado fica FORA}}. Não se afirma valor de renda sem base documental.}}
<!-- SOJ: F(indicios renda) | P(cnh etc.) | PED04 | - -->

## Da ausência de título executivo anterior

Não existe sentença, acordo homologado judicialmente ou instrumento extrajudicial com força executiva que estabeleça obrigação alimentar em favor dos menores. A presente ação visa à constituição de obrigação nova, exigível a partir da decisão judicial que a fixar.
<!-- SOJ: F(sem titulo) | - | PED01 | - -->

# Do direito

## Da obrigação alimentar

Dispõe o art. 1.694 do Código Civil que "podem os parentes, os cônjuges ou companheiros pedir uns aos outros os alimentos de que necessitem para viver de modo compatível com a sua condição social, inclusive para atender às necessidades de sua educação", devendo os alimentos ser fixados "na proporção das necessidades do reclamante e dos recursos da pessoa obrigada" (§ 1º) — o binômio necessidade-possibilidade, temperado pela proporcionalidade. O direito é recíproco entre pais e filhos (art. 1.696 do CC).
<!-- SOJ: F(filiacao) | - | PED01 | CC:art1694 -->

No mesmo sentido, o art. 22 do Estatuto da Criança e do Adolescente, **na redação dada pela Lei n.º 15.240/2025**, impõe: "Aos pais incumbe o dever de sustento, guarda, convivência, assistência material e afetiva e educação dos filhos menores, cabendo-lhes ainda, no interesse destes, a obrigação de cumprir e fazer cumprir as determinações judiciais." {{CONFERIR VALIDADE do verbete ECA:art22 — 30 dias!}}
<!-- SOJ: F(filiacao) | - | PED01,PED03 | ECA:art22 -->

Tratando-se de alimentandos **menores** ({{IDADES}}), sua necessidade é **presumida**, decorrendo do poder familiar — entendimento consolidado no Superior Tribunal de Justiça (v.g. REsp 1.312.706/AL): enquanto menor o alimentando, a obrigação decorre do dever de sustento inerente à parentalidade, sendo desnecessária prova específica da necessidade. {{Tese T2}}
<!-- SOJ: F(filiacao) | - | PED01 | STJ:REsp1312706 -->

## Da tutela de urgência para alimentos provisórios

Na ação de alimentos sob o rito especial, a lei impõe ao juiz a fixação liminar: "As despachar o pedido, o juiz fixará **desde logo** alimentos provisórios a serem pagos pelo devedor, salvo se o credor expressamente declarar que deles não necessita" (art. 4º da Lei n.º 5.478/1968). A norma especial cria verdadeira presunção de urgência, dispensando a demonstração autônoma dos requisitos do art. 300 do CPC — que, de todo modo, estão presentes: probabilidade do direito ({{ELEMENTOS}}) e perigo de dano ({{ELEMENTOS DO CASO}}). {{Tese T1}}
<!-- SOJ: F(filiacao),F(inadimplencia) | P01,P02 | PED01 | LEI5478:art4,CPC:art300 -->

## Da guarda compartilhada

A guarda compartilhada é a regra legal: "Quando não houver acordo entre a mãe e o pai quanto à guarda do filho, encontrando-se ambos os genitores aptos a exercer o poder familiar, será aplicada a guarda compartilhada, salvo se um dos genitores declarar ao magistrado que não deseja a guarda da criança ou do adolescente **ou quando houver elementos que evidenciem a probabilidade de risco de violência doméstica ou familiar**" (art. 1.584, § 2º, do CC, **na redação dada pela Lei n.º 14.713/2023**{{SE SEM_VIOLENCIA: — ressalva final sem incidência no caso concreto, em que não há alegação de violência}}{{SE HOUVER QUALQUER INDÍCIO DE VIOLÊNCIA: PARAR — decisão reservada nº 7}}). Compreende-se por guarda compartilhada "a responsabilização conjunta e o exercício de direitos e deveres do pai e da mãe que não vivam sob o mesmo teto" (art. 1.583, § 1º, do CC), e "a cidade considerada base de moradia dos filhos será aquela que melhor atender aos interesses dos filhos" (art. 1.583, § 3º). O poder familiar é exercido em igualdade de condições por ambos os genitores (art. 21 do ECA).
<!-- SOJ: F(guarda de fato) | - | PED02 | CC:art1583,CC:art1584,ECA:art21 -->

{{SE GENITORES_EM_CIDADES_DIFERENTES (Tese T3): A distância geográfica entre os genitores não é óbice: a Terceira Turma do STJ, no REsp 1.878.041/SP (Rel. Min. Nancy Andrighi, 2021), assentou que a guarda compartilhada "impõe o compartilhamento de responsabilidades, não se confundindo com a custódia física conjunta da prole", inexistindo impedimento à sua fixação "na hipótese em que os genitores residem em cidades, estados, ou, até mesmo, países diferentes", sendo recomendável a definição de residência principal — no caso, {{CIDADE_BASE}}, onde os menores têm rotina escolar e o cuidado cotidiano.}}
<!-- SOJ: F(guarda),F(residencia reu) | - | PED02 | STJ:REsp1878041,CC:art1583 -->

## Da regulamentação de convivência

O direito à convivência familiar é garantia fundamental dos menores (art. 19 do ECA), e a redação vigente do art. 22 do ECA inclui expressamente a **convivência** e a **assistência afetiva** entre os deveres parentais. {{REGIME conforme praxe §convivencia: consensualização + homologação, com mínimos: férias escolares, datas comemorativas, comunicação remota periódica — considerar a distância}}.
<!-- SOJ: F(convivencia) | - | PED03 | ECA:art19,ECA:art22 -->

# Da tutela de urgência — alimentos provisórios

Com fundamento no art. 4º da Lei n.º 5.478/1968 e, subsidiariamente, no art. 300 do CPC, requer a Autora a fixação imediata de alimentos provisórios em favor dos menores **{{MENORES}}**.
<!-- SOJ: F(filiacao) | P01,P02 | PED01 | LEI5478:art4,LEI5478:art1,CPC:art300 -->

**Fundamentos da urgência:**

- A filiação dos menores está documentalmente comprovada (DOC-01 e DOC-02);
- Os menores têm {{IDADES}} — necessidade presumida;
- Não existe título executivo anterior que assegure obrigação alimentar exigível;
- {{DEMAIS ELEMENTOS DO CASO: irregularidade alegada/provada; precariedade da renda do guardião; etc.}}

**Critério do pedido:** {{conforme praxe §alimentos e DECISAO_SISTEMA do caso — padrão renda desconhecida: mínimo de 30% da renda líquida mensal do Réu para os {{N}} filhos em conjunto, requerendo-se, em qualquer caso, o arbitramento judicial, observado o piso objetivo indicado a seguir}}.
<!-- SOJ: F(inadimplencia) | - | PED01 | - -->

{{SE RENDA_DESCONHECIDA: Como a renda do Réu é desconhecida neste momento, requer-se que Vossa Excelência **arbitre o valor dos provisórios com base nos indícios disponíveis nos autos** — {{INDICIOS}} —, tomando-se como **piso objetivo 30% (trinta por cento) do salário mínimo nacional POR FILHO** — {{VALOR_POR_FILHO}} para cada um, totalizando **{{TOTAL}}/mês** (salário mínimo de {{SM}} — Decreto n.º {{DECRETO — verificar PARAM:SM do ano!}}) —, até que o contraditório e a instrução permitam fixação definitiva adequada.}}
<!-- SOJ: F(indicios) | P(cnh) | PED01 | - -->

Os alimentos provisórios deverão ser depositados mensalmente, até o dia **{{DIA}}** de cada mês, na seguinte conta bancária:

> {{BANCO — Código — Agência — Conta}}

> Titular: {{TITULAR — CPF}}

# Dos pedidos

Com base nos fatos narrados e nos fundamentos de direito expostos, requer a Autora:

**A) Da Tutela de Urgência (a ser apreciada imediatamente, antes da citação):**

**1.** A **concessão de tutela de urgência**, na forma de alimentos provisórios (art. 4º da Lei n.º 5.478/1968), {{CRITERIO + PISO conforme cap. III}}, a ser depositado até o dia {{DIA}} de cada mês na conta bancária indicada, com efeitos a partir da decisão.
<!-- SOJ: F | - | PED01 | LEI5478:art4 -->

**B) Dos Pedidos Principais (mérito):**

**2.** A **condenação definitiva do Réu ao pagamento de alimentos** em favor dos menores, em valor a ser fixado {{após instrução/no percentual de...}}, com base no binômio necessidade-possibilidade (art. 1.694, § 1º, do CC), retroagindo os efeitos à data da citação, na forma do art. 13, § 2º, da Lei n.º 5.478/1968, devidos os provisórios até a decisão final (art. 13, § 3º);
<!-- SOJ: F | - | PED01 | LEI5478:art13p2,CC:art1694 -->

**3.** O estabelecimento da **guarda compartilhada legal** dos menores em favor de ambos os genitores (arts. 1.583 e 1.584, § 2º, do CC, este na redação da Lei n.º 14.713/2023), com **residência fixa dos menores junto à {{GUARDIA(O)}}** em {{CIDADE_BASE}} (art. 1.583, § 3º, do CC{{SE DISTANCIA: ; STJ, REsp 1.878.041/SP}});
<!-- SOJ: F | - | PED02 | CC:art1583,CC:art1584 -->

**4.** A **regulamentação da convivência** dos menores com o Réu (arts. 19 e 22 do ECA), {{REGIME: consensualização + homologação com mínimos / calendário detalhado}}, e, na ausência de acordo em prazo razoável, que o Juízo fixe a regulamentação preservando os melhores interesses dos menores;
<!-- SOJ: F | - | PED03 | ECA:art19 -->

**C) Dos Pedidos Subsidiários e Instrumentais:**

{{SE RENDA_DESCONHECIDA:}}
**5.** A **expedição de ofícios**, com fundamento no art. 20 da Lei n.º 5.478/1968 — que obriga as repartições públicas, "inclusive do Imposto de Renda", a prestar informações —, à Receita Federal (IRPF e cadastro do Réu), ao INSS/CNIS (vínculos e remunerações) e ao SISBAJUD (contas e movimentações);
<!-- SOJ: F | - | PED04 | LEI5478:art20 -->

**6.** Caso confirmado vínculo empregatício do Réu, o **desconto em folha de pagamento** na forma do **art. 529 do CPC** (NUNCA os arts. 16-18 da L5478 — revogados), com as especificações do § 2º;
<!-- SOJ: F | - | PED05 | CPC:art529 -->

**7.** A **concessão dos benefícios da gratuidade da justiça** à Autora (arts. 98 e 99, § 3º, do CPC; art. 1º, §§ 2º e 3º, da Lei n.º 5.478/1968; entendimento do STJ — em alimentos de menor não se exige prova de insuficiência do representante): {{SITUACAO ECONOMICA}};
<!-- SOJ: F(renda) | P(ctps) | - | CPC:art98,CPC:art99p3,LEI5478:art1,STJ:gratuidade-alimentos -->

**D) Dos Requerimentos Processuais:**

**8.** A **tramitação do processo em segredo de justiça** (art. 189, II, do CPC);
<!-- SOJ: F | - | - | CPC:art189 -->

**9.** A **citação do Réu {{NOME}}**{{SE ENDERECO_CONHECIDO: no endereço declinado}}{{SE ENDERECO_DESCONHECIDO (Tese T5): — e, considerando que o endereço atual é desconhecido (art. 319, §§ 1º a 3º, do CPC), sucessivamente: (a) tentativa no último endereço conhecido: {{ENDERECO_ANTERIOR + fonte documental}}; (b) requisição judicial de endereço nos cadastros de órgãos públicos e concessionárias (art. 256, § 3º, do CPC), inclusive pelo SERASAJUD (Termo de Cooperação Técnica CNJ n.º 015/2019); (c) citação por edital na forma do art. 5º, § 4º, da Lei n.º 5.478/1968 e, subsidiariamente, dos arts. 256 e 257 do CPC}};
<!-- SOJ: F(endereco) | - | - | CPC:art319,CPC:art256,CPC:art257,LEI5478:art5p4 -->

**10.** A **intimação do Ministério Público** (art. 178, II, do CPC — interesse de incapazes);
<!-- SOJ: F | - | - | CPC:art178 -->

**11.** O julgamento de **procedência total dos pedidos** ao final.
<!-- SOJ: - | - | PED01,PED02,PED03 | - -->

# Das provas

A Autora pretende demonstrar o alegado por todos os meios de prova em direito admitidos, requerendo desde logo: **a) documentais** (rol anexo); **b) depoimento pessoal do Réu**; **c) oitiva de testemunhas**, a serem arroladas no momento processual oportuno; **d) exibição de documentos pelo Réu** ({{recibos, extratos, IR, contratos — e comprovantes de depósitos de pensão, se a irregularidade for alegada}}); **e) informações dos ofícios judiciais** requeridos.
<!-- SOJ: - | P(principais) | PED01,PED04 | - -->

# Da gratuidade da justiça

A Autora declara, sob as penas da lei, não possuir condições de arcar com as custas e despesas processuais sem prejuízo do seu sustento e de seus filhos. {{SITUACAO: renda, nº de dependentes, ausência de contribuição do outro genitor}}. A presunção de veracidade da declaração é legal (CPC, art. 99, § 3º; Lei n.º 5.478/1968, art. 1º, §§ 2º e 3º).
<!-- SOJ: F(renda) | P(ctps) | - | CPC:art98,CPC:art99p3,LEI5478:art1 -->

# Do valor da causa

Nos termos do art. 292, III e VI, do CPC (12 prestações mensais pedidas, somados os pedidos cumulados), atribui-se à causa o valor de **{{VALOR = 12 × prestação mensal pedida/piso}}** ({{EXTENSO}}), correspondente a 12 × {{PRESTACAO}} {{MEMORIA DE CALCULO com o SM do decreto vigente}}.
<!-- SOJ: - | - | PED01 | CPC:art292 -->

# Dos requerimentos finais

Requer, por fim:

- O recebimento e processamento desta petição;
- A concessão dos benefícios da gratuidade da justiça;
- A apreciação imediata do pedido de tutela de urgência, antes da citação (art. 4º da Lei n.º 5.478/1968);
- Que as publicações e intimações sejam realizadas em nome do advogado subscritor, pelo Portal Eletrônico do {{TRIBUNAL}}, e-mail {{ADVOGADO_EMAIL}};
- A procedência de todos os pedidos, com a condenação do Réu ao pagamento das custas processuais e honorários advocatícios.

Termos em que,

Pede deferimento.

{{CIDADE}}, ____ de ______________ de {{ANO}}.

> {{ADVOGADO_NOME}}

> OAB/{{UF}} n.º {{OAB}}

# Rol de documentos

{{Gerar do CASO.yaml (view rol_documentos.md) — listar só o que EXISTE na
pasta; documentos esperados ficam como pendência (PEN##) com numeração
reservada, nunca como linha do rol}}
- DOC-01 — {{...}};
- DOC-02 — {{...}};
