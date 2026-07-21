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

1. **[TRT-8] Download dos autos no PJe-Kz** — ✅ **MAPEADO E IMPLEMENTADO**
   (21/07/2026, `trt8_kz.py`, `MAPA_PJE.md §13.10`). Resta o teste com o Bearer do
   titular (baixar de verdade os 5) e montar as fichas PROC-0001..0005.
2. **Download em massa por EMPRESA (CNPJ / razão social)** — dado um CNPJ/nome,
   pesquisar, **enumerar TODOS os processos** e baixar os autos de cada um. Caso
   de uso: litígio contra uma empresa (mapear o adversário inteiro de uma vez).
3. **Download em massa por CPF / pessoa** — idem para pessoa física.
4. **Download por recorte (comarca / órgão / tribunal)** — enumerar e baixar um
   conjunto (ex.: todos os do titular numa comarca; um bloco de um tribunal).
5. **Radar de novidades multi-tribunal** — `consultarAlteracao` (MNI) e a API do
   PDPJ para detectar movimento diário, alimentando o cockpit sozinho.

## O rito de cada capacidade nova

(a) **Sessão de mapeamento logada** com o titular — ver por dentro, sem chutar
seletor (regra da casa: padrão vem do dado real). (b) **Código no CONECTOR**
respeitando a R7 (só GET/leitura; `guarda_de_url`/`guarda_de_clique`; a rota de
avisos/ciência fica de fora). (c) **Teste**. (d) **Registro no `MAPA_PJE.md`** —
a inteligência destilada, para não redescobrir na próxima.
