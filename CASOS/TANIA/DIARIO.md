# DIÁRIO — TANIA (caso 2026-0002)

Ledger append-only (blueprint, seção 4). NUNCA edite ou apague uma entrada:
correção é entrada NOVA referenciando a antiga. Formato e tipos de entrada:
ESCRITORIO/MODELOS/DIARIO.formato.md

---
## #001 | 2026-07-04 17:47 | NOTA
Caso criado pelo novo_caso.py. Id: 2026-0002. Area: familia. Modulo: familia/alimentos_guarda_convivencia. Complexidade: padrao. Fase: E1_intake.
---
## #002 | 2026-07-04 17:55 | NOTA
[MIGRACAO F2 — 2026-07-04] Caso migrado integralmente do sistema antigo
(pasta CASO_TESTE_001, 37 arquivos, intocada como arquivo historico).
Correspondencias: fatos F-01..F-22 antigos -> F01-F14; provas P-01..P-09 antigas
-> P01-P12 (alinhadas aos DOC-NN); boleto internet DOC-08 antigo -> DOC-11/P11;
CNPJ DOC-09 antigo -> DOC-12/P12 (DOC-08/DOC-09 ficam reservados p/ extrato e
matricula, conforme o rol da minuta). Prosa consolidada: 13 arquivos de triagem
-> INTAKE.md; 8 de estrategia -> ESTRATEGIA.md; minuta_inicial_v01 -> MINUTA_v01.md
com tags SOJ (conteudo intocado).
---
## #003 | 2026-07-04 17:55 | NOTA
[HISTORICO — 31/05 a 02/06/2026] Documentos recebidos da cliente em lote:
10 arquivos + relato FATOS.txt, lacrados em 00_originais/ exatamente como
recebidos. Copias renomeadas DOC-01..07, DOC-10, DOC-11, DOC-12 em
01_documentos/; provas P01-P12 registradas no CASO.yaml com cadeia de custodia
(campo original). Conferencia humana dos CPFs ilegiveis por OCR feita em
02/06/2026 (P04, P05, P06).
---
## #004 | 2026-07-04 17:55 | CONTATO_CLIENTE
[HISTORICO — 02/06/2026] Atendimento complementar realizado. A cliente
confirmou: identidade (Tania, CPF 028.405.932-38); endereco (Rua Quatro, 46,
Primavera, Parauapebas/PA — conta de luz em nome da co-residente Eudicleia);
conta p/ deposito (Itau 341, Ag. 1019, CC 33883-7); separacao "no ano de 2024";
inexistencia de processo/acordo anterior; guarda de fato exclusiva; escola
publica; sem plano de saude; baba desconsiderada; FLASH = cartao alimentacao
da mae. Checklist documental apresentado a cliente (CHECKLIST_DOCUMENTAL_CLIENTE
do sistema antigo; regenerado agora em _views/checklist_cliente.md).
Itens que permaneceram pendentes: extrato bancario (PEN01) e matricula escolar (PEN03).
---
## #005 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Estrutura da acao: ACAO UNICA CUMULADA — alimentos
+ guarda compartilhada + regulamentacao de convivencia, com tutela de urgencia.
Fundamento: economia processual; pedidos conexos com identidade de partes e
causa de pedir proxima; rito especial da acao de alimentos comporta a cumulacao.
Alternativa descartada: acao de alimentos isolada com guarda em acao posterior —
duplicaria custos e atos processuais sem ganho de velocidade real na tutela.
Confianca: alta · Tier A · Afeta: PED01, PED02, PED03.
(Decisao tomada com o advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.1 do sistema antigo.)
---
## #006 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Alimentos: tutela de urgencia INCLUIDA; criterio =
minimo 30% da renda liquida do reu para os 2 filhos em conjunto + requerimento
de arbitramento judicial pelos indicios (renda do reu desconhecida); deposito
ate o dia 5 na conta Itau da autora; definitivos com retroacao a citacao.
Fundamento: ramo "renda desconhecida" — praxe jurisprudencial nacional para 2
filhos; presuncao de urgencia da lei especial de alimentos; indicios objetivos
(CNH-D, residencia no RJ) sustentam o arbitramento.
Alternativa descartada: valor fixo baseado nas despesas — inviavel sem
comprovantes formais (lista P07 e informal); % sobre salario minimo apenas —
menos favoravel se a renda real do reu for maior.
Confianca: alta · Tier A · Afeta: PED01.
(Decisao do advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.2.)
---
## #007 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Guarda: COMPARTILHADA LEGAL com residencia fixa dos
menores junto a mae em Parauapebas/PA. Ameacas do genitor entram apenas como
contexto narrativo — SEM salvaguardas restritivas e sem pedido cautelar.
Fundamento: compartilhada e a regra legal quando ambos os genitores sao aptos;
distancia PA-RJ inviabiliza alternancia fisica; cidade-base = onde os menores
tem rotina e cuidado principal.
Alternativa descartada: guarda unilateral — sem base fatica (ameacas sem prova,
nunca concretizadas; convivencia paterna existente e saudavel).
Confianca: alta · Tier A · Afeta: PED02.
(Decisao do advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.3.)
---
## #008 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Convivencia: proposta de CONSENSUALIZACAO entre as
partes com homologacao judicial; na falta de acordo, fixacao pelo juizo.
Minimos na peticao: ferias escolares, datas comemorativas, comunicacao remota
periodica (videochamadas), considerada a distancia PA-RJ.
Fundamento: convivencia informal ja existe e e positiva; regime consensual tem
maior adesao; posicao do genitor desconhecida.
Alternativa descartada: calendario detalhado unilateral — risco de rejeicao
e de conflito desnecessario antes do contraditorio.
Confianca: media · Tier A · Afeta: PED03.
(Decisao do advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.4.)
---
## #009 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Investigacao de renda e execucao: oficios a Receita
Federal (IRPF), INSS/CNIS e SISBAJUD; CNPJ do DOC-12 NAO mencionado na peticao
(relacao com o reu nao confirmada — os oficios ja cobrem a investigacao);
desconto em folha como pedido SUBSIDIARIO condicionado a confirmacao de vinculo.
Fundamento: nao afirmar fato sem prova (credibilidade perante o juizo); oficios
sao o meio proprio de apuracao patrimonial.
Alternativa descartada: mencionar o CNPJ como indicio — risco de comprometer a
credibilidade da peticao se a relacao nao existir.
Confianca: alta · Tier A · Afeta: PED04, PED05.
(Decisao do advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.5-3.6/3.8.)
---
## #010 | 2026-07-04 17:55 | DECISAO_SISTEMA
[HISTORICO — 02/06/2026] Requerimentos processuais: gratuidade de justica
REQUERIDA (renda R$ 1.621,00 + responsabilidade exclusiva por 2 menores);
segredo de justica requerido expressamente; citacao em cascata (endereco
anterior das certidoes -> localizacao via SERASAJUD -> edital); valor da causa
= 12x a prestacao mensal (calcular com SM vigente antes do protocolo); baba
DESCONSIDERADA (sem valor nem comprovante); data da separacao narrada como
"no ano de 2024"; sem mencao a outros filhos do reu (informacao ausente).
Fundamento: presuncao de veracidade da declaracao de insuficiencia por pessoa
natural; praxe de citacao com endereco desconhecido; regra do valor da causa
em acao de alimentos.
Alternativa descartada: nao requerer gratuidade — exporia a autora a custas
incompativeis com a renda; incluir a baba — alegacao sem qualquer comprovante.
Confianca: alta · Tier A · Afeta: PED01 e requerimentos processuais.
(Decisao do advogado em 02/06/2026 — DECISOES_REGISTRADAS.md §3.7/3.9/3.10.)
---
## #011 | 2026-07-04 17:55 | RATIFICACAO
[HISTORICO — 02/06/2026] O advogado ratificou EM BLOCO as decisoes #005, #006,
#007, #008, #009 e #010, todas tomadas e confirmadas expressamente por ele na
reuniao de definicoes de 02/06/2026 (registro historico: DECISOES_REGISTRADAS.md
do sistema antigo, blocos 1-5). Nenhum veto.
---
## #012 | 2026-07-04 17:55 | NOTA
[HISTORICO — 02/06/2026] minuta_inicial_v01 redigida no sistema antigo com
marcadores [VALIDAR]/[PESQUISAR]/[ANEXAR]. Migrada como MINUTA_v01.md com tags
SOJ por paragrafo (conteudo intocado). Excecao justificada de prova (QUADRO
FATO-PROVA-PEDIDO de 02/06/2026): PED02, PED03 e PED04 apoiam-se em fatos
narrados expressamente como declaracao da autora (F03, F04, F10, F11) — decisao
consciente de narrativa "com ressalva", sujeita a prova posterior na instrucao;
PED04 e pedido instrumental fundado justamente na ausencia de prova de renda.
PED01 NAO recebe excecao: depende do extrato (PEN01).
---
## #013 | 2026-07-04 17:55 | PESQUISA
[HISTORICO — 03/07/2026] PESQUISA_JURIDICA_v01 concluida no sistema antigo:
12 fundamentos CONFIRMADOS em fonte oficial (planalto.gov.br) — L5478 arts. 1,
4, 5§4, 13§2, 20; CPC arts. 22, 53, 98, 99§3; ECA arts. 19, 21, 22;
10 fundamentos APURADOS sem verificacao na fonte (CC 1583/1584/1694-1696;
CPC 178/189/256-257/292/300-302) — conferir antes do protocolo (PEN05);
SERASAJUD: resolucao CNJ NAO confirmada — busca manual obrigatoria (PEN05).
Espelho completo em fundamentos_citados do CASO.yaml. Na Fase 3 esta pesquisa
semeia ESCRITORIO/BASE_LEGAL/familia.md como ativo permanente do escritorio.
---
## #014 | 2026-07-04 17:55 | ALERTA
[HISTORICO — 03/07/2026] Duas descobertas criticas da pesquisa juridica:
(1) ECA art. 22 teve a redacao ALTERADA pela Lei 15.240/2025 — passa a incluir
expressamente convivencia e assistencia material/afetiva; a minuta deve citar
o texto ATUAL (favorece o pedido de convivencia); validade do verbete: 30 dias.
(2) Arts. 16-18 da Lei 5.478/68 (desconto em folha) foram REVOGADOS pelo
CPC/2015 (art. 1.072, I) — o pedido 6 da minuta NAO pode cita-los; o artigo
substituto do CPC precisa ser verificado na fonte (PEN05). Afeta: PED05.
---
## #015 | 2026-07-04 17:55 | ALERTA
[2026-07-04 — constatado na migracao] O prazo PZ01 (protocolar ate 11/06/2026,
enquanto o contrato de trabalho da autora vigia) VENCEU SEM PROTOCOLO. O STATUS
do sistema antigo nunca registrou o fato — falha que motivou o SOJ. Efeitos:
(a) a CTPS (P10) deixou de provar renda EM VIGOR; (b) a narrativa de urgencia
da minuta (§1.5 e cap. III, itens que citam o termino "iminente") esta
DESATUALIZADA e precisa ser reescrita na E3 conforme o cenario real;
(c) aberta PEN04 (confirmar com a cliente se o contrato foi renovado).
Nota: qualquer dos cenarios mantem a urgencia — o que muda e a prova de renda.
---
## #016 | 2026-07-04 17:55 | GATE
G1 executado: APROVADO. 7/7 itens. Relatorio: _views/gate_G1_2026-07-04.md
---
## #017 | 2026-07-04 17:55 | GATE
G2 executado: APROVADO. 6/6 itens. Relatorio: _views/gate_G2_2026-07-04.md
---
## #018 | 2026-07-04 17:55 | GATE
G3 executado: REPROVADO. 2/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Zero marcadores [VALIDAR]/[PESQUISAR] na minuta; Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Fundamentos na BASE_LEGAL, dentro da validade; nucleo rechecado na vespera; Checklist anti-erro fatal (modulo ainda em construcao — rodar o generico e registrar 'anti-erro' no DIARIO); Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Advogado declarou revisao humana integral da peca (DIARIO)
---
## #019 | 2026-07-04 17:56 | GATE
G3 executado: REPROVADO. 2/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Zero marcadores [VALIDAR]/[PESQUISAR] na minuta; Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Fundamentos na BASE_LEGAL, dentro da validade; nucleo rechecado na vespera; Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs registrada no DIARIO (entrada com 'CONFERENCIA' + 'valores'); Advogado declarou revisao humana integral da peca (DIARIO)
---
## #020 | 2026-07-04 17:57 | GATE
G3 executado: REPROVADO. 1/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Zero marcadores [VALIDAR]/[PESQUISAR] na minuta; Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Fundamentos na BASE_LEGAL, dentro da validade; nucleo rechecado na vespera; Checklist anti-erro fatal (modulo ainda em construcao — rodar o generico e registrar 'anti-erro' no DIARIO); Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs registrada no DIARIO (entrada com 'CONFERENCIA' + 'valores'); Advogado declarou revisao humana integral da peca (DIARIO)
---
## #021 | 2026-07-04 21:31 | CONTATO_CLIENTE
Cliente informou em 04/07/2026: (1) o contrato de trabalho FOI RENOVADO apos
11/06/2026 — resolve PEN04; aberta PEN06 (folha atualizada da CTPS digital como
comprovante); PZ01 marcado como prejudicado (perdeu o objeto); a narrativa de
urgencia da minuta (§1.5 e cap. III) sera reescrita na E3 para o cenario
"contrato renovado"; (2) o extrato bancario AINDA NAO foi obtido — PEN01 segue
aberta; (3) o endereco do reu segue desconhecido — PEN02 segue aberta.
---
## #022 | 2026-07-04 21:31 | PESQUISA
Verificacao na fonte oficial (04/07/2026): paginas do Planalto baixadas
integralmente (CC, CPC, L5478, ECA) e artigos extraidos localmente — supera a
limitacao tecnica que impediu a pesquisa de 03/07. RESULTADO:
(a) os 10 fundamentos "apurados" foram CONFIRMADOS e viraram verbetes
verificados: CC 1583, 1584, 1694 (+1695/1696), CPC 178, 189, 256, 257, 292,
300 (+302);
(b) CPC art. 529 CONFIRMADO como fundamento vigente do desconto em folha
(substituto dos revogados arts. 16-18 da L5478) — PED05 fundamentado;
(c) SERASAJUD: NAO existe resolucao do CNJ — o sistema opera pelo Termo de
Cooperacao Tecnica CNJ n. 015/2019; ancora legal do pedido de localizacao =
CPC art. 256, §3º (requisicao de endereco em cadastros publicos);
(d) DIVERGENCIAS contra a pesquisa de 03/07: CC 1584 §2º tem redacao NOVA
(Lei 14.713/2023 — excecao de violencia domestica; o texto apurado era o
anterior a 2023); CC 1583 §2º vigente TERMINA em "interesses dos filhos"
(incisos transcritos pela pesquisa estao revogados desde 2014); L5478 art. 20
tem texto diverso do transcrito (menciona expressamente o Imposto de Renda);
L5478 art. 4 contem "desde logo" (omitido) e a pagina grafa "As despachar"
[sic]; L5478 art. 13 §1º trata de REVISAO de provisorios (nao de desconto em
folha como transcrito); CPC 257, I fala em "presenca das circunstancias
autorizadoras". Verbetes completos: ESCRITORIO/BASE_LEGAL/familia.md.
Resolve: PEN05 (o item "valor da causa" fica coberto pelo marcador [VALIDAR
VALOR DA CAUSA] da minuta, a calcular na E3 com o salario minimo vigente).
---
## #023 | 2026-07-04 21:31 | NOTA
Excecao justificada de prova — PED05 (desconto em folha): pedido SUBSIDIARIO e
instrumental, expressamente condicionado a confirmacao futura de vinculo
empregaticio do reu; nao depende de prova previa de F05 (mesma logica da
excecao do PED04 registrada em #012). Fundamento verificado: CPC art. 529.
---
## #024 | 2026-07-04 21:34 | GATE
G3 executado: REPROVADO. 3/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Zero marcadores [VALIDAR]/[PESQUISAR] na minuta; Checklist anti-erro fatal (modulo ainda em construcao — rodar o generico e registrar 'anti-erro' no DIARIO); Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs registrada no DIARIO (entrada com 'CONFERENCIA' + 'valores'); Advogado declarou revisao humana integral da peca (DIARIO)
---
## #025 | 2026-07-04 21:35 | GATE
G3 executado: REPROVADO. 2/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Zero marcadores [VALIDAR]/[PESQUISAR] na minuta; Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Checklist anti-erro fatal (modulo ainda em construcao — rodar o generico e registrar 'anti-erro' no DIARIO); Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs registrada no DIARIO (entrada com 'CONFERENCIA' + 'valores'); Advogado declarou revisao humana integral da peca (DIARIO)
---
## #026 | 2026-07-04 22:25 | PESQUISA
Verificacoes complementares na fonte (04/07/2026, E3):
(a) CPC art. 319, §§1º-3º CONFIRMADO (arquivo oficial ja baixado): permite
ajuizar sem os dados completos do reu, requerendo diligencias judiciais, e
veda o indeferimento da inicial quando a exigencia inviabilizar o acesso a
justica — base legal do cenario "protocolar ja" (com CPC art. 256 §3º);
(b) SALARIO MINIMO 2026 verificado na norma: R$ 1.621,00 (Decreto nº 12.797,
de 23/12/2025, art. 1º, planalto.gov.br) — ATENCAO: noticia da Camara citava
R$ 1.631, mas era o projeto de orcamento; vale o decreto. Valor da causa:
12 x 30% x 1.621,00 = R$ 5.835,60 (CPC 292, III e VI);
(c) JURISPRUDENCIA verificada em fonte oficial do STJ e incorporada a
BASE_LEGAL/familia.md: REsp 1.878.041/SP (guarda compartilhada com genitores
em cidades diferentes — 3a Turma, Nancy Andrighi, 2021; noticia oficial
stj.jus.br 23/06/2021); REsp 1.312.706/AL (presuncao de necessidade do
alimentando menor; inteiro teor oficial); tese de que a gratuidade em acao de
alimentos de menor nao exige prova de insuficiencia do representante
(noticia oficial stj.jus.br). NAO VERIFICADO (nao citado na minuta): patamar
de 30% p/ 2 filhos no TJPA — tratado como praxe forense + arbitramento.
---
## #027 | 2026-07-04 22:25 | DECISAO_SISTEMA
MINUTA_v02 redigida (E3), substituindo a v01. O que mudou:
(1) TODOS os fundamentos legais incorporados com texto verificado na fonte —
zerados os 25 marcadores [VALIDAR]/[PESQUISAR]; citada SEMPRE a redacao
vigente (CC 1584 §2º com a Lei 14.713/2023; ECA 22 com a Lei 15.240/2025;
CPC 529 no desconto em folha; CPC 319/256 §3º + SERASAJUD-TCT 015/2019 na
citacao; L5478 arts. 1, 4, 5 §4, 13 §2, 20);
(2) narrativa de urgencia REESCRITA para o cenario "contrato renovado":
urgencia fundada na presuncao legal (L5478 art. 4), na precariedade
estrutural do vinculo a termo e na renda materna de 1 SM — nao mais no
termino iminente do contrato;
(3) valor da causa fixado: R$ 5.835,60 (12 x R$ 486,30 = 30% do SM 2026);
(4) jurisprudencia: apenas a verificada (REsp 1.878.041/SP; REsp 1.312.706/AL;
tese de gratuidade) — sem citacao de patamar TJPA nao verificado;
(5) qualificacao do advogado preenchida (ADVOGADO.md); testemunhas "a arrolar
no momento oportuno"; honorarios de sucumbencia REQUERIDOS (praxe).
Fundamento: incorporacao mecanica de pesquisa verificada + decisoes ja
ratificadas (#005-#011); praxe forense nos pontos acessorios.
Alternativa descartada: manter marcadores ate a jurisprudencia TJPA — atrasaria
a peca sem ganho (a tese nacional verificada cobre a argumentacao).
Confianca: alta · Tier A (ratificacao em bloco no proximo gate) ·
Afeta: PED01-PED05, valor_causa. Marcadores remanescentes (legitimos):
[ANEXAR DOCUMENTO] extrato/matricula/CTPS-renovacao e [INSERIR DATA DO
PROTOCOLO] — dependem de PEN01/PEN03/PEN06 e da vespera.
---
## #028 | 2026-07-04 22:25 | DECISAO_SISTEMA
DESTRAVAMENTO DO PROTOCOLO — cenarios analisados (aguarda decisao do advogado):

CENARIO A — PROTOCOLAR JA (sem extrato e sem endereco do reu):
Base legal verificada: CPC art. 319 §§1º-3º (inicial sem os dados do reu +
diligencias) c/c art. 256 §3º (requisicao de endereco em cadastros publicos,
via SERASAJUD-TCT CNJ 015/2019) — pedido 9 da MINUTA_v02 ja formulado assim;
inadimplencia narrada como alegacao + exibicao de comprovantes pelo reu +
oficios (pedidos 5 e V-d). O que muda na peca: nada — a v02 ja esta pronta
para este cenario. Riscos: (i) provisorios arbitrados conservadoramente sem o
extrato (mitigado: parametro objetivo de 30% do SM ja sugerido); (ii) citacao
pode demorar (mitigado: cascata endereco anterior -> SERASAJUD -> edital).
Ganho decisivo: os alimentos RETROAGEM A DATA DA CITACAO (L5478 art. 13 §2º)
— cada mes sem protocolo e um mes de alimentos que os menores perdem para
sempre; protocolar ja poe o relogio da citacao para correr.

CENARIO B — PROTOCOLAR SO COM O EXTRATO (PEN01):
Ganho: urgencia documentada (extrato vazio = prova direta da irregularidade);
provisorios tendem a vir menos conservadores. Custo: espera indefinida (a
cliente ainda nao obteve o documento) SEM retroacao compensatoria — o tempo
perdido nao volta. O que mudaria na peca: §1.3 afirmaria a irregularidade
como comprovada (DOC-08) em vez de alegada.

CENARIO C — AGUARDAR TUDO (extrato + endereco):
Ganho marginal sobre B (citacao pessoal imediata, sem cascata). Custo maximo
de tempo; o endereco pode simplesmente nunca ser obtido extrajudicialmente —
e exatamente para isso existem o art. 256 §3º e o SERASAJUD em juizo.

RECOMENDACAO DO SISTEMA: CENARIO A. Fundamento: a retroacao a citacao
(L5478 13 §2º) torna o tempo o fator dominante; a lei autoriza expressamente
o ajuizamento sem os dados do reu (CPC 319 §§1º-3º); a fragilidade probatoria
da inadimplencia e mitigavel em juizo (exibicao + oficios) e o extrato pode
ser juntado a qualquer momento como DOC-08. Alternativa descartada: cenarios
B e C — trocam meses de alimentos das criancas por conforto probatorio que o
processo obtem por outros meios.
Confianca: alta · TIER B — decisao reservada: AGUARDA O "OK" EXPRESSO DO
ADVOGADO (registrar DECISAO_ADVOGADO citando esta entrada). Afeta: momento do
protocolo; PEN01/PEN02 (deixariam de bloquear o G3 se aprovado o cenario A,
convertendo-se PEN02 em diligencia judicial e PEN01 em juntada posterior).
---
## #029 | 2026-07-04 22:27 | GATE
G3 executado: REPROVADO. 3/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Checklist anti-erro fatal generico executado — modulo em construcao (declaracoes.anti_erro_fatal); Rol = arquivos da pasta = referencias DOC-NN na peca; Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs (declaracoes.conferencia_final); Advogado declarou revisao humana integral da peca (declaracoes.revisao_humana_integral)
---
## #030 | 2026-07-04 22:27 | GATE
G3 executado: REPROVADO. 4/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) ou tem excecao no DIARIO; Checklist anti-erro fatal generico executado — modulo em construcao (declaracoes.anti_erro_fatal); Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final de valores/datas/nomes/CPFs (declaracoes.conferencia_final); Advogado declarou revisao humana integral da peca (declaracoes.revisao_humana_integral)
---
## #031 | 2026-07-04 22:37 | DECISAO_ADVOGADO
RATIFICACAO DA TIER B #028 — DECISAO DO ADVOGADO: OK, CENARIO A (protocolar
ja, sem extrato e sem endereco do reu), CONDICIONADO a:
(1) VALOR DA CAUSA reconciliado com a decisao de alimentos ANTES de qualquer
ato de vespera — constatada divergencia entre fontes historicas (30 por cento
TOTAL na DECISOES_REGISTRADAS de 02/06/2026, migrada como #006, base da v02;
30 por cento POR FILHO no exemplo do blueprint): questao SUBMETIDA ao advogado
com explicacao; a peca NAO sera alterada ate a resposta;
(2) evento do Calendar conferido: era a meta interna ficticia do
caso-laboratorio TESTE_FICTICIO (PZ01, 31/07) — rotulo corrigido para
[SOJ-TESTE] com descricao explicita;
(3) PEN02 convertida em diligencia judicial (pedido 9-b da MINUTA_v02: CPC
319 par.1 + 256 par.3 + SERASAJUD); PEN01 (extrato) e PEN03 (matricula)
reclassificadas como JUNTADA POSTERIOR (DOC-08/DOC-09 reservados); UNICA
pendencia de protocolo: PEN06 (CTPS renovada — ja cobrada da cliente);
(4) nova regra do G3 (ja gravada pelo advogado no blueprint, secao 6, item 8):
conferencia final INCLUI checagem cruzada peca-decisoes — todo valor,
percentual ou quantum da minuta deve bater com a DECISAO_SISTEMA de origem;
implementada no gate_check nesta data;
(5) vespera do protocolo somente apos resolvida a condicao (1); DOCX no
timbrado somente apos revisao humana integral assinada; Fase 4 autorizada a
iniciar quando a peca congelar.
Afeta: PED01 (excecao de prova ratificada — irregularidade como alegacao com
exibicao e oficios), PEN01, PEN02, PEN03, PEN06, valor_causa, G3.
---
## #032 | 2026-07-04 22:38 | GATE
G3 executado: REPROVADO. 5/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Checklist anti-erro fatal generico executado — modulo em construcao (declaracoes.anti_erro_fatal); Nenhuma pendencia aberta com bloqueia: [G3]; Conferencia final + checagem cruzada peca-decisoes (declaracoes.conferencia_final c/ cruzada_com_decisoes; valor da causa confere); Advogado declarou revisao humana integral da peca (declaracoes.revisao_humana_integral)
---
## #033 | 2026-07-04 22:51 | DECISAO_ADVOGADO
DECISAO RETIFICADORA DO QUANTUM (Tier B decidida pelo advogado — opcao c),
retificando o criterio da #006 (ratificada em #011), no ambito do cenario A
(#028, ok condicionado em #031):
(1) PEDIDO PRINCIPAL mantido: minimo de 30 por cento da renda liquida do reu
para os DOIS filhos em conjunto (fiel a decisao historica de 02/06/2026);
(2) PISO OBJETIVO ELEVADO no cenario de renda desconhecida: arbitramento com
piso de 30 por cento do salario minimo POR FILHO — R$ 486,30 cada, total
R$ 972,60 mensais (SM 2026 = R$ 1.621,00, Decreto 12.797/2025, verificado na
fonte em 04/07 — verbete PARAM:SM2026);
(3) VALOR DA CAUSA recalculado pelo parametro: 12 x R$ 972,60 = R$ 11.671,20
(CPC art. 292, III c/c VI, ambos verificados na fonte em 04/07);
(4) CTPS ANTIGA (DOC-10) mantida como prova de renda da autora na inicial —
PEN06 (folha atualizada) reclassificada como JUNTADA POSTERIOR, deixando de
bloquear o protocolo;
(5) consequencias: MINUTA_v03 (cap. III criterio e parametro; Pedido 1;
cap. VII; §1.5 sem marcador de anexo da renovacao), caso.valor_causa e
PED01.parametro atualizados; vespera do protocolo liberada.
Afeta: PED01, valor_causa, PEN06, MINUTA_v03.
---
## #034 | 2026-07-04 22:53 | NOTA
CHECKLIST ANTI-ERRO FATAL executado sobre a MINUTA_v03 (generico do G3 +
itens conhecidos do modulo familia em construcao) — TODOS CONFERIDOS:
1. Competencia = domicilio do alimentando: enderecada a Vara de Familia de
   Parauapebas/PA com nota expressa do CPC art. 53, II. OK
2. MP como custos legis: pedido 10 (CPC art. 178, II — interesse de incapaz). OK
3. Alimentos provisorios pedidos EXPRESSAMENTE: cap. III + pedido 1 (L5478
   art. 4, desde logo). OK
4. Segredo de justica requerido: preambulo + pedido 8 (CPC art. 189, II). OK
5. Percentual sobre base correta: principal = 30 por cento da renda LIQUIDA do
   reu p/ os 2 filhos; piso = 30 por cento do SM POR FILHO (R$ 972,60) —
   conforme #006 retificada por #033. OK
Genericos: nenhuma lei citada sem verbete verificado na BASE_LEGAL (OK);
nenhum fato afirmado como provado sem prova — alegacoes narradas como
declaracao da autora (OK); CNPJ OGP/DOC-12 NAO mencionado na peca, conforme
#009 (OK — unico CNPJ citado e o do empregador da autora, URM); rol = 8
documentos existentes, DOC-08/09 apenas reservados (OK).
---
## #035 | 2026-07-04 22:53 | NOTA
CONFERENCIA FINAL da MINUTA_v03 — valores, datas, nomes e CPFs conferidos
contra os documentos e fonte da verdade, e CHECAGEM CRUZADA peca-decisoes:
DADOS x DOCUMENTOS: Tania Silva Rodrigues CPF 028.405.932-38 nasc. 15/09/1993
(DOC-04/DOC-10); salario R$ 1.621,00 (DOC-10); conta Itau 341/Ag.1019/
CC 33883-7 (confirmada pela cliente em 02/06 — #004); endereco Rua Quatro 46
Primavera CEP 68.515-000 (declarado — #010); reu Cicero CPF 014.640.832-23
RG 7213033 SSP/PA nasc. 02/04/1992 Timbiras/MA (DOC-03/certidoes); Jullia
nasc. 15/09/2014 CPF 079.215.852-05 (DOC-01/DOC-06); Cicero Jr. nasc.
11/06/2018 CPF 074.003.542-80 (DOC-02/DOC-05); endereco anterior de citacao
Rua G-13 Qd.148 Lt.35 Ipiranga (certidoes); termo do contrato 11/06/2026
(DOC-10). TODOS CONFEREM.
CRUZADA PECA x DECISOES: PED01 (30 por cento renda liquida + piso 972,60) x
#006/#033 OK; PED02 (compartilhada legal, residencia materna, sem salvaguardas)
x #007 OK; PED03 (consensualizacao + minimos) x #008 OK; PED04 (3 oficios, sem
CNPJ) x #009 OK; PED05 (subsidiario, CPC 529) x #009/#022 OK; gratuidade/
segredo/citacao em cascata/honorarios x #010/#027 OK; valor da causa
R$ 11.671,20 x #033 OK (12 x 972,60; CPC 292 III c/c VI). NENHUMA DIVERGENCIA.
---
## #036 | 2026-07-04 22:54 | GATE
G3 executado: REPROVADO. 8/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
Itens reprovados: Advogado declarou revisao humana integral da peca (declaracoes.revisao_humana_integral)
---
## #037 | 2026-07-04 22:58 | DECISAO_ADVOGADO
REVISAO HUMANA INTEGRAL DA PECA — declaracao do advogado (D11, ato humano
obrigatorio): o advogado Herbeth Matheus Mendonca do Nascimento (OAB/PA 39.261)
declara ter realizado a revisao humana integral da MINUTA_v03 nesta data, com
apoio do relatorio de revisao (_efemeros/RELATORIO_REVISAO_MINUTA_v03.md),
e APROVA o texto para protocolo, sem ajustes. A peca sai sob sua
responsabilidade e assinatura (Estatuto da OAB). Texto CONGELADO — a partir
daqui, alteracao = nova versao + nova revisao. Referencias: #027 (v02), #031
(cenario A), #033 (quantum), #034 (anti-erro), #035 (conferencia cruzada).
Autoriza: G3, preparar_protocolo e geracao do DOCX no timbrado. Fase 4
liberada (template a colher da v03 aprovada).
---
## #038 | 2026-07-04 22:58 | GATE
G3 executado: APROVADO. 9/9 itens. Relatorio: _views/gate_G3_2026-07-04.md
---
## #039 | 2026-07-04 22:58 | NOTA
Pacote de protocolo montado em PROTOCOLO/ a partir de MINUTA_v03.md (10 documento(s), tags SOJ removidas). Proximo passo: formatar em DOCX timbrado (skill formatacao-peticoes-nascimento), protocolar e registrar EVENTO_PROCESSUAL.
---
## #040 | 2026-07-04 23:04 | NOTA
DOCX NO TIMBRADO GERADO (skill formatacao-peticoes-nascimento, apos a revisao
humana integral #037 e o G3 aprovado #038):
PROTOCOLO/PETICAO INICIAL - TANIA - ALIMENTOS GUARDA E CONVIVENCIA.docx
(Century Gothic 11, timbrado oficial, titulos I-IX, 103 paragrafos).
Fonte: MINUTA_v03 congelada, via peticao_markup.md. Adaptacoes DE FORMA (sem
alteracao de conteudo juridico): remocao das anotacoes internas (caixas de
comentario, marcadores [ANEXAR], nota de competencia sob o enderecamento),
data do fecho em branco para preenchimento no protocolo, rol convertido de
tabela para lista numerada, dados bancarios centralizados. Quantum conferido
no DOCX: piso R$ 972,60 e valor da causa R$ 11.671,20 presentes.
PROXIMOS PASSOS DO ADVOGADO: (1) preencher a data; (2) protocolar no PJe/TJPA
com os DOC-01..07 e DOC-10 da pasta PROTOCOLO/; (3) registrar
EVENTO_PROCESSUAL com numero do processo; (4) cadastrar os prazos reais
(PZ##) — o vigia e o Calendar assumem dali em diante.
---
## #041 | 2026-07-06 15:01 | DECISAO_ADVOGADO
DECISAO DO ADVOGADO (auditoria da Onda 1/F6): contrato de honorarios NAO
bloqueia o protocolo — e regularizavel em qualquer fase do processo.
Efeitos: (1) regra do kernel retificada: a pendencia padrao do intake nasce
com prioridade alta e bloqueia: [] (novo_caso.py, blueprint secao 13,
LEIA-ME); (2) neste caso (migrado antes da regra): aberta PEN07 para
regularizar o contrato da cliente, SEM bloquear nada; (3) bloco financeiro
deste caso segue vazio ate o advogado informar os dados reais do contrato
(tipo/valor/parcelas) — nada sera inventado.
---
