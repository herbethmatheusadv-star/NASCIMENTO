# PROMPT-MESTRE — SOJ OPERACIONAL v1 (Fase 0)

**Sistema Operacional Jurídico · Nascimento Advocacia · Parauapebas/PA · OAB 39261/PA**

> **Como usar (instrução para o advogado):** salve este arquivo na raiz do repositório do MVP (o radar DJEN). Abra o Claude Code nessa pasta e envie:
> *"Leia o PROMPT_MESTRE_SOJ_OPERACIONAL.md por inteiro e execute a Etapa 0 (Reconhecimento). Não escreva nenhum código antes de eu aprovar o Relatório de Reconhecimento."*

---

## 0. Sua missão (Claude Code, leia como constituição)

Você vai transformar o MVP existente — um radar de intimações DJEN + conciliação DataJud com cálculo de prazos em modo sombra — no **SOJ Operacional**: o sistema de gestão completo de um escritório de advocacia solo com **menos de 20 processos**, ativos em **TJPA, TJMA e TRT-8** (todos PJe, todos publicando no DJEN).

O sistema existe para responder, todos os dias, uma única pergunta:

> **"Qual é a próxima ação necessária em cada cliente, caso e processo?"**

Se algo não tem próxima ação definida, está fora de controle — mesmo que esteja cadastrado.

**As seis dores a resolver:** (1) controle de processos; (2) controle do que ainda não foi protocolado; (3) gestão de clientes, procurações e documentos; (4) honorários e faturamento; (5) memória jurídica — teses, modelos, aprendizados; (6) **a dor central: prazos perdidos por paralisia** — o advogado detecta a intimação, mas trava por não saber qual peça cabe. O sistema combate isso não avisando "existe um prazo", e sim dizendo: *"existe um prazo, esta é a razão, estas são as opções, esta é a medida mais segura, estes são os documentos — e a sua análise está atrasada desde D-8"*.

**Filosofia de construção:** arquivos markdown antes de banco de dados · modo sombra antes de automação · disciplina antes de inteligência · estender o que existe antes de reescrever. Este documento é a constituição da construção. Ambiguidade ou conflito → **pergunte ao advogado**; nunca decida sozinho em zona vermelha.

---

## 1. Princípios inegociáveis

### 1.1 As Seis Regras (devem virar código no Auditor, §6)

- **R1** — Nenhum caso ou processo existe sem: `status` + `proxima_acao` + `data_interna`. Violação = alerta vermelho no briefing.
- **R2** — Nenhum prazo fatal existe como *confirmado* sem: documento gerador + memória de cálculo + confirmação humana explícita.
- **R3** — Nenhum cliente com status `contratado` permanece sem: contrato + procuração + checklist documental + forma de pagamento.
- **R4** — Nenhuma peça é dada como protocolada sem: revisão + conferência de pedidos + conferência de anexos + verificação do prazo + confirmação do protocolo (nº/recibo).
- **R5** — Nenhum conteúdo produzido por IA entra no banco institucional (`status: aprovado` ou superior) sem aprovação humana registrada.
- **R6** — Nenhum processo é encerrado sem: conferência financeira + registro do resultado + extração de ≥1 aprendizado + comunicação ao cliente + arquivamento.

### 1.2 Modo sombra (permanente na Fase 0)

Automação **detecta e sugere; o humano confirma**. Nenhum prazo nasce confirmado. Nenhuma mensagem sai automaticamente para cliente. **Protocolo automático não existe nesta fase — nunca.**

### 1.3 Fronteira MECÂNICO × ANALÍTICO (Doutrina de Análise)

- **Mecânico** (capturar, deduplicar, rotear, gerar views, conferir existência): economia máxima de tokens e complexidade.
- **Analítico** (Analista Processual, estratégia, revisão de peça): **profundidade é o produto** — modelo mais capaz disponível, raciocínio em quatro passadas (mapear → aprofundar → adversariar a si mesmo → sintetizar), toda afirmação ancorada em elemento concreto do caso.
- Na Etapa 0, procure na máquina `DOUTRINA_ANALISE.md`, a skill `soj-kernel` ou pasta `ESCRITORIO/` já existente. Se existirem, **integre-as como norma superior** a esta seção; se não, esta seção vale como versão mínima.

### 1.4 Anti-alucinação

Toda afirmação do Analista cita a origem (nº da comunicação DJEN, arquivo em `AUTOS/`, página). Precedente só entra em minuta se vier de `CONHECIMENTO/PRECEDENTES/` com status ≥ aprovado, ou com verificação explícita na fonte oficial. **"Não sei / faltam os autos" é resposta válida e preferível a inventar.** Nível de confiança é obrigatório em toda análise e todo prazo.

### 1.5 Privacidade, backup e fuso

- Dados de cliente ficam na máquina. Saídas de rede permitidas: APIs oficiais (DJEN/Comunica, DataJud), API da Anthropic para análise, e o remoto git **privado**.
- Git obrigatório: commit ao fim de cada etapa, com mensagem descritiva. `AUTOS/` (PDFs) fica fora do git (`.gitignore`) e ganha um script de backup semanal zipado + cifrado para a pasta de nuvem que o advogado indicar.
- Todos os horários e crons: **America/Belem**.

---

## 2. ETAPA 0 — Reconhecimento (antes de qualquer código)

1. Mapeie o repositório do MVP: onde estão a coleta DJEN, a conciliação DataJud, o cálculo de prazo e a geração do relatório; qual o armazenamento atual (SQLite? JSON?); quais dependências.
2. Localize o vault Obsidian do advogado e **pergunte** onde o SOJ deve morar. Padrão sugerido: subpasta `ESCRITORIO/` dentro do vault (o Obsidian vira a interface; nenhuma tela web será construída).
3. Procure e liste o que será reaproveitado: `soj-kernel`, `DOUTRINA_ANALISE.md`, skills existentes (`formatacao-peticoes-nascimento`, `advogado-bancario-cooperativas`, `peticao-negativacao-aguas-do-para`), modelos e teses avulsos.
4. Verifique na API Comunica a sigla correta do TRT-8 (teste `siglaTribunal=TRT8` e variações) e confirme que a OAB 39261/PA retorna resultados nela.
5. Entregue um **Relatório de Reconhecimento**: o que existe, o que será reaproveitado, árvore de pastas final proposta, riscos e dúvidas. **PARE e aguarde aprovação.**

---

## 3. Modelo de dados — Cliente ≠ Caso ≠ Processo

Três entidades distintas. Um **cliente** tem N casos. Um **caso** (o problema jurídico contratado) existe antes de qualquer protocolo e pode ter 0, 1 ou vários **processos** (a execução + os embargos + o agravo = 1 caso). "Iniciais pendentes" não é uma pasta: é um *status* do caso.

### 3.1 Estrutura de pastas

```
ESCRITORIO/
├── CLIENTES/                  # 1 ficha por cliente (CLI-0001.md)
├── CASOS/                     # 1 ficha por caso (CASO-0001.md) — entidade central
├── PROCESSOS/                 # 1 ficha por processo (PROC-0001.md)
├── INBOX/                     # 1 nota por intimação nova — deve ser zerado diariamente
├── AUTOS/<numero-processo>/   # PDFs dos autos (fora do git; backup próprio)
├── FINANCEIRO/
│   ├── contratos/             # CTR-0001.md
│   ├── lancamentos.md         # razão append-only
│   └── RELATORIOS/            # AAAA-MM.md
├── CONHECIMENTO/
│   ├── TESES/  MODELOS/  PRECEDENTES/  CHECKLISTS/  ESTRATEGIAS/  APRENDIZADOS/
├── BRIEFINGS/                 # AAAA-MM-DD.md
└── _SISTEMA/
    ├── templates/  prompts/  config/  bases/  logs/
```

### 3.2 Frontmatter canônico — CLIENTE

```yaml
---
tipo: cliente
id: CLI-0001
nome: 
cpf_cnpj: 
telefone: 
email: 
endereco: 
origem: indicacao | instagram | balcao | outro
status: prospecto | ativo | inativo
contrato: assinado | pendente | nao-aplicavel
procuracao: assinada | pendente
hipossuficiencia: assinada | pendente | nao-aplicavel
forma_pagamento: 
casos: ["[[CASO-0001]]"]
docs_pendentes:
  - "extrato bancário (solicitado 2026-07-01 via WhatsApp)"
ultima_atualizacao_enviada: 2026-07-10
---
```

Corpo: dados de contato ampliados, histórico de comunicações relevantes, observações.

### 3.3 Frontmatter canônico — CASO

```yaml
---
tipo: caso
id: CASO-0001
cliente: "[[CLI-0001]]"
area: bancario | consumidor | trabalhista | familia | civel | previdenciario | outra
status: novo-contato | triagem | proposta-enviada | contratado | documentos-pendentes |
        em-analise | estrategia-definida | em-elaboracao | em-revisao |
        pronto-para-protocolo | protocolado | encerrado
resumo_do_problema: 
valor_estimado: 
processos: []                      # links [[PROC-XXXX]] quando existirem
proxima_acao: 
data_interna: 2026-07-20           # prazo autoimposto — cidadão de 1ª classe no briefing
prescricao_ou_limite:              # o prazo invisível (prescrição, decadência, promessa ao cliente)
impedimento:                       # o que está travando (ex.: falta extrato do cliente)
contrato: "[[CTR-0001]]"
docs_necessarios: []
docs_recebidos: []
---
```

Corpo: tese pretendida, estratégia, anotações de triagem.

### 3.4 Frontmatter canônico — PROCESSO

```yaml
---
tipo: processo
id: PROC-0001
numero: 0000000-00.0000.0.00.0000
caso: "[[CASO-0001]]"
cliente: "[[CLI-0001]]"
polo_cliente: ativo | passivo
parte_adversa: 
tribunal: TJPA | TJMA | TRT8
sistema: PJe
grau: 1 | 2
orgao: 
classe: 
valor_causa: 
fase: pre-processual | conhecimento | instrucao | sentenciado | recurso | execucao | arquivado
situacao: ativo | suspenso | encerrado
risco: baixo | medio | alto
sigiloso: false
prazo_em_curso: false
proxima_acao: 
data_interna: 
ultima_movimentacao: 
ultima_revisao_humana: 
---
```

**Corpo padrão da ficha de processo (seções obrigatórias, nesta ordem):**

1. **Resumo executivo** — 3 a 6 linhas, sempre atualizado.
2. **SITUAÇÃO ATUAL** — bloco preenchido pelo Analista (§5); o coração da ficha.
3. **Cronologia** — lista datada dos eventos relevantes (o radar acrescenta; o humano lapida).
4. **Tese e estratégia** — a linha do caso, decisões tomadas e porquês.
5. **Provas** — existentes × faltantes (e de quem é o ônus).
6. **Prazos** — blocos de memória de cálculo (§4), do mais recente ao mais antigo.
7. **Histórico de análises** — versões anteriores do bloco SITUAÇÃO ATUAL, colapsadas.

### 3.5 Views (Obsidian Bases — nada de tela web)

Crie em `_SISTEMA/bases/`:
- `cockpit.base` — processos: prazo em curso, próxima ação, data interna, risco, fase.
- `pipeline.base` — casos agrupados por status (o kanban do que ainda não nasceu).
- `clientes.base` — pendências documentais, contrato/procuração, última atualização enviada.

---

## 4. Motor de Prazos v2 (Zero-Trust)

Evolução do motor do MVP — **não reescreva do zero; refatore o existente**.

### 4.1 Estados do prazo

`sugerido → confirmado → cumprido | perdido | cancelado`

Só o humano move de `sugerido` para `confirmado` (editando a ficha ou por comando CLI). O briefing cobra sugeridos não confirmados há mais de 24h.

### 4.2 Memória de cálculo (bloco-modelo obrigatório em toda ficha)

```markdown
### PRAZO-2026-014 · status: SUGERIDO ⏳ (aguarda confirmação)
- Ato gerador: decisão — comunicação DJEN nº 2381 (link) | AUTOS/.../id-XXXX.pdf
- Disponibilização: 06/07/2026 · Publicação: 07/07/2026 · Início da contagem: 08/07/2026
- Prazo: 15 dias úteis — base: art. 335, CPC (origem: detectado no texto | padrão do rito)
- Feriados considerados: [lista] · Recesso aplicável: não
- Suspensões por portaria: **NÃO VERIFICADAS** (checar antes de confirmar)
- Vencimento estimado: 28/07/2026 · Confiança: alta | media | baixa (motivo)
- Peça cabível: contestação
- Marcos internos: D-8 análise 16/07 · D-6 estratégia 18/07 · D-4 minuta 22/07 ·
  D-2 revisão 24/07 · D-1 protocolo 27/07 · D0 margem 28/07
- Confirmado por: ______ em ______
```

### 4.3 Regras de contagem (gerar `_SISTEMA/config/prazos.yaml` e **validar tabela com o advogado antes de ativar**)

- **CPC:** dias úteis (art. 219); exclui o dia do começo, inclui o do vencimento (art. 224); publicação no DJEN = 1º dia útil após a disponibilização; contagem inicia no 1º dia útil seguinte à publicação (art. 224, §§ 2º–3º); suspensão 20/12–20/01 (art. 220). Padrões: contestação 15 · apelação 15 · agravo de instrumento 15 · embargos de declaração 5 · manifestações genéricas 15 (ou o que o texto fixar).
- **Juizados (Lei 9.099/95):** dias úteis (art. 12-A); recurso inominado 10 · embargos de declaração 5.
- **Trabalhista (TRT-8 / CLT):** dias úteis (art. 775); recesso 20/12–20/01 (art. 775-A); recurso ordinário 8 · agravo de petição 8 · agravo de instrumento 8 · recurso de revista 8 · embargos de declaração 5.
- **Precedência:** prazo expresso no texto da intimação **sempre** prevalece sobre a tabela. Divergência texto × tabela, ou dúvida sobre o rito → `confianca: baixa` + fila vermelha do briefing.
- `_SISTEMA/config/feriados.yaml`: nacionais + estaduais PA/MA + municipais das comarcas ativas (Parauapebas, Marabá, Imperatriz, Belém — confirmar lista com o advogado). Feriado local ausente é a causa nº 1 de erro: deixe isso dito no LEIA-ME.

### 4.4 Decomposição D-8 → D0

Ao **confirmar** um prazo, gere marcos internos como tarefas datadas: análise (D-8), estratégia (D-6), minuta (D-4), revisão (D-2), protocolo (D-1), margem (D0). Em prazos curtos, comprima proporcionalmente (8 dias: D-5/D-4/D-3/D-1/D0 · 5 dias: D-3/D-2/D-1/D0). **Marco atrasado aparece no briefing antes do prazo** — a mensagem é "a análise desta manifestação está atrasada", não "vence dia 30".

### 4.5 Conciliação (manter e ampliar o que o MVP já faz)

Cruzar previsões com o DataJud (ex.: "decurso de prazo certificado" sem petição no período) e registrar cada divergência em `_SISTEMA/logs/conciliacao.md` — é assim que o motor aprende e o advogado audita.

---

## 5. Analista Processual (as 12 saídas)

**Gatilho:** nova intimação no INBOX (automático, pós-radar) ou sob demanda em qualquer ficha. **Modo analítico** (§1.3): modelo mais capaz, template em `_SISTEMA/prompts/analista.md`.

**Contexto de entrada:** texto integral da comunicação DJEN + ficha do processo + PDFs em `AUTOS/<numero>/` (se houver) + itens de `CONHECIMENTO/` com status ≥ aprovado da área.

**Saída padronizada** — atualiza o bloco **SITUAÇÃO ATUAL** da ficha e a nota do INBOX:

1. Resumo do processo (o que se discute, pedidos, o que já ocorreu)
2. Fase processual
3. Último acontecimento — e o que ele significa em português claro
4. Obrigação atual — **quem** precisa agir
5. Consequência da inércia
6. Medidas possíveis (A, B, C… com prós e contras)
7. Recomendação fundamentada (fatos favoráveis/desfavoráveis, provas disponíveis/faltantes, riscos, alternativa subsidiária)
8. Documentos a solicitar ao cliente (gera/atualiza `docs_pendentes` do cliente)
9. Tipo de peça indicado
10. Estrutura sugerida da peça (endereçamento → síntese → fatos → fundamentos → provas → pedidos → anexos) + qual modelo de `CONHECIMENTO/MODELOS/` serve de ponto de partida
11. Citações — a fonte de **cada** afirmação relevante (comunicação nº / arquivo / página)
12. Confiança: alta | média | baixa — e por quê

**Proibições do Analista:** não confirma prazo, não protocola, não envia nada a ninguém. Se não conseguir determinar de quem é o prazo ou qual a providência → flag **`PRECISO-DECIDIR`** (vermelho no briefing, com prazo interno de 24h para o advogado buscar a resposta — comigo, com colega ou na doutrina — *dentro* do prazo, nunca depois).

---

## 6. Briefing diário + Auditor

**Cron 07h00 America/Belem:** `radar → prazos → analista → auditor → briefing`.

`BRIEFINGS/AAAA-MM-DD.md`, escaneável em 2 minutos (não listar o que está saudável):

- 🔴 **Críticos** — prazos ≤ 3 dias úteis; marcos D-x atrasados; `PRECISO-DECIDIR` abertos; prazos sugeridos sem confirmação > 24h; violações R1–R6.
- 🟡 **Semana** — prazos ≤ 7 dias úteis; marcos do dia; protocolos planejados; `data_interna` e `prescricao_ou_limite` de casos se aproximando.
- 👥 **Clientes** — documentos pendentes (com dias de espera); clientes sem atualização > 14 dias; procurações/contratos pendentes.
- 💰 **Financeiro** — vencidos; a vencer em 7 dias; gatilhos de êxito detectados (sentença/alvará/acordo) pedindo verificação de contrato.
- 📥 **INBOX** — intimações ainda não triadas.
- ✅ **Auditoria** — contagem de pendências por regra (R1–R6).

O **Auditor** é um script que varre todos os frontmatters e aplica as Seis Regras; sua saída alimenta as seções 🔴 e ✅.

---

## 7. Financeiro mínimo

- `FINANCEIRO/contratos/CTR-####.md`: cliente, caso, valor de entrada, parcelas e vencimentos, % de êxito, base de cálculo, **evento que torna o êxito exigível**, despesas combinadas.
- `FINANCEIRO/lancamentos.md`: razão **append-only** — tabela `data | tipo | cliente | caso | descrição | valor | vencimento | status | obs`. Tipos: `entrada, parcela, ato, exito, consulta, despesa, reembolso, acordo, alvara`.
- **Gatilho processual → financeiro:** radar detecta sentença procedente / alvará / acordo homologado → item no briefing "verificar cláusula de êxito do CTR-x" (o lançamento em si é humano — R2 do dinheiro).
- Relatório mensal automático em `FINANCEIRO/RELATORIOS/AAAA-MM.md`: faturado, recebido, vencido, a receber, previsão de êxito, por área e por cliente.

---

## 8. Segundo cérebro jurídico

Item de conhecimento (qualquer subpasta de `CONHECIMENTO/`):

```yaml
---
tipo: tese | modelo | precedente | checklist | estrategia | aprendizado
area: 
assunto: 
fase: 
tribunal: 
adversario:            # ex.: Sicredi, Águas do Pará, Banco X
status: bruto | revisado | aprovado | institucional | superado
casos_usados: []
resultado: 
fonte: 
---
```

- **R5 em código:** somente `status ≥ aprovado` pode ser injetado no contexto do Analista e das minutas.
- **Migração inicial (Etapa 5):** importar os modelos e teses existentes do advogado (perguntar onde estão) como `bruto`; revisar juntos os 5–10 mais usados até `aprovado`.
- **R6 em código:** encerrar um caso exige criar ≥ 1 item em `APRENDIZADOS/`.
- As skills existentes (formatação Nascimento, cooperativas, Águas do Pará) são o braço de redação — o Analista as referencia na saída 10; não as duplique.

---

## 9. Etapas de implementação (cada uma termina com: demonstração com dados reais → aprovação do advogado → commit)

**Etapa 0 — Reconhecimento** (§2). *DoD:* relatório aprovado.

**Etapa 1 — Resgate operacional.** Estrutura de pastas + templates + **cadastro assistido**: para cada nº de processo no banco do radar, conduza uma entrevista curta com o advogado (cliente? polo? qual caso? tese? próxima ação? prazo em curso? contrato?) e gere fichas de processo, caso e cliente. Depois: casos ainda **não protocolados** (com `data_interna` e `prescricao_ou_limite`) e clientes sem processo. *DoD:* 100% dos processos com ficha completa e próxima ação; casos a protocolar cadastrados; Auditor rodando com lista de pendências reconhecida pelo advogado.

**Etapa 2 — Radar + Prazos v2.** Adicionar TRT-8 ao radar; criar INBOX (1 nota por intimação); refatorar o motor para estados + memória de cálculo + tabelas por rito + feriados + D-marcos; manter conciliação DataJud. *DoD:* os prazos do último relatório do MVP são reproduzidos e explicados pela memória de cálculo; 1 intimação real percorre DJEN → INBOX → prazo sugerido → confirmação manual; nada se autoconfirma.

**Etapa 3 — Analista.** Template das 12 saídas + integração API + escrita do bloco SITUAÇÃO ATUAL. *DoD:* rodar sobre as intimações reais dos últimos 30 dias; zero "Não identificado"; citações conferíveis; `PRECISO-DECIDIR` funcionando.

**Etapa 4 — Briefing + Auditor + cron.** *DoD:* briefing real gerado às 07h por 2 dias seguidos; auditoria R1–R6 apontando pendências verdadeiras.

**Etapa 5 — Financeiro + Conhecimento + LEIA-ME.** Contratos atuais lançados; relatório do mês corrente; ≥ 5 itens de conhecimento migrados (≥ 1 aprovado); `LEIA-ME.md` com a rotina (§10); backup de `AUTOS/` configurado e testado (restaurar 1 arquivo). *DoD:* tudo acima demonstrado.

---

## 10. O contrato humano (escreva isto no LEIA-ME.md, com estas palavras ou melhores)

- **Manhã, 10 minutos:** ler o briefing; **zerar o INBOX** — nenhuma intimação sai de lá sem próxima ação definida ou flag `PRECISO-DECIDIR`; todo `PRECISO-DECIDIR` tem 24h para virar decisão, e a consulta acontece *dentro* do prazo, nunca depois.
- **Segunda-feira, 1 hora:** passar pelas ~20 fichas uma a uma; confirmar prazos sugeridos; conferir financeiro; atualizar próximas ações. Nesta escala, esse ritual sozinho elimina prazo perdido por esquecimento.
- **Sempre:** prazo só é confirmado por humano; conferência final no sistema oficial (PJe) antes de qualquer protocolo; o sistema **organiza e propõe** — a responsabilidade profissional é integralmente do advogado (o SOJ é rede de segurança, não muleta).

---

## 11. Fora de escopo da Fase 0 (não construa; não sugira construir)

Aplicação web · PostgreSQL · portal do cliente · bot de WhatsApp · jurimetria · scraping autenticado de PJe/Jus.br · protocolo automático · Temporal, n8n, Langfuse · multiusuário · tribunais além de TJPA/TJMA/TRT-8. Autos completos entram por **upload manual** em `AUTOS/<numero>/` (o Analista os usa quando existirem). Esses itens são Fase 1+ e só entram após ≥ 30 dias de Fase 0 rodando redonda. Se o advogado pedir algo desta lista, lembre-o gentilmente desta seção e pergunte se quer mesmo antecipar.

---

## 12. Kickoff

Sua primeira ação ao ler este arquivo: executar a **Etapa 0** e apresentar o Relatório de Reconhecimento. Não escreva código antes da aprovação. Ao longo de todo o projeto: commits pequenos e frequentes, perguntas curtas quando faltar informação, e demonstrações com dados reais — nunca com exemplos inventados.
