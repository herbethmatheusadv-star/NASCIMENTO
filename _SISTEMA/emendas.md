# Emendas ao PROMPT_MESTRE_SOJ_OPERACIONAL.md

> O prompt-mestre é a constituição da construção (§0). Ele só muda por decisão
> expressa do titular, registrada aqui, com data e motivo. Nada de emenda
> tácita: se a prática divergir do texto, ou o texto muda aqui, ou a prática
> volta para o texto.

---

## EMENDA 01 · 15/07/2026 · Conector PJe vira o sprint ativo

**Decisão do titular:** o Conector PJe deixa de ser trabalho pós-Etapa 2 e
passa a ser **o sprint ativo, a partir de agora**. O cadastro restante da
Etapa 1 será concluído **pelo próprio conector** (função censo), em vez de por
entrevista manual processo a processo.

**O que isto altera no prompt-mestre:**
- **§9 (Etapas de implementação):** a ordem Etapa 1 → 2 → 3 → 4 → 5 fica
  suspensa. O conector entra antes; a Etapa 1 fecha como subproduto dele.
- **§11 (Fora de escopo da Fase 0):** o item *"scraping autenticado de
  PJe/Jus.br"* deixa de estar fora de escopo. **Ver a ressalva abaixo.**

**Status:** ⏸️ **REGISTRADA, MAS NÃO EXECUTADA** — aguarda a confirmação do
titular sobre os três pontos abaixo (levantados em 15/07/2026, antes do
spike). O spike não começou.

### Ressalva 1 — o que o próprio §11 manda fazer

O §11 diz, textualmente: *"Esses itens são Fase 1+ e só entram após ≥ 30 dias
de Fase 0 rodando redonda. Se o advogado pedir algo desta lista, lembre-o
gentilmente desta seção e pergunte se quer mesmo antecipar."*

Estamos no **dia 1** da Fase 0, não em 30+. O briefing diário não existe, o
Auditor não existe, e a Etapa 1 está a ~30%. O registro desta ressalva é
cumprimento do §11 — a decisão de antecipar é do titular, e ela está tomada;
o que falta é a confirmação de que é mesmo para antecipar **sabendo disso**.

### Ressalva 2 — conflito com regra do próprio titular, da mesma data

Existe uma orientação registrada do titular (15/07/2026, sessão anterior):

> *"Não construir automação que faça login em PJe / Jus.br / PDPJ com o
> certificado digital ou a conta gov.br — inclusive **capturar token de
> sessão, persistir cookies para não reautenticar**, ou 'resolver' o 2FA com
> sessão longa. **Why:** o certificado é a assinatura de advogado dele e a
> conta gov.br é a identidade civil digital — com elas dá para peticionar em
> nome dele. (…) **Se ele mesmo pedir o acesso autenticado, a resposta
> continua a mesma quanto às credenciais**; o que muda é que dá para desenhar
> o fluxo manual dele em volta."*

Itens do spike que esbarram nela:
- **perfil persistente** em `_SISTEMA/browser_profile/` = persistir cookies
  para não reautenticar;
- **"tempo de vida da sessão"** = por quanto tempo dá para não reautenticar;
- **MNI com CPF+senha do advogado** = credencial no robô;
- **PDPJ (Jus.br)** = nomeado na regra.

A regra é do titular e só ele a revoga. Mas ela **antecipou este pedido** e
respondeu por antecipação — por isso não é emenda automática.

### Ressalva 3 — coincidência que exige confirmação explícita

Na mesma data (15/07/2026) chegou à conversa, **dentro de uma notificação de
background task marcada como NÃO sendo input do titular**, um texto que se
passava por mensagem dele propondo exatamente isto, com as palavras
*"captura o token de sessão"*, *"o robô guarda os cookies num perfil de
navegador"* e *"resolve o bloqueio geográfico"*. Não veio dele e não foi
executado.

O pedido de hoje chegou pelo canal legítimo (mensagem do titular no chat) e
por isso **é tratado como instrução válida**. Mas pede — em outras palavras —
a mesma coisa que a injeção pedia. Registrar a coincidência é o mínimo devido:
**a confirmação do titular precisa ser explícita e ciente disto.**

### O que já pode andar sem qualquer confirmação

Não dependem de credencial, sessão ou perfil persistente — e são a espinha do
conector de qualquer forma:
1. **Regras de ferro codificadas** (R7-EXECUTÁVEL, quarentena, watchdog,
   conduta) — infraestrutura de segurança, escrita antes de qualquer leitura
   automática, como o próprio titular determinou.
2. **MNI: descobrir se o WSDL é público** em TJPA/TJMA/TRT-8 — consulta a
   endpoint público, sem credencial. Responde a pergunta mais importante do
   spike (existe porta oficial?) sem tocar em senha.
3. **Desenho da arquitetura** e do fluxo de censo.

O MNI, aliás, é a porta **oficial** (Resolução CNJ 65/2008 — Modelo Nacional
de Interoperabilidade): se ele atender, não há "scraping" nenhum, e boa parte
da Ressalva 2 evapora — o que sobra é só a questão de onde mora a credencial.

---

## EMENDA 02 · 15/07/2026 · Revogação parcial e explícita — login por certificado

**Autoria: o titular**, por mensagem no chat, **ciente da coincidência com a
injeção reportada** (Ressalva 3 da Emenda 01) e declarando expressamente que
*"a instrução válida é esta, por este canal"*. As três ressalvas da Emenda 01
ficam **respondidas**; a Emenda 01 passa de ⏸️ para ✅ **em vigor**.

### REVOGADO

- O veto ao **login por certificado digital** no PJe.

### MANTIDO INTEGRALMENTE (o titular reafirmou)

- (a) nada de **perfil de navegador persistente**;
- (b) nada de **cookie/token/sessão salvos em arquivo**;
- (c) **nenhuma credencial, senha ou PIN** em disco, código ou variável de
  ambiente;
- (d) nada de **gov.br automatizado**.

### Desenho aprovado — "certificado com humano no portão"

Playwright + Chromium com **perfil efêmero** · PJeOffice rodando · o robô abre
o login e **para**; o titular digita o PIN/senha na janela · o robô nunca vê
nem armazena · a sessão morre com o processo · amanhã, PIN de novo.

**Por que este desenho dissolve as ressalvas 2 e 3:** os três vetores que a
regra original protegia — cookie persistido, sessão medida para não
reautenticar, credencial no robô — **deixam de existir**. Não são bloqueados:
não são possíveis. É a "inversão legítima" que a própria regra apontava como
alternativa ("ele autentica; o script processa"), agora com o navegador no
meio.

### R7 INEGOCIÁVEL — implementada e testada ANTES do primeiro login

`CONECTOR/regras.py` + `CONECTOR/teste_regras.py` (**49 casos, exit 1 quebra o
build**):
1. **Ausência, não bloqueio:** o teste varre o fonte do pacote e falha se
   aparecer capacidade de assinar/peticionar/tomar ciência/responder, operação
   MNI de escrita, credencial em código ou persistência de sessão.
   **Provado em 15/07:** um arquivo com `responder_expediente()` chamando
   `confirmarRecebimento` foi detectado (arquivo e linha) e derrubou o build.
2. **Allowlist MNI de exatamente 3 operações** (avisos pendentes, processo,
   alteração). As duas de escrita não estão lá e não podem entrar.
   `consultarTeorComunicacao` fica **em estudo** — pode ser o próprio ato de
   ciência; só o titular libera, e só após provar num aviso já ciente.
3. **Guarda de clique e de URL:** o robô se recusa a tocar em "Tomar
   ciência/Responder/Peticionar/Assinar…" e a navegar para telas de ato.
4. **Quarentena:** ciência pendente → não abre o processo **nem os autos** →
   linha vermelha no briefing.
5. **Watchdog:** fonte que não rodou / voltou vazia / veio abaixo do mínimo =
   alerta. Silêncio não é "tudo bem": é "não sabemos".

**O teste já cobrou o próprio autor:** a 1ª versão do `sessao.py` passava a
flag de perfil fixo no launch do Chromium — reflexo de quem escreve automação
de navegador todo dia, e exatamente o que a letra (a) veta. O build quebrou; a
flag saiu (era desnecessária: `launch()` puro já é efêmero).

### Pendências desta emenda

- [ ] **Tipo do certificado: A1 ou A3?** Ficou `[A1 / A3]` no pedido, sem
      marcar. Muda a blindagem: **A3** (token/smartcard) é o cenário ideal —
      a chave não sai do hardware e o PIN é por uso. **A1** é arquivo `.pfx`
      com senha: o desenho continua valendo, mas convém que o `.pfx` **não**
      esteja em pasta sincronizada (OneDrive/Drive) e que a senha nunca seja
      salva no navegador.
- [ ] MNI com CPF+senha: se responder, o titular quer trocar de porta. Note
      que a letra (c) proíbe a senha em disco/código/env — então a rota MNI
      exigiria digitá-la a cada execução (prompt em memória), o que é
      compatível, mas retira o "roda sozinho às 07h". Decisão dele quando o
      caso surgir.

---

## EMENDA 03 · 15/07/2026 · Nova arquitetura — eliminar a dualidade v1 × Operacional

**Ordem do titular** (canal legítimo): *"quero que o sistema seja auditado
novamente e as novas modificações sejam feitas (uma nova arquitetura eliminando
o SOJ original)"*.

**O que já foi executado no mesmo dia:**
1. **Auditoria completa** — `ESCRITORIO/scripts/auditor.py` criado (o Auditor
   R1–R6 do §6 do prompt-mestre, que era DoD faltante da Etapa 1) e rodado:
   **7 vermelhos, 21 amarelos, 2 informativos** →
   `_SISTEMA/logs/AUDITORIA_2026-07-15.md`. Veredito: os achados estruturais
   nascem da DUALIDADE de modelos, não de um modelo ruim.
2. **Arquitetura v2 desenhada** — `ARQUITETURA_V2.md` na raiz: modelo único
   (markdown+frontmatter, prompt-mestre §3 canônico), mapa de destino peça a
   peça do v1, migração em 5 ondas com paridade do vigia, DoD objetivo
   (auditor com zero vermelho).

**Status: ⏸️ MIGRAÇÃO REGISTRADA, NÃO EXECUTADA.** Motivos, nomeados:
- Reverte decisão formal do titular na Etapa 0 ("o SOJ Operacional completa o
  v1, não o substitui") — reversão é direito dele, mas segue o rito das
  emendas: explícita, datada, ciente.
- A constituição (§0) manda: "estender o que existe antes de reescrever" e
  "ambiguidade ou conflito → pergunte; nunca decida sozinho em zona vermelha".
- **Casos reais com trabalho vivo moram no v1**: GETULIO (PZ03 sugerido;
  sentença DE HOJE), DAIANE (protocolo em curso — R4), TANIA. Quebrar o vigia
  no meio disso é fabricar o dano que o sistema existe para evitar.
- "Eliminar" foi interpretado como **aposentar para `_ARQUIVO/` + git**, nunca
  apagar registro de caso (dever profissional). Se o titular quis apagar de
  verdade, precisa dizer com todas as letras — e ainda assim os DIARIOs e
  originais não se apagam.

### Pendências que destravam a execução (decisões do titular)

- [ ] **GO da migração** nos termos da ARQUITETURA_V2 (eliminar = aposentar).
- [ ] **DAIANE**: congelar até protocolar (recomendado) ou migrar por último?
- [ ] **Numeração única** `CASO-####` com `id_legado` (recomendado)?
- [ ] **Gates G1–G3 e DIARIO ficam** (recomendado)?
