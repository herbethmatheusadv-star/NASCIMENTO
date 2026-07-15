# Diagnóstico da skill "formatacao-peticoes-nascimento"

Análise feita a partir das 3 peças reais enviadas (LUCIANA, EDIO/"00 - PETIÇÃO
INICIAL", DANIEL), extraindo a formatação exata via python-docx + XML de
`numbering.xml` e conferindo visualmente por renderização em PDF. Comparado
linha a linha com `scripts/formatar_peticao.py` (script atual da skill).

**Importante:** não consegui alterar a skill salva nesta sessão (o pacote em
`skills-plugin/.../formatacao-peticoes-nascimento` é um cache só-leitura
aqui). Este documento + o arquivo `formatar_peticao_CORRIGIDO.py` (testado e
funcionando) são para você aplicar via Configurações > Capacidades,
substituindo `scripts/formatar_peticao.py` pelo conteúdo corrigido.

## Erros confirmados e corrigidos

1. **Recuo dos parágrafos numerados ("1. 2. 3.") — FALTAVA por completo.**
   O script atual força recuo zero em tudo. As 3 peças reais têm recuo de
   primeira linha de **2,0 cm** exatamente nesses parágrafos (o número entra
   recuado; a linha seguinte volta pra margem). Corrigido.

2. **Numeração dos itens reiniciava errado.** O script atual reinicia a
   contagem "1. 2. 3." a cada linha em branco/parágrafo normal. Nas 3 peças
   reais a numeração é **contínua do início ao fim do corpo** — no documento
   do EDIO, por exemplo, ela vai de "1." em DOS FATOS até "15." dentro de DO
   DIREITO, sem nunca reiniciar (nem por subtítulo, nem por título).
   Corrigido: os contadores de item e de pedido agora só correm pra frente.

3. **Bloco de espaço em branco antes da qualificação — não existia.** Você
   descreveu isso e as 3 peças confirmam: entre o endereçamento ("AO
   JUÍZO...") e o nome da parte há vários parágrafos em branco (7 a 10,
   variando com o tamanho do texto), empurrando a qualificação pro fim da
   folha 1. Adicionei `--espacos-topo N` (padrão 9) — **ajuste manual
   dependendo do tamanho da qualificação**, porque não dá pra acertar sempre
   com um número fixo (nomes/qualificações mais longos precisam de menos
   linhas em branco).

4. **Faltavam os níveis de pedido (letras).** "DA TUTELA DE URGÊNCIA" e "DOS
   PEDIDOS" usam letras minúsculas contínuas "a) b) c)..." (recuo 1,27cm) —
   inclusive **continuando a mesma sequência de letras entre os dois
   títulos** (ex.: a,b em um título, c,d no próximo). Quando um pedido lista
   sub-itens ("no mérito, a procedência dos pedidos para:"), usa uma
   sub-lista "a. b. c." (recuo 2,54cm). Nenhum dos dois existia no script
   antigo — a peça da DAIANE teve que simular isso "na mão" como texto
   puro. Adicionei os níveis `pedido` e `pedido-sub`.

5. **Faltava sub-lista para itens dentro de um fato numerado** (ex.: listar
   duas dívidas, cinco faturas). Adicionei o nível `subitem-romano`
   ("i. ii. iii.", recuo 3,81cm) como padrão, com bullet (•) como
   alternativa — as 3 peças usam os dois estilos (uma usa bullet, duas usam
   romano).

## Pontos que variam entre as suas próprias peças (preciso que você confirme)

- **Alinhamento do nome da ação** ("AÇÃO DECLARATÓRIA..."): no script atual
  é sempre centralizado. Nas 3 peças, **2 justificam e 1 centraliza**
  (LUCIANA centraliza; EDIO e DANIEL justificam). Troquei o padrão pra
  **justificado**, com `--acao-centralizada` disponível se você preferir
  centralizar. **Qual dos dois é o que você quer como padrão daqui pra
  frente?**
- **Tamanho da fonte:** o script atual usa 11. Ao conferir as 3 peças, 2
  usam 11 e 1 usa 11,5 (a "00 - PETIÇÃO INICIAL.docx"). Mantive 11 (maioria),
  mas se a intenção for 11,5 em tudo, é só avisar.
- **Sub-lista de itens dentro de um fato** (item 5 acima): bullet vs.
  romano — mantive romano como padrão por já usar a mesma "família" de
  numeração dos pedidos/títulos, mas se você preferir sempre bullet, também
  dá pra trocar o padrão.

## O que NÃO precisou de correção (já estava certo)

- Título "I) II) III)..." maiúsculo, negrito, sem recuo.
- Subtítulo "1.1. / 2.1." negrito + sublinhado, sem recuo.
- Espaçamento de parágrafo (antes 20pt / depois 10pt, espaçamento simples).
- Margens (3cm superior; 2cm nas outras três).
- Timbrado (logo no cabeçalho + contatos no rodapé) — mecânica já funciona.

## Como aplicar

1. Copie o conteúdo de `formatar_peticao_CORRIGIDO.py` para
   `scripts/formatar_peticao.py` dentro da skill (via Configurações >
   Capacidades — é lá que dá pra editar a skill de verdade).
2. Teste com uma peça real e confira o resultado (títulos, subtítulos,
   itens numerados com recuo, pedidos com letras, bloco de espaço na
   página 1).
3. Ajuste `--espacos-topo` conforme o tamanho de cada qualificação.

---

## RODADA 2 — precisão por nível (a partir dos seus prints do Word)

Você mandou os prints do diálogo "Ajustar Recuos da Lista" do Word pra
"I) DOS FATOS" e pros parágrafos numerados, e pediu mais precisão. A rodada 1
tinha lido só a `numbering.xml` solta, sem cruzar com o `w:numPr` real de
cada parágrafo — por isso vários níveis saíram menos precisos do que
pareciam. Nesta rodada, reextraí cruzando parágrafo por parágrafo com a
definição de lista que ele realmente usa. Tabela — igual aos campos que
aparecem no seu Word:

| Nível | Posição do número | Recuo do texto | Seguir número com | Negrito do marcador |
|---|---|---|---|---|
| Título "I) DOS FATOS" | 0 cm | 0 cm | espaço | sim |
| Subtítulo "1.1. Da relação..." | 0 cm | 0 cm | espaço | sim (+ sublinhado) |
| Item "1. 2. 3." | 2 cm | 0 cm | espaço | **sim** (só o número — corrigido nesta rodada) |
| Pedido "a) b) c)" | 0,635 cm | 1,27 cm | tab | **não** (corrigido — rodada 1 tinha posto negrito por engano) |
| Sub-pedido "a. b. c." | 1,905 cm | 2,54 cm | tab | não |
| Sub-item "i. ii. iii." | 3,175 cm | 3,81 cm | tab | não |
| Sub-item "•" | 3,175 cm | 3,81 cm | tab | não |

Repare que, do "item" pra baixo, a lógica de qual coluna é maior se inverte:
no item o número fica mais pra dentro que o texto (recuo do texto é 0, o "2"
da posição é a primeira linha entrando); no pedido/sub-item é o contrário,
o texto que fica mais pra dentro que o marcador (recuo do texto sempre
maior que a posição do número) — é o recuo "pendurado" clássico.

Todos os parágrafos, em qualquer nível: espaçamento antes 20pt, depois
10pt, entre linhas simples, Century Gothic 11 — confirmado uniforme em
título, subtítulo, item, pedido, corpo e até nas linhas em branco do bloco
antes da qualificação (bati o antes/depois de cada um contra o XML, não é
só o item numerado que tem isso).

### O que mudou nesta rodada

1. **Título estava alinhado à esquerda, o certo é justificado.** Não dava
   pra notar visualmente numa linha curta como "DOS FATOS", mas o XML das
   3 peças confirma justificado — corrigido (só importa se algum título
   for longo o bastante pra quebrar linha).
2. **Número do item ("1." "2."...) virou negrito.** Confirmado no XML de
   2 das 3 peças (EDIO e DANIEL): o marcador do item é negrito, o texto
   do item continua normal.
3. **Letra do pedido ("a)" "b)"...) deixou de ser negrito.** Isso foi um
   erro meu na rodada 1 — o XML mostra claramente que não é negrito.
4. **Sub-item em bullet tem recuo pendurado diferente do romano.** Na
   rodada 1 os dois usavam o mesmo valor; agora bullet usa 0,635cm e
   romano usa... (ver item 5 abaixo, achei um bug e ajustei).
5. **Bug real que encontrei testando:** o valor cru extraído do XML pro
   recuo pendurado do sub-item romano era 0,3175cm (bem apertado). Ao
   gerar um teste com "i." e "ii.", o "i." alinhava certo mas o "ii."
   (mais largo) estourava essa margem e o texto pulava pra uma parada de
   tabulação padrão bem mais longe — ficava com um espaço enorme e feio
   antes do texto. Corrigi aumentando esse recuo pra 0,635cm (mesmo do
   bullet), que comporta "ii.", "iii." etc. sem estourar. Testei de novo
   e o alinhamento ficou uniforme.
6. **"Seguir número com" = tab nos níveis pedido/sub-pedido/sub-item**
   (confirmado no XML — é o padrão do Word quando não se define nada).
   Como o script digita o marcador como texto puro (não usa numeração
   nativa do Word), um TAB sozinho não alinharia certo — por isso agora
   o script define uma parada de tabulação exatamente na posição do
   recuo antes de usar o TAB. Só título/subtítulo/item usam espaço
   simples mesmo (confirmado nos seus prints).

### Ainda em aberto (resolvido na Rodada 3 abaixo, exceto o alinhamento da ação)

- Alinhamento do nome da ação (justificado vs. centralizado) — 2 das 3
  peças justificam, 1 centraliza; mantive justificado como padrão. Se
  quiser trocar, é só avisar.

### Como conferir por conta própria

Se quiser bater os números você mesmo: abra qualquer peça, clique num
parágrafo numerado, vá em formatar lista → "Ajustar Recuos da Lista" — os
valores de "Posição do número" e "Recuo do texto" devem bater com a
tabela acima para cada nível.

---

## RODADA 3 — bugs reais encontrados ao aplicar na petição da DAIANE

Você pediu pra aplicar o script corrigido na petição real da DAIANE
(modo `--docx`, reformatando o DOCX que já existia em PROTOCOLO/, gerado
pela versão antiga). Rodar em um documento real — em vez dos testes
sintéticos das rodadas 1-2 — revelou 3 problemas que só aparecem com
texto de verdade:

1. **Nível "item" não era tratado no modo `--docx`.** As rodadas 1-2 só
   tinham corrigido o modo `--texto` (a partir de markup `# `/`- `/`+ `).
   O modo `--docx` (reformatar um arquivo já pronto) ainda caía tudo no
   nível genérico "corpo", perdendo o recuo de 2cm e o negrito do número
   dos fatos numerados. Corrigido: `--docx` agora trata "item" com a
   mesma regra do modo texto.

2. **Marcador duplicado ao reformatar um `.docx` existente.** Quando o
   parágrafo de origem já tem o marcador como texto literal (ex.: "1. "
   ou "a)" no início do primeiro run), copiar os runs do jeito antigo
   duplicava o marcador (saía "1. 1. Texto..." ou "a) a) texto...").
   Corrigido com uma função nova que remove o marcador do primeiro run
   antes de copiar, preservando negrito/itálico/sublinhado do resto do
   texto.

3. **Letra de pedido confundida com título (bug mais sério).** Títulos
   desta casa usam algarismo romano ("I)", "II)", "III)", "IV)") e a
   detecção de título — por engano — não diferenciava maiúscula de
   minúscula. Como pedidos usam letra minúscula contínua ("a) b) c)..."),
   e várias letras do alfabeto TAMBÉM são algarismos romanos válidos
   (c=100, i=1, l=50, v=5, x=10, d=500, m=1000), os pedidos "c)" e "i)"
   da própria petição da DAIANE estavam sendo lidos como título novo —
   saíam em CAIXA ALTA, quebrando a sequência de letras dos pedidos
   seguintes. Corrigido: detecção de título por marcador já digitado
   agora exige maiúscula (o padrão real desta casa: título sempre
   maiúsculo, pedido sempre minúsculo — a exigência resolve a ambiguidade
   sem risco).

4. **Assinatura do advogado sendo lida como título.** Havia um fallback
   que lia qualquer texto curto, em negrito, caixa alta e sem ponto final
   como um título "sem marcador" (pensado pra peças que não usam "I)"
   explícito). Esse fallback capturou por engano a **assinatura final**
   ("CARLOS EDUARDO DE SOUSA DO NASCIMENTO"), que também é negrito e
   caixa alta. Removido: todos os títulos reais desta casa já vêm com
   marcador explícito ("I)", "II)"...), capturado antes desse fallback
   — ele não fazia falta e só criava risco de confundir nomes/assinaturas
   com títulos.

Verificação feita depois dos 4 ajustes, na petição real da DAIANE:
fidelidade textual 100% (52/52 parágrafos batendo com o original, fora
os marcadores, e a sequência de marcadores I-IV/1-8/2.1-2.7/a-j idêntica)
e inspeção visual das 7 páginas renderizadas. Sem esses ajustes, a peça
teria saído com 2 "títulos" fantasmas (nos lugares de "c)" e "i)") e a
assinatura do advogado destacada como se fosse uma nova seção.
