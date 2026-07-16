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

---

## 7. Leitura literal do Manual do Advogado (16/07/2026)

> Transcrição fiel das seções operacionais do Manual do Advogado oficial
> (docs.pje.jus.br/manuais-de-uso/Manual do advogado — **página única**, ~43
> seções por âncora). Substitui as anotações de segunda mão dos §2–3. O que está
> entre aspas é do manual; o resto é leitura. **Marcações de confiança:** ✅
> literal do manual · 🧪 provado no TJPA real · ⚠️ o manual trunca / não diz.

### 7.1 Autos digitais — as 15 ações (✅ literal)

Abrir: *"clicar sobre o link do processo (que fica sobre o número), uma nova
janela surgirá contendo os autos digitais"*. Cabeçalho recuperado: **classe
judicial, assunto, autuação, última distribuição, valor da causa, segredo de
justiça, prioridade, órgão colegiado, órgão julgador, relator, polo ativo, polo
passivo, outros interessados**.

| # | Ação (texto do manual) | Uso no SOJ |
|---|---|---|
| 1 | apresenta os autos digitais + cabeçalho | leitura |
| 2 | ordenar e **filtrar só documentos ou só movimentos** | leitura |
| 3 | pesquisar dentro da listagem | leitura |
| 4 | atualizar a relação | leitura |
| 5 | ocultar/expandir a cronologia | leitura |
| 6 | navegar entre os documentos juntados | leitura |
| 7 | adicionar documento aos favoritos | — |
| 8 | visualizar certidão do documento | leitura |
| 9 | imprimir documento atual | — |
| **10** | **download do documento atual** | 🎯 baixar peça |
| 11 | visualizar dados da assinatura | leitura |
| 12 | ver favoritos + **download de todos os favoritos** | 🎯 lote |
| 13 | imprimir a lista de documentos | — |
| **14** | **"download por Id, Período ou todo o conteúdo"** | 🎯🎯 **autos integrais num passo** |
| 15 | navegar entre as **abas do processo** | ⚠️ o manual não nomeia as abas |

**A ação 14 é o coração da escala.** Não é peça a peça — é o processo inteiro (ou
um período) de uma vez. Responde à objeção dos 150 processos.

### 7.2 Acervo — enumerar os 150 (✅ literal)

*"O advogado visualiza todos os processos nos quais consta como representante ou
parte direta. Também tem acesso ao 'Acervo geral', que encerra todos os processos
de que os entes por ele representados são parte."* Pesquisa pela barra "Pesquisar".
10 controles: abrir todas as caixas · jurisdição · caixas · atualizar · ordenar
por · mover selecionados · **autos digitais (clique no número abre os autos)** ·
painel de ações (mover/selecionar/ver detalhes) · histórico de movimentações ·
pesquisar. **É a fonte do censo** — foi daqui que saíram os 25 processos.

### 7.3 Caixas — organização por filtro automático (✅ literal)

Botão direito na jurisdição → **"Nova caixa"** ou **"Distribuir expedientes
utilizando filtros"** → nomear → **"Criar caixa"**. Editar dá três abas:
principal (nome/descrição), **períodos de inativação**, e **filtros da caixa** —
*"processos distribuídos para a jurisdição redirecionam-se automaticamente"*.
Nota para o SOJ: as **caixas do PJe são espelho natural das caixas do SOJ**
(área, risco, comarca). Se um dia lermos a estrutura de caixas dele, ela já é uma
classificação humana pronta.

### 7.4 A FRONTEIRA DA R7 — agora com os rótulos exatos (✅ literal + 🧪)

**Aba Expedientes, as 6 ações, texto do manual:**
1. "Mover expediente para caixa"
2. "Selecionar para mover vários expedientes"
3. "Ver detalhes do processo"
4. **"Visualizar expediente"**
5. **"Responder"**
6. **"Tomar ciência"**

**Dois achados que afinam a guarda de clique:**

- ✅ **"Visualizar expediente" (4) é ação SEPARADA de "Tomar ciência" (6).**
  Visualizar o expediente **não** registra ciência. O robô pode ler; a lupa
  vermelha da ciência é outro botão.
- ✅ **"Responder" (5) leva à ciência.** O manual: responder *"leva à ciência e a
  uma página em que a resposta pode ser elaborada"*. **Responder é tomar ciência
  + peticionar num gesto só** — dupla proibição da R7. Confirma o achado do spike
  (no MNI, `confirmarRecebimento` e `entregarManifestacaoProcessual` são a mesma
  família): responder = ciência + resposta, e nenhum dos dois é do robô.

**Os 6 agrupadores (✅ rótulos literais do CNJ — batem com o censo de 15/07):**
1. **"Pendentes de ciência ou de seu registro"** → 🔴 quarentena: não abrir
2. "Ciência dada pelo destinatário direto ou indireto e dentro do prazo" → ✅ ler
3. "Ciência dada pelo PJe e dentro do prazo" (ficta, Lei 11.419/2006) → ✅ ler
4. "Cujo prazo findou nos últimos 10 dias" → ✅ ler
5. "Sem prazo" → ✅ ler
6. "Respondidos nos últimos 10 dias" → ✅ ler

Regra de ferro reconfirmada: **o robô lê o que está nos agrupadores 2–6; nunca
toca no 1, nem nos botões "Responder"/"Tomar ciência".** É o que `regras.py`
garante por ausência + guarda de clique + quarentena.

### 7.5 A face de escrita — o que o robô NUNCA opera (✅ + ⚠️)

O peticionamento segue: **"Tipo de documento"** (a inicial é "Petição inicial") →
**"Descrição"** (título, preenchido automaticamente) → **"Número"** (referência
opcional do usuário) → **"Sigiloso"** → **[assinatura e protocolo]**. ⚠️ **O
manual trunca exatamente aqui** — não detalha as telas de assinar/protocolar.

Para o SOJ isso é indiferente, e de propósito: **essa é a metade que o sistema
não automatiza.** O robô lê os autos e **redige a minuta** (skills do escritório,
`/soj-preparar-peca`); quem seleciona tipo, assina e protocola é **o titular**.
A regra 2 do PLANO_SOJ ("nenhum ato processual autônomo: protocolar, assinar,
dar/tomar/confirmar ciência, enviar, juntar, peticionar") e a divisão de trabalho
da Emenda 05/02 mandam aqui. Ver `regras.VOCABULARIO_PROIBIDO`.

### 7.6 Acesso e autenticação (✅ + ⚠️ versão do manual)

O manual descreve o cadastro/login por **certificado digital**: *"inserir seu
dispositivo criptográfico na leitora (smartcards) ou na porta USB (token), e
acionar o botão 'Certificado digital'"*. ⚠️ **Este manual é a versão-base do CNJ
e NÃO menciona gov.br, PJeOffice nem MFA** — mas o TJPA real, desde a Portaria CNJ
140/2024 (18/05/2026), **exige MFA por aplicativo**. Ou seja, o login real do
titular é certificado (A1 via PJeOffice) **+ autenticador** — os dois passos que
ele descreveu, e que confirmam o desenho "humano no portão" (Emenda 02): o robô
não faz nem o certificado nem o MFA; o titular autentica, o robô lê o que já está
na tela.

### 7.7 Intimação de pauta e Minhas petições (✅ literal)

- **"Intimação de pauta"**: atos de intimação de **sessão de julgamento** (data,
  horário, tipo). *"Detalhe da Intimação"* abre o inteiro teor. **Relevante para o
  2º grau** — é aqui que aparece pauta de apelação (ex.: PROC-0021 no TJPA).
- **"Minhas petições"**: *"acesso geral a todas as petições juntadas aos processos
  por ele mesmo"* — histórico do que o titular protocolou. Fonte de auditoria útil.

---

## 8. Seletores REAIS do painel TJPA (sessão de mapeamento — 16/07/2026)

> 🧪 Colhidos na primeira sessão real (`sessao.py --mapear`, titular no portão,
> perfil efêmero apagado no fim). 5 telas do painel retratadas; o interior dos
> autos **não** foi capturado (a janela foi fechada antes). Os HTML e o mapa
> completo ficam em `_efemeros/mapeamento_pje/` — **fora do Git** (dado de
> cliente). Aqui só a estrutura.

**Painel:** `https://pje.tjpa.jus.br/pje/Painel/painel_usuario/advogado.seam`.
As abas trocam por **AJAX** — a URL não muda, o conteúdo sim.

### 8.1 Menu — URLs reais (o que a guarda precisava conhecer)

| Função | URL | R7 |
|---|---|---|
| Consulta de processo | `/pje/Processo/ConsultaProcesso/listView.seam` | ✅ ler |
| **Área de download** | `/pje/AreaDownload/listView.seam` | ✅ **onde cai o download integral** |
| Pauta de audiência | `/pje/ProcessoAudiencia/PautaAudiencia/listView.seam` | ✅ ler |
| Push (monitoramento) | `/pje/Push/listView.seam` | ✅ ler |
| **Peticionar** | `/pje/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam` | 🔴 bloqueado |
| **Assinar documentos** | `/pje/Painel/advogado/consultaDocnaoAssinado.seam` | 🔴 bloqueado |
| Novo processo (ajuizar) | `/pje/Processo/cadastrar.seam` | 🔴 bloqueado |

**O achado que valeu a sessão:** os padrões antigos de `URLS_PROIBIDAS` eram
**chutados e furavam** — `peticion` não pega `peticaoavulsa` (petiCAO ≠ petiCION),
`assinatur` não pega `naoAssinado`. **As três URLs de escrita passavam batido.**
Provado e corrigido: `regras.URLS_PROIBIDAS` agora usa os tokens reais
(`peticaoavulsa`, `naoassinado`, `cadastrar\.seam`…); `teste_regras.py §4 [REAL]`
trava as 4 de escrita e libera as 4 de leitura. R7: 49 → **56 casos**.

### 8.2 Aba Expedientes — os 6 agrupadores, com seletor

Padrão: **`formAbaExpediente:listaAgrSitExp:{N}:j_id158`** (link `<a>`), texto real:

| N | Texto (rótulo real do TJPA) | R7 |
|---|---|---|
| **0** | **"Pendentes de ciência ou de resposta"** | 🔴 **quarentena — não abrir** |
| 2 | "Ciência dada pelo destinatário direto ou indireto - pendente" | ✅ |
| 3 | "Ciência dada pelo Judiciário - pendente de resposta" | ✅ |
| 4 | "Cujo prazo findou nos últimos 10 dias - sem resposta" | ✅ |
| 5 | "Sem prazo" | ✅ |

Botão "Mover expedientes": `frmMoverPara:btMvPr`. Form: `formAbaExpediente`.

### 8.3 Aba Acervo — árvore por comarca

Padrão dos nós: **`formAbaAcervo:trAc:{N}::jNd`** (o nó da comarca/jurisdição),
com `formAbaAcervo:trAc:{N}::j_id814:handle` para expandir/recolher. Form:
`formAbaAcervo`. É uma **árvore** (as comarcas do titular — Parauapebas, Canaã…),
não uma lista plana; abrir um nó revela os processos daquela comarca.

### 8.4 ⚠️ Fragilidade a respeitar

Os sufixos **`j_id158` / `j_id814` são gerados pelo JSF** e **mudam** entre
versões do PJe e, às vezes, entre sessões. O que é **estável**: os prefixos de
form (`formAbaExpediente`, `formAbaAcervo`, `listaAgrSitExp`, `trAc`) e as URLs.
**Regra para o leitor de autos:** ancorar por prefixo estável + texto do elemento
(ex.: o `<a>` cujo texto casa "Pendentes de ciência"), **nunca** pelo `j_idNNN`
cru. Se o seletor quebrar, é sinal de mudança de versão → parar e remapear com o
titular, nunca clicar às cegas (regra do §10.4 do PLANO_SOJ).

### 8.5 O que ainda falta mapear (uma próxima sessão curta)

O **interior dos autos digitais** — as 15 ações do §7.1, em especial o **download
"todo o conteúdo" (ação 14)** e as abas internas do processo (ação 15). Não foi
capturado porque a janela fechou antes. Basta uma sessão de ~2 min: abrir os autos
de **um** processo pela Acervo e **deixar aberto ~15 segundos** antes de fechar,
para o robô retratar a nova aba. Só então o `baixar_autos.py` terá o seletor do
download integral.

### 8.6 O modelo de interação REAL — engenharia reversa dos HTML (16/07/2026)

Disseca dos 5 HTML capturados (não do manual — do sistema). Três verdades que
mudam como o leitor de autos precisa ser escrito:

**1. O painel é RichFaces / A4J (AJAX).** Uma só tela tinha **116
`A4J.AJAX.Submit`**. Quase nenhum controle do painel é uma URL — a maioria é um
`onclick` que dispara submit AJAX (ex.: a árvore do Acervo usa
`filtrosFormAcervo:j_idNNN.component.eventCellOnClick`). **Consequência para a
R7:** dentro do painel, a defesa principal **não** é a guarda de URL (não há URL
a navegar) — é a **guarda de clique** sobre o *texto* do elemento ("Tomar
ciência", "Responder"). A guarda de URL cobre o **menu** (Peticionar/Assinar/Novo
processo, §8.1), que são `.seam` de verdade. As duas camadas se dividem o trabalho,
e agora sabemos exatamente qual cobre o quê.

**2. Os autos abrem por `window.open`, em nova janela** — era a "nova aba" que o
mapeador detectou. A URL real:

```
/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado.seam?id={ID}
```

O **`{ID}` é o id interno do processo (numérico), NÃO o CNJ.** Cada linha do Acervo
carrega o seu `window.open(...id=NNN...)`. É **leitura** — a guarda de URL a libera
(confirmado: não casa nenhum padrão proibido). É o ponto de entrada dos autos
digitais (as 15 ações do §7.1) e, portanto, do download integral (ação 14).

**3. O fluxo do leitor de autos, agora inteiro (do sistema real):**
```
[humano no portão: certificado + MFA]
   ↓
Acervo (árvore por comarca)  →  cada processo tem window.open(...id=NNN)
   ↓  o robô LÊ a lista e extrai os pares  CNJ ↔ id interno
listProcessoCompletoAdvogado.seam?id=NNN   (nova janela = autos digitais)
   ↓  ação 14: download "todo o conteúdo"
AreaDownload/listView.seam   (o pacote fica aqui para baixar)
```
Falta só o seletor do botão da ação 14 (interior dos autos) — a mini-sessão do §8.5.

### 8.7 O que o manual dá e o sistema NÃO, e vice-versa (a lição da rota)

- Só o **sistema** revelou: `peticaoavulsa.seam` (a R7 furada), o modelo A4J, e
  `listProcessoCompletoAdvogado.seam?id=` (como os autos abrem). O manual jamais
  diria isso — ele fala em "clicar no número do processo", sem a URL nem o `id`.
- Só o **manual** dá: o *significado* (o que é ciência, por que o agrupador 1 é
  perigoso, que a ação 14 baixa "todo o conteúdo"). O HTML mostra `j_id158` sem
  dizer que ali mora a quarentena.
- **Regra de trabalho:** manual para o *sentido*, engenharia reversa para a
  *verdade*, sempre cruzados. Nenhum seletor entra em código sem os dois — e
  nenhum seletor `j_idNNN` cru entra nunca (§8.4).

---

## 9. A ARQUITETURA — e a API REST que muda o plano (docs oficiais + rede real, 16/07/2026)

> Da documentação de arquitetura do CNJ (`docs.pje.jus.br/manuais-basicos/`) +
> do código aberto (`git.cnj.jus.br/pje`) + **da chamada de rede real capturada
> na sessão**. Esta seção reordena a estratégia: **o alvo é a API REST, não o
> HTML.** O HTML (§7–8) vira subsidiário, exatamente como o titular apontou.

### 9.1 O sistema tem DOIS frontends sobre UM backend

- **Legado (PJe 1.x):** JSF + JBoss Seam 2.2 sobre WildFly. É o **painel** que
  raspamos no §8 (`advogado.seam`, RichFaces/A4J).
- **Moderno (PJe 2.x):** **Angular** (6+) falando com **microserviços Spring
  Boot/Spring Cloud** via **REST**, atrás de um **API Gateway (Zuul)**, service
  discovery (Eureka), mensageria (RabbitMQ), auth **OAuth2/SSO (Keycloak)**.
- Os dois coexistem: a tela de autos moderna é `/pje/ng2/dev.seam#/autos-digitais/{idProcesso}`
  e conversa com o legado **por REST**.

### 9.2 A API REST — o padrão, e o endpoint REAL capturado

**Padrão documentado:** `/{modulo}/api/v{N}/recurso` — recursos como
`/processos/{id}/documentos`, `/colegiados/api/v1/sessoes/{id}/processos`.
Resposta JSON padronizada: `{status, code, messages, result, page-info}`.
Query: `filter` (eq/lt/gt/like/in), `fields`, `order`, `page`/`size`.

**E o que o sistema real entregou — a chamada capturada quando o titular abriu
um processo:**
```
GET  /pje/seam/resource/rest/pje-legacy/documento/download/{idDocumento}   → 200
```
Este é o **RESTEasy do Seam legado**: `…/seam/resource/rest/pje-legacy/…`. O
`documento/download/{id}` **retorna o binário da peça** — é a via limpa que o
`baixar_autos.py` deveria usar, no lugar do `listView.seam` com `cid` de
conversação (§4, que dava 404 fora do clique). Aqui o `{id}` é o **idDocumento**
(ex.: 181987438), o mesmo que aparece nos hrefs dos autos.

### 9.3 O que isto reordena

| Camada | Antes (o que eu vinha fazendo) | Agora (o alvo certo) |
|---|---|---|
| Ler documento | raspar `listView.seam` (JSF, `cid`, frágil) | **GET `…/rest/pje-legacy/documento/download/{id}`** (binário direto) |
| Listar peças | scraping do HTML dos autos | **REST `/processos/{id}/documentos`** (JSON) |
| Estado/movimentos | DJEN + DataJud (já temos) | idem, ou REST interno |
| HTML/JSF | era o plano | **subsidiário** — só onde a REST não alcança |

### 9.4 O que NÃO muda (a autenticação e a R7)

- **Continua exigindo o portão humano.** A API interna é protegida por
  **OAuth2/SSO (Keycloak)** — o mesmo login (certificado + MFA). O robô não
  autentica; o titular sim, e a sessão do navegador carrega o token. O robô, já
  dentro da sessão autenticada, chama os endpoints REST de **leitura**.
- **R7 por ALLOWLIST de endpoints, como no MNI.** O base `…/rest/pje-legacy/…`
  também pode expor escrita (ciência, protocolo). Então o leitor **não** usa
  blocklist: usa uma **lista branca** de rotas de leitura (`documento/download`,
  `processos/{id}/documentos`, consulta) — espelhando `OPERACOES_MNI_PERMITIDAS`.
  O `documento/download` é GET de leitura: a guarda de URL o libera (não casa
  padrão proibido).

### 9.5 Próximo passo concreto (e por que a mini-sessão agora vale muito mais)

A mini-sessão de ~2 min do §8.5 deixou de ser "pegar o seletor do botão" e virou
**"capturar os endpoints REST da tela de autos"** — que é o que o mapeador já faz
no log de rede (foi assim que o `documento/download` apareceu). Abrindo os autos
de um processo e deixando ~15s, o log de rede revela: o endpoint que **lista os
documentos**, o que faz o **download integral**, e o padrão de auth (cookie/
JSESSIONID ou Bearer). Com isso, `baixar_autos.py` fala REST com o backend, dentro
da sessão que o titular abriu — limpo, estável, e sem `j_idNNN`.

### 9.6 Autenticação — o desenho FECHADO (Keycloak SSO)

Do `servico-sso-pje-kc`:
- **Keycloak**, protocolos **OAuth2 + OpenID Connect** (+ SAML). **Realm: `pje`**.
  **Client por tribunal/grau**: `pje-tj{uf}-{grau}g` → no TJPA 1º grau,
  **`pje-tjpa-1g`**.
- **JWT em três tokens:** Access (curto, para chamar a API), ID (identidade),
  Refresh. Os microserviços autenticam por header **`Authorization: Bearer {access_token}`**.
- **Certificado (PJeOffice) + 2FA** são o que gera os tokens: login → valida no
  legado → authorization code → troca por JWT no backend.

**A nuance que só a rede confirma:** o endpoint que capturei é do **legado Seam**
(`/pje/seam/resource/rest/pje-legacy/…`). Legado Seam costuma autenticar por
**cookie de sessão (JSESSIONID)**, não por Bearer — os microserviços *novos* é que
usam Bearer. Qual dos dois o `documento/download` exige, os **headers da
requisição** dizem (a mini-sessão de captura resolve).

**🔒 Guardrail de segurança — inegociável (liga com `recusa-automacao-credenciais`):**
o leitor roda **DENTRO** do navegador que o titular autenticou e usa o token/cookie
**na sessão**, viva. **Nunca extrai o JWT nem persiste o cookie para fora** — isso
seria "capturar token de sessão", exatamente o que o titular vetou. A sessão morre
com o processo; amanhã, cert + 2FA de novo. O token é do navegador dele, não do robô.

### 9.7 O teto honesto da documentação

Os docs fecham **arquitetura + padrão de API + auth**. Mas **não publicam o
catálogo de endpoints** — o doc do Autos Digitais é descrição de sprints, o do
PJeLegacy está "em construção", e não há Swagger linkado. O contrato completo
(listar documentos, download integral, e o header de auth exato) sai de **uma**
via prática: a **captura de rede na sessão autenticada** (o mapeador já pegou o
`documento/download`). Ou seja: o *desenho* está fechado; o *catálogo* se fecha na
mini-sessão, não em mais leitura de doc.

### 9.8 Fontes

- Arquitetura PJe (CNJ): `docs.pje.jus.br/manuais-basicos/arquitetura-pje/`
- Padrões de API: `docs.pje.jus.br/manuais-basicos/padroes-de-api-do-pje/`
- SSO Keycloak: `docs.pje.jus.br/servicos-negociais/servico-sso-pje-kc/`
- PJeLegacy: `docs.pje.jus.br/servicos-negociais/servico-pje-legacy/`
- Autos Digitais: `docs.pje.jus.br/servicos-negociais/servico-autos-digitais/`
- Código aberto: `git.cnj.jus.br/pje` (Resolução CNJ 185/2013)
- Endpoint real: `_efemeros/mapeamento_pje/mapa_2026-07-16_1226.md`

---

## 10. Manual do Advogado — leitura completa (as seções restantes)

Percorridas as ~30 seções finais (fluxo "Novo processo"). Quase tudo é a face de
**criar/ajuizar** processo — território da R7 (o robô nunca ajuíza), lido aqui
só para completude. **Um achado importa direto ao SOJ:**

### 10.1 Segredo de justiça (RN443) — mapeia a nossa classificação de sigilo

Ao ajuizar, o segredo de justiça é "Sim" + um **motivo** legal, e são só dois:
- **Art. 155, I (CPC/73)** — *"exigência do interesse público"*. É o caso da
  **ação penal de violência doméstica** (PROC-0011): corre em segredo por interesse
  público (Lei 11.340/2006).
- **Art. 155, II** — *"casamento, filiação, separação, divórcio, **alimentos e
  guarda de menores**"*. É o caso da **execução de alimentos** (PROC-0014).

Isto **confirma pela raiz** por que aqueles dois são sigilosos, e casa com a regra
6 do PLANO_SOJ (`segredo_justica: true ⇒ sigilo: sigiloso`). O DJEN, nesses, só
devolve *"Processo sigiloso"* — coerente: o próprio ato de ajuizamento os marcou.

### 10.2 Juntada de documento (a face de escrita, de novo truncada)

O fluxo é: **Incluir petições e documentos → Tipo de documento** (a inicial é
"Petição inicial") **→ Descrição → Número** (referência opcional) **→ Sigiloso →
[assinar e protocolar]**. Pela terceira fonte independente, **o manual trunca em
"assinar e protocolar"** — as telas finais de assinatura não são publicadas. Para
o SOJ é indiferente: essa é a metade que o titular executa, nunca o robô.

### 10.3 Estado da leitura

**Manual do Advogado: lido por inteiro** (§7, §8, §10). **Arquitetura + API + auth:
fechados** (§9). O que resta não está em documento nenhum — é o **catálogo de
endpoints REST**, que só a captura de rede na sessão autenticada entrega (§9.7).
