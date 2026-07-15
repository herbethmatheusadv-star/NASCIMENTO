# Monitor de Prazos — DJEN

Consulta as comunicações publicadas no **Diário de Justiça Eletrônico Nacional**
(DJEN/CNJ) em nome de uma OAB e monta um relatório de prazos estimados, ordenado
por urgência.

Roda com a biblioteca padrão do Python. Sem `pip install`, sem cadastro, sem
chave de API — o DJEN é público.

---

## Antes de tudo: o que isto é e o que não é

Este script **organiza** as suas intimações e faz uma **estimativa** de
vencimento. Ele não substitui a conferência nos autos.

O que ele calcula bem:
- data de publicação e início da contagem (arts. 224, §§2º e 3º, do CPC);
- contagem em dias úteis (art. 219 do CPC, art. 775 da CLT);
- feriados nacionais, incluindo os móveis (Carnaval, Sexta-feira Santa,
  Corpus Christi — derivados da Páscoa de cada ano);
- recesso de 20/12 a 20/01 (art. 220 do CPC, art. 775-A da CLT).

Ele também resolve feriado **por tribunal**: 28/07 é feriado no Maranhão e dia
útil no Pará, e os seus processos do TJMA e do TJPA recebem tratamento
diferente. Ver *Feriados locais*, abaixo.

O que ele **não** sabe, e que pode mudar a sua data:
- feriados municipais e da comarca (aniversário da cidade, padroeiro…) →
  cadastre em `feriados_locais.txt`;
- suspensão de expediente por portaria do tribunal;
- prazo em dobro (litisconsortes com procuradores distintos, Fazenda Pública,
  Defensoria, MP);
- prazos próprios de cada rito e regras específicas de cada tribunal;
- se o prazo não vem escrito na intimação, ele **assume** o padrão do
  `config.json` (15 dias úteis). A linha do relatório diz qual foi o caso:
  *"detectado no texto"* ou *"padrão assumido"*.

**Use como rede de segurança, não como fonte única.**

---

## Configuração

Abra o `config.json` e preencha a sua OAB:

```json
{
  "oab": "39261",
  "uf": "PA",
  "prazo_padrao": 15,
  "janela_dias": "auto"
}
```

| campo | o que faz |
|---|---|
| `oab` | número da OAB, só dígitos (sem pontos, sem a UF) |
| `uf` | sigla da seccional, ex.: `PA` |
| `prazo_padrao` | dias úteis assumidos quando a intimação não diz o prazo |
| `janela_dias` | `"auto"` (recomendado) ou um número fixo de dias |

### Por que a janela é calculada e não fixa

**Deixe em `"auto"`.** O DJEN filtra por **data de disponibilização**, mas o
prazo vive muito além dela: 15 dias úteis são ~23 dias corridos, e passam de 50
se atravessarem o recesso. Uma janela curta *parece* que mostrou tudo e esconde
prazo vigente — na primeira versão deste script, uma janela de 15 dias omitiu um
prazo que vencia **naquele mesmo dia**.

Em `"auto"`, o script anda para trás até a disponibilização mais antiga cujo
prazo ainda estaria correndo, e usa isso. Em julho dá ~54 dias; depois do
recesso, ~85. Ele mostra a conta ao rodar.

Fixar um número só faz sentido para consulta pontual de histórico (`--dias 120`).

## Como rodar

```bash
python monitor_prazos.py
```

O relatório sai no terminal e abre no navegador. Fica salvo em
`relatorios/prazos_AAAA-MM-DD.html`.

Opções:

```bash
python monitor_prazos.py --dias 120       # janela fixa (histórico)
python monitor_prazos.py --prazo 5        # assumir 5 dias quando não vier no texto
python monitor_prazos.py --oab 12345 --uf PA   # ignora o config.json
python monitor_prazos.py --sem-navegador  # só o terminal
```

Códigos de saída: `0` tudo certo, `2` relatório incompleto (o DJEN não respondeu
para algum período — útil se você agendar a tarefa).

## Quando o DJEN cai

Ele cai. Em testes, a **mesma** consulta falhou com HTTP 500 em 2 de 3
tentativas. O script trata isso:

- **repete** até 4 vezes com espera crescente (erro 4xx não, que é consulta
  errada e insistir não adianta);
- **fatia** janelas grandes em blocos de 45 dias, que caem menos;
- se um bloco cair mesmo assim, **avisa qual período faltou** — no terminal e no
  topo do HTML — em vez de te entregar um relatório incompleto com cara de
  completo.

Se aparecer o aviso de incompleto, rode de novo daqui a pouco.

## Feriados locais (e por que eles têm escopo)

Edite `feriados_locais.txt`. O formato é:

```
YYYY-MM-DD  [ESCOPO]  Descrição
```

`ESCOPO` é a sigla do tribunal como o DJEN devolve (`TJPA`, `TJMA`, `TRT8`,
`TRF1`…) ou `*` para valer em todos. Omitir equivale a `*`.

```
2026-07-28  TJMA  Adesão do Maranhão      -> só nos processos do TJMA
2026-08-15  TJPA  Adesão do Pará          -> só nos processos do TJPA
2026-03-02  *     Suspensão geral         -> em todos
```

**Por que o escopo existe:** feriado estadual não é nacional. 28/07 é feriado no
Maranhão e dia útil no Pará. Como você atua nos dois, um calendário único daria
data errada num dos lados — empurraria os prazos paraenses por causa de um
feriado maranhense. Já vem pré-cadastrado o feriado estadual de cada um.

**Cuidado com a direção do erro:** cadastrar um feriado que **não** existe
empurra o vencimento para frente e te dá a impressão de ter mais tempo do que
você tem. Um feriado a menos antecipa a data — chato, mas seguro. Só mantenha o
que você confirmou no calendário oficial do tribunal.

Ao rodar, o script lista os feriados locais em vigor justamente para você
revisar.

---

## O que ele lê da intimação

O DJEN entrega o **teor integral** do ato, não só o aviso. O script lê e responde três coisas:

**O que é** — Despacho, Decisão, Sentença, Acórdão, Ato ordinatório, Audiência,
Distribuição ou Sigiloso.

**O que pede** — recolher preparo, custas, contrarrazões, contestar, impugnar,
emendar, especificar provas, manifestar-se…

Ele lê isso **só nos trechos de ordem** (`Intime-se X para Y`, `sob pena de Z`),
nunca no relatório da peça. Um acórdão de 10 mil caracteres cita "contrarrazões",
"embargos" e "custas" ao narrar o histórico — nada disso é ordem para você. Sem
esse filtro, uma única decisão aparecia pedindo seis providências diferentes.

**Sob pena de quê** — deserção, revelia, extinção, arquivamento, preclusão,
multa… Só conta o que vem depois de "sob pena de": uma sentença que *julga*
extinto o processo não está *ameaçando* ninguém.

### É meu ou da parte contrária?

Você aparece na publicação por ser advogado nos autos — isso **não** significa
que a obrigação é sua. Cruzando o campo `polo` (A=ativo, P=passivo) do seu
cliente com quem o ato manda agir, o relatório separa:

| veredito | significado |
|---|---|
| `MEU` | o ato intima o polo do seu cliente |
| `DA_OUTRA_PARTE` | o ato intima o polo oposto — vai para uma seção à parte |
| `INCERTO` | não deu para afirmar — **aparece normalmente, com aviso** |

**Na dúvida, mostra.** Só diz "não é seu" quando o texto nomeia um polo, o polo
do cliente é conhecido e os dois são opostos. Esconder por engano custa um
prazo; mostrar a mais custa dez segundos de leitura.

## Cruzamento com o CNJ (`--datajud`)

```bash
python monitor_prazos.py --datajud
```

O DJEN conta o que foi **publicado**; o DataJud conta o que **aconteceu**. Juntos
respondem a pergunta que nenhum dos dois responde sozinho: *o prazo foi
cumprido?*

> DJEN: *"há intimação mandando recolher preparo em 5 dias sob pena de deserção"*
> DataJud: *"decurso de prazo em 30/06, concluso para julgamento em 01/07"*
> → **prazo perdido, recurso prestes a ser julgado deserto**

Situações que ele reporta: `houve petição dentro do prazo`, `o tribunal
certificou DECURSO DE PRAZO`, `sem sinal claro`, `sem dados no DataJud`.

**É sinal, não prova.** Um processo tem vários prazos correndo ao mesmo tempo: o
decurso registrado pode ser de outro, e a petição do período pode tratar de outra
coisa. Serve para dizer "olha isto aqui", nunca para dar baixa em prazo.

Limites medidos: o DataJud **não indexa advogado** (a lista de processos vem do
DJEN; aqui só se consulta um a um), tem **defasagem de ~4 dias** e **rate limit
agressivo**. Por isso só consulta o que muda decisão — prazo vivo ou vencido com
sanção grave — e mantém cache local (`.cache_datajud.json`, 12h).

A chave usada é a **chave pública** que o CNJ divulga na documentação. Não é
credencial pessoal e não dá acesso a nada sigiloso.

### O que exige certificado digital

Processo em segredo de justiça não sai no DJEN — vem como *"Processo sigiloso.
Para visualização do documento consulte os autos digitais"*. Para esses, e para
as peças completas, só o PJe com seu certificado. Isso está fora deste script.

## Como ler o relatório

As comunicações vêm classificadas por urgência:

| etiqueta | significado |
|---|---|
| `VENCIDO GRAVE` | **venceu e o texto prevê sanção grave — vai para o topo** |
| `VENCE HOJE` | vence hoje |
| `CRITICO` | faltam 2 dias úteis ou menos |
| `ATENCAO` | faltam 5 dias úteis ou menos |
| `NO PRAZO` | mais de 5 dias úteis |

**Por que `VENCIDO GRAVE` fica no topo.** A primeira versão presumia que prazo
vencido é assunto encerrado e mandava tudo para o rodapé. Não é: um agravo com
preparo pendente *sob pena de deserção* ficou enterrado na lista de "provavelmente
já cumpridos" enquanto o recurso ia a julgamento. Enquanto não há julgamento, a
consequência ainda está em curso. Vencido **com sanção grave** sobe; vencido sem
sanção desce.

**Ordem de leitura:** vencidos graves → vence hoje → crítico → atenção → no prazo
→ vencidos comuns → prazos da parte contrária → informativas → resolvidos.

## Marcando o que você já tratou (`resolvidos.txt`)

Um prazo que você já resolveu continua no topo do relatório até sair da janela —
até 54 dias piscando "VENCIDO GRAVE" por algo já feito. Alerta que você já tratou
e continua gritando faz você parar de ler o relatório, e aí a ferramenta não
serve mais para nada.

```
NUMERO_PROCESSO  AAAA-MM-DD  # nota opcional
```

A data é a de **disponibilização** — a mesma da linha "Disponibilizado" no
relatório. O número aceita com ou sem máscara.

```
0807884-75.2026.8.14.0000  2026-06-19  # preparo recursal resolvido
```

**Ele rebaixa, não some.** O item sai do topo e vai para uma seção própria no
fim, com a sua nota, ainda visível e conferível. Some de vez seria trocar um
risco (esquecer o prazo) por outro (achar que tratou o que não tratou). O rótulo
`VENCIDO GRAVE` também continua — o fato não muda porque você o marcou; o que
muda é onde ele fica.

Marcar também poupa consulta ao DataJud (o rate limit é curto).

**"N comunicações deste mesmo ato"** — o DJEN emite uma comunicação separada
para cada destinatário do mesmo ato. O mesmo processo aparece 2, 3, 4 vezes no
mesmo dia, com textos ligeiramente diferentes. O relatório junta essas
ocorrências numa linha só (o prazo é um só) e guarda o link de cada uma.

**Informativas** — "Lista de distribuição" e pauta normalmente não abrem prazo,
então vão para o fim do relatório, sem cálculo. Confira mesmo assim.

---

## Rodar todo dia de manhã

Agendador de Tarefas do Windows:

1. Abra o Agendador de Tarefas → *Criar Tarefa Básica*
2. Disparo: diariamente, ex. 08:00
3. Ação: *Iniciar um programa*
   - Programa: `python`
   - Argumentos: `monitor_prazos.py`
   - Iniciar em: `C:\Users\nasci\OneDrive\Desktop\Brand Nascimento\monitor-prazos`

O relatório abre sozinho no navegador quando a tarefa roda.

---

## Detalhes técnicos

- **Endpoint:** `GET https://comunicaapi.pje.jus.br/api/v1/comunicacao`
- **Filtros usados:** `numeroOab`, `ufOab`, `dataDisponibilizacaoInicio`,
  `dataDisponibilizacaoFim`, com paginação de 100 em 100.
- **Cobertura:** o DJEN concentra as comunicações dos tribunais integrados ao
  sistema. Tribunais que ainda publicam em diário próprio podem não aparecer —
  confira se os seus estão cobertos antes de confiar no relatório.
- Sem dependências externas: `urllib`, `json`, `datetime`, `re`, `argparse`.

### Estrutura

```
monitor-prazos/
├── monitor_prazos.py       # orquestra: DJEN, prazos, relatório
├── classificador.py        # lê o teor: o que é, o que pede, é meu?
├── datajud.py              # API do CNJ: andamentos e decurso de prazo
├── config.json             # sua OAB e preferências
├── feriados_locais.txt     # feriados do seu foro, por tribunal
├── resolvidos.txt          # intimações que você já tratou
├── relatorios/             # HTML gerado por dia
├── .cache_datajud.json     # cache das consultas ao CNJ (12h)
└── teste_*.py              # ~110 casos
```

### Testes

```bash
python teste_calendario.py     # cálculo de prazo, feriados, janela
python teste_rede.py           # instabilidade do DJEN, relatório incompleto
python teste_classificador.py  # teor, providência, sanção, de quem é
python teste_datajud.py        # cruzamento com o andamento do CNJ
```

Rode antes de confiar em qualquer alteração no cálculo. Vários deles travam bugs
reais que já aconteceram: Carnaval atravessando o recesso, feriado estadual
aplicado no estado errado, janela curta escondendo prazo vivo, narrativa de
acórdão virando ordem falsa.
