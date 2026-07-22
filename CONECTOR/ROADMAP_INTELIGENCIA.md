# ROADMAP DE INTELIGÊNCIA — o que falta para operar como as plataformas grandes

> Diretiva do titular (22/07/2026): incorporar ao SOJ toda funcionalidade de
> jurimetria, inteligência processual, análise de documentos, jurisprudência,
> análise adversarial, diário oficial e coleta que Escavador/Jusbrasil/Harvey
> oferecem — **desde que lícita**. Complementa
> `ESCRITORIO/DOUTRINA_INTELIGENCIA_ADVERSARIA.md`.

## JÁ TEMOS (22/07/2026)

| Capacidade | Ferramenta |
|---|---|
| Mapa de processos de uma parte | `mapear_adversario.py` (DJEN `nomeParte`) |
| Download de peças sem login | `baixar_por_chave.py` (ConsultaDocumento) |
| Jurisprudência nacional por texto | `buscar_jurisprudencia.py` (DJEN `texto`) |
| Radar diário do acervo próprio | `RADAR/` (DJEN `numeroOab` + DataJud) |
| Degravação em escala | `motor_audio.py` |
| OCR local de scans | `anexar_autos.py` |

---

## 1. ÍNDICE DE ENTIDADES — a resposta certa sobre "busca por CPF/CNPJ" ⭐

**O mal-entendido a desfazer:** a API do DJEN **não tem** filtro de CPF/CNPJ
(testados 8 nomes de parâmetro em 22/07/2026 — todos ignorados). **Mas o
Jusbrasil também não consulta "um campo CPF".** Ele **extrai as entidades dos
documentos** que ingere e **constrói** o índice. É engenharia, não privilégio
de acesso.

**O que fazer:** varrer todo PDF/texto já baixado (`ADVERSARIOS/*/docs/`,
`AUTOS/`, `CASOS/*/01_documentos/`) extraindo CPF, CNPJ, OAB, nomes de parte e
de advogado, e montar `_SISTEMA/indice_entidades.db` — `entidade → processo →
documento → página`.

**Rende:** "todos os processos deste CNPJ" mesmo quando a razão social muda ·
identificar **quem advoga** para as rés · achar sócios e testemunhas repetidas ·
cruzar o CNPJ do PIX com o CNPJ do contrato.

**Custo:** baixo — os documentos já estão em disco. **Prioridade: 1ª.**

⚠️ **Limite ético/legal, inegociável:** os documentos trazem CPF e endereço de
**consumidores alheios**. O índice serve para achar **o adversário e o
precedente** — nunca para compilar dado pessoal de terceiro. Ver Doutrina §6.6.

## 2. MONITORAMENTO DE PARTE (o produto central do Escavador) ⭐

Hoje o `RADAR` vigia o acervo **do titular** (pela OAB). Falta vigiar
**qualquer parte**: cadastrar "FERREIRA REPRESENTAÇÕES" e receber alerta a cada
nova publicação.

**Rende duas coisas ao mesmo tempo:** inteligência (cada novo caso enriquece a
jurimetria e revela mudança de tática) e **captação** — quando um novo
consumidor processa a Ferreira, o escritório sabe no mesmo dia.

**Custo:** baixo — é o `mapear_adversario` com um delta diário, no modelo
baseline+delta que a MARCHA VIVA já usa. **Prioridade: 2ª.**

⚠️ Captação tem limite de publicidade (Provimento OAB). **Decisão do advogado.**

## 3. JURIMETRIA ESTRUTURADA (hoje é contagem manual)

Transformar os movimentos do DataJud em métricas: **tempo médio até sentença**
por vara · **taxa de procedência** por magistrado e por classe · **valor médio**
de condenação · **taxa e momento do acordo** · sobrevida do processo.

Hoje isso foi feito à mão para os 28 processos da Ferreira. Deve virar script,
com saída em tabela e as ressalvas de amostra pequena embutidas.
**Prioridade: 3ª.**

## 4. CLASSIFICADOR DE DESFECHO

Ler a sentença publicada e extrair automaticamente: procedente / improcedente /
parcial / extinto / acordo · o **fundamento** da derrota · o **valor**. O
`RADAR/classificador.py` já faz algo parecido com intimações — estender.
Isto é o que transformou 34 publicações no `O_QUE_GANHA_E_O_QUE_PERDE`.
**Prioridade: 4ª.**

## 5. BANCO DE PEÇAS INDEXADO (o que o Harvey faz)

Os 50 documentos baixados são matéria-prima morta enquanto não forem
pesquisáveis. Indexar por **tese**, não por arquivo: "me mostre como as
administradoras alegam ilegitimidade", "todas as preliminares usadas pela
Ferreira". O `index/` FTS5 já existe para autos — estender às peças do acervo
adversário. **Prioridade: 5ª.**

## 6. VERBETADOR DE JURISPRUDÊNCIA

Do acórdão colhido no DJEN até o verbete formal em `BASE_LEGAL/`, com teor,
fonte, data e validade — hoje é manual. Semiautomático: o script propõe, o
advogado ratifica (nunca automático: a regra de ferro exige conferência).
**Prioridade: 6ª.**

## 7. DADOS PÚBLICOS DE EMPRESA (CNPJ)

Situação cadastral, sócios, CNAE, data de abertura, endereço — por API pública
de CNPJ. Serve para: qualificar a ré na inicial · descobrir **sócios em comum**
entre "empresas diferentes" · saber se a ré está **ativa** antes de litigar
(execução contra empresa baixada é perda de tempo) · e conferir se a "Lima
Financeira" é mesmo uma financeira. **Prioridade: 7ª.**

## 8. LINHA DO TEMPO UNIFICADA DO CASO

Fundir numa só cronologia: mensagens, áudios degravados, imagens, documentos,
movimentos processuais e publicações. É o que permitiu ver que o Edson pagou
**dez dias depois** da apresentação. Hoje foi feito lendo à mão.
**Prioridade: 8ª.**

---

## O QUE **NÃO** ENTRA (e por quê)

- **Resolver captcha** — nem com autorização do titular.
- **Usar credencial do titular sem ele ao teclado.**
- **Raspar sistema que exija login** ou burlar limite técnico de acesso.
- **Compilar dado pessoal de terceiros** (consumidores alheios que aparecem
  nos autos). Usa-se o precedente e a tese, não a pessoa.
- **Peticionar, dar ciência ou assinar** — o conector é de LEITURA (regra que
  já constava do `ROADMAP_CAPACIDADES`).

## A ORDEM RECOMENDADA

**1 → 2 → 4 → 3** primeiro: o índice de entidades destrava a busca por
documento, o monitoramento faz a base crescer sozinha, e o classificador +
jurimetria transformam volume em estratégia. Os itens 5-8 são refinamento.
