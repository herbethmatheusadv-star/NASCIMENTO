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

## Pendências de decisão do titular (15/07/2026)

- [ ] Confirmar a antecipação do conector ciente do §11 (Ressalva 1).
- [ ] Revogar, manter ou **restringir** a regra de credenciais (Ressalva 2).
      Sugestão de meio-termo: manter o veto a certificado/gov.br e a perfil
      persistente; permitir **MNI com CPF+senha no Windows Credential
      Manager**, se o MNI atender — é credencial de consulta, não de
      assinatura.
- [ ] Confirmar ciência da Ressalva 3.
