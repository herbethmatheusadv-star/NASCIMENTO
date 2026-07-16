# MAPA DO PJe — como o advogado navega, e onde o robô pode ou não pisar

> Destilado do **Manual do Advogado oficial** (docs.pje.jus.br/manuais-de-uso/
> Manual do advogado), lido em 16/07/2026, cruzado com o que já provamos no
> TJPA real. O PJe é o **mesmo software** em todos os tribunais (TJPA, TJPB,
> TRF5, TRT6, TJCE, TJRJ…): a rota `Processo/ConsultaDocumento/listView.seam` é
> idêntica em todos. Aprender o PJe uma vez é aprender o país.
>
> Este documento existe para o robô **navegar como especialista** — e para a
> **R7** ter contornos precisos, não intuídos. Ver `regras.py` e `PLANO_SOJ` §7.

---

## 1. As três portas de entrada (em ordem de custo)

| Porta | O que dá | Login? | Escala |
|---|---|---|---|
| **DJEN + DataJud** | estado dos processos: publicação, teor, movimento, andamento | ❌ não | ✅ 150 processos, diária, de graça (já opera no RADAR) |
| **ConsultaDocumento por chave** | a **peça específica** cuja chave o DJEN publicou | ❌ **não** | ✅ headless, sem MFA — provado 16/07 (ver §4) |
| **Painel do Advogado** (autos completos) | tudo: acervo, expedientes, autos integrais | ✅ certificado + MFA | ⚠️ humano no portão, sob demanda (§3) |

**Princípio de arquitetura:** só se sobe de porta quando a de baixo não basta.
O estado dos 150 vem de graça; a peça avulsa vem pela chave; o auto integral do
processo que se vai **trabalhar hoje** vem do painel, com o advogado no portão.
Escala porque as duas primeiras camadas não dependem de ninguém ao teclado.

---

## 2. O Painel do Advogado — a máquina de estado (autenticado)

O painel tem cinco abas. Três importam para o SOJ:

### Aba ACERVO — os 150 processos
Lista **todos os processos em que o advogado consta como representante ou
parte**, incluindo o "Acervo geral" das entidades representadas. Filtra,
ordena, pagina, move para caixas, abre os autos. **É a fonte canônica do censo**
— o que o SOJ transcreveu para `censo_tjpa.yaml` em 15/07 saiu daqui.

### Aba EXPEDIENTES — os prazos vivos
Mostra os atos de comunicação (citação, intimação, notificação) dirigidos ao
advogado, **de que ele teve ciência (real ou ficta) e que estão dentro do prazo
de manifestação**. Ações por expediente: mover para caixa, ver detalhes, e —
🔴 as duas proibidas — **tomar ciência** e **responder**.

### Aba AGRUPADORES — a taxonomia oficial dos prazos
Seis categorias, e elas **são** a máquina de estado que o `regras.Quarentena`
implementa. Nomes canônicos do CNJ:

| # | Agrupador | Significado | R7 |
|---|---|---|---|
| 1 | **Pendentes de ciência** | ainda sem registro de ciência; mostra o prazo-limite para ciência | 🔴 **QUARENTENA — não abrir** |
| 2 | Ciência dada, dentro do prazo | ciência registrada, prazo correndo | ✅ ler os autos |
| 3 | Ciência ficta | ciência automática por decurso (Lei 11.419/2006) | ✅ ler |
| 4 | Prazo expirado | prazo findou nos últimos 10 dias | ✅ ler |
| 5 | Sem prazo | comunicação sem prazo de resposta | ✅ ler |
| 6 | Respondidos | respondidos nos últimos 10 dias | ✅ ler |

O agrupador **1** é exatamente a linha que a quarentena bloqueia: enquanto um
expediente está "pendente de ciência", **abrir o processo pode ser o próprio ato
de ciência** — e ciência dispara o prazo. Por isso o robô não toca nele. Os
demais já tiveram ciência: ler não muda nada.

---

## 3. Autos digitais — o que o robô lê, e o que ele nunca clica

Clicar no número do processo abre os **autos digitais** em nova janela. Dentro:

- **ordenar/filtrar** documentos × movimentos;
- **pesquisar** na listagem;
- **navegar** entre documentos juntados;
- por documento: favoritar, ver certidão, imprimir, **baixar o documento atual**,
  ver dados de assinatura;
- 🎯 **download por Id, Período ou TODO o conteúdo** — os autos integrais em um
  passo. É a operação-chave para o SOJ: não é peça a peça, é o processo inteiro.

### A fronteira exata da R7 (confirmada no manual, 16/07/2026)
> **Visualizar os autos ≠ tomar ciência.** São ícones distintos e explícitos:
> a **lupa vermelha** toma ciência; o **ícone de resposta** leva à ciência + à
> página de resposta. Abrir e ler não registra ciência.

Ou seja: o robô pode abrir os autos, listar documentos e baixar o conteúdo
integral **sem nunca disparar prazo** — desde que jamais toque a lupa vermelha
nem o ícone de resposta. Isso não é disciplina de runtime; é o que `regras.py`
garante por ausência (nenhuma função clica nesses ícones) + guarda de clique
(recusa rótulos "tomar ciência"/"responder") + quarentena (nem abre o processo
com ciência pendente). **Três camadas para a mesma linha.**

---

## 4. ConsultaDocumento por chave — a descoberta de 16/07/2026

O DJEN, em muitas intimações, publica ao fim:

> *"Para ter acesso aos documentos do processo, basta acessar o link abaixo e
> informar a chave de acesso."* + a lista `Título → chave (25+ dígitos)`.

**Provado no TJPA (16/07):** a página
`pje.tjpa.jus.br/pje/Processo/ConsultaDocumento/listView.seam` é **pública** —
sem login, sem captcha, sem certificado, sem MFA. Informada a chave da Petição
Inicial do GETULIO (0817105-93), o sistema respondeu *"A assinatura é válida
para o documento"* e ofereceu o PDF real (`Petição… .pdf`, 196 Kb).

**A chave contém o idBin:** `25100714462019100000`**`143053560`** → o link de
download traz `idBin=143053560`. A chave é auto-suficiente.

**Limites reais (não romantizar):**
- **Cobertura parcial:** das 92 comunicações da OAB em 12 meses, só **3
  processos** trazem a lista de chaves (60 documentos). É padrão do JEC de
  Parauapebas; nem toda vara publica. **Não cobre o acervo inteiro.**
- **É JSF/Seam:** o campo é `pesquisaProcessoDocumentoForm:numeroDocumento…`, o
  botão `botaoConsultar` é ajax RichFaces e o link de download é ação com `cid`
  de conversação — funciona **clicado no navegador**, não com `fetch`/`urllib`
  cru. Playwright com download habilitado é o caminho; POST às cegas não é.
- **DNS quebrado do próprio tribunal:** o TJPA imprime nas intimações o host
  `pje-consultas.tjpa.jus.br`, que **não resolve**. O host vivo é
  `pje.tjpa.jus.br`. Reescrever o host ao usar a chave.

---

## 5. O que isto NÃO resolve, e por que o navegador com humano segue necessário

- Processos **sem chave publicada** (a maioria) → só pelo painel autenticado.
- **Autos de processo sigiloso / segredo de justiça** (PROC-0011, 0014) → nem a
  chave nem o DJEN entregam; exigem o certificado dele.
- **O MFA obrigatório desde 18/05/2026** (Portaria CNJ 140/2024) fecha, por
  desenho do CNJ, o robô que loga sozinho. A resposta não é burlar: é **humano
  no portão** (Emenda 02) para o que exige login, e as portas públicas (§1) para
  o resto.

---

## 6. Consequência para o conector (próximos passos, quando houver GO)

1. **Colher chaves do DJEN** — o `RADAR` já baixa as comunicações; extrair a
   lista `título → chave` é um parser sobre texto que já temos. Custo baixo,
   ganho imediato: 60 documentos a um passo de distância.
2. **`baixar_por_chave.py`** — Playwright headless, reusa a página pública,
   preenche `numeroDocumento`, clica `botaoConsultar`, clica o link, salva o PDF
   em `AUTOS/<cnj>/`. **Sem login → roda sozinho, de madrugada.** Passa por
   `regras.guarda_de_url`.
3. **Sessão de painel com o advogado** (`sessao.py --mapear`) — só para o que as
   portas públicas não alcançam. Descoberta assistida de seletores das abas
   Acervo/Expedientes/Agrupadores e do **download integral** (§3), com ele ao
   teclado, nunca inventados. `_efemeros/mapeamento_pje/` ainda está vazio.
4. **Importador (Fase 3 do PLANO_SOJ)** — o que transforma PDF baixado em texto
   com `===[p.N]===`, hash, dedup e citação de página. **É o elo que faltava e o
   que responde à crítica dele:** entender o que há DENTRO do processo. Vale para
   os PDFs vindos por qualquer das três portas — inclusive os 105 MB de autos do
   TRT-8 que já estão em `AUTOS/`, parados.
