# Bugs do radar encontrados com dados reais — fila da Etapa 2

> Regra da casa: bug achado com dado real vira teste antes de virar correção
> (`RADAR/teste_*.py`). Nenhum destes foi corrigido ainda — o radar segue
> rodando às 07h com estas limitações conhecidas.

---

## BUG-01 · ✅ CORRIGIDO em 15/07/2026 (commit 39f7cf8) · era CRÍTICO

> **Correção aplicada:** `detectar_prazos()` lê contexto por cláusula, descarta
> prazo de arquivamento/cumprimento voluntário/decurso, captura a forma
> "prazo legal (10 dias)" e, havendo mais de um prazo do cliente, **adota o
> menor e marca ambíguo** (console e HTML mostram os candidatos e mandam
> conferir). Testes: `teste_calendario.py` §10.1, com fixture do teor real.
> **Verificado no dado real:** o mesmo processo que dizia "NO PRAZO, vence
> 28/07" passou a dizer "VENCIDO GRAVE, venceu 14/07, ambíguo 5 ou 10".
>
> *Percalço registrado:* a 1ª versão da correção escrevia os padrões sem acento
> (`voluntario`) e o texto real trazia `voluntário` — dois prazos alheios
> passaram batido. Pego pelos próprios testes ao conferir `candidatos`. Lição:
> os padrões rodam sobre `classificador.normalizar()`; escrevê-los com acento é
> escrevê-los para nunca casar.

### O problema original (histórico)

**Descoberto:** 15/07/2026, na triagem TJPA do PROC-0006
(0808637-09.2026.8.14.0040).

**O que aconteceu:** a sentença extintiva do JEC diz, em cláusulas diferentes:
- *"em caso de interposição de recurso inominado no prazo legal (**10 dias**)"*
  → este é o prazo do cliente;
- *"decorrido o prazo de **15 dias** sem manifestação das partes, arquive-se"*
  e *"aguarde-se o prazo de **15 (quinze) dias** para cumprimento voluntário"*
  → estes **não são** prazo do cliente.

O `detectar_prazo()` pegou **15 dias** e reportou *"detectado no texto"* —
rótulo que transmite confiança alta. Resultado: vencimento estimado em
**28/07** quando o real é **21/07**. **Erro de 7 dias, na direção perigosa**
(mais tempo do que existe).

**Por que é grave:** é o mesmo padrão do bug já corrigido "narrativa do acórdão
virando ordem" — o classificador lê o texto todo e não distingue *o prazo que
me obriga* de *prazos que a decisão menciona*. Um erro para mais é o que faz
perder prazo; e o rótulo "detectado no texto" desarma a desconfiança do leitor.

**Correção proposta (Etapa 2):**
1. Extrair prazo **só da vizinhança de gatilhos de recurso/providência da
   parte** ("interposição de", "recorrer", "interpor", "prazo para
   apresentar/manifestar"), nunca de "arquive-se", "cumprimento voluntário",
   "sob pena de arquivamento".
2. Quando o texto contiver **mais de um prazo distinto**, não escolher em
   silêncio: reportar **todos**, adotar o **menor** e marcar
   `confianca: baixa` + fila vermelha do briefing.
3. Tabela por rito (Motor v2): sentença em JEC → recurso inominado 10 dias;
   ED 5 dias. A tabela deve **prevalecer sobre a captura textual quando esta
   for maior que a tabela** — o inverso do que ocorreu aqui.
4. Teste de regressão com o teor real desta sentença (guardar amostra).

---

## BUG-02 · ✅ CORRIGIDO em 15/07/2026 (commit 39f7cf8)

> **Correção aplicada:** termo/ata de audiência é informativo salvo se a
> **ordem** trouxer prazo. A detecção é pelo próprio texto
> (`RE_TERMO_AUDIENCIA`), não por `tipo_de_ato()` — o termo real traz
> "conclusos para decisão" e era classificado como decisão. O gatilho é o
> **prazo na ordem**, não "sob pena de": o termo transcreve pedido do advogado
> **adverso** ("intimação exclusiva… sob pena de nulidade"), e pedido de
> terceiro não é ordem ao cliente. Testes: `teste_calendario.py` §10.2.
> **Verificado no dado real:** o alerta falso `[ATENÇÃO] 20/07` sumiu.

### O problema original (histórico)

**Descoberto:** mesma triagem, mesmo processo.

**O que aconteceu:** o **termo de audiência de conciliação** (sem acordo,
disp. 26/06) foi tratado como ato que abre prazo, com *"15 dias, padrão
assumido"* → alerta `[ATENCAO]` de vencimento em 20/07. **Não existe esse
prazo:** o termo apenas registra que a conciliação foi infrutífera.

**Efeito colateral perigoso:** ruído. Um alerta falso de 20/07 competindo com
o prazo verdadeiro de 21/07 embaralha a leitura — exatamente o mecanismo que o
`resolvidos.txt` foi criado para combater ("alerta que grita sem motivo faz
parar de ler o relatório").

**Correção proposta (Etapa 2):** classificar "termo/ata de audiência" como
informativo por padrão (como já se faz com "lista de distribuição"), **exceto**
quando o texto contiver ordem expressa com prazo à parte. Prazo "padrão
assumido" em ato informativo não deve virar `[ATENCAO]`.

---

## BUG-03 · 🟡 DJEN: bloco em HTTP 500 persistente esconde processo inteiro

**Descoberto:** 15/07/2026 (o processo PROC-0005 só apareceu porque o advogado
entregou os autos).

**O que aconteceu:** a janela **28/09→11/11/2025** respondeu 500 em ~28
tentativas ao longo do dia. A fatia **28/09→12/10** falha em **todos** os
tamanhos de página (5, 10, 20, 25, 30, 50, 75, 100) — não é o `itensPorPagina`
(hipótese testada e **descartada**). É intermitência com ponto quente: a mesma
janela respondeu uma vez com `pp=5`, e a **paginação recupera parte dos itens
mesmo quando a consulta cheia falha** (10 de 14 comunicações recuperadas
assim).

**Correção proposta (Etapa 2):**
1. **Fila de re-tentativa persistente entre execuções**: bloco falho é gravado
   em `_SISTEMA/logs/` e re-tentado nos dias seguintes até responder — avisar
   uma vez não basta (o aviso apareceu, e ainda assim o processo ficou 8 meses
   fora do radar).
2. **Sub-fatiamento adaptativo:** ao falhar, quebrar o bloco em fatias menores
   (15 → 7 → 3 → 1 dia) antes de desistir; e **paginar mesmo assim**, guardando
   o que vier.
3. **Vigilância por número** dos processos já cadastrados (`numeroProcesso=`),
   como segunda camada independente da busca por OAB.

---

## BUG-04 · ✅ CORRIGIDO em 15/07/2026 · "De quem é" ficava INCERTO em processo do próprio cliente

> **Correção aplicada:** o radar passou a **ler as fichas** (`RADAR/fichas.py`) e
> a tirar o polo de `polo_cliente` — **mas só de ficha que um humano conferiu**
> (`ultima_revisao_humana` preenchida). O portão não é detalhe: o censo de 15/07
> inferiu polo a partir da *lista* do painel, que traz as partes e não quem
> contratou — a ficha do PROC-0014 avisa "confiança MÉDIA, confirmar antes de
> agir". Tratar palpite do censo como autoridade trocaria um erro visível
> (INCERTO) por um invisível (`DA_OUTRA_PARTE` errado), e errar para "não é seu"
> faz perder prazo. Sem ficha, sem revisão ou sem `PROCESSOS/`, tudo volta a
> adivinhar: **a ficha só melhora o veredito, nunca piora**.
> `fichas.py` é stdlib pura (lê pares `chave: valor` planos, não é parser YAML) —
> o radar roda em tarefa agendada, sem venv.
> Testes: `teste_classificador.py` §12, §12.1 e §12.2 (contra as 25 fichas reais).
> **Verificado no dado real:** o VENCIDO GRAVE do topo (0808637-09) passou de
> *"INCERTO — a comunicação lista as duas partes"* para *"**MEU** — o ato intima
> os dois polos e a ficha (conferida por você) diz que seu cliente é do polo
> ativo"*, e o relatório agora aponta `[PROC-0006]`. Hoje: 25 fichas indexadas,
> 7 com polo conferido.
>
> **O que isto abre:** era a primeira vez que o radar e as fichas se falaram.
> É a direção da ARQUITETURA_V2 ("um modelo que o Obsidian, o Auditor, o radar e
> o conector já leem") — e o caminho para o campo `audiencia` da Onda 1.
> **Efeito colateral bom:** conferir uma ficha agora torna o radar mais preciso
> naquele processo. Revisar passou a pagar juros.

### O problema (histórico)

**Descoberto:** mesma triagem (PROC-0006 e TJMA 0805885-75).

**O que aconteceu:** o veredito saiu `INCERTO` mesmo com o termo de audiência
nomeando "AUTOR: DANIEL ... acompanhado de seu advogado Herbeth Matheus
Mendonça do Nascimento, OAB/PA 39.261" — o dado necessário estava no texto.

**Correção proposta (Etapa 2):** quando as fichas de PROCESSOS/ existirem
(agora existem), o polo do cliente vem da **ficha**, não da adivinhação
textual. O `INCERTO` deve ser exceção, não regra. Enquanto isso: usar o nome
do próprio advogado no texto como pista do polo.

---

## BUG-05 · ✅ CORRIGIDO em 15/07/2026 · era CRÍTICO — **escondia audiência**

> **Correção aplicada:** o radar passou a distinguir **INTIMAÇÃO PARA
> audiência** (ato futuro, com data e hora, comparecimento obrigatório) de
> **TERMO de audiência** (registro do que já ocorreu — o do BUG-02). Três peças,
> porque corrigir só uma não resolvia:
> 1. `classificador.tipo_de_ato()` ganhou o tipo `intimacao_audiencia`;
> 2. `classificador.data_da_audiencia()` extrai dia/hora — **de propósito
>    independente do tipo do ato**, para que uma decisão que defere tutela *e*
>    designa audiência não perca a data por causa do rótulo;
> 3. o relatório ganhou **seção própria de audiências**, retirada da fila
>    **antes** de `de_quem` e de `informativo`.
> A peça 3 é a que faltava e a mais importante: sem ela, marcar a convocação
> como informativa (peça 2) apenas **trocava** um esconderijo por outro.
> Testes: `teste_classificador.py` §11 e §11.1, `teste_calendario.py` §18 e
> §18.1, com o teor real em `fixtures/intimacao_audiencia_edio.txt`.
> **Verificado no dado real:** o relatório passou de "EM ABERTO: nenhum prazo
> correndo", com o processo no rodapé como "Não identificado", para
> "**AUDIÊNCIA AMANHÃ**" no topo e no chip do cabeçalho.

### O problema

**Descoberto:** 15/07/2026, à noite, na triagem dos 3 "prazos decorridos" do
censo — **a 14 horas do ato**.

O PROC-0015 (EDIO × Águas do Pará) tinha audiência de conciliação em **16/07
às 11:15**. O radar rodou às 07h do dia 15 e listou o processo como **"Não
identificado"**, no rodapé, com prazo assumido de 15 dias já "vencido".

Cadeia do erro:
1. o regex de audiência exigia `termo de audiencia` ou `audiencia de
   conciliacao`. O texto real diz **"INTIMAÇÃO PARA AUDIÊNCIA"** e **"Data da
   Audiência: 16/07/2026 11:15, Tipo: Conciliação"** — não casava nenhum;
2. caindo em `indefinido`, não era informativo → ganhou o prazo padrão de 15
   dias sobre a disponibilização (02/06) → "venceu" em ~24/06;
3. vencido sem sanção grave → `prioridade()` = rodapé, junto do que não
   importa mais. **Quanto mais perto do ato, mais fundo o item afundava.**

**Por que é grave:** audiência não é prazo — não se cumpre antes nem se
compensa depois. Faltar leva à extinção do processo do autor (art. 51, I, da
Lei 9.099/95) e à perda da liminar. O radar existe para que isso não dependa de
memória, e era justamente aqui que ele calava.

**Não era um caso isolado:** a mesma correção revelou **duas** audiências
escondidas — EDIO (16/07 11:15) e **Luciana (0808548-83, 21/07 08:30)** — mais
uma terceira no TJMA (12/08) que já aparecia, mas como prazo, não como agenda.

**Relação com o BUG-04:** o censo do painel atribuiu o "decurso" ao cliente e a
ficha mandou "descobrir o que se perdeu". Não havia o que descobrir: era a
janela de ciência da convocação. O BUG-04 (de quem é o prazo) e o BUG-05
(o que é o ato) se somaram para transformar uma agenda em falso luto.

**Lição:** o BUG-02 ensinou que termo de audiência não abre prazo. A conclusão
foi correta e a generalização, não: virou "audiência = informativo". Mas as
duas coisas se chamam "audiência" e são **opostas** — uma é passado sem ação, a
outra é futuro com hora marcada. Silenciar pela palavra, e não pelo que o ato
faz, silencia o lado errado.
