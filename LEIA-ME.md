# LEIA-ME — Sistema Operacional Jurídico NASCIMENTO (SOJ)
## 2ª edição — 07/07/2026

> Este arquivo explica o sistema em linguagem simples, para quem não é
> programador. A especificação técnica completa está em `SOJ_BLUEPRINT_v1.md`
> (v1.10). A 1ª edição descrevia o sistema do piloto (5 scripts); esta 2ª
> edição descreve o sistema completo após a expansão F6: 17 comandos, 4
> portas de entrada, motor de mídia, motor de autos e porta de importação.

---

## 1. O que é isto?

Esta pasta é o seu escritório digital. Ela funciona com uma regra de ouro:

**Cada informação vive em UM único lugar. Todo o resto é gerado automaticamente.**

No sistema antigo, o mesmo dado (um fato, uma prova, um prazo) era copiado em
vários arquivos — e quando um mudava, os outros ficavam desatualizados. Aqui
isso não acontece: os dados do caso vivem num único arquivo (`CASO.yaml`), e
os quadros, checklists e relatórios são produzidos por pequenos programas
("scripts") a partir dele. Se um quadro está errado, corrige-se a fonte e
gera-se de novo — nunca se edita o quadro.

Você não decora comando nenhum: fala em português com o Claude Code ("chegou
o extrato da Tânia", "anexar autos do caso X") e ele aciona o programa certo.

## 2. O mapa da pasta

```
NASCIMENTO/
├── LEIA-ME.md          ← você está aqui
├── SOJ_BLUEPRINT_v1.md ← a "lei" do sistema (especificação aprovada)
├── PAINEL.md           ← visão geral de TODOS os casos (gerado automaticamente)
│
├── ESCRITORIO/          ← o que é do escritório, não de um caso
│   ├── ADVOGADO.md      ← seus dados profissionais (fonte única da qualificação)
│   ├── BASE_LEGAL/      ← leis e jurisprudência verificadas NA FONTE, com validade
│   ├── MODULOS/         ← o conhecimento por área:
│   │     familia/            (completo: praxe, teses, anti-erro, template)
│   │     consumidor_aguas/   (negativação × Águas do Pará, JEC)
│   │     bancario_ccb/       (defesa em execução de CCB — nasce réu)
│   │     trabalhista/ previdenciario/  (esqueletos — nascem do 1º caso)
│   ├── ACERVO/          ← modelos de referência anonimizados (fichas M-NN)
│   ├── MODELOS/         ← modelos comentados do CASO.yaml e do DIARIO
│   ├── RELATORIOS/      ← relatório mensal do escritório
│   └── scripts/         ← os 17 programas que operam o sistema
│
└── CASOS/
    └── NOME_DO_CLIENTE/
        ├── 00_originais/   ← documentos COMO CHEGARAM, lacrados com impressão
        │                     digital (hash SHA-256). NUNCA mexer.
        ├── 01_documentos/  ← cópias renomeadas (DOC-01, DOC-02…)
        ├── CASO.yaml       ← A FONTE DA VERDADE: partes, fatos, provas,
        │                     pedidos, prazos, pendências, financeiro, autos
        ├── DIARIO.md       ← o livro de registro: só se ACRESCENTA, nunca se edita
        ├── INTAKE.md / ESTRATEGIA.md  ← a prosa do caso
        ├── MINUTA_v01.md…vNN ← a peça em versões (nada se sobrescreve)
        ├── AUDIENCIAS/     ← pasta de cada audiência com roteiro para SUA revisão
        ├── _views/         ← relatórios GERADOS (status, pendências, índice dos
        │                     autos, revisão de colaborador…). Nunca editar.
        ├── _efemeros/      ← rascunhos descartáveis e texto extraído dos autos
        └── PROTOCOLO/      ← o pacote final para protocolar
```

## 3. As regras que nunca se quebram

1. **`00_originais/` é sagrado.** O que chegou fica lá intocado, para sempre —
   e desde a Onda 4 todo original ganha **hash SHA-256** na entrada (a
   "impressão digital" que prova que ninguém alterou um byte: cadeia de
   custódia).
2. **`DIARIO.md` só cresce.** Errou? Nova entrada corrigindo — nunca se apaga.
   Cada entrada registra a **origem**: titular, sistema ou colaborador.
3. **`_views/` nunca se edita à mão.** Errado? Corrija a fonte e regenere.
4. **Nenhuma lei é citada de memória.** Todo artigo tem texto literal, fonte
   oficial e data de verificação na `BASE_LEGAL/` — e verificação vence
   (90 dias os códigos estáveis, 30 as leis mexidas há pouco). Vale para
   você, para o sistema e para peça de colaborador.
5. **A versão protocolada é SEMPRE a última que o sistema conhece.** Melhorou
   a peça no Word? Ela volta pela porta de retorno ("absorver minha versão")
   antes de qualquer protocolo.
6. **Prazo antes de tudo.** Chegou decisão, sentença ou intimação? O prazo é
   identificado, calculado e registrado ANTES de qualquer análise.
7. **Nada de colaborador vira decisão sem a sua ratificação** — e nada de
   gravação de atendimento sem o consentimento do cliente registrado no
   DIÁRIO **antes**.

## 4. O caminho de um caso

```
E1 INTAKE ──G1──► E2 ESTRATÉGIA ──G2──► E3 MINUTA ──G3──► E4 PROTOCOLO
```

- **G1 (7 itens)** — "o intake está completo?" Documentos lacrados e
  registrados (prova OU instrumental), partes qualificadas, fatos com status
  honesto, prazos identificados, checklist enviado. **Cliente réu/executado
  (modo defesa): item zero — o prazo de resposta tem que estar no vigia.**
- **G2 (7 itens)** — "prontos para escrever?" Estratégia com simulação
  adversária e juiz rigoroso, decisões com fundamento/alternativa/confiança,
  ratificação em bloco, riscos com contramedida — e **nenhuma proposta de
  colaborador pendente de ratificação**.
- **G3 (9 itens)** — "pode protocolar?" Zero pendência bloqueante, leis
  do núcleo reverificadas na véspera, checagem cruzada peça↔decisões
  (inclusive valor da causa conferido mecanicamente), anti-erro fatal do
  módulo, e a sua **declaração de revisão humana integral**.

Portão reprovado = etapa seguinte **bloqueada**. Os gates leem CAMPOS
estruturados do CASO.yaml (nunca interpretam texto livre) e cada execução
gera relatório + entrada no DIÁRIO + fotografia no git.

## 5. As quatro portas (como as coisas ENTRAM no sistema)

**Porta única (`chegou … do caso X`).** Todo documento novo entra por aqui.
O roteador identifica o tipo e aplica o rito: *prova* → P## com hash;
*peça do adversário* → análise adversarial (teses deles, fraquezas); *decisão/
sentença/intimação* → prazo ANTES de tudo + evento processual (a fase do
processo atualiza sozinha: contestação → propõe réplica; sentença → propõe
recurso [decisão sua]; trânsito → cumprimento); *sentença favorável* →
candidata ao Acervo; *ata de audiência* → baixa a audiência e dispara a
colheita.

**Porta de retorno (`absorver minha versão da peça`).** Sua versão melhorada
volta, o sistema compara com a dele e classifica cada mudança: estilo
(absorve), fato novo (exige prova ou vira alegação), citação nova (verifica
NA FONTE antes de aceitar), quantum/pedido (reconcilia com as decisões).
Vira versão nova, re-roda o gate, e só então DOCX.

**Porta de importação (`importar caso trabalhado: [pasta]`).** Caso
pré-trabalhado por sócio/estagiário entra com **confiança zero**: deduplica
por hash, separa provas de **instrumentais** (procuração assinada, RG,
honorários, hipossuficiência — provam representação, não fato), manda
rascunho para os efêmeros, confere TODA citação da minuta na BASE_LEGAL e
gera o **Relatório de Revisão do Colaborador** (o que está bom com crédito,
lei morta, fato sem prova, juiz rigoroso, adversário). Decisões embutidas na
peça (quantum, foro) viram propostas aguardando a sua ratificação — o G2
trava até você decidir. Duas minutas na pasta? O sistema PARA e pergunta.

**Motor de autos (`anexar autos do caso X`).** Processo que chega de fora
(PJe): o PDF é lacrado, o texto extraído de graça por script, as páginas
digitalizadas passam por **OCR local** (o do próprio Windows, em português —
nada sai da máquina), e os autos viram um **índice por documento e folha**
(`_views/AUTOS_INDICE.md`) com um **plano de leitura com orçamento**:
peças e decisões se leem integrais; certidões, ARs e guias **nunca**; o
resto sob demanda. Autos com mais de 100 folhas: **nada é lido antes do seu
ok ao plano**. O que foi lido é destilado UMA vez para a ficha (fatos com
"fls. X-Y", teses, prazos direto no vigia) e **nunca se relê** — sessões
futuras usam a ficha, jamais o PDF.

## 6. O motor de mídia (WhatsApp e áudios)

- **`chegou export de conversa do WhatsApp`** — a pasta exportada do celular
  é lacrada inteira com manifesto de hashes e vira uma **cronologia
  unificada**: mensagens e falas na ordem, cada áudio apontando o arquivo de
  origem. A conversa vira prova P## (força indiciária, fragilidade anotada).
- **`degravar a pasta do export` / `degravar o áudio X`** — transcritor
  **100% local** (faster-whisper, modelo small): o áudio do cliente nunca sai
  do computador. Toda degravação sai rotulada: *"degravação de trabalho — não
  substitui perícia nem ata notarial"*; se a autenticidade virar ponto
  controverso, o sistema manda providenciar prova técnica.
- Transcrição pronta que o cliente mandou do celular = RELATO (não é
  degravação do sistema). Gravação de atendimento = consentimento no DIÁRIO
  primeiro.

## 7. Os rituais do tempo

- **Vigia de prazos — TODA sessão, antes de qualquer coisa.** Varre os prazos
  de todos os casos; vencido ou a ≤7 dias = ALERTA no diário + destaque no
  PAINEL. Prazos ativos são espelhados na agenda Google **anonimizados**
  ("SOJ 2026-0002 · PZ01" — nunca nomes de partes).
- **Revalidação mensal da biblioteca.** Na 1ª sessão do mês o vigia lembra:
  verbetes vencidos são reverificados NA FONTE, com a lista de casos afetados.
- **Relatório mensal** — retrato do mês: casos, prazos, gates reprovados e
  por quê, decisões, pendências, estimativa de horas.
- **Radar de verbetes** no PAINEL: o que vence nos próximos 15 dias.

## 8. O conhecimento do escritório (o que se acumula)

- **BASE_LEGAL/** — verbete por dispositivo: texto literal, fonte, data,
  situação, validade. O trabalho de verificação é pago UMA vez por período,
  não por caso.
- **MODULOS/** — por área: árvore de praxe decisória (Tier A/B, com fontes),
  decisões reservadas a você, checklist documental, anti-erro fatal, teses
  **com antíteses** ("nunca usar" — ex.: tese morta, súmula inaplicável) e
  template de peça. A camada de **praxe local** anota o que cada juízo da
  comarca decide — e só vira recomendação com 3+ amostras do MESMO juízo
  (local divergindo do nacional = sempre decisão sua).
- **ACERVO/** — modelos de referência com curadoria (ficha M-NN). Regra de
  ferro: modelo empresta **estilo e técnica, nunca lei** — citação só entra
  com verbete válido. Anonimização na entrada; autos sigilosos são recusados.
- **Ciclo de colheita** — ao protocolar/encerrar, o sistema propõe os
  aprendizados do caso (1 página). **Captura é automática; promoção ao
  módulo só com a sua ratificação.**

## 9. Quem decide o quê

O sistema decide o TÉCNICO com praxe estabelecida (Tier A), sempre
registrando fundamento, alternativa descartada e confiança. O que é **seu**
(Tier B e reservadas): quantum fora do padrão, momento do protocolo,
recorrer ou não, acordo, tutela arriscada — e a palavra final sobre proposta
de colaborador. Você não é consultado a cada detalhe: **ratifica em bloco
nos portões**, com veto pontual. Irredutível: a revisão final e a assinatura
— peça só sai com a sua declaração de revisão humana integral no DIÁRIO.

## 10. Dinheiro do caso

Bloco `financeiro` no CASO.yaml: contrato de honorários (fixo, percentual,
êxito, misto ou pro bono), custas e recebimentos. Contrato assinado é
pendência padrão de caso novo, mas **não trava protocolo** (regularizável em
qualquer fase). A view FINANCEIRO.md mostra o caso; o PAINEL soma o
escritório. Cada caso também tem a `fase_processual` (pré-protocolo →
postulatória → instrutória → decisória → recursal → cumprimento →
encerrado), que os gatilhos do roteador atualizam sozinhos.

## 11. Os 17 comandos (referência rápida)

Você fala em português; a tabela existe só para você saber o que há.

| Programa | O que faz | Você diz… |
|---|---|---|
| `novo_caso.py` | Cria a árvore do caso | "novo caso da fulana" |
| `receber_documento.py` | Porta única com roteador de tipos | "chegou … do caso X" |
| `receber_whatsapp.py` | Conversa de WhatsApp → cronologia lacrada | "chegou export de conversa" |
| `degravar.py` | Transcritor 100% local | "degrava o áudio / a pasta" |
| `anexar_autos.py` | Motor de autos: índice + plano + cache | "anexar autos do caso X" |
| `importar_caso.py` | Porta de importação (confiança zero) | "importar caso trabalhado" |
| `absorver_versao.py` | Porta de retorno da peça | "absorver minha versão" |
| `diff_pecas.py` | Compara duas versões da peça | "diff da v02 com a v03" |
| `gerar_views.py` | Regenera relatórios e PAINEL | (automático) |
| `gate_check.py` | Portões G1/G2/G3 | "rodar o G2 da fulana" |
| `preparar_protocolo.py` | Pacote final de protocolo | "preparar protocolo" |
| `preparar_audiencia.py` | Pasta + roteiro de audiência | "preparar audiência" |
| `vigia_prazos.py` | Vigia de prazos (toda sessão) | (automático; "vigia") |
| `revalidar_biblioteca.py` | Ritual mensal da BASE_LEGAL | (o vigia lembra) |
| `colher_aprendizados.py` | Colheita de aprendizados | (automática no protocolo) |
| `guardar_modelo.py` | Entrada curada no Acervo | "guardar modelo" |
| `relatorio_mensal.py` | Retrato do mês | "relatório do mês" |

E os modos de trabalho sobre a peça: **"revisar peça"**, **"juiz rigoroso na
vNN"**, **"adversário contra a vNN"** — diagnósticos objetivos que não tocam
a peça; melhoria só entra com proposta + diff + sua aprovação.

## 12. Git e backup (as redes de segurança)

- **Git** fotografa a pasta inteira a cada portão e a cada entrega —
  automático. Prova o que existia em cada momento e recupera qualquer estado.
- **Nuvem** (OneDrive/Drive) mantém cópia contínua fora do computador.
- O transcritor e o OCR rodam **dentro da sua máquina**: áudio e página de
  processo não saem daqui. Em serviços externos (agenda), só id do caso e
  número do prazo — nunca nomes de partes.

## 13. O laboratório

`CASOS/TESTE_FICTICIO` é o caso-laboratório PERMANENTE. **Qualquer script
alterado roda primeiro nele** — foi assim que se pegou, antes de chegar a
caso real: gate lendo texto errado (4 vezes), porta única quebrando por um
símbolo de porcentagem, fatiador de autos fragmentando peças, dedupe
guardando o nome errado. `CASOS/TESTE_IMPORTACAO` é o fixture da porta de
importação (mantê-lo ou apagá-lo: decisão sua, pendente).

## 14. Se você se perder

Abra o Claude Code nesta pasta e diga: **"status do escritório"** ou
**"status do caso FULANO"**. O sistema explica onde cada caso está e o que
falta. Na dúvida sobre qualquer comportamento, a regra está no
`SOJ_BLUEPRINT_v1.md` — e se o blueprint e a prática divergirem, o blueprint
manda e a divergência é bug para o laboratório.
