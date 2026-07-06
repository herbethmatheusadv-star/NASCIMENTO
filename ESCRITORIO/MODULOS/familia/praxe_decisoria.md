# PRAXE DECISÓRIA — FAMÍLIA (alimentos · guarda · convivência)

> A árvore de decisão da área (D11): como o sistema decide sozinho, com
> fontes, o que um advogado sênior decidiria. Construída na **Fase 4
> (2026-07-04)** a partir das decisões reais tomadas e ratificadas no caso
> 2026-0002 (DIARIO #005–#010, retificação #033, ratificações #011/#031).
>
> **Regras de uso:** (1) toda decisão tomada por esta árvore vira
> DECISAO_SISTEMA no DIARIO com fundamento, alternativa descartada e
> confiança; (2) ramo sem fonte na BASE_LEGAL não decide — rebaixa para
> Tier B; (3) o que está em `decisoes_reservadas.md` NUNCA é decidido sem o
> "ok" expresso do advogado; (4) fontes = verbetes de
> `ESCRITORIO/BASE_LEGAL/familia.md` (respeitar validade).

---

## §estrutura — Uma ação ou ações separadas?

- **Regra (Tier A):** pedidos de alimentos + guarda + convivência dos mesmos
  menores contra o mesmo genitor → **ação única cumulada**, rito especial da
  Lei de Alimentos. Fundamento: economia processual; identidade de partes e
  conexão; o rito especial comporta a cumulação (LEI5478:art1).
- Alternativa a descartar registrando: ação de alimentos isolada com guarda
  posterior — duplica atos sem acelerar a tutela (a liminar do art. 4º já é
  imediata na cumulada). *(Origem: #005)*

## §alimentos — Critério e percentual

Árvore por ramo de RENDA DO RÉU:

1. **Renda comprovada (holerite/CNIS nos autos):** pedido principal em
   percentual da **renda líquida** — praxe de partida: **30% para dois
   filhos em conjunto**, ajustável pelo trinômio (CC:art1694 §1º). Despesas
   extraordinárias de saúde/educação: 50% mediante comprovação, como pedido
   acessório quando houver base fática.
2. **Renda desconhecida (ramo do caso-fonte):**
   - pedido principal: **mínimo de 30% da renda líquida do réu para os dois
     filhos em conjunto** (preserva o ganho se a renda real for alta);
   - **+ arbitramento judicial com PISO objetivo: 30% do salário mínimo POR
     FILHO** (piso fixado pelo advogado em #033 — para 2 filhos, 60% do SM);
   - sustentar o arbitramento em indícios objetivos (CNH profissional,
     cidade de residência, ausência de alegação de hipossuficiência) e pedir
     ofícios (§oficios).
   - Fontes: LEI5478:art4 (fixação desde logo); CC:art1694/1695; PARAM:SM
     vigente (SEMPRE reverificar o decreto do ano); STJ:REsp1312706
     (necessidade presumida do menor).
3. **Nº de filhos ≠ 2:** manter a lógica "30% do SM POR FILHO" como piso do
   arbitramento; o percentual principal sobre renda líquida é DECISÃO
   RESERVADA quando fugir do padrão (ver decisoes_reservadas.md — quantum).
- **Sempre:** depósito em conta da representante (dados no CASO.yaml),
  vencimento dia 5; **retroação à citação** (LEI5478:art13p2) e provisórios
  devidos até a decisão final (§3º). *(Origem: #006 + #033)*

## §guarda — Modelo

- **Regra (Tier A):** **guarda compartilhada LEGAL** com residência fixa
  junto ao genitor que exerce o cuidado cotidiano, na cidade-base que melhor
  atende aos menores (CC:art1583 §§1º/3º; CC:art1584 §2º — redação da Lei
  14.713/2023; ECA:art21). Distância entre genitores NÃO impede
  (STJ:REsp1878041 — inclusive estados/países diferentes).
- **Desvios que rebaixam para Tier B:** (a) genitor declara não querer a
  guarda; (b) **qualquer elemento de risco de violência doméstica ou
  familiar** (exceção expressa do art. 1.584 §2º/2023) — nesses casos, parar
  e submeter ao advogado com os elementos.
- Ameaças relatadas SEM prova e nunca concretizadas: narrar como contexto,
  SEM pedido cautelar e SEM salvaguardas restritivas. *(Origem: #007)*

## §convivencia — Regime

- **Regra (Tier A) quando a posição do outro genitor é desconhecida:**
  propor **consensualização + homologação judicial**, com mínimos expressos:
  férias escolares, datas comemorativas, comunicação remota periódica
  (videochamadas); considerar a distância geográfica; pedir fixação judicial
  na falta de acordo. Fontes: ECA:art19; ECA:art22 (redação 2025 — inclui
  convivência e assistência afetiva). *(Origem: #008)*
- Regime detalhado unilateral: só quando já há histórico de conflito sobre
  convivência (aí desenhar calendário e submeter — confiança média).

## §competencia — Foro

- **Regra (Tier A):** domicílio ou residência do ALIMENTANDO (CPC:art53, II).
  Item do anti-erro fatal. Jurisdição brasileira garantida com credor
  domiciliado no Brasil (CPC:art22, I, a).

## §rito_tutelas — Rito, segredo, gratuidade

- Rito especial da Lei de Alimentos, independente de distribuição prévia
  (LEI5478:art1). Provisórios "desde logo" (LEI5478:art4) — citar o CPC
  art. 300 apenas como reforço subsidiário.
- **Segredo de justiça:** requerer expressamente sempre que houver menores
  (CPC:art189, II) — item do anti-erro fatal.
- **Gratuidade:** requerer quando a renda da parte for compatível com
  hipossuficiência (parâmetro do caso-fonte: 1 SM) — CPC:art98, CPC:art99p3,
  LEI5478:art1 §§2º-3º, STJ:gratuidade-alimentos (em ação de alimentos de
  menor, não se exige prova de insuficiência do representante).
  *(Origem: #010)*

## §citacao — Réu com endereço desconhecido

- **Cascata padrão (Tier A):** (1) tentativa no último endereço conhecido
  (documentos dos autos); (2) requisição judicial de endereço em cadastros
  públicos/concessionárias — CPC:art256 §3º — mencionando o SERASAJUD como
  meio operacional (TCT CNJ 015/2019; NÃO existe "resolução do SERASAJUD");
  (3) edital pela norma especial LEI5478:art5p4 (+ CPC:arts 256/257
  subsidiários).
- **Ajuizar SEM o endereço é autorizado** por CPC:art319 §§1º-3º (diligências
  + vedação de indeferimento). O MOMENTO do protocolo nesse cenário é
  decisão reservada (Tier B — ver decisoes_reservadas.md), porque troca
  conforto probatório por tempo de retroação. *(Origem: #010 + #028/#031)*

## §execucao_futura — Desconto em folha

- **Regra (Tier A):** incluir pedido SUBSIDIÁRIO de desconto em folha
  condicionado à confirmação de vínculo — fundamento **CPC:art529** (os
  arts. 16-18 da L5478 estão REVOGADOS — LEI5478:art16a18; NUNCA citá-los).
  *(Origem: #009 + #022)*

## §oficios — Investigação de renda

- **Regra (Tier A) com renda desconhecida:** ofícios à Receita Federal
  (IRPF), INSS/CNIS e SISBAJUD — LEI5478:art20 (menção expressa ao Imposto
  de Renda). **Indício não confirmado (ex.: CNPJ de terceiro) NÃO entra na
  petição** — os ofícios cobrem a investigação sem o risco de credibilidade.
  *(Origem: #009)*

## §acessorios — Honorários, testemunhas, intimações

- Honorários de sucumbência: requerer (praxe universal). Testemunhas: "a
  arrolar no momento processual oportuno". Intimações: em nome do advogado
  (ADVOGADO.md), portal do tribunal. MP: intimação como custos legis com
  menores (CPC:art178, II). *(Origem: #027)*

## §valor_causa — Valor da causa

- **Regra (Tier A):** alimentos = 12 × a prestação mensal PEDIDA
  (CPC:art292, III); cumulação = soma dos pedidos com conteúdo econômico
  (inciso VI); com renda do réu desconhecida, calcular sobre o PISO do
  arbitramento (§alimentos). **SEMPRE verificar o SM vigente no decreto do
  ano** (verbete PARAM:SM####) — nunca usar valor de memória ou de notícia.
  *(Origem: #033 — e a lição do R$ 1.631 fake da notícia da Câmara)*

---

## Camada LOCAL (regra de kernel — Onda 3/F6)

Anotações de praxe do juízo local, alimentadas pelas sentenças e decisões do
ACERVO desta área (calibração local da árvore — blueprint §9):

> *(nenhuma anotação ainda — n=0; o primeiro material virá das decisões do
> processo da Tânia na Vara de Família de Parauapebas)*

Formato ao anotar: `LOCAL (juízo) — ANOTAÇÃO (n=X; fontes: M-NN, M-NN): ...`
**Regras duras:** anotação NÃO é recomendação — o sistema não decide por
ela; vira recomendação apenas com **n≥3 amostras consistentes do MESMO
juízo** (registradas no Acervo, com fichas); e **camada local divergindo da
praxe nacional = SEMPRE Tier B** (o advogado decide qual seguir).

## Distribuição Tier A × Tier B deste módulo

**Tier A (decide, fundamenta, ratificação em bloco no gate):** estrutura da
ação · critério de alimentos DENTRO do padrão (30% renda líquida p/ 2 filhos
+ piso 30% SM/filho) · guarda compartilhada legal sem elementos de risco ·
convivência consensual · competência · segredo · gratuidade · cascata de
citação · desconto em folha subsidiário · ofícios · acessórios · valor da
causa pela fórmula.

**Tier B (decide, recomenda e AGUARDA o "ok"):** ver `decisoes_reservadas.md`.
Confiança baixa em qualquer ramo → rebaixa automaticamente para Tier B.
