# DIÁRIO — GETULIO (caso 2026-0005)

Ledger append-only (blueprint, seção 4). NUNCA edite ou apague uma entrada:
correção é entrada NOVA referenciando a antiga. Formato e tipos de entrada:
ESCRITORIO/MODELOS/DIARIO.formato.md

---
## #001 | 2026-07-07 15:40 | NOTA
Caso criado pelo novo_caso.py. Id: 2026-0005. Area: civel. Modulo: a_definir. Complexidade: padrao. Fase: E1_intake.
---
## #002 | 2026-07-07 15:41 | AUTOS_ANEXADOS
Origem: sistema.
AUTOS ANEXADOS: Autos completos JEC Parauapebas — obrigacao de fazer (66 fls., SHA-256 8b93af204382c66290e56d7c2a85b8feaf44b88703f1152a1e259475a9d8345e). Extracao por script; OCR local nas fls. nenhuma. 28 fatias no indice (_views/AUTOS_INDICE.md). PLANO: 0 integrais (~0 tokens), 1 nunca-ler (excluidas), 27 sob demanda (~28768 tokens). Tier A (<=100 fls.): destilacao das integrais autorizada pelo D11 — fundamento: piramide da secao 13; alternativa descartada: leitura completa; confianca: alta. Midias: nenhuma. Cadeia de custodia: manifesto SHA-256 por arquivo.
---
## #003 | 2026-07-07 15:43 | EVENTO_PROCESSUAL
Audiencia de INSTRUCAO designada para 2026-07-08 11:00 (Vara do JEC de Parauapebas (hibrida - Teams Sala 2)). Roteiro para revisao do advogado em AUDIENCIAS/2026-07-08_instrucao/ROTEIRO.md. Prazo PZ01 no vigia. Proximos passos: sessao completa o roteiro (perguntas, ataques, riscos), advogado revisa, espelhar no Calendar (anonimizado). Apos a audiencia: 'chegou a ata' pela porta unica.
---
## #004 | 2026-07-07 15:46 | ALERTA
VIGIA-PRAZO PZ01 [PROXIMO]: 'AUDIENCIA de instrucao (11:00, Vara do JEC de Parauapebas (hibrida - Teams Sala 2))' vence em 2026-07-08 (em 1 dia(s), criticidade alta).
---
## #005 | 2026-07-09 11:44 | ALERTA
VIGIA-PRAZO PZ01 [VENCIDO]: 'AUDIENCIA de instrucao (11:00, Vara do JEC de Parauapebas (hibrida - Teams Sala 2))' VENCEU em 2026-07-08 (ha 1 dia(s)). Providenciar imediatamente ou registrar no CASO.yaml o status cumprido/prejudicado com justificativa.
---
## #006 | 2026-07-15 14:29 | AUTOS_ANEXADOS
Origem: sistema.
AUTOS ANEXADOS: Autos pos-audiencia de instrucao 08-07-2026 (75 fls., SHA-256 137cb8378e3807e06bab9c007a00f5893d201e25307ae5df3b19c56bbdc3bc58). Extracao por script; OCR local nas fls. nenhuma. 33 fatias no indice (_views/AUTOS_INDICE.md). PLANO: 0 integrais (~0 tokens), 1 nunca-ler (excluidas), 32 sob demanda (~34078 tokens). Tier A (<=100 fls.): destilacao das integrais autorizada pelo D11 — fundamento: piramide da secao 13; alternativa descartada: leitura completa; confianca: alta. Midias: nenhuma. Cadeia de custodia: manifesto SHA-256 por arquivo.
---
## #007 | 2026-07-15 15:05 | EVENTO_PROCESSUAL
Origem: sistema (autos pos-audiencia anexados pelo titular em 15/07; destilacao das fls. novas 67-75).
AUDIENCIA DE INSTRUCAO REALIZADA em 08/07/2026 11h (ata: fls. 71, Num. 182402245 p.1). Presentes: autor Weslley Macedo da Costa (adv. Alef Vinicius Silva dos Santos, OAB/PA 35.567, com prazo de 5 dias deferido para regularizar procuracao) e reu GETULIO (adv. titular, OAB/PA 39.261). Colhido depoimento pessoal do REU, gravado em 3 videos MP4 (Ids 183192978/183192983/183192987 — fora do PDF; acesso pelo PJe, agrupador Documentos; certidao de juntada fls. 67, 15/07). Sem outras provas orais. Autos conclusos para julgamento; audiencia encerrada 10h38 (a propria ata registra 10h38 — divergencia de horario com a abertura 11h, conferir se relevante).
SENTENCA assinada em 15/07/2026 14:02 (fls. 71-75, Num. 182402245), Juiz Liberio Henrique de Vasconcelos. Dispositivo:
- a.1) multas E010483207 (18/05/2019) e SA00034173 (12/07/2019): responsabilidade EXCLUSIVA do AUTOR (favoravel);
- a.2) IPVA principal 2020-2025: responsabilidade EXCLUSIVA do REU (desfavoravel);
- a.3) encargos moratorios do IPVA 2020-2025: 50%/50% por culpa concorrente (parcialmente favoravel);
- a.4) cumprimento coordenado em 4 etapas: E1 autor paga multas + ATPV-e (30d) -> E2 reu apresenta demonstrativo DETRAN/SEFAZ (30d) -> E3 autor deposita 50% dos encargos (15d) -> E4 reu paga IPVA integral e transfere o veiculo (30d);
- b) danos morais do autor: IMPROCEDENTE (favoravel);
- c) pedido contraposto do reu (R$ 5.000): IMPROCEDENTE — fundamento expresso: BO e declaracao unilateral e o reu "quedou-se inerte na fase de especificacao de provas, deixando precluir o direito de produzir prova testemunhal" (desfavoravel — CANDIDATO A APRENDIZADO, ver colheita);
- Sem custas/honorarios (art. 55, Lei 9.099); GRATUIDADE deferida a AMBAS as partes (relevante: dispensa preparo em eventual recurso — conferir na interposicao).
---
## #008 | 2026-07-15 15:06 | ALERTA
Origem: sistema. PZ01 (audiencia) CUMPRIDO — baixa registrada. PZ02 CRIADO em estado SUGERIDO (nunca confirmar sem o advogado — ordem do titular de 15/07/2026):
MEMORIA DE CALCULO — PZ02 · RECURSO INOMINADO · status: SUGERIDO (aguarda confirmacao)
- Ato gerador: SENTENCA parcialmente procedente — fls. 71-75 dos autos (Num. 182402245), assinada 15/07/2026 14:02.
- Termo inicial: AINDA NAO DISPARADO — sentenca nao proferida em audiencia (ata de 08/07 apenas encerrou a instrucao); intimacao se dara pela publicacao no DJEN, ainda nao ocorrida ate 15/07 ~15h. O radar diario (07h) captura a disponibilizacao real.
- Prazo: 10 dias uteis — base: art. 42 c/c art. 12-A, Lei 9.099/95 (contagem em dias uteis; ciencia pela publicacao).
- Cenarios (motor do radar, escopo TJPA, arts. 224 §§2-3 e 219 CPC): disponibilizacao 15/07 -> publicacao 16/07, inicio 17/07, VENCIMENTO 30/07/2026 | disp. 16/07 -> vence 31/07 | disp. 17/07 -> vence 03/08.
- Data registrada no PZ02: 2026-07-30 (PIOR CASO, conservador).
- Feriados considerados: nenhum nacional/estadual TJPA no periodo; recesso: nao aplicavel. Suspensoes por portaria: NAO VERIFICADAS. Feriados MUNICIPAIS de Parauapebas: NAO CADASTRADOS ainda (tabela da Etapa 2) — motivo da confianca MEDIA.
- Preparo: gratuidade deferida a ambas as partes na sentenca (conferir dispensa do preparo na interposicao).
- Peca cabivel: recurso inominado (art. 41 ss., Lei 9.099/95). Decisao de recorrer = TIER B do titular.
- Confirmado por: ______ em ______ (PENDENTE — so o advogado confirma).
---
## #009 | 2026-07-15 15:40 | DECISAO_ADVOGADO
Origem: titular. NAO RECORRER da sentenca de 15/07/2026 — fundamento do titular: "a sentenca foi favoravel". PZ02 (recurso inominado, sugerido, pior caso 30/07) passa a estado CANCELADO; a memoria de calculo fica preservada no #008 para auditoria. Nenhum recurso sera interposto pelo escritorio.
LEITURA DO SISTEMA (registro, nao objecao): o resultado e liquido favoravel — as ~15 multas alegadas cairam para 2 e ambas foram declaradas do AUTOR; danos morais do autor improcedentes; a transferencia do veiculo, travada ha 6 anos, ganhou rito com prazos. Custos assumidos: IPVA principal 2020-2025 integral do cliente (mas ele e o proprietario de fato desde set/2019 — imposto que ja seria dele), metade dos encargos moratorios e a improcedencia do contraposto de R$ 5.000.
ALERTA DE SIMETRIA: o prazo recursal do AUTOR corre igual. Se ELE recorrer, o cliente sera intimado para contrarrazoes (10 dias uteis) — o radar diario captura a publicacao; nao ha nada a fazer agora alem de vigiar.
---
## #010 | 2026-07-15 15:41 | NOTA
Origem: sistema. PZ03 criado (SUGERIDO, confianca baixa): vigilancia do cumprimento coordenado do item a.4 da sentenca. Ordem das etapas: E1 AUTOR (30 dias — pagar multas E010483207/SA00034173 de 2019 + disponibilizar ATPV-e) -> E2 CLIENTE (30 dias — demonstrativo oficial DETRAN/SEFAZ discriminando IPVA principal 2020-2025 e encargos) -> E3 AUTOR (15 dias — depositar 50% dos encargos) -> E4 CLIENTE (30 dias — pagar IPVA integral e concluir a transferencia).
CONSEQUENCIA PRATICA: o relogio do cliente (E2) so dispara APOS o cumprimento da E1 pelo autor. Nada a fazer ate o transito e ate o autor agir; a vigilancia existe para que a inercia do autor nao vire, mais tarde, alegacao de mora do cliente. Data provisoria 31/08/2026 — recalcular quando a publicacao definir o termo inicial.
APRENDIZADO CANDIDATO (aguarda ratificacao do titular): "especificacao de provas e porta que fecha" — a sentenca julgou o pedido contraposto (R$ 5.000, danos morais) improcedente com fundamento expresso na PRECLUSAO da prova testemunhal/depoimento pessoal na fase de especificacao (BO sozinho = declaracao unilateral, presuncao relativa). Regra proposta: em caso com pedido contraposto/reconvencional, a fase de especificacao de provas entra no calendario como marco proprio, com decisao registrada sobre CADA meio de prova (arrolar ou dispensar com motivo).
---
