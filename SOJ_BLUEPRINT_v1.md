# SOJ — SISTEMA OPERACIONAL JURÍDICO NASCIMENTO
## Blueprint de Arquitetura v1.7

**Data:** 2026-07-04
**Status:** v1.7 — porta única ganha **roteador de tipos de documento** e **modo defesa** (seção 7): análise de peças adversárias, decisões e sentenças com extração automática de prazos; casos com o cliente no polo passivo; Acervo com extração autônoma de técnicas. v1.6: Acervo. v1.5: mão dupla (colheita + porta de retorno). Obra entregue na v1.4 (Fases 1–4 em 04/07/2026). Histórico: D11 (v1.3), contrato de entrada (v1.2), D2 (v1.1).
**Origem:** Redesenho crítico do sistema testado no CASO_TESTE_001 (37 arquivos → arquitetura dados + visões)
**Premissas:** Operador único (advogado + IA). Volume atual baixo, ambição de escala — a arquitetura custa o mesmo em 5 ou 50 casos/mês; o que muda é o retorno.

---

# 0. OS SETE PRINCÍPIOS DO SISTEMA

Tudo neste blueprint deriva destes princípios. Se uma decisão futura violar um deles, a decisão está errada — não o princípio.

1. **Dados + visões, não arquivos.** Cada informação vive em UM lugar (a fonte da verdade). Todo o resto — status, quadros, checklists, róis — é visão gerada por script a partir dessa fonte. Visão nunca é editada à mão; se está errada, corrige-se a fonte e regenera-se.

2. **Escrever uma vez, referenciar sempre.** Fatos, provas, pedidos, partes, prazos e pendências têm IDs estáveis (F01, P01, PED01, PT01, PZ01, PEN01). A minuta, o diário e as análises referenciam os IDs — nunca reescrevem o conteúdo.

3. **Append-only para o que é histórico.** Decisões (do sistema e do advogado), gates, eventos e recebimentos entram num diário imutável: nunca editado, só acrescido. Isso preserva o que se sabia em cada momento — valor probatório e de auditoria que um "documento vivo" destrói.

4. **Gates executáveis, não pareceres.** A prontidão do caso não é uma opinião escrita num arquivo; é o resultado de um checklist objetivo que a IA executa e que bloqueia o avanço se falhar.

5. **Efêmero ≠ permanente.** Roteiros de entrevista, rascunhos e mensagens ao cliente são artefatos legítimos — mas descartáveis. Nascem em `_efemeros/`, são regeneráveis a partir da fonte da verdade, e podem ser apagados sem perda.

6. **Verificação com prazo de validade.** Todo dispositivo legal citado tem texto literal + fonte + data de verificação. Verificação envelhece; o gate final exige revalidação do que venceu. Nunca se cita lei de memória.

7. **Kernel + módulos.** O kernel é agnóstico de área (intake, rastreabilidade, diário, gates, views, protocolo). Cada área do direito é um módulo que fornece: árvore de decisão (praxe decisória com fontes), lista curta de decisões reservadas, checklist documental, template de minuta, banco de teses e checklist anti-erro fatal. Suas skills de Águas do Pará e CCB já são proto-módulos — provam o padrão.

---

# 1. DECISÕES DE ARQUITETURA (D1–D10)

Cada decisão traz o porquê e a alternativa rejeitada. **Aprove ou vete por número.**

### D1 — Escopo: kernel genérico + módulo FAMÍLIA primeiro
**Decisão:** Construir o kernel agnóstico de área e o módulo `familia` (alimentos, guarda, convivência) como primeiro módulo completo. CCB/cooperativas e Águas do Pará são adaptados ao kernel na Fase 5, sem reescrita.
**Por quê:** O CASO_TESTE_001 já pagou o custo de aprendizado em família; o material existe (minuta, pesquisa, estratégia) e vira template. E suas duas skills verticais provam que módulos funcionam — o que nunca existiu foi o kernel comum.
**Rejeitado:** Multi-área desde o início (dispersa o esforço antes de validar o kernel); pipeline só de família (condena o sistema a ser reescrito quando a segunda área chegar).

### D2 — Ambiente: Claude Code sobre pasta local + sync Google Drive + git
**Decisão:** O escritório vive numa pasta local do seu computador, ex.: `~/NASCIMENTO/`, com um subdiretório por cliente dentro de `CASOS/`. Essa pasta:
- é operada pelo **Claude Code** (que lê, escreve, roda scripts e gates — com persistência real entre sessões);
- é sincronizada pelo **Google Drive para desktop** (backup contínuo, acesso remoto e leitura no celular pelo app do Drive);
- é versionada com **git** (commit automático a cada gate = trilha de auditoria técnica imutável, complementar ao DIARIO).

Sem dependência de nenhum outro programa: o sistema inteiro é pasta + arquivos de texto + scripts.

**Por quê:** O claude.ai reseta o sistema de arquivos entre conversas — é por isso que hoje você reenvia tudo. Só um filesystem persistente permite os três pilares do sistema: scripts que geram views **a custo zero de token**, gates executáveis, e contexto mínimo por sessão. O claude.ai continua sendo usado para conversas de estratégia e pesquisa — mas subindo apenas o `CASO.yaml` + a view relevante (contexto pequeno), nunca a pasta inteira.
**Rejeitado:** Google Drive como ambiente primário (Claude não roda scripts sobre ele; edição via conector é lenta para uma árvore de caso); upload manual (o modelo atual — é a causa direta da dor de hoje).

### D3 — Fonte da verdade: um `CASO.yaml` por caso
**Decisão:** Todos os DADOS do caso (partes, fatos, provas, pedidos, fundamentos, prazos, pendências, classificação, estado dos gates) vivem num único arquivo estruturado. Ver schema completo na seção 3.
**Por quê:** Mata os Problemas 2 e 3 do manual pela raiz. O mapeamento fato→prova→pedido→parágrafo é feito UMA vez, como dados — e as quatro tabelas que o sistema antigo gerava viram quatro visões do mesmo dado. O STATUS nunca mais desatualiza porque ele não é mantido: é gerado.
**Rejeitado:** Consolidar 37 arquivos em 7 arquivos de prosa (a proposta do próprio manual) — resolve o sintoma (quantidade), não a doença (informação duplicada mantida à mão em vários lugares).

### D4 — `DIARIO.md` append-only por caso
**Decisão:** Um diário imutável com entradas numeradas e datadas registra: decisões do sistema (D11) e do advogado, documentos recebidos, gates executados, pesquisas concluídas, contatos com o cliente, eventos processuais e alertas. Substitui: `decisoes_do_advogado_humano.md`, `DECISOES_REGISTRADAS.md`, `PARECER_DE_PRONTIDAO.md` e a função histórica do `STATUS_DO_CASO.md`.
**Por quê:** Preserva o melhor conceito do sistema antigo (decisão humana explícita e registrada) e corrige sua fraqueza: registro editável não prova nada. Append-only + git dão trilha temporal real — o que se sabia, quando se sabia, quem decidiu o quê.

### D5 — Views geradas por script, nunca por LLM, nunca à mão
**Decisão:** `gerar_views.py` produz de `CASO.yaml` + tags da minuta: STATUS de 1 página, quadro de rastreabilidade completo, rol de documentos, checklist do cliente (formato WhatsApp), pendências priorizadas. Regeneradas a cada mudança na fonte.
**Por quê:** Views por script custam **zero token** e são sempre consistentes. No sistema antigo, cada uma dessas tabelas era uma geração de LLM separada — e quatro fontes de inconsistência.

### D6 — `BASE_LEGAL/` compartilhada entre casos, com validade
**Decisão:** Um verbete por dispositivo legal (área a área): texto literal + fonte oficial + data de verificação + situação (vigente / alterado / revogado) + notas. Os casos referenciam a base; não repetem a pesquisa. Janelas de validade: 90 dias para códigos estáveis, 30 dias para leis com alteração recente — e **rechecagem obrigatória dos dispositivos-núcleo no G3**, na véspera do protocolo.
**Por quê:** É o maior vazamento de tokens do sistema antigo: a verificação do art. 1.694 do CC era paga por caso. Com a base, é paga por período. O achado real do CASO_TESTE (ECA art. 22 alterado em 2025; arts. 16–18 da Lei 5.478 revogados) já entra como verbete — trabalho pago vira ativo permanente. O banco `referencias/jurisprudencia.md` da sua skill Águas do Pará é exatamente isso em embrião; a decisão generaliza o padrão.

### D7 — Minuta nasce de template do módulo, com tags de rastreabilidade por parágrafo
**Decisão:** Cada tipo de ação tem um template validado (`MODULOS/familia/templates/alimentos_guarda_convivencia.md`) no markup que a skill de formatação Nascimento já aceita (`#`, `##`, `-`, `>`). Todo parágrafo fático/de pedido carrega uma tag em linha própria: `<!-- SOJ: F04 | P03,P05 | PED01 | CC:1694 -->`. O gate lê as tags para auditar cobertura; o script de protocolo as remove antes da formatação.
**Por quê:** (a) A minuta parte 60–70% pronta em estrutura — geração de LLM só onde há juízo, não onde há boilerplate. (b) A rastreabilidade bidirecional (parágrafo↔fato↔prova↔lei) que o sistema antigo tentou 4 vezes vira propriedade automática do texto. (c) A saída pluga direto no seu timbrado sem retrabalho.

### D8 — Três gates executáveis: G1, G2, G3
**Decisão:** G1 (intake completo), G2 (pronto para minutar), G3 (pronto para protocolar). Cada gate é um checklist objetivo que `gate_check.py` + Claude executam; o resultado (aprovado/reprovado + lista do que falta) vira entrada no DIARIO. Gate reprovado **bloqueia** a etapa seguinte. Ver seção 6.
**Por quê:** Formaliza e automatiza o "REVISÃO ANTI-ERRO FATAL" que sua skill de Águas do Pará já faz à mão. É também sua defesa estrutural contra a Recomendação 159/2024-CNJ: em litigância de massa, o gate é o que separa volume de qualidade de litigância predatória.

### D9 — Profundidade adaptativa: simples / padrão / complexo
**Decisão:** O intake classifica o caso por critérios objetivos (nº de documentos, nº de partes, controvérsia fática, valor, urgência). A classificação decide o que sequer nasce: cadeia de custódia formal só em caso documental pesado; simulação adversária resumida em caso simples de rito padronizado, completa em caso controverso; etc.
**Por quê:** O manual identificou corretamente que a burocracia útil num caso de 200 documentos é gordura num caso de 10. A resposta certa não é cortar o artefato — é condicioná-lo.

### D10 — Integração nativa com o ecossistema existente
**Decisão:** (a) A skill `formatacao-peticoes-nascimento` é o passo final obrigatório do E4 — a minuta aprovada no G3 vira DOCX no timbrado por ela. (b) As skills `peticao-negativacao-aguas-do-para` e `advogado-bancario-cooperativas` são adaptadas na Fase 5 para ler/escrever `CASO.yaml` e DIARIO — viram módulos plenos sem perder nada do que já fazem. (c) Uma nova skill fina, `soj-kernel`, encapsula os comandos do sistema para que qualquer sessão de Claude opere o padrão sem reexplicação.
**Por quê:** Você já investiu nos módulos e no padrão visual. O kernel deve ser o denominador comum deles, não um concorrente.

### D11 — Autonomia decisória: o sistema decide como um sênior; o advogado ratifica por exceção
**Decisão:** Toda decisão técnico-jurídica com praxe identificável — percentual e critério de alimentos, modelo de guarda, regime de convivência, verbas e valores, quantum indenizatório, competência, rito, tutelas — é **tomada pelo próprio sistema**, aplicando a árvore de decisão do módulo (`praxe_decisoria.md`: praxe jurisprudencial nacional + legislação + tabelas, com fontes), e registrada no DIARIO como `DECISAO_SISTEMA` — sempre com fundamento, alternativa descartada e grau de confiança. O advogado não é consultado decisão a decisão: **ratifica em bloco nos gates**, lendo o resumo de decisões (1 página), com veto pontual.
**Dois níveis:** **Tier A** (praxe pacífica → decide e segue; ratificação em bloco) e **Tier B** (alta consequência, vontade do cliente ou jurisprudência dividida → decide, recomenda e aguarda o "ok": ex. prisão civil do alimentante, renúncia a excedente de alçada, acordo vs. litígio, aceitação de risco apontado na simulação adversária). Confiança baixa rebaixa automaticamente a decisão para Tier B. A distribuição A/B é definida por módulo e migra para A conforme a árvore amadurece.
**O irredutível (por lei, não por desenho):** a peça sai com a assinatura e sob a responsabilidade do advogado (Estatuto da OAB). O G3 mantém, portanto, **uma única ação humana obrigatória**: revisão final + ratificação. O sistema é autossuficiente até a porta do protocolo; a porta é do advogado.
**Por quê:** É o comportamento de um sênior real: ele não pergunta o percentual — fixa pela praxe e submete a peça pronta. O DIARIO fundamentado transforma autonomia em processo auditável (defesa documental perante OAB/CNJ) e reduz o papel do advogado de ~15 microdecisões por caso para 1–2 ratificações.
**Substitui:** o conceito original de `decisoes_obrigatorias.md` ("o que a IA nunca decide") por `praxe_decisoria.md` ("como o sistema decide, com fontes") + `decisoes_reservadas.md` (lista curta do que exige confirmação expressa).

---

# 2. TOPOLOGIA DE DIRETÓRIOS

```
~/NASCIMENTO/                          ← raiz = repositório git = pasta sincronizada no Drive
│
├── ESCRITORIO/
│   ├── ADVOGADO.md                    ← dados fixos (qualificação, OAB, assinatura) — fonte única
│   ├── BASE_LEGAL/
│   │   ├── familia.md                 ← verbetes verificados (seção 8)
│   │   ├── consumidor.md
│   │   └── bancario.md
│   ├── ACERVO/                        ← modelos de referência (M-01…): peças e decisões, anonimizados, com ficha de curadoria
│   ├── MODULOS/
│   │   ├── familia/
│   │   │   ├── MODULO.md              ← contrato do módulo (seção 9)
│   │   │   ├── praxe_decisoria.md
│   │   │   ├── decisoes_reservadas.md
│   │   │   ├── checklist_documental.md
│   │   │   ├── teses.md
│   │   │   └── templates/
│   │   │       └── alimentos_guarda_convivencia.md
│   │   ├── consumidor_aguas/          ← adaptação da skill existente (Fase 5)
│   │   └── bancario_ccb/              ← adaptação da skill existente (Fase 5)
│   └── scripts/
│       ├── novo_caso.py               ← cria a árvore do caso + CASO.yaml esqueleto
│       ├── receber_documento.py       ← o ponto único de entrada (seção 7)
│       ├── gerar_views.py             ← regenera _views/ a partir da fonte
│       ├── gate_check.py              ← executa G1/G2/G3
│       └── preparar_protocolo.py      ← strip de tags, chama a formatação, monta o pacote
│
├── CASOS/
│   └── TANIA/                         ← pasta = NOME DO CLIENTE (padrão do escritório; o id do caso vive no CASO.yaml)
│       ├── 00_originais/              ← IMUTÁVEL. Exatamente como recebido. (mantido do sistema antigo)
│       ├── 01_documentos/             ← DOC-01… renomeados, em PDF (padrão das suas skills)
│       ├── CASO.yaml                  ← FONTE DA VERDADE (seção 3)
│       ├── DIARIO.md                  ← ledger append-only (seção 4)
│       ├── INTAKE.md                  ← prosa: resumo do atendimento, cronologia narrativa, contradições
│       ├── ESTRATEGIA.md              ← prosa: diagnóstico, estratégia, simulação adversária, juiz rigoroso, riscos
│       ├── MINUTA_v01.md … v_final    ← produto, com tags SOJ
│       ├── _views/                    ← 100% gerado. Nunca editar à mão.
│       │   ├── STATUS.md              (1 página; frontmatter alimenta o painel multi-casos)
│       │   ├── rastreabilidade.md     (fato × prova × pedido × parágrafo × fundamento — A matriz, única)
│       │   ├── rol_documentos.md
│       │   ├── checklist_cliente.md   (pronto para colar no WhatsApp)
│       │   └── pendencias.md
│       ├── _efemeros/                 ← roteiros, rascunhos, mensagens. Apagável.
│       └── PROTOCOLO/                 ← criado no E4: peça DOCX final + DOC-01…NN + índice
│
└── PAINEL.md                          ← visão do escritório: todos os casos, fase, gate, próximo prazo (gerada)
```

**O que cada caso tem de permanente escrito por LLM: 4 arquivos** (INTAKE, ESTRATEGIA, MINUTA, DIARIO — este último só recebe entradas). Todo o resto é dado estruturado, view gerada ou efêmero.

---

# 3. `CASO.yaml` — A FONTE DA VERDADE

Schema comentado, com trechos baseados no CASO_TESTE_001 — **valores ilustrativos**. Regra de precedência (lição da E3): a fonte da verdade de um caso é sempre o seu próprio CASO.yaml + DIARIO; em conflito entre exemplo desta planta e registro do caso, **o registro do caso governa**:

```yaml
caso:
  id: 2026-0001               # identificador do sistema — a PASTA usa o nome do cliente
  titulo: "Tânia x Cícero — Alimentos c/c Guarda e Regulamentação de Convivência"
  area: familia
  modulo: familia/alimentos_guarda_convivencia
  complexidade: padrao          # simples | padrao | complexo  (D9)
  fase: E3_minuta               # E1_intake | E2_estrategia | E3_minuta | E4_protocolo | ativo | encerrado
  comarca: "Parauapebas/PA"
  segredo_justica: true         # menores envolvidos
  gates:
    G1: { status: aprovado, data: 2026-06-20, diario: "#012" }
    G2: { status: aprovado, data: 2026-06-28, diario: "#019" }
    G3: { status: pendente }

partes:
  - { id: PT01, papel: autora_representante, nome: "Tânia …", cpf: "…", renda_mensal: 1621.00,
      qualificacao: completa }
  - { id: PT02, papel: reu, nome: "Cícero …",
      endereco: { status: nao_confirmado, pendencia: PEN03 } }   # ← lacuna vira dado, não parágrafo
  - { id: PT03, papel: alimentanda, nome: "Jullia …", nascimento: 2014-…, doc: P01 }
  - { id: PT04, papel: alimentando, nome: "Cícero Jr. …", nascimento: 2018-…, doc: P02 }

fatos:                          # status: provado | alegado | controverso
  - id: F01
    descricao: "Filiação dos menores em relação ao réu"
    status: provado
    provas: [P01, P02]
    pedidos: [PED01, PED02, PED03]
  - id: F04
    descricao: "Inadimplência alimentar do réu desde a separação"
    status: alegado             # ← a distinção-coração do trabalho jurídico, agora como dado
    provas: []
    pendencias: [PEN01]
  - id: F06
    descricao: "Réu reside no Rio de Janeiro/RJ; menores em Parauapebas/PA"
    status: alegado
    provas: [P05]               # CNH com endereço — força relativa

provas:
  - id: P01
    doc: "01_documentos/DOC-01_CERTIDAO_NASCIMENTO_JULLIA.pdf"
    original: "00_originais/D-03.jpg"     # ← a cadeia de custódia vira um campo, não um arquivo
    o_que_prova: "Filiação e idade da menor"
    forca: plena
    fragilidade: null

pedidos:
  - id: PED01
    tipo: alimentos_provisorios_e_definitivos
    parametro: "30% SM/filho — DECISAO_SISTEMA #015, ratificada em #019"   # fixado pela árvore do módulo
    fundamentos: [LEI5478:art4, CC:art1694, CC:art1706]
    fatos: [F01, F04]
  - id: PED02
    tipo: guarda_compartilhada_residencia_materna
    fundamentos: [CC:art1583, CC:art1584]
    fatos: [F01, F06]

fundamentos_citados:            # espelho local do que este caso usa da BASE_LEGAL
  - { ref: "CC:art1694", verificado_em: 2026-06-30, status: vigente }
  - { ref: "ECA:art22",  verificado_em: 2026-06-30, status: vigente_com_alteracao_2025,
      nota: "redação alterada — usar texto atual, ver verbete" }

prazos:
  - { id: PZ01, descricao: "…", data: 2026-07-15, criticidade: alta }

pendencias:                     # responsavel: cliente | advogado | terceiro
  - { id: PEN01, descricao: "Extrato bancário 12 meses (comprovar F04)",
      responsavel: cliente, prioridade: critica, bloqueia: [G3] }
  - { id: PEN03, descricao: "Confirmar endereço atual do réu no RJ",
      responsavel: advogado, prioridade: critica, bloqueia: [G3] }
```

**Este único arquivo absorve 12 dos 37 arquivos antigos:** fatos_identificados, pessoas_e_entidades, prazos_e_urgencias, documentos_solicitados, PENDENCIAS_PRIORIZADAS, indice_de_provas, matriz_fato_prova, correspondencia_originais_copias, QUADRO_FATO_PROVA_PEDIDO, mapa_fato_prova_paragrafo (via tags da minuta), MARCADORES_PENDENTES e pendencias_da_minuta (pendências com `bloqueia: [G3]`).

---

# 4. `DIARIO.md` — O LEDGER

Formato de entrada (numeração sequencial, nunca editar, só acrescentar ao fim; o conteúdo do exemplo é ilustrativo):

```markdown
## #015 | 2026-06-27 16:40 | DECISAO_SISTEMA
Alimentos: 30% do salário mínimo por filho (60% total) + 50% das despesas
extraordinárias de saúde e educação mediante comprovação.
Fundamento: renda do réu não comprovada → ramo "renda desconhecida" da árvore
(praxe_decisoria.md §alimentos); praxe consolidada TJPA/STJ na BASE_LEGAL.
Alternativa descartada: % sobre rendimentos líquidos — inviável sem prova de renda.
Confiança: alta · Tier A (ratificação em bloco no G2) · Afeta: PED01
---
## #019 | 2026-06-28 10:12 | GATE
G2 executado: APROVADO. 9/9 itens. Relatório: _views/gate_G2_2026-06-28.md
---
## #021 | 2026-07-02 09:30 | DOC_RECEBIDO
Recebido extrato bancário Caixa 07/2025–06/2026 → 00_originais/E-01.pdf →
DOC-11. Registrado como P11, vinculado a F04 (status alterado: alegado → provado).
Resolve: PEN01
---
```

**Tipos de entrada:** `DECISAO_SISTEMA` · `DECISAO_ADVOGADO` (vetos e reservadas) · `RATIFICACAO` · `DOC_RECEBIDO` · `GATE` · `PESQUISA` · `CONTATO_CLIENTE` · `EVENTO_PROCESSUAL` · `ALERTA` · `NOTA`.

**Regras duras:** (1) entradas jamais são editadas — correção é nova entrada referenciando a anterior; (2) decisão sem registro não existe: toda decisão técnico-jurídica do sistema entra como DECISAO_SISTEMA com fundamento, alternativa descartada e confiança; vetos e decisões reservadas do advogado entram como DECISAO_ADVOGADO; ratificações em bloco, como RATIFICACAO; (3) todo gate gera entrada, aprovado ou não.

---

# 5. AS VIEWS

| View | Gerada de | Regenerada quando |
|---|---|---|
| `STATUS.md` (1 página) | CASO.yaml + últimas 5 entradas do DIARIO + próximos 3 prazos | Qualquer mudança na fonte |
| `rastreabilidade.md` | fatos × provas × pedidos (CASO.yaml) × tags SOJ da minuta | Mudança em CASO.yaml ou na minuta |
| `rol_documentos.md` | `provas[]` na ordem dos DOC-NN | Nova prova |
| `checklist_cliente.md` | `pendencias[responsavel: cliente]`, linguagem leiga, pronto p/ WhatsApp | Mudança em pendências |
| `pendencias.md` | `pendencias[]` por prioridade, com o que cada uma bloqueia | Mudança em pendências |
| `resumo_decisoes.md` | Entradas DECISAO_SISTEMA agrupadas: decisão + fundamento + tier — a folha de ratificação de 1 página | Antes de cada gate |
| `PAINEL.md` (raiz) | frontmatter dos STATUS.md de todos os casos | Qualquer caso mudar |

Regra única: **se está em `_views/`, foi gerado.** Divergiu da realidade? A fonte está errada — corrija lá.

---

# 6. OS TRÊS GATES

Executados por `gate_check.py` + revisão da IA; resultado vira entrada no DIARIO e relatório em `_views/`. **Reprovado = etapa seguinte bloqueada.** **Robustez (aprendizado da Fase 3):** os checks leem campos estruturados do CASO.yaml, nunca raspagem de texto livre do DIARIO — exceções e justificativas são campos com referência à entrada do diário, não frases a interpretar.

### G1 — Intake completo (habilita a Etapa 2)
- [ ] `00_originais/` preservado; todo documento renomeado em `01_documentos/` e registrado como P## com campo `original`
- [ ] Toda parte registrada (PT##) com qualificação completa OU pendência aberta apontando o que falta
- [ ] Fatos essenciais registrados com status honesto (provado/alegado/controverso)
- [ ] Prazos identificados (PZ##) — inclusive prescrição/decadência quando aplicável
- [ ] Pendências críticas registradas com responsável e o que bloqueiam
- [ ] Complexidade classificada (D9) e módulo definido
- [ ] Checklist do cliente gerado e enviado

### G2 — Pronto para minutar (habilita a Etapa 3)
- [ ] ESTRATEGIA.md completo: diagnóstico + estratégia + **simulação da defesa adversária** + **análise do juiz rigoroso** (profundidade conforme D9)
- [ ] **Toda decisão da árvore `praxe_decisoria.md` do módulo foi tomada e fundamentada (DECISAO_SISTEMA)** — no família: pedidos incluídos, critério/percentual de alimentos, modelo de guarda, regime de convivência, comarca, gratuidade, segredo de justiça, dados para depósito
- [ ] Decisões Tier B / reservadas com "ok" expresso do advogado; **ratificação em bloco** do `resumo_decisoes.md` registrada no DIARIO (RATIFICACAO)
- [ ] Todo pedido pretendido (PED##) tem ≥1 fato vinculado; fatos-chave sem prova têm pendência ou justificativa estratégica registrada
- [ ] Nenhuma pendência com `bloqueia: [G2]` aberta
- [ ] Riscos da simulação adversária têm contramedida na estratégia ou aceitação expressa no DIARIO

### G3 — Pronto para protocolar (habilita a Etapa 4)
- [ ] **Zero** marcadores `[VALIDAR…]`/`[PESQUISAR…]` na minuta
- [ ] Todo parágrafo fático e todo pedido da minuta carrega tag SOJ válida (fato existente, prova existente)
- [ ] Todo PED## fecha o circuito: pedido ↔ fato(s) ↔ prova(s) ↔ parágrafo(s) ↔ fundamento(s) — ou exceção justificada no DIARIO
- [ ] Todo fundamento citado existe na BASE_LEGAL com `verificado_em` dentro da validade; **dispositivos-núcleo rechecados na fonte oficial na véspera do protocolo**
- [ ] Checklist anti-erro fatal do módulo executado (ex.: no família — competência = domicílio do alimentando; MP como custos legis; alimentos provisórios pedidos expressamente)
- [ ] Rol de documentos = arquivos da pasta = referências DOC-NN na peça (conferência automática)
- [ ] Nenhuma pendência com `bloqueia: [G3]` aberta
- [ ] Valores, datas, nomes e CPFs conferidos contra os documentos — e contra as decisões registradas (checagem cruzada peça ↔ DECISAO_SISTEMA: todo quantum/percentual da minuta bate com a decisão que o originou)
- [ ] **Entrada final no DIARIO: advogado declara revisão humana integral da peça** (a IA prepara; você assina)

---

# 7. FLUXO OPERACIONAL

### O pipeline (6 etapas viram 4)

```
E1 INTAKE      → povoar 00_originais, 01_documentos, CASO.yaml, INTAKE.md; gerar views  → G1
E2 ESTRATÉGIA  → ESTRATEGIA.md (diagnóstico, simulação adversária, juiz rigoroso);
                 decisões do advogado → DIARIO                                          → G2
E3 MINUTA      → template do módulo + BASE_LEGAL (pesquisa só do que falta/venceu);
                 minuta com tags SOJ; iterações v01→vNN                                 → G3
E4 PROTOCOLO   → strip de tags → skill de formatação Nascimento (timbrado DOCX) →
                 pasta PROTOCOLO/ (peça + DOC-01…NN + índice) → entrada DIARIO → arquivo
```

### O contrato de entrada: a bagunça é sua, a ordem é do sistema

A pasta do cliente nasce do jeito mais preguiçoso possível: um arquivo de texto/DOCX com o relato + os documentos exatamente como vieram (fotos, PDFs, prints), sem nomeação nem organização. O comando `novo caso` / `organizar a pasta de X` recebe esse caos e produz a estrutura da seção 2:

1. Lê tudo e **identifica a área e o módulo sozinho** — anuncia quando for óbvio, pergunta quando for ambíguo; a classificação (e eventual correção do advogado) vira entrada no DIARIO;
2. Lacra os originais em `00_originais/`, cria as cópias DOC-NN em `01_documentos/`;
3. Povoa o CASO.yaml (partes, fatos com status, provas, prazos, pendências), escreve o INTAKE.md;
4. Gera as views + o checklist do cliente e roda o G1.

**A estrutura do caso é SAÍDA do sistema, nunca tarefa do advogado.** Convenção única e opcional: havendo vários arquivos de texto, nomear o principal como RELATO ajuda — mas o sistema descobre sozinho.

**Roteador de tipos e modo defesa (v1.7):** a porta única classifica todo documento por tipo e destino — prova → P##; **peça do adversário** → análise adversarial (teses deles, fraquezas, pontos de ataque) alimentando a defesa; **decisão/despacho/sentença do próprio processo** → EVENTO_PROCESSUAL com *extração automática do prazo* (PZ## no vigia e no Calendar antes de qualquer outra análise); **sentença favorável** → candidata ao ACERVO (praxe local). Casos iniciados por peça adversária (cliente réu/executado) entram em **modo defesa**: campo `polo` no CASO.yaml, alegações do adversário com status próprio (alegado_pelo_adversario/controverso), G1 com item zero — *prazo de resposta identificado, calculado e no vigia* —, produto = peça de defesa do módulo, e simulação adversária invertida (simula-se a réplica do autor). A inteligência de leitura é nativa do motor; o roteador é o que a torna disciplinada: toda tese extraída passa pela BASE_LEGAL, toda estratégia pelo G2.

### O ponto único de entrada (resolve o "Problema 4" do manual)

Quando qualquer coisa nova chega — documento, informação, decisão — existe UM fluxo:

```
"chegou o extrato bancário da Tânia"
→ copia p/ 00_originais (intocado)     → converte/renomeia p/ 01_documentos (DOC-11)
→ registra P11 em CASO.yaml            → vincula a F04 (alegado → provado)
→ baixa PEN01                          → entrada #021 no DIARIO
→ regenera views                       → reporta: "F04 agora provado; G3 ainda bloqueado por PEN03"
```

Uma ação do usuário, consistência total. Nada de atualizar 4 arquivos à mão.

### Comandos padrão do kernel (a interface homem-sistema)

`novo caso` · `chegou documento X do caso Y` · `registrar decisão:` · `rodar G1/G2/G3` · `status do caso Y` · `status do escritório` · `gerar minuta` · `revisar peça` (ciclo diagnóstico → alvo → reescrita → diff) · `absorver minha versão da peça` · `colher aprendizados do caso X` · `preparar protocolo` — encapsulados na skill `soj-kernel` (Fase 4) para que qualquer sessão opere igual.

**Vigia de prazos (aprendizado do piloto da Fase 2):** o sistema é movido a evento, mas prazo é movido a tempo. Regra: toda sessão, sobre qualquer caso, começa varrendo os prazos de TODOS os casos contra a data do dia; prazo vencido ou a ≤ 7 dias gera entrada ALERTA no DIARIO do caso e destaque no PAINEL. Complemento recomendado: espelhar prazos no Google Calendar do advogado (antecipável da Fase 5), como rede de segurança independente de sessões. Regra de privacidade do espelhamento (aprovada na Fase 3): eventos anonimizados — id do caso + id do prazo (ex.: "SOJ 2026-0002 · PZ01"), nunca nomes das partes.

**Colheita de aprendizados (era da operação):** ao protocolar/encerrar um caso, o kernel varre o DIARIO e propõe promoções ao acervo — decisões Tier B e vetos → ramos/ajustes da árvore ou novas reservadas; falso-positivos e quase-erros → anti-erro fatal; fontes inexistentes/revogadas → antiteses; desvios de template → variantes; verbetes novos já estão na BASE_LEGAL (apenas listados). Sai uma PROPOSTA_DE_APRENDIZADO de 1 página; o advogado ratifica em bloco (padrão D11) e só então o módulo é atualizado. **Captura é automática; promoção é ratificada** — a catraca avança um dente por caso e nunca desliza para trás.

**Porta de retorno (a mão dupla da minuta):** o advogado pode devolver ao sistema uma versão melhorada da peça (.md ou DOCX). O kernel faz o diff contra a última versão e classifica cada mudança: estilo → absorve e vira candidato de colheita; fato novo → exige F## com prova ou status de alegação; citação nova → verificação na fonte antes de aceitar (a regra "nunca de memória" vale também para o humano); quantum/pedido → reconciliação com as decisões (DECISAO_ADVOGADO retificadora). Depois: re-tagueia, versiona (vNN — nada se sobrescreve), registra no DIARIO e re-roda o gate da fase antes de regerar o DOCX. Regra de ouro: **a versão protocolada é sempre a última que o sistema conhece** — peça editada por fora e protocolada sem retornar é a única forma de quebrar o sistema.

---

# 8. `BASE_LEGAL/` — FORMATO DO VERBETE

```markdown
## CC:art1694 — Código Civil, art. 1.694
**Texto literal:** "Podem os parentes, os cônjuges ou companheiros pedir uns aos
outros os alimentos de que necessitem para viver de modo compatível com a sua
condição social, inclusive para atender às necessidades de sua educação."
**Fonte:** planalto.gov.br/ccivil_03/leis/2002/L10406compilada.htm
**Verificado em:** 2026-06-30 · **Situação:** vigente · **Validade:** 90 dias
**Notas de uso:** binômio necessidade × possibilidade (§1º). Par com art. 1.706 (provisórios).
**Casos que citam:** 2026-0001
```

Regras: (1) verbete vencido não passa no G3 sem revalidação; (2) dispositivo com histórico de alteração recente (ex.: ECA art. 22, alterado em 2025) recebe validade de 30 dias; (3) o campo "Casos que citam" permite, quando uma lei mudar, saber **instantaneamente quais casos ativos são afetados** — impossível no sistema antigo; (4) jurisprudência segue o mesmo formato em seção própria (o `referencias/jurisprudencia.md` da skill Águas do Pará migra para cá na Fase 5, sem perda).

---

# 9. CONTRATO DO MÓDULO (o que toda área fornece ao kernel)

| Componente | Função | Já existe no seu ecossistema? |
|---|---|---|
| `MODULO.md` | Tipos de ação cobertos, rito, foro padrão, particularidades | Águas do Pará: seções 1 e 4 (sub-hipóteses) |
| `praxe_decisoria.md` | A árvore de decisão da área: como um sênior fixa percentuais, verbas, quantum e regimes — critérios, faixas e ramos, com fontes | Embrião: tabela de danos morais da skill Águas do Pará |
| `decisoes_reservadas.md` | Lista curta do que exige "ok" humano expresso (Tier B) | Evolução do `decisoes_do_advogado_humano.md` |
| `checklist_documental.md` | Docs típicos por tipo de ação (alimenta pendências do intake) | Águas do Pará: seção 7 |
| `teses.md` | Banco de teses da área + seção **antiteses — "nunca usar"** (dispositivos revogados, redações superadas, fontes inexistentes: conhecimento negativo codificado; padrão de kernel desde a Fase 4) | Águas do Pará: `referencias/teses-juridicas.md` |
| `templates/*.md` | Esqueletos de minuta no markup da formatação Nascimento | Águas do Pará: `referencias/modelo-peticao.md` |
| Checklist anti-erro fatal | Itens específicos da área no G3 | Águas do Pará: seção 8 (ex.: Súmula 608 ≠ concessionária) |
| Tabelas de quantum (se houver) | Dosimetria padronizada | Águas do Pará: `tabela-danos-morais.md` |

O módulo **família** nasce na Fase 3–4 extraindo tudo isso do CASO_TESTE_001 (a pesquisa vira BASE_LEGAL; a minuta vira template; as decisões registradas viram a lista de decisões obrigatórias).

**Área nova sem módulo (ex.: trabalhista, previdenciário):** o kernel funciona integralmente — intake, ficha, diário, gates, views. Só a minuta parte do zero e o anti-erro fatal roda no genérico do G3. E o **primeiro caso da área constrói o módulo como subproduto**: a pesquisa semeia `BASE_LEGAL/<area>.md`, a minuta aprovada vira o primeiro template, as decisões tomadas e ratificadas viram os primeiros ramos de `praxe_decisoria.md`, e os erros que o advogado apontar na revisão viram o checklist anti-erro fatal. O caso 1 de uma área é mais caro; o caso 2 já herda. Não se "constrói o sistema da área" antes — atende-se o primeiro caso dentro do kernel, e o módulo nasce dele. (Escopo do sistema: **contencioso** de qualquer área — tudo que termina em peça processual. Consultivo/contratos seria um módulo de natureza distinta, fora do alvo atual.)

**Acervo de modelos (v1.6):** o escritório guarda peças e decisões de referência em `ESCRITORIO/ACERVO/` (IDs M-01…), cada uma com ficha de curadoria (origem, área, ano, *por que foi guardada*, ressalvas, resultado) e **anonimizada na entrada** — dados pessoais de terceiros não se armazenam, e peças de autos sigilosos não entram. Regra de ferro: **modelo é professor de estilo e técnica, nunca de lei** — citação jurídica vinda de modelo só entra em peça após verificação na BASE_LEGAL (modelo antigo = lei possivelmente superada). Modelos alimentam **o molde, não cada peça**: sua sabedoria é destilada para template/teses via colheita ratificada; consulta direta só sob demanda na revisão. Extensão natural: decisões e sentenças dos próprios processos entram no acervo — semente da calibração **local** da árvore (o que o juízo da comarca costuma deferir). **Curadoria autônoma (v1.7):** quem analisa o modelo primeiro é o sistema — técnicas, movimentos, estrutura, o que é copiável e o que é datado — e preenche a ficha; a nota do advogado é campo opcional.

---

# 10. MAPA DE MIGRAÇÃO — OS 37 ARQUIVOS

| Arquivos antigos | Destino no SOJ |
|---|---|
| `00_entrada_bruta/` | `00_originais/` — **mantido intacto** |
| fatos, pessoas, prazos, docs solicitados, pendências, índice de provas, matriz, correspondência, QUADRO, mapa por parágrafo, marcadores, pendências da minuta (12 arquivos) | **`CASO.yaml`** (+ tags SOJ na minuta) |
| resumo do atendimento, cronologia, contradições/lacunas, perguntas complementares (4) | **`INTAKE.md`** (prosa, 4 seções) |
| hipóteses, classificação jurídica, diagnóstico, estratégia, simulação adversária, juiz rigoroso, riscos, providências (8) | **`ESTRATEGIA.md`** (a classificação vira campo `modulo` no YAML; providências viram pendências) |
| decisões do advogado, DECISOES_REGISTRADAS, PARECER_DE_PRONTIDAO (3) | **`DIARIO.md`** (entradas DECISAO_SISTEMA, RATIFICACAO e GATE) |
| STATUS, PENDENCIAS_PRIORIZADAS, checklist do cliente, rol (4) | **`_views/`** — geradas |
| PLANO_DA_PETICAO, PONTOS_PARA_PESQUISA, ROTEIRO_ATENDIMENTO (3) | **`_efemeros/`** — legítimos, descartáveis |
| PESQUISA_JURIDICA_v01 | **`BASE_LEGAL/familia.md`** — de custo por caso a ativo do escritório |
| minuta_v01 | **`MINUTA_v01.md`** + template do módulo extraído dela |
| documentos_renomeados/ | `01_documentos/` — mantido (padrão DOC-NN das suas skills) |

**Nada de valor se perde. Tudo muda de natureza:** o que era prosa duplicada vira dado único; o que era parecer vira gate; o que era custo por caso vira ativo do escritório.

---

# 11. ECONOMIA ESTIMADA (honesta)

| Vetor | Antes | Depois | Mecanismo |
|---|---|---|---|
| Geração por caso | ~18.500 linhas, ~40% redundantes | ~1.500–2.500 linhas úteis | LLM só escreve INTAKE, ESTRATEGIA, MINUTA e entradas do DIARIO |
| Tabelas/painéis | 4 mapeamentos + STATUS gerados por LLM, N vezes | **0 tokens** | Views por script |
| Pesquisa legal | Integral, por caso | Só o que falta/venceu | BASE_LEGAL amortizada |
| Minuta | Do zero | Template 60–70% pronto | Módulo |
| Contexto por sessão | Reler dezenas de arquivos | CASO.yaml + STATUS + cauda do DIARIO (~400–600 linhas) | Fonte única compacta |
| Consistência | 4 versões divergentes possíveis | 1 fonte, N views | Arquitetura |

Estimativa conservadora: **60–75% menos tokens por caso** já no segundo caso do módulo, e caindo conforme a BASE_LEGAL engorda. Números exatos medimos no piloto (Fase 2).

---

# 12. RISCOS E SALVAGUARDAS

1. **Sigilo e LGPD (dados sensíveis de menores).** Pasta em disco criptografado (BitLocker/FileVault); conta Google dedicada do escritório para o sync; nunca colar dados identificados em conversas fora do ambiente controlado — em consultas conceituais no claude.ai, usar dados anonimizados. `segredo_justica: true` no YAML lembra o tratamento também no digital.
2. **Alucinação jurídica.** Já mitigada por desenho: BASE_LEGAL com fonte + data, G3 com rechecagem, princípio "nunca citar de memória", e a regra herdada das suas skills: **diante de lacuna, parar e perguntar — nunca inventar fato.**
3. **Litigância predatória (Rec. 159/2024-CNJ).** Os gates são a resposta estrutural: cada peça protocolada passou por checklist objetivo + revisão humana registrada. Volume vira consequência de qualidade replicável — não o contrário.
4. **Staleness da BASE_LEGAL.** Janelas de validade + rechecagem dos dispositivos-núcleo no G3 + campo "casos que citam" para propagação de alterações.
5. **Ponto único de falha (você).** Backup em três camadas: Drive (contínuo), git (histórico), e opcionalmente um zip mensal frio. O DIARIO + git reconstituem qualquer estado passado.
6. **Disciplina de append-only.** O risco humano é editar o DIARIO "só dessa vez". O git denuncia; a regra é absoluta.

---

# 13. ROADMAP DE IMPLEMENTAÇÃO

| Fase | Entrega | Esforço estimado |
|---|---|---|
| **F1 — Fundação** | Árvore `~/NASCIMENTO/`, schema CASO.yaml, formato do DIARIO, scripts (novo_caso, receber_documento, gerar_views, gate_check), git + Drive configurados | 1 sessão de Claude Code |
| **F2 — Piloto** | Migrar o CASO_TESTE_001 inteiro: povoar CASO.yaml a partir dos 37 arquivos, reconstruir DIARIO das decisões registradas, gerar views, rodar G1/G2 reais. **Medir tokens.** | 1 sessão |
| **F3 — Ativo legal** | Semear `BASE_LEGAL/familia.md` a partir da PESQUISA_JURIDICA_v01 (reaproveita trabalho pago); definir validades | 1 sessão curta |
| **F4 — Módulo família + kernel-skill** | Extrair template da minuta_v01; escrever `praxe_decisoria.md` (árvore de alimentos/guarda/convivência, com fontes), `decisoes_reservadas.md`, checklist documental e anti-erro fatal do família; criar a skill `soj-kernel` com os comandos padrão | 1–2 sessões |
| **F5 — Expansão (opcional)** | Adaptar Águas do Pará e CCB ao kernel; prazos → Google Calendar | conforme demanda |

**Critério de sucesso do piloto (F2):** o G3 do CASO_TESTE_001 reprovar exatamente pelas pendências reais conhecidas (extrato bancário, endereço do réu) — provando que o gate enxerga o que o advogado enxerga.

---

# 14. PONTOS QUE FICAM ABERTOS PARA VOCÊ

1. **Validades da BASE_LEGAL** — propus 90/30 dias; ajuste ao seu apetite de risco.
2. **Nomenclatura de caso — RESOLVIDO:** pasta com o **nome do cliente** (seu padrão atual, o mesmo que as skills verticais já esperam). O `id` único do caso vive dentro do CASO.yaml. Se o mesmo cliente um dia tiver dois processos, o segundo ganha sufixo do objeto (ex.: `TANIA - execucao alimentos`) — o sistema se orienta pelo id, não pelo nome da pasta.
3. **Git** — recomendo fortemente, mas funciona sem; o DIARIO já dá a trilha jurídica, o git dá a técnica.
4. **Fase 5 (Calendar)** — deixei como opcional de propósito; o núcleo não depende dela.

---

*SOJ Blueprint v1.0 — preparado para aprovação. Nenhuma linha deste desenho exige ferramenta paga além do que você já usa.*
