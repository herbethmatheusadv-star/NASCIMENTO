# DOUTRINA DE ANÁLISE v1

> Peça de KERNEL (aprovada pelo titular em 07/07/2026). Leitura OBRIGATÓRIA
> antes de qualquer tarefa analítica, em toda sessão. Integrada ao CLAUDE.md,
> à skill soj-kernel e ao G2 (item de profundidade).

## 1. DOIS MODOS DE TRABALHO — a fronteira sagrada

**MECÂNICO** (organizar, rotear, gerar views, conferir, lacrar): economia
máxima.

**ANALÍTICO** (diagnóstico, estratégia, simulação adversária, juiz rigoroso,
propostas Tier B, revisão de peça e de colaborador, destilação de autos,
preparação de audiência): **PROFUNDIDADE É O PRODUTO.** Token gasto aqui é
investimento, não custo. É PROIBIDO economizar profundidade em tarefa
analítica — a economia da mecânica existe para FINANCIAR a análise.

## 2. MODELO E RACIOCÍNIO

Tarefa analítica exige o modelo mais capaz disponível e raciocínio
estendido. Se a sessão estiver em modelo rápido, AVISE antes de começar:
*"tarefa analítica em modelo econômico — recomendo trocar no seletor"* —
e só prossiga com o ok.

## 3. PROTOCOLO DAS QUATRO PASSADAS (análise de uma passada é proibida)

- **P1 MAPEAR** — todos os ângulos antes de aprofundar qualquer um:
  mérito, prova, processo, prazos, riscos, custos, adversário, juiz,
  cliente.
- **P2 APROFUNDAR** — cada ângulo relevante desce até o concreto DESTE
  caso.
- **P3 ADVERSARIAR A SI MESMO** — reler como um sócio impiedoso: o que
  está raso? o que é genérico? o que um analista melhor veria? Corrigir.
- **P4 SINTETIZAR** — conclusões acionáveis, com grau de confiança e o
  que mudaria cada conclusão.

## 4. REGRAS ANTI-SUPERFICIALIDADE (invioláveis)

a) Toda afirmação analítica cita o elemento concreto do caso (F##, P##,
   PED##, verbete, fls. dos autos). **Análise que serviria para QUALQUER
   caso é análise de nenhum caso — refazer.**

b) **Teste do "e daí?"**: toda observação declara o que ela MUDA na peça,
   na estratégia ou no risco. Observação sem consequência não entra.

c) **Veredito sem base é proibido**: "boas chances" só existe como
   "probabilidade na faixa X porque A, B e C — e cairia para Y se D".

d) Toda recomendação apresenta ao menos **um caminho rival** e por que
   perdeu.

e) Cenários sempre com **faixas honestas** e os **gatilhos** que movem a
   faixa.

## 5. PADRÕES MÍNIMOS POR ARTEFATO

- **Simulação adversária:** TODAS as teses defensivas plausíveis — cada
  uma com fundamento, força (alta/média/baixa), a prova que nos exigiria
  e a contramedida específica (qual parágrafo da peça a neutraliza).
- **Juiz rigoroso:** leitura capítulo a capítulo — o que corta, o que
  manda emendar, o que indefere de plano, e o teor provável do primeiro
  despacho.
- **Diagnóstico:** mérito, prova, processo, riscos, cenários
  melhor/provável/pior com gatilhos — e a resposta à pergunta que o
  cliente fará ("vou ganhar? quanto? quando?") em linguagem honesta.
- **Proposta Tier B:** cenários completos com riscos, custos e o relógio.

## 6. G2 MEDE PROFUNDIDADE, não existência

Amostrar 3 afirmações aleatórias da ESTRATEGIA — devem passar nos testes
4a e 4b; simulação adversária sem contramedida específica por tese =
REPROVADO, com a lista do que está raso.

*Implementação (gate lê estrutura, não interpreta mérito):* o G2 verifica
mecanicamente o 4a (âncora concreta — F##/P##/PED##/verbete/fls. — em 3
afirmações sorteadas) e a contramedida por tese na simulação; o 4b (a
consequência declarada) é dever de sessão sob esta doutrina e objeto da
auditoria humana por amostragem.

## 7. CONTEXTO ANALÍTICO

Tarefa analítica lê MAIS, não menos — ficha + INTAKE integral +
provas-chave + teses e antíteses do módulo + verbetes citados + modelos
relevantes do Acervo. A pirâmide de leitura vale para autos brutos, nunca
para o material do próprio caso em tarefa analítica.

---

# 8. LEITURA INTEGRAL (ordem do titular, 22/07/2026)

> Acrescentado depois de um erro concreto: a sentença que julgou procedente o
> caso `0815826-72.2025` foi lida **por amostragem** (o dispositivo e as
> citações), e por isso a razão de decidir — **publicidade enganosa**, com o
> parágrafo que desmonta a blindagem documental — **passou despercebida**. A
> análise foi entregue como se fosse completa. O advogado teve de apontar.

## 8.1 A regra

**Documento decisivo se lê INTEIRO. Sem exceção, sem amostragem, sem grep.**

São decisivos, sempre: **sentença · acórdão · contestação · petição inicial ·
o contrato objeto do caso · laudo · ata de audiência · denúncia**.

`grep`/regex servem para **localizar** dentro de um documento já lido — **nunca
para substituir a leitura**. Achar o trecho não é ler a peça: a razão de decidir
raramente está onde a palavra-chave está.

## 8.2 O mecanismo — DECLARAR A COBERTURA

Toda entrega analítica declara, por documento decisivo, **quanto foi lido**:

> *"Sentença 0815826-72.2025 — **lida integralmente** (8.192 caracteres)."*
> *"Contestação da Ferreira — **lidos títulos e 4 trechos de 18 páginas; NÃO
> integral**."*

**Sem a declaração, a análise está incompleta por definição.** O objetivo não é
burocracia: é tornar **visível** a leitura parcial, que hoje se disfarça de
conclusão segura. Leitura parcial não declarada é o erro; leitura parcial
declarada é uma limitação honesta que o advogado pode decidir aceitar ou não.

## 8.3 Corolários

a) **Autos: leitura integral do que é decisivo.** A pirâmide de leitura do motor
   de autos (ler_integral / nunca_ler / sob_demanda) continua valendo para
   triar o VOLUME — mas o que cai em `ler_integral` se lê **inteiro**, e o
   plano de leitura não é desculpa para amostrar a peça central.

b) **Publicação de diário não é o processo.** O DJEN entrega a decisão e o
   raciocínio; **não entrega as provas**. Quando a decisão referencia documentos
   por ID, esses documentos **não foram vistos** — dizer isso explicitamente, e
   propor o acesso aos autos.

c) **Imagem é documento.** Print, foto e anexo se abrem **um a um**. No caso
   2026-0006, dez imagens não abertas continham a administradora, o grupo, a
   cota, três protocolos de lance, o comprovante de PIX e o anúncio de origem —
   tudo o que decidiu o caso.

d) **Se não deu para ler tudo, a entrega diz isso na primeira linha** — não na
   última, não em nota de rodapé.

## 8.4 O que isto custa, e por que se paga

Ler inteiro é mais lento e gasta mais contexto. É exatamente o que a seção 1
desta doutrina já mandava: **em tarefa analítica, profundidade é o produto, e a
economia da mecânica existe para financiar a análise.** Amostrar uma sentença
para "economizar" é economizar no único lugar onde não se pode.
