# SOJ — Regras de sessão (Claude Code)

Este é o Sistema Operacional Jurídico do escritório NASCIMENTO. A especificação
que manda em tudo é `SOJ_BLUEPRINT_v1.md` (v1.3 + adendos). O dono é advogado
e NÃO programa: explique tudo em português simples e pergunte antes de decisões
importantes.

## SOJ Operacional — Fase 0 (desde 15/07/2026)

- A expansão (clientes, processos, INBOX, prazos v2, briefing, financeiro) é
  regida por `PROMPT_MESTRE_SOJ_OPERACIONAL.md` (raiz). Complementa o
  blueprint; em conflito entre os dois, pergunte ao advogado.
- Radar DJEN: `RADAR/` (ex-monitor-prazos; tarefa agendada "SOJ Radar DJEN
  (07h)" no Task Scheduler, diária, hora local = America/Belem).
- Entidades novas: `CLIENTES/` (CLI-####), `PROCESSOS/` (PROC-####), `INBOX/`,
  `FINANCEIRO/`, `BRIEFINGS/`, `AUTOS/` (fora do git), `_SISTEMA/`.
- Numeração: `_SISTEMA/config/numeracao.yaml`. Propriedade de cada campo:
  `_SISTEMA/config/fonte_da_verdade.md`.
- **REGRA DA CASA (OneDrive): toda sessão termina com `git commit` + `git
  push`** — ver `_SISTEMA/config/repositorio.md`.

## Início de TODA sessão (ordem obrigatória)

0. **Git health check** (diretiva 15/07/2026): `python ESCRITORIO/scripts/git_health.py`
   — acusa index.lock órfão (>30min sem git ativo), mudanças sem commit >24h e
   commits sem push >24h. Log em `_SISTEMA/logs/git_health.md`.
1. **Vigia de prazos** (blueprint, seção 7): `python ESCRITORIO/scripts/vigia_prazos.py`
   — antes de qualquer outra coisa, sobre qualquer caso. Depois, espelhar
   prazos ativos novos na agenda Google "SOJ — Prazos" (eventos anonimizados:
   "SOJ <id-do-caso> · PZ##" — nunca nomes de partes). Se o vigia lembrar o
   ritual mensal: rodar `revalidar_biblioteca.py` e reverificar NA FONTE os
   verbetes vencidos (casos afetados listados pelo próprio comando).
2. Se for trabalhar um caso: leia `CASOS/<CLIENTE>/CASO.yaml` +
   `_views/STATUS.md` + cauda do `DIARIO.md`. NÃO releia a pasta inteira.

## Doutrina de Análise (kernel — 07/07/2026)

Antes de QUALQUER tarefa analítica (diagnóstico, estratégia, simulação
adversária, juiz rigoroso, Tier B, revisão de peça/colaborador, destilação
de autos, preparação de audiência): **ler `ESCRITORIO/DOUTRINA_ANALISE.md`
e obedecê-la**. Resumo inegociável: mecânico = economia máxima; analítico =
PROFUNDIDADE É O PRODUTO (proibido economizar); quatro passadas
(mapear → aprofundar → adversariar a si mesmo → sintetizar); toda afirmação
ancorada em elemento concreto do caso e com consequência declarada; veredito
só com base e faixa; tarefa analítica LÊ MAIS (ficha + INTAKE integral +
provas + teses do módulo), nunca menos.

## ORDEM DO SISTEMA — não se limitar (diretiva do advogado, 22/07/2026)

**Antes de dizer "não dá", pergunte: como o Jusbrasil, o Escavador, o Harvey
fariam isso?** São ferramentas lícitas e regulamentadas que acessam a mesma
informação pública. Se elas conseguem e eu não, **o problema é a minha rota,
não a informação**.

O método, que já rendeu três vezes em 22/07/2026:

1. **A porta óbvia costuma ser a errada.** DataJud não traz parte; consulta de
   tribunal tem captcha. Isso não é "impossível" — é a porta errada.
2. **Pergunte de onde eles tiram.** A resposta quase sempre é o **DIÁRIO
   OFICIAL**: o DJEN publica nome de parte, íntegra de sentença, ementa de
   acórdão e chave de acesso a documento. `comunicaapi.pje.jus.br` aceita
   `nomeParte`, `siglaTribunal` e **`texto`** (busca nacional em texto integral).
3. **Tela SPA = existe API JSON por baixo.** Inspecionar a rede antes de
   desistir do site.
4. **Testar em vez de supor.** Foi testando que se descobriu que o POST do
   `ConsultaDocumento` funciona por script — o `MAPA_PJE` afirmava o contrário.

Ferramentas nascidas daí: `CONECTOR/mapear_adversario.py` (todos os processos
de uma empresa) · `CONECTOR/baixar_por_chave.py` (autos por chave do DJEN) ·
`CONECTOR/buscar_jurisprudencia.py` (jurisprudência nacional por texto livre).

**O limite que continua de pé:** captcha não se resolve, credencial não se usa
sem o titular, e nada disso dispensa conferir o teor na fonte antes de citar.

**Antes de redigir peça contra alguém: ler `ESCRITORIO/DOUTRINA_INTELIGENCIA_ADVERSARIA.md`
e rodar o protocolo P1-P5.** Saber como aquele adversário já perdeu e já ganhou
naquele foro é o que separa a petição correta da petição que vence. No caso
2026-0006 o levantamento mudou a tese, o rito, o valor e o nome da ação — antes
de a inicial existir.

## Regras duras (blueprint)

- `00_originais/` é imutável. `DIARIO.md` é append-only (corrigir = nova
  entrada). `_views/` nunca se edita à mão (regenerar com `gerar_views.py`).
- Documento novo entra SÓ pelo `receber_documento.py` (ponto único de entrada).
- Gates G1/G2/G3 pelo `gate_check.py`; gate reprovado bloqueia a etapa.
- Exceções/justificativas são CAMPOS do CASO.yaml com referência ao DIARIO
  (blueprint, seção 6 — robustez); os gates não leem texto livre.
- Nunca citar lei de memória: verbete verificado em `ESCRITORIO/BASE_LEGAL/`
  dentro da validade; diante de lacuna, parar e perguntar — nunca inventar fato.
- Decisões técnico-jurídicas: DECISAO_SISTEMA no DIARIO com fundamento,
  alternativa descartada e confiança (D11); ratificação em bloco nos gates.

## Módulos e kernel

- Comandos padrão do sistema: skill `soj-kernel` (.claude/skills/soj-kernel/).
- Módulos PLENOS: `familia/` · `consumidor_aguas/` (negativação × Águas do
  Pará, JEC) · `bancario_ccb/` (defesa em execução de CCB × cooperativas —
  **modo defesa nativo: novo caso da área nasce --polo passivo**) ·
  `civel/` (honra e reputação digital — nascido do caso 2026-0004). Cada um:
  praxe_decisoria (árvore Tier A/B + camada LOCAL), decisoes_reservadas,
  checklist_documental, anti_erro_fatal, teses (com antiteses) e templates.
  Esqueletos: `trabalhista/`, `previdenciario/` (módulo nasce do caso 1).
- Módulo SEMEADO `consumidor_consorcio/` — **golpe do falso consórcio**
  (vende-se casa, assina-se intermediação; a "entrada" é corretagem a fundo
  perdido). Nasceu do caso 2026-0006 em 22/07/2026; n=1. **Ler
  `ANATOMIA_DO_GOLPE.md` primeiro.** Área de especialização declarada pelo
  advogado em Parauapebas. Regra própria: **degravar os áudios ANTES de opinar
  sobre viabilidade** — o papel está todo contra o cliente, o caso vive na
  prova oral. Jurisprudência ainda NÃO verbetada; Lei 11.795 `a_confirmar`.
- Camada LOCAL da praxe: anotação com contagem (fontes = Acervo); vira
  recomendação só com n≥3 do MESMO juízo; divergiu do nacional = Tier B.

## Regra do laboratório

`CASOS/TESTE_FICTICIO` é o caso-laboratório PERMANENTE. Alterou qualquer
script? Rode tudo nele ANTES de tocar em caso real.

## Dados sensíveis

Casos com `segredo_justica: true` envolvem menores: nunca colar dados
identificados fora deste ambiente; em serviços externos (ex.: Calendar),
usar só o id do caso e o PZ## — nunca nomes de partes.
