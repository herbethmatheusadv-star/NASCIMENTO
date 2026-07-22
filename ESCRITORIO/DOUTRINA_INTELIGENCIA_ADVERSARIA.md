# DOUTRINA DE INTELIGÊNCIA ADVERSÁRIA v1

> Peça de KERNEL, aprovada pelo titular em 22/07/2026 ("esse processo de
> mapeamento adversário, jurimetria, sentenças, pesquisa CNPJ/CPF vai ser
> indispensável para nossas estratégias jurídicas").
>
> Nasceu do caso **2026-0006 (EDSON)**, onde o levantamento mudou a tese
> principal, o rito, o valor e o próprio nome da ação — **antes** de a inicial
> ser escrita.

## 1. O PRINCÍPIO

**Antes de redigir contra alguém, saiba como esse alguém já perdeu e já ganhou
naquele foro.** Não é curiosidade: é a diferença entre escrever uma petição
tecnicamente correta e escrever a petição que vence **aquele** adversário
naquele juízo.

No caso-fonte isso rendeu, em uma tarde:
- a descoberta de que **a mesma dupla de rés responde a 28 processos**;
- a **sentença do caso gêmeo**, que **perdeu** — e o porquê;
- a **sentença que ganhou**, e a fórmula dela;
- **o manual de defesa das rés**, nas palavras delas;
- **o patamar de acordo** que elas pagam (R$ 15.000 em 5×) e **quando**;
- os **endereços de citação** corretos, tirados dos autos alheios;
- e a correção do **nome da ação** — de "rescisão" (que mata o pedido) para
  "nulidade" (que devolve tudo).

## 2. A REGRA DE OURO DA ROTA

> **Antes de dizer "não dá": como o Jusbrasil, o Escavador, o Harvey fariam?**

São ferramentas lícitas sobre informação pública. Se elas conseguem e nós não,
o problema é a **rota**, não a informação. Três vezes em 22/07/2026 declarei
algo impossível e três vezes estava errado.

**O erro sistemático:** a porta óbvia (API oficial de metadados, consulta do
tribunal) é a que está fechada — e sua porta fechada parece um veredito sobre
a informação. Não é. É um veredito sobre aquela porta.

**A resposta quase sempre é o DIÁRIO OFICIAL.** O DJEN publica:
nome de parte · íntegra de sentença e de acórdão · ementa · **chave de acesso
aos documentos** do processo. É a espinha dorsal dos agregadores comerciais, e
é pública.

## 3. AS QUATRO FERRAMENTAS (e o que cada uma responde)

| Pergunta | Ferramenta | Porta |
|---|---|---|
| *Contra quem estou litigando, e o que já aconteceu com ele?* | `CONECTOR/mapear_adversario.py` | DJEN `nomeParte` + DataJud |
| *O que dizem as peças e sentenças desses processos?* | `CONECTOR/baixar_por_chave.py` | `ConsultaDocumento` por chave |
| *O que os tribunais decidem sobre esta tese?* | `CONECTOR/buscar_jurisprudencia.py` | DJEN `texto` (nacional) |
| *Este processo andou?* | `RADAR/` (já existia) | DJEN `numeroOab` + DataJud |

Todas: **sem login, sem certificado, sem captcha, sem custo.**

## 4. O PROTOCOLO — na ordem, sempre

**P1. Mapear o adversário.** `mapear_adversario.py "NOME" --tribunal XX --datajud`
Rodar **variantes** do nome (razão social do contrato costuma não ser a dos
autos) e **conferir a lista de partes** de cada processo antes de tratá-lo como
do alvo.

**P2. Ler os desfechos antes das peças.** Os movimentos do DataJud e as
publicações longas dizem quem ganhou e quem perdeu. **Comece pelo que perdeu** —
o motivo da derrota alheia é a instrução mais barata que existe.

**P3. Baixar as peças que importam.** Contestações (o manual de defesa),
sentenças, e a inicial que venceu. `baixar_por_chave.py`.

**P4. Destilar em três documentos** (padrão do módulo `consumidor_consorcio`):
`DOSSIE_ADVERSARIO.md` (quem são, onde litigam, com quem, quanto acordam) ·
`O_QUE_GANHA_E_O_QUE_PERDE.md` (a comparação que vira regra) ·
`ESTRATEGIA.md` do caso (o esqueleto, com a defesa antecipada).

**P5. Jurisprudência da tese**, por texto livre, priorizando o **tribunal
local** — vale mais que ementa de outro estado.

## 5. O QUE PROCURAR (checklist do que costuma render)

- **A sentença do caso mais parecido** — e se o autor recorreu (recorreu = perdeu
  ou ganhou pouco).
- **O nome exato da ação** que venceu. Palavra errada muda o enquadramento e
  mata o pedido de dinheiro.
- **O terreno onde o colega morreu.** Não pisar nele.
- **O que o juiz reprovou expressamente** na petição perdedora — costuma ser
  falha de redação, não de direito, e é grátis consertar.
- **Quem julga.** Placar por vara e por magistrado.
- **A contestação padrão** e as preliminares que sempre vêm.
- **Os acordos**: valor, parcelamento, e **em que momento** eles aceitam.
- **Qualificação e endereço** das rés, tirados dos autos alheios (o juízo já
  conferiu).
- **Co-rés recorrentes** — no caso-fonte, a corretora troca de administradora a
  cada safra; isso é o modus operandi aparecendo.
- **Peças em que um adversário acusa o outro.** Uma administradora chamou a
  nossa ré de "empresa fraudulenta" em contestação assinada.

## 6. OS LIMITES — que não se contornam

1. **Captcha não se resolve.** TJMG exige; nenhuma autorização do titular muda
   isso. Se a informação só existe atrás de captcha, é tarefa do advogado.
2. **Credencial não se usa sem o titular.**
3. **Busca por NOME erra dos dois lados** — traz homônimo e perde variação de
   razão social. Nunca tratar resultado como do alvo sem conferir as partes.
4. **O DJEN indexa o que foi PUBLICADO**, não o acervo histórico do tribunal.
5. **Nada disso dispensa o teor na fonte.** Ementa colhida do diário é fonte
   oficial do ato, mas a publicação pode vir truncada: conferir o inteiro teor
   antes de citar. A regra de ferro da casa continua valendo integralmente.
6. **Dado de terceiro é dado de terceiro.** Os processos trazem nomes, CPFs e
   endereços de consumidores alheios. Usa-se o **precedente** e a **tese** —
   não se replica dado pessoal de quem não é nosso cliente.

## 7. A REGRA DE MÉTODO QUE ISTO DEIXOU

**Conclusão negativa registrada no sistema deve vir com *como foi testada*.**

Em 16/07 o `MAPA_PJE` registrou que baixar documento "só funciona clicado no
navegador; POST às cegas não é". Estava errado — faltava o `ViewState` — e essa
linha **travou o download em massa por seis dias**, porque eu a tratei como
prova em vez de retestar. Veredito sem o teste que o produziu vira dogma.

Corolário: **testar é barato, supor é caro.**
