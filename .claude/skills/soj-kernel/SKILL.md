---
name: soj-kernel
description: >-
  Opera o Sistema Operacional Jurídico (SOJ) do escritório NASCIMENTO. Use
  quando o advogado disser qualquer comando do kernel: "novo caso", "chegou
  documento/extrato/certidão de X", "registrar decisão", "rodar G1/G2/G3",
  "status do caso X", "status do escritório", "gerar minuta", "preparar
  protocolo", "vigia de prazos" — ou qualquer pedido de trabalho sobre um
  caso em CASOS/. Encapsula os scripts de ESCRITORIO/scripts/ e as regras do
  SOJ_BLUEPRINT_v1.md para que toda sessão opere igual.
---

# SOJ Kernel — comandos padrão (blueprint, seção 7)

O dono é advogado e NÃO programa: explique em português simples, pergunte
antes de decisões importantes, e NUNCA invente fato ou lei (diante de lacuna,
pare e pergunte). Regras completas: `CLAUDE.md` da raiz + `SOJ_BLUEPRINT_v1.md`.

## Antes de qualquer comando (TODA sessão)

1. `python ESCRITORIO/scripts/vigia_prazos.py` — vigia de prazos, sempre primeiro.
2. Para trabalhar um caso: leia `CASOS/<X>/CASO.yaml` + `_views/STATUS.md` +
   cauda do `DIARIO.md`. NÃO releia a pasta inteira (Princípio: contexto mínimo).

## Comandos → o que fazer

| O advogado diz | Você faz |
|---|---|
| "novo caso" (+ pasta bagunçada) | `novo_caso.py NOME --titulo --area --modulo --comarca [--segredo]`; identifique a área sozinho (anuncie; pergunte só se ambíguo); lacre originais e registre cada documento via `receber_documento.py`; povoe CASO.yaml + INTAKE.md usando `MODULOS/<area>/checklist_documental.md` para abrir pendências; gere views; rode G1 |
| "chegou <documento> do caso X" | `receber_documento.py X <arquivo> --descricao ... [--fato F## --marca-provado] [--resolve PEN##]` + **ROTEADOR** `--tipo`: **prova** (padrão) · **peca_adversaria** (depois: análise adversarial → ESTRATEGIA — teses deles, fraquezas, pontos de ataque; alegações viram fatos `alegado_pelo_adversario`; TODA lei citada por eles passa pela BASE_LEGAL antes de entrar em defesa; prazo de resposta → PZ## `resposta: true` + vigia) · **decisao** (EXIGE `--prazo-data/--prazo-descricao` ou `--sem-prazo "motivo"` — prazo ANTES de qualquer análise; rodar vigia + Calendar em seguida) · **sentenca_favoravel** (idem + candidata ao ACERVO). Nunca copie arquivo à mão |
| caso novo com cliente RÉU/executado | `novo_caso.py ... --polo passivo` → **MODO DEFESA**: G1 ganha ITEM ZERO (prazo de resposta ativo no vigia); produto = peça de defesa; simulação adversária INVERTIDA (simular a réplica do autor) |
| **GATILHOS DE FASE (Onda 2)** — chegou contestação/sentença/trânsito/ata | Rotas extras do `--tipo`: **contestacao** (→ propõe RÉPLICA com prazo; análise adversarial; fase→postulatoria) · **sentenca** (→ propõe embargos/apelação com prazo — recurso é Tier B; fase→decisoria) · **transito** (→ propõe CUMPRIMENTO; fase→cumprimento) · **ata_audiencia** (`--audiencia-data` marca a audiência realizada + ata; colheita de audiência; fase→instrutoria). TODAS exigem `--prazo-*` ou `--sem-prazo`. Peça intermediária SEM template no módulo: gerar do zero e marcar o texto aprovado com `COLHEITA:` (candidato a template) |
| "preparar audiência do caso X em [data], tipo [instrução/conciliação]" | `preparar_audiencia.py X --data ... --tipo ...` → pasta `AUDIENCIAS/<data>_<tipo>/` com ROTEIRO (a sessão completa: perguntas por testemunha nossas/deles, pontos de ataque ao depoimento adverso, provas DOC-refs, riscos, checklist logístico) **para revisão do advogado**; PZ## no vigia; espelhar no Calendar. Depois: "chegou a ata" pela porta única |
| "relatório mensal" | `relatorio_mensal.py [--mes AAAA-MM]` → ESCRITORIO/RELATORIOS/AAAA-MM.md (novos/protocolados/encerrados; reprovações de gate E MOTIVOS; Tier B e vetos; prazos; verbetes; pendências de clientes; horas/custo de IA como ESTIMATIVA marcada) |
| "extrair template do M-NN" (peças antigas do advogado) | Fluxo: "guardar modelo" (anonimizado) → sessão destila o M-NN em PROPOSTA de template em `MODULOS/<area>/templates/` → só vira template oficial com RATIFICACAO do advogado (colheita) |
| "registrar decisão" | Decida pela árvore `MODULOS/<area>/praxe_decisoria.md`: DECISAO_SISTEMA no DIARIO com fundamento + alternativa descartada + confiança + Tier; se estiver em `decisoes_reservadas.md` (Tier B) → recomende e AGUARDE o "ok" (DECISAO_ADVOGADO) |
| "rodar G1/G2/G3" | `gate_check.py X G#` — reprovado bloqueia; gates leem CAMPOS (`excecao_prova`, bloco `declaracoes:` com ref ao DIARIO), não texto livre |
| "status do caso X" | Leia e resuma `_views/STATUS.md` (se suspeitar de desatualização: `gerar_views.py X` antes) |
| "status do escritório" | Leia `PAINEL.md` (radar de prazos no topo) |
| "gerar minuta" | Parta de `MODULOS/<area>/templates/*.md` (v1 = template preenchido do CASO.yaml); tags SOJ por parágrafo; fundamentos SÓ com verbete válido na BASE_LEGAL — pesquise apenas o que falta/venceu e vire verbete |
| "preparar protocolo" | Véspera: anti-erro fatal (`MODULOS/<area>/anti_erro_fatal.md`) + conferência final com checagem cruzada peça↔decisões → declaracoes no CASO.yaml → G3 → revisão humana assinada do advogado → `preparar_protocolo.py X` → DOCX pela skill formatacao-peticoes-nascimento (NUNCA antes da assinatura) |
| "protocolado, processo nº N" | DIARIO: EVENTO_PROCESSUAL com o número; cadastrar prazos reais (PZ##); espelhar no Calendar (anonimizado: "[SOJ] <id> · PZ##"; laboratório = "[SOJ·TESTE]"); **disparar `colher_aprendizados.py X --evento "protocolado processo N"`** |
| "encerrar caso X" | fase: encerrado no CASO.yaml + NOTA no DIARIO + **disparar `colher_aprendizados.py X --evento encerramento`** |
| "colher aprendizados do caso X" | `colher_aprendizados.py X` → `_views/PROPOSTA_DE_APRENDIZADO.md` (Tier B/vetos→árvore ou reservada; quase-erros→anti-erro; fontes revogadas/inexistentes→antiteses; desvios→variantes; verbetes→inventário). **NADA entra no módulo sem RATIFICACAO em bloco do advogado** — depois do ok, promover item a item |
| "absorver minha versão da peça" (.md/.docx) | `absorver_versao.py X <arquivo>` → diff em `_efemeros/ABSORCAO_*.md`; classificar CADA mudança: **estilo** (absorve + marca COLHEITA:) · **fato novo** (exige F## com prova/alegação) · **citação nova** (VERIFICAR NA FONTE antes de aceitar) · **quantum/pedido** (reconciliar com decisões; DECISAO_ADVOGADO com ok). Depois: re-taguear → salvar vNN (nunca sobrescrever) → DIARIO → re-rodar o gate da fase → regerar DOCX |

## MODO REVISÃO DE PEÇA (diálogo de melhoria sobre a minuta)

Comandos que ativam o modo:

- **"revisar peça [do caso X]"** — abre o diálogo de melhoria sobre a minuta
  atual (ou a vNN indicada).
- **"juiz rigoroso na vNN"** / **"adversário contra a vNN"** — diagnósticos
  rodáveis sobre QUALQUER versão. Saída SEMPRE em **lista objetiva de pontos
  atacáveis** (ponto → onde na peça → por que ataca → contramedida sugerida),
  salva em `_efemeros/DIAGNOSTICO_JUIZ_vNN.md` / `_efemeros/DIAGNOSTICO_ADVERSARIO_vNN.md`.
  Diagnóstico não altera a peça — só alimenta o diálogo.
- **"absorva este parágrafo meu e nivele o resto pelo padrão dele"** — o
  texto do advogado vira REFERÊNCIA DE ESTILO da peça: absorver o parágrafo
  e reescrever o restante no MESMO registro, sem tocar em fatos, citações ou
  quantum (que seguem as portas abaixo).
- Formato sempre aceito: **"Objetivo: X. Restrição: Y. Reescreva com isso em
  mente."** — a restrição é vinculante (ex.: "não afirmar fato sem prova").

Regras INEGOCIÁVEIS do modo:

1. **Toda mudança vira PROPOSTA antes de virar versão**: rascunho em
   `_efemeros/PROPOSTA_vNN.md` + diff apresentado ao advogado
   (`diff_pecas.py BASE PROPOSTA` — sem efeitos colaterais) ANTES de qualquer
   aprovação. Só com o ok: salvar como `MINUTA_vNN.md` (NUNCA sobrescrever),
   re-taguear, DIARIO.
2. **Classificação da porta de retorno vale dentro do modo**: estilo →
   absorve; fato novo → exige F## com prova/alegação; citação nova →
   verificar NA FONTE (verbete) antes de aceitar; quantum/pedido →
   reconciliar com as decisões (DECISAO_ADVOGADO com ok).
3. **Re-rodar o gate da fase ANTES de regerar qualquer DOCX.**
4. **Melhoria aprovada = candidata de colheita**: marcar `COLHEITA:` no
   DIARIO (vai para template/teses na próxima colheita do caso).

## MOTOR DE MÍDIA (Onda 4/F6 — WhatsApp, áudios, custódia)

- **"chegou export de conversa do WhatsApp"** → `receber_whatsapp.py X
  <pasta_do_export> --descricao ... [--fato F##]`: lacra TODOS os arquivos
  em `00_originais/whatsapp_<slug>/` com **manifesto SHA-256**, parseia o
  .txt e monta a **cronologia unificada** (mensagens + falas inline, cada
  fala apontando o arquivo de origem); áudio com sidecar `<arquivo>.txt`
  entra degravado; sem sidecar = "degravação pendente". A conversa vira P##
  (categoria conversa_whatsapp).
- **Cadeia de custódia:** TODO original que entra pela porta única ganha
  **SHA-256 na ficha** automaticamente (receber_documento e receber_whatsapp).
- **Rótulo obrigatório** em toda degravação: *"degravação de trabalho — não
  substitui perícia/ata notarial"*; se a AUTENTICIDADE do áudio/conversa for
  ponto controverso no caso → ALERTA no DIARIO: providenciar prova técnica.
- **Regras de mídia:** consentimento do cliente para gravação de atendimento
  = **entrada obrigatória no DIARIO ANTES** do áudio entrar; áudio de
  atendimento entra LACRADO em 00_originais; transcrição pronta do celular
  é aceita como RELATO (contrato de entrada).
- **Transcritor local INSTALADO (ok do advogado em 06/07/2026):**
  faster-whisper, modelo `small`, 100% nesta máquina (nenhum áudio sai do
  computador). Comandos: **"degravar a pasta do export"** (ANTES do
  receber_whatsapp — cria os sidecars `<audio>.txt`, nunca sobrescreve) e
  **"degravar o áudio X"** (avulso → `DEGRAVACAO_<nome>.md` com rótulo).
  Script: `degravar.py CAMINHO [--modelo small|medium|large-v3-turbo]
  [--sidecar]` — roda com o Python normal (se relança sozinho no ambiente
  próprio em `~/.soj/transcritor/`). Se a qualidade do `small` não bastar
  num áudio real, propor upgrade de modelo ANTES de baixar (download novo).

## PORTA DE IMPORTAÇÃO (blueprint v1.10 §7 — caso pré-trabalhado)

- **"importar caso trabalhado: [pasta]"** → `importar_caso.py CLIENTE PASTA
  --colaborador "NOME" [--area ... --modulo ... --titulo ... --comarca ...
  --polo ... --segredo --probono]`. Também dispara sozinho: se um "novo
  caso" encontrar MINUTA DE TERCEIRO na pasta, rotear para a importação.
- O que a porta faz: deduplica por SHA-256 (mantém o melhor nome; cópias
  ficam lacradas, fora do roteamento); roteia provas → P## (com hash),
  **instrumentais** (procuração ASSINADA, RG/CNH, contrato de honorários,
  hipossuficiência) → classe `instrumentais:` (provam representação, não
  fato — o G1/G3 os reconhece); rascunho de instrumental em formato
  editável → `_efemeros/importacao/`.
- **Mais de uma minuta candidata → PARE** (o script sai sem criar NADA):
  perguntar ao titular se são versões da mesma ação (reexecutar com
  `--minuta "NOME"`; as preteridas viram rascunho) ou ações distintas
  (importar em casos separados).
- **Engenharia reversa com CONFIANÇA ZERO** (na mesma sessão): fatos
  afirmados → F## cruzados com as provas anexas (sem prova = `alegado` +
  pendência); pedidos → PED##; TODA citação → BASE_LEGAL (o script já
  varre e marca revogada/vencida/não verificada — a revisão semântica
  cobre o resto); decisões embutidas (quantum, foro, tutelas) →
  `propostas_colaborador:` com `status: aguardando_ratificacao` — **o G2
  bloqueia enquanto houver proposta pendente** (item 7). A peça vira
  MINUTA_v01 (importada, com aviso) e segue os gates normais.
- Saída obrigatória: `_views/REVISAO_COLABORADOR.md` (congelado; parte
  mecânica = script; seções 4-8 — crédito, órfãos, juiz rigoroso,
  adversário, propostas — preenchidas pelo sistema NA sessão de importação).
- **GOVERNANÇA DE AUTORIA (kernel, vale para TUDO):** entradas do DIARIO e
  decisões ganham campo `origem` (titular / colaborador X / sistema) — no
  `append_diario(..., origem=...)`. Nada de colaborador vira decisão sem
  ratificação do titular (DECISAO_ADVOGADO citando o PC##).

## ACERVO DE MODELOS (ESCRITORIO/ACERVO/ — blueprint §9)

- **"guardar modelo"** → `guardar_modelo.py ARQUIVO --area ... --tipo
  peca|decisao|sentenca --origem --acao --ano --porque ... [--ressalva]
  [--resultado] [--proprio] [--anon "NOME=SUBSTITUTO"]...`
  Fluxo obrigatório da sessão ANTES do comando: ler o texto, identificar
  TODOS os nomes de terceiros e passá-los em `--anon` (a varredura mecânica
  do script cobre CPF/CNPJ/CEP/e-mail/telefone). O script RECUSA autos
  sigilosos (sem exceção) e PDFs (converter antes). Aceita decisões e
  sentenças dos processos do PRÓPRIO escritório (`--proprio`) — semente da
  praxe local.
- **REGRA DE FERRO:** modelo é professor de ESTILO e TÉCNICA, nunca de lei.
  Citação jurídica vinda de modelo só entra em peça após verificação na
  BASE_LEGAL (verbete válido) — sem verbete, a citação é BARRADA.
- **Uso sob demanda, nunca automático:** só quando o advogado pedir
  ("compare com o M-02", "inspire o capítulo X no M-03") ou na colheita
  (a proposta lista as técnicas do acervo da área como candidatas a
  destilação para template/teses — promoção só com ratificação).

## Regras duras (não negociar)

- `00_originais/` imutável · `DIARIO.md` append-only (corrigir = nova entrada)
  · `_views/` nunca à mão (`gerar_views.py`).
- Verificação com validade: verbete vencido não passa no G3; SM e afins pelo
  decreto vigente (verbete PARAM), nunca de notícia/memória.
- Alterou script? Teste TUDO em `CASOS/TESTE_FICTICIO` (laboratório
  permanente) ANTES de tocar caso real.
- `segredo_justica: true` = dados de menores: nada identificado sai deste
  ambiente; serviços externos só com id do caso + PZ##.
- Commits: automáticos a cada gate; não fazer push sem ordem.
- **REGRA DE OURO da peça:** a versão protocolada é SEMPRE a última que o
  sistema conhece — versão melhorada do advogado entra SÓ pela porta de
  retorno (absorver_versao), nunca por fora.
