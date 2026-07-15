# Log de conciliação — radar (DJEN) × DataJud

> Cada divergência registrada aqui é uma aula: é assim que o motor aprende e o
> advogado audita (prompt-mestre, §4.5).

## 2026-07-15 · 0001766-17.2024.5.08.0126 (TRT8) — defasagem de ~5 meses

- **DJEN:** sentença de extinção da execução (art. 924, II, CPC) publicada em
  19/03/2026 — comunicações nº 562857953 e 562858252.
- **DataJud:** último movimento em 23/10/2025 ("Baixa Definitiva"). Toda a fase
  de 2026 (descumprimento do acordo, multa de R$ 2.513,57, extinção) **não
  consta**.
- **Lição:** a defasagem do DataJud pode ser de meses, não de dias. Conciliação
  é sinal, nunca baixa automática — e a ausência de movimento novo no DataJud
  jamais prova que nada aconteceu.

## 2026-07-15 · Cobertura DJEN — lacunas conhecidas da varredura TRT8

- Janela **28/09/2025 → 11/11/2025**: o DJEN respondeu HTTP 500 em todas as
  tentativas (2 rodadas de retry) — período **não coberto** pela varredura
  ampliada. Repetir em dia de API saudável.
- Ano de 2024: a consulta respondeu `count=0` para a OAB no TRT8 (integração
  do tribunal ao DJEN possivelmente posterior). Publicações de 2024 podem
  existir só no diário antigo.
- Consequência prática: o advogado informou **2 processos TRT8 além dos 3
  triados**; a varredura por OAB achou 1 (0000017-16.2025.5.08.0130). O 2º
  (**0001128-32.2025.5.08.0131**, 4ª VT de Parauapebas) **só apareceu porque o
  advogado entregou os autos** — a busca por `numeroOab=39261&ufOab=PA` no
  período 2025–2026 **não o retornou**.

### Diagnóstico conclusivo (investigado no mesmo dia — hipótese inicial DESCARTADA)

Cheguei a registrar aqui que "a busca por OAB não seria exaustiva". **Errado —
e a investigação provou o contrário.** Os fatos:

- Consulta ao Comunica **por número** (`numeroProcesso=00011283220255080131`):
  5 comunicações, e o titular **consta como destinatário** em 2 delas, ambas
  disponibilizadas em **29/10/2025**.
- Consulta **por OAB** (`numeroOab=39261&ufOab=PA`) na janela estreita
  27→31/10/2025: **retorna as mesmas 2 comunicações**. A busca por OAB
  funciona.
- **29/10/2025 está dentro do bloco 28/09→11/11/2025** — exatamente o período
  que respondeu HTTP 500 em todas as tentativas da varredura.

**Causa raiz: a indisponibilidade do DJEN, não o filtro.** O processo existia,
a OAB o alcançava, mas a API estava fora do ar naquele pedaço da janela.

**Lição (a mais importante do dia):** *o relatório incompleto que se apresenta
como completo é pior do que relatório nenhum* — princípio que o MVP já
implementa (avisa qual período faltou, exit 2). Hoje ele foi validado com
dados reais: **um bloco em 500 escondeu um processo inteiro.** Consequências:
1. Bloco que falha **tem que ser reconsultado até responder** — não basta
   avisar uma vez. Pauta da Etapa 2: fila de re-tentativa persistente das
   janelas falhas (o radar já sabe quais são).
2. Vigiar **também por número** os processos já cadastrados é defesa em
   profundidade barata — pauta da Etapa 2.
3. O universo de processos nasce da **entrevista com o advogado**; a API
   confirma e movimenta, mas não descobre sozinha.
