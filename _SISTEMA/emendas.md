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

---

## EMENDA 04 · 15/07/2026 · O PLANO_SOJ vira a especificação técnica da Onda 1

**Origem:** o titular trouxe o `PLANO_SOJ.md` (síntese do *SOJ PJe Intelligence*
com o *Repositório Jurídico Executável*) e mandou executá-lo. O documento manda,
na Fase 0, inventariar o que existe antes de criar qualquer arquivo — e foi
justamente a Fase 0 que impediu a execução literal.

**O conflito que a Fase 0 encontrou:** o plano descreve construir uma árvore
`SOJ/` do zero, com esquema próprio de ficha (`prazo_confirmado_por/_em`,
`sigilo` em 3 camadas, `ia_autorizada`, `PROCESSOS/{numero}/ficha.md`). Executado
ao pé da letra, criaria um **terceiro modelo** ao lado do v1 e do Operacional —
exatamente a dualidade que a AUDITORIA_2026-07-15 apontou como causa dos 7
vermelhos ("o problema não é o SOJ v1 nem o Operacional: é existirem os dois").
Além disso, o plano manda cadastrar "~20 processos" (já são 25, fichados) e trata
DataJud/DJEN como expansão futura sob gatilho (o radar roda às 07h desde 14/07).

**Decisão do titular (15/07/2026):** o `PLANO_SOJ.md` **não** será executado como
árvore nova. Ele passa a ser a **especificação técnica da Onda 1** do
`ARQUITETURA_V2.md` (o laboratório: `soj_lib` v2). Mesmo alvo — modelo único em
markdown+frontmatter — e a V2 já traz a disciplina de migração (paridade provada
antes de desligar, DoD por onda, `_ARQUIVO/` em vez de apagar).

**O que o plano acrescenta, e que hoje não existe** (é por isto que ele importa):

| Órgão | Estado hoje |
|---|---|
| `wrapper.py` — conteúdo de autos é dado, nunca instrução | **não existe**; petição da parte contrária é conteúdo adversarial por definição |
| Hooks determinísticos (`validar_ficha.py`) | **não existem** — o `settings.local.json` só tem permissões. Regra sem mecanismo não é regra |
| CNJ por dígito verificador (módulo 97) | validação hoje é por formato |
| SHA-256 + dedup + originais imutáveis + manifest | parcial (v1 tem `00_originais/`) |
| Texto com `===[p.N]===` → **citar página** | não existe |
| `prazo_confirmado_por` / `_em` | o modelo tem `prazo_em_curso`, sem quem/quando confirmou |
| `ia_autorizada` + sigilo em 3 camadas (LGPD) | hoje `sigiloso: bool` |
| Fixtures adversariais | não existem |

**Onde o plano precisa ceder à realidade encontrada:**
1. **Fase 2 (cadastrar ~20 processos)** — já feita: 25 fichas do censo.
2. **Fase 6 (DataJud/DJEN sob gatilho)** — já construído: `RADAR/` é o braço de
   captura, com ~130 testes e tarefa agendada.
3. **Fase 6 (Playwright)** — `CONECTOR/` é sprint ativo, com R7 testada (49 casos)
   e o desenho "certificado com humano no portão". As regras do plano (nunca
   automatizar login/2FA/certificado) **coincidem** com a Emenda 02 e com
   `recusa-automacao-credenciais` — não há conflito, há confirmação.
4. **Topologia `PROCESSOS/{numero}/ficha.md`** — cede para `PROC-####.md` +
   `CASO-####` da V2 (§3), que já é o que as 25 fichas usam.

**Campo que o incidente do dia provou faltar:** nenhuma ficha tem `audiencia`.
O PROC-0015 tinha audiência marcada para o dia seguinte e o modelo só sabia
representar *prazo* — a agenda virou um "prazo decorrido" e afundou. **A Onda 1
deve tratar audiência como entidade de primeira classe** (data, hora, formato,
link, comparecimento obrigatório), não como um prazo com nome diferente. Ver
BUG-05 em `_SISTEMA/logs/bugs_radar.md`.

**Status:** ✅ **APROVADA E EM VIGOR** quanto ao papel do documento. A execução
da Onda 1 continua atrás do **GO da Emenda 03** e das 3 decisões abertas do
titular (DAIANE congela?; numeração `CASO-####`?; gates/DIARIO ficam?).

**O documento:** `PLANO_SOJ.md` movido da pasta de marca
(`Desktop/Brand Nascimento/`) para a raiz deste repositório — é documento do SOJ,
não de marketing, e fora do repo não tem histórico nem auditoria.

---

## EMENDA 05 · 15/07/2026 · MNI com senha digitada a cada execução

**Decisão do titular:** autorizado o acesso ao PJe/TJPA pelo **MNI** com
**CPF + senha digitada na hora**. A senha não vai para disco, `.env`, código nem
log — vive na memória do processo e morre com ele (`getpass`).

**O que muda em relação à Emenda 02 (e por que ele foi avisado):** o desenho
aprovado até aqui era *"certificado com humano no portão"* — ele digita o PIN
numa janela Java que o robô não alcança, e a credencial **nunca** passa pelo
código. No MNI é diferente: `idConsultante`/`senhaConsultante` são parâmetros da
chamada, então **a senha atravessa a memória do script**. Isso foi apresentado a
ele como escalada real de confiança, com a alternativa (navegador + descoberta
assistida de seletores) na mesa. Ele escolheu o MNI, ciente.

**O que NÃO muda:** nada de credencial em disco/env/código; nada de sessão
persistida; e a R7 continua sendo **ausência**.

### A decisão técnica que sustenta a R7 aqui: envelope à mão, sem `zeep`

Uma biblioteca SOAP gera o cliente **a partir do WSDL** — e criaria um método
para **cada** operação anunciada pelo servidor, inclusive as duas proibidas.
Tomar ciência viraria uma linha, existente e pronta. Montando o XML à mão, só
existe o que está escrito: em `CONECTOR/mni.py` só há consulta. As operações de
escrita não são bloqueadas — **não têm função, não têm envelope, não têm nome**.
Chamá-las é `AttributeError`, não uma decisão de runtime que alguém inverta num
dia apressado.

### Contrato (lido do WSDL real, não inventado)

- endpoints: `pje.tjpa.jus.br/pje/intercomunicacao` (1º) e `/pje-2g/` (2º)
- document/literal, SOAP 1.1; wrapper em `servico-intercomunicacao-2.2.2/`
- **filhos em `tipos-servico-intercomunicacao-2.2.2` com `form="qualified"` em
  cada elemento** — sobrepõe o `elementFormDefault` do schema. Escrever os
  filhos sem prefixo (o erro natural de quem chuta) renderia fault opaco.
- `consultarProcesso` aceita **`incluirDocumentos`** — é a porta dos autos.

### Alcance (diagnóstico de 15/07, sem credencial)

| Tribunal | MNI | Situação |
|---|---|---|
| **TJPA 1º e 2º** | ✅ WSDL vivo | a porta — **18 dos 25 processos** |
| TRT-8 | ❌ 21 caminhos testados | `/pjekz/` dá 200 mas é o SPA Angular devolvendo `index.html` para qualquer rota — falso positivo. Os 5 autos já estão em `AUTOS/` |
| TJMA | ❌ 403 | não é filtro de user-agent/referer (testado com 4 combinações) — bloqueio de origem. 1 processo |

### Estado

- `CONECTOR/mni.py` — cliente, stdlib pura, 3 operações e nada mais.
- `CONECTOR/teste_mni.py` — 22 casos, **sem rede e sem credencial**: envelope
  contra o contrato, senha não vaza em repr/str, R7 no envelope, CNJ validado
  antes da rede, escape de XML.
- `teste_regras.py` varre `mni.py` e segue **49/49**.
- **PENDENTE — o teste decisivo:** `python CONECTOR/mni.py --teste`. Só ele
  responde se a conta do titular tem MNI habilitado no TJPA. Muitos tribunais
  exigem habilitação prévia; se vier fault de credencial, é isso que se
  investiga antes de qualquer outra coisa.

### ❌ EMENDA 05 — RESOLVIDA EM 15/07/2026, SEM EFEITO PRÁTICO: o MNI está DESLIGADO

**O teste decisivo foi feito pelo titular e a resposta é definitiva:**

```
faultstring = "O MNI está desabilitado nesta instância."   (faultcode: soap:Server)
```

**Nos DOIS graus**, e — o que fecha a questão — **a recusa vem sem credencial
nenhuma**: repetimos a chamada com campos vazios e a mensagem é idêntica. Não é
senha errada. Não é falta de habilitação da conta. **O TJPA publica o WSDL e
mantém a implementação desativada.**

| Tribunal | Porta oficial | Veredito final |
|---|---|---|
| TJPA 1º e 2º | MNI | ❌ **desabilitado na instância** (WSDL no ar, serviço off) |
| TRT-8 | MNI | ❌ 21 caminhos; `/pjekz/` = SPA devolvendo index.html |
| TJMA | MNI | ❌ 403 de origem (4 combinações de cabeçalho testadas) |
| PDPJ | REST | ❌ exige token |

**Consequência: não existe porta oficial de leitura para este escritório.** O
`consultarProcesso`/`incluirDocumentos` — que seria a via limpa para os autos —
não é alcançável.

**A autorização da Emenda 05 fica sem uso, e isso é uma boa notícia:** a senha
do titular **nunca foi validada por canal nenhum**; o serviço recusou antes de
olhar para ela. E o corolário de segurança é favorável — **não existe porta que
leia o acervo dele só com CPF+senha**. O 2FA continua sendo o controle que o
protege, exatamente como ele exigiu. A regra "nunca contornar o 2FA" segue
íntegra por construção do tribunal, não por disciplina nossa.

**O que sobra, e volta a ser o caminho:** a **Emenda 02** — navegador efêmero
com **humano no portão**, leitura por DOM. Isso exige a **descoberta assistida
de seletores** (`sessao.py --mapear`), com ele ao teclado — que é a regra §10.4
do PLANO_SOJ ("não inventar seletores; descobrir na página real, com o advogado
presente"). O `_efemeros/mapeamento_pje/` está **vazio**: nunca rodou.

**`CONECTOR/mni.py` fica no repo, e não é código morto:**
- o **desembrulhador MTOM/XOP** é necessário em qualquer cliente do CXF (o TJPA
  responde multipart; foi o que escondeu o motivo da recusa no 1º teste real);
- o desenho **R7-como-ausência sem `zeep`** está provado e testado (49+22 casos);
- se o TJPA religar o MNI, está pronto — o contrato já foi lido do WSDL real.
