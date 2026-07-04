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
