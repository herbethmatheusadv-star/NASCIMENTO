# CONECTOR — Roadmap de Capacidades (leitura/automação)

> **A visão (titular, 21/07/2026):** a partir de UMA sessão logada do titular, o
> conector deve executar **qualquer atividade de LEITURA / consulta / download**
> dentro do PJe (TJPA, TRT-8 e outros tribunais), para o titular não precisar
> fazer o trabalho braçal. O conector já baixou **16 processos do TJPA em
> segundos** — a mesma máquina se estende a novos recortes (por empresa, por CPF,
> por comarca). A inteligência de cada sistema, quando dominada, vira **código no
> CONECTOR** + registro no **`MAPA_PJE.md`** (a navegação destilada).
> Construímos **incremental, sob demanda** — conforme o titular precisa, a gente
> mapeia numa sessão logada e implementa.

## A fronteira que NÃO muda: R7

Tudo aqui é **LEITURA**. O conector enumera, busca e baixa — **nunca** assina,
peticiona, toma ciência nem protocola. Isso é a **R7** (Emenda 02/05, decisão do
titular): a capacidade de agir simplesmente **não existe** no código (ausência,
não bloqueio — ver `regras.py`). "Qualquer atividade" = qualquer atividade de
**leitura/consulta/download**. Ampliar para atos processuais seria uma **revogação
explícita da R7** — decisão deliberada do titular, nunca efeito colateral de
"automatizar mais".

## Já dominado

- **TJPA / TJMA (PJe Seam):** login por certificado → acervo → **download integral
  dos autos** (window.open/S3 no TJPA; form POST no TJMA). 16 processos em segundos.
  Código: `baixar_autos.py` + `instancias.py`. Import: `soj_import.py` (PDF→texto).
- **TRT-8 (PJe novo / PDPJ):** leitura do **acervo (lista)** pela API REST
  (`trt8_api.py`, `/pje-comum-api`). Ver `MAPA_PJE.md §13.9`.
- **TRT-8 — download dos AUTOS (app Kz):** o Kz usa a MESMA API REST; timeline +
  `/documentos/id/{idDoc}/conteudo` devolvem a lista e o PDF de cada peça.
  `trt8_kz.py` junta tudo num `autos_integral` (pronto p/ o `soj_import`).
  Mapeado na sessão logada de 21/07/2026. Ver `MAPA_PJE.md §13.10`. *Falta só o
  teste com o Bearer do titular (baixar de verdade) — depois, fichas 0001..0005.*

## Backlog — pendente, a mapear/implementar sob demanda

1. **[TRT-8] Download dos autos no PJe-Kz** — ✅ **FEITO (21/07/2026).** Os 5
   trabalhistas baixados, importados e indexados (819 pgs → PROC-0001..0005). O
   caminho vencedor foi o **botão nativo "Baixar processo completo"** no front do
   Kz (sem token, pela sessão logada — `MAPA_PJE.md §13.12`), dirigido pelo Claude.
   `trt8_kz.py` (API+token, §13.10-13.11) fica como via programática/fallback.
   *Pendente: enriquecer as fichas PROC-0001..0005 com o conteúdo dos autos.*
2. **Download em massa por EMPRESA (CNPJ / razão social)** — ✅ **FEITO
   (22/07/2026)**, com uma correção de premissa: **não se busca por CNPJ**. O
   DataJud público **não devolve parte nenhuma** (testado: só tribunal, grau,
   número, ajuizamento, sigilo, órgão, classe, assuntos, movimentos), e a
   consulta do TJPA busca por **nome**, com captcha e teto de resultados.
   A via que funciona é a mesma do Jusbrasil/Escavador: o **DIÁRIO**.
   `CONECTOR/mapear_adversario.py` usa `nomeParte` na API do DJEN e enumerou
   **28 processos** das rés do caso 2026-0006; `CONECTOR/baixar_por_chave.py`
   baixou **50 documentos** pelas chaves publicadas, sem login e sem captcha.
   *Limite honesto: busca por NOME erra dos dois lados — traz homônimo e perde
   variação de razão social (no caso-fonte, "J FERREIRA REPRESENTAÇÕES" acha
   ZERO no TJPA e "FERREIRA REPRESENTAÇÕES" acha 58). Sempre rodar variantes,
   filtrar por tribunal e conferir a lista de partes.*
3. **Download em massa por CPF / pessoa** — ✅ **mesma ferramenta**: o
   `nomeParte` vale para pessoa física (usado para achar HAYARA PATRICIA LIMA
   DE SOUZA, titular da Lima Financeira). Vale a mesma ressalva de homonímia,
   **agravada** em pessoa física.
3-B. **Jurisprudência nacional por texto livre** — ✅ **FEITO (22/07/2026)**,
   capacidade que nem estava neste roadmap. A mesma API do DJEN aceita o
   parâmetro **`texto`** e busca em **texto integral** o que foi publicado por
   **todos os tribunais do país** — sem captcha, sem login.
   `CONECTOR/buscar_jurisprudencia.py`. Testado: "golpe do consórcio" → 625
   publicações nacionais; "consórcio vício de consentimento" no TJPA → 12
   acórdãos de 2º grau com ementa. *Limite: acha o que foi PUBLICADO no diário
   no período indexado, não o acervo histórico de um tribunal.*
4. **Download por recorte (comarca / órgão / tribunal)** — enumerar e baixar um
   conjunto (ex.: todos os do titular numa comarca; um bloco de um tribunal).
5. **Radar de novidades multi-tribunal** — `consultarAlteracao` (MNI) e a API do
   PDPJ para detectar movimento diário, alimentando o cockpit sozinho.

## A MARCHA PROCESSUAL VIVA (norte do titular, 21/07/2026)

Baixar os autos é só o **retrato de hoje** (o baseline). O processo **anda**, e o
sistema tem de andar junto: os autos **não podem ficar mortos** ocupando espaço —
servem para **automatizar a marcha** (sabendo o teor da inicial/contestação, monta-se
estratégia: alegações finais etc.). Não dá para rebaixar os autos inteiros todo dia;
a regra é **baseline 1× + delta diário** (capturar só o que é NOVO). Assim nunca se
fica cego. Sequência **A → B → C**:

- **(A) Estruturar os autos** — índice cronológico de peças (tipo + data + id), do
  mais antigo ao mais novo. `ESCRITORIO/scripts/estruturar_autos.py` a partir da
  timeline do Kz → `AUTOS/{cnj}/estrutura_cronologica.md` + `timeline_baseline.json`
  (a régua do delta). *Iniciado 21/07: PROC-0003 (Beatryz) estruturado, 39 peças.*
- **(B) O elo do DELTA** ⭐ o coração — o `RADAR/` já sabe QUE mexeu (DJEN +
  DataJud); falta ele **buscar só a peça nova** (a timeline diz o que entrou depois
  da régua), encaixar na estrutura e atualizar ficha/prazo. Baseline 1×, delta todo dia.
- **(C) Onboarding automático** — processo novo protocolado → baseline baixado 1× →
  entra no radar diário sozinho.

**Regra dos ARQUIVADOS (titular, 21/07):** processo arquivado vai para uma
**classificação à parte, só a título de registro** — **não entra no radar diário**
(não anda mais). Só os **ativos/não-arquivados** são vigiados. Dos 5 trabalhistas de
21/07, só **PROC-0003 (Beatryz, em execução)** é ativo; os outros 4 são registro.

## O rito de cada capacidade nova

(a) **Sessão de mapeamento logada** com o titular — ver por dentro, sem chutar
seletor (regra da casa: padrão vem do dado real). (b) **Código no CONECTOR**
respeitando a R7 (só GET/leitura; `guarda_de_url`/`guarda_de_clique`; a rota de
avisos/ciência fica de fora). (c) **Teste**. (d) **Registro no `MAPA_PJE.md`** —
a inteligência destilada, para não redescobrir na próxima.
