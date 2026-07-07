# MANUAL DO OPERADOR
## SOJ — Sistema Operacional Jurídico · Nascimento Advocacia

**2ª edição · Versão do sistema: Blueprint v1.10 · Julho de 2026**

Escrito para que qualquer pessoa — estagiário, secretária ou cidadão sem
formação jurídica — consiga entender, operar e AUDITAR o sistema.

[SUMARIO]

---

# PARTE I — ENTENDER O SISTEMA

## 1. O que é o SOJ, em uma página

O SOJ não é um programa que se instala. Ele é três coisas somadas: (1) uma pasta comum no computador do escritório, chamada NASCIMENTO, organizada segundo regras rígidas; (2) um conjunto de regras escritas dentro dessa pasta, que definem o que pode e o que não pode ser feito; e (3) uma inteligência artificial (o Claude) que trabalha dentro dessa pasta obedecendo a essas regras — lendo, escrevendo, conferindo e organizando, sempre por comandos em português.

A melhor analogia é um escritório físico bem administrado. Existe o arquivo lacrado onde ficam os documentos originais dos clientes — e, desde esta edição, cada documento entra com uma impressão digital eletrônica (o "hash"), que prova para sempre que ninguém alterou um byte. Existe o prontuário de cada caso. Existe o livro de atas, em páginas costuradas que não se arrancam — e agora cada entrada diz também QUEM fez: o advogado, o sistema ou um colaborador. Existe a biblioteca com a legislação conferida na fonte. Existem portões de qualidade que travam o trabalho malfeito. E existe um estagiário sênior incansável — a IA — que faz o trabalho pesado, inclusive tarefas que antes exigiam serviços externos: transcrever áudios e ler páginas digitalizadas de processos acontecem dentro do computador do escritório, sem que nenhum dado de cliente saia da máquina.

O objetivo continua um só: transformar a entrada bagunçada — a pasta do cliente, a conversa de WhatsApp, os autos baixados do PJe, até a minuta de um colaborador — no melhor trabalho jurídico possível, com cada afirmação rastreável até uma prova, cada lei conferida na fonte oficial, cada decisão registrada com autor e justificativa, e nada protocolado sem revisão humana.

## 2. Para quem é este manual e como lê-lo

Este manual foi escrito para qualquer pessoa: o advogado titular, um estagiário no primeiro dia, uma secretária, ou um auditor externo sem formação jurídica. Ele não pressupõe conhecimento de Direito nem de informática além do básico.

Parte I (Entender) explica o que cada peça do sistema é e por que existe. Leia uma vez, inteira. Parte II (Usar) é o manual de operação do dia a dia. Parte III (Auditar) ensina a conferir se o sistema está dizendo a verdade — oito testes que qualquer pessoa executa em minutos. Parte IV (Futuro) mostra o que a 1ª edição prometia e já foi entregue, o que permanece no radar, e o glossário.

**O que mudou da 1ª para a 2ª edição.** A 1ª edição descrevia o sistema do Blueprint v1.7. De lá para cá o sistema ganhou, em cinco ondas de expansão auditadas uma a uma: o painel financeiro e o ciclo de vida processual na ficha (Onda 1); o relatório mensal, a preparação de audiências e os gatilhos automáticos de fase (Onda 2); os módulos de consumidor (Águas do Pará) e bancário (defesa em execução de CCB), os esqueletos de trabalhista e previdenciário e a camada de praxe local (Onda 3); o motor de mídia — conversas de WhatsApp como prova, transcritor de áudio 100% local e cadeia de custódia com hash em todo original (Onda 4); e o motor de autos — processos inteiros baixados do PJe viram índice com plano de leitura orçado (Onda 5). Fora das ondas, o sistema ganhou a porta de importação (trabalho de colaborador entra com confiança zero) e a governança de autoria (toda entrada e decisão registra a origem).

## 3. A ideia inteira em 60 segundos

O cliente chega e entrega documentos e uma história. Você joga tudo, do jeito que veio, numa pasta com o nome dele e diz: "novo caso". O sistema lacra os originais com impressão digital, cria cópias organizadas, monta a ficha do caso (fatos, provas, pedidos, prazos, pendências — tudo etiquetado), identifica sozinho a área do Direito e escreve a história limpa. Um portão de inspeção confere se a entrada está completa. Depois o sistema monta a estratégia — simulando o advogado adversário e um juiz rigoroso —, toma as decisões técnicas pela praxe (sempre com justificativa escrita) e espera você ratificar em uma página. Com seu "ok", escreve a petição a partir de um molde testado, com cada parágrafo etiquetado à prova que o sustenta e cada lei conferida na fonte oficial. Um último portão só abre com tudo verde — e o último item verde é a sua leitura e assinatura. A peça vira um Word no timbrado, pronta para o protocolo. Tudo ficou registrado num diário que não se apaga, com o autor de cada ato; o que o caso ensinou é colhido para os próximos.

E se a entrada não for uma pasta de cliente? O sistema tem portas para tudo: a conversa de WhatsApp vira cronologia lacrada com as falas degravadas; os autos de um processo em andamento viram índice e plano de leitura; a minuta pronta de um colaborador entra por engenharia reversa, com cada afirmação e cada citação desconfiadas por padrão.

## 4. Os sete princípios (as leis da casa)

Tudo no SOJ deriva de sete princípios. Quando houver dúvida sobre "como fazer", a resposta é sempre o princípio.

1. **Dados + visões, não arquivos.** Cada informação vive em UM lugar (a ficha do caso). Painéis, listas e quadros são impressos automaticamente a partir da ficha, como um extrato bancário. Se um painel está errado, não se rabisca o painel: corrige-se a conta (a ficha) e imprime-se de novo.

2. **Escrever uma vez, referenciar sempre.** Fatos, provas, pedidos, partes, prazos e pendências ganham etiquetas fixas (F01, P01, PED01, PT01, PZ01, PEN01) — e agora também instrumentais (INS01), propostas de colaborador (PC01) e fatias de autos com folhas ("fls. 24-25"). Todo o resto aponta para as etiquetas.

3. **O que é histórico só cresce, nunca se apaga.** O diário é um livro de atas: entrada errada corrige-se com entrada nova que cita a antiga. E cada entrada registra a origem — titular, sistema ou colaborador.

4. **Portões executáveis, não opiniões.** "O caso está pronto?" não é um parecer: é um checklist objetivo. Reprovado, o caminho trava e sai a lista exata do que falta. Os portões leem campos da ficha, nunca interpretam frases — regra escrita com o sangue de quatro falsos positivos nos testes.

5. **Efêmero não é permanente.** Rascunhos, roteiros e o texto extraído dos autos vivem em pasta própria e podem ser apagados sem perda: são regeneráveis.

6. **Verificação com prazo de validade.** Nenhuma lei entra numa peça "de memória" — nem vinda de modelo, nem da sua caneta, nem da minuta de um colaborador. Texto literal, fonte oficial, data e validade. Venceu, reconfere.

7. **Um núcleo, vários módulos.** O núcleo (ficha, diário, portões, painéis, portas) é igual para qualquer área. O que muda é o livro de receitas de cada área: o módulo.

## 5. O mapa do escritório digital (pasta por pasta)

Tudo vive dentro de NASCIMENTO, no computador do escritório (com cópia automática na nuvem). A coluna "quem mexe" é a base da auditoria.

| Pasta / arquivo | O que é | Quem mexe |
|---|---|---|
| LEIA-ME.md | Explicação em linguagem simples (versão curta deste manual, 2ª ed.) | Sistema |
| PAINEL.md | Visão geral de TODOS os casos: fase, portão, prazos, financeiro, alertas | Ninguém (é gerado) |
| CLAUDE.md | As instruções que a IA lê automaticamente em toda sessão | Sistema, com aval do advogado |
| SOJ_BLUEPRINT_v1.md | A planta do sistema (v1.10) — quem manda em caso de dúvida | Advogado (edita o corpo) |
| ESCRITORIO/ADVOGADO.md | Dados profissionais do advogado usados nas peças | Advogado |
| ESCRITORIO/BASE_LEGAL/ | A biblioteca de leis e julgados VERIFICADOS na fonte, com validade | Sistema (verbete só entra verificado) |
| ESCRITORIO/ACERVO/ | Modelos de referência anonimizados, com ficha de curadoria (M-01…) | Sistema, a pedido do advogado |
| ESCRITORIO/MODULOS/ | Os livros de receitas: família (completo), consumidor_aguas, bancario_ccb, esqueletos trabalhista/previdenciário | Sistema, só com ratificação |
| ESCRITORIO/MODELOS/ | Formulários-modelo da ficha e do diário | Sistema |
| ESCRITORIO/RELATORIOS/ | O retrato mensal do escritório (um arquivo por mês) | Ninguém (é gerado) |
| ESCRITORIO/scripts/ | Os 17 robôs que operam o sistema | Sistema (toda alteração testa no laboratório antes) |
| CASOS/NOME DO CLIENTE/ | A pasta de cada caso (anatomia no capítulo 6) | Sistema + advogado, conforme as regras |
| CASOS/TESTE_FICTICIO/ | O caso-laboratório permanente (boneco de crash-test) | Sistema (nunca apagar) |
| CASOS/TESTE_IMPORTACAO/ | O laboratório da porta de importação (caso fictício de colaborador) | Sistema |

Fora da pasta (de propósito, para não inflar a nuvem): o motor do transcritor de áudio e o modelo de reconhecimento de voz vivem em área local do computador; o OCR é o do próprio Windows. Nenhum dos dois manda dados para fora.

## 6. A anatomia de um caso (arquivo por arquivo)

Abra qualquer pasta de cliente e você encontrará sempre a mesma estrutura:

**00_originais/ — o saco de evidências lacrado.** Os documentos exatamente como chegaram. Ninguém toca, nunca. Novidade da 2ª edição: todo original ganha, na entrada, a sua impressão digital SHA-256 anotada na ficha — a cadeia de custódia. Exports de WhatsApp e autos de processo entram com um manifesto: a lista de cada arquivo com o seu hash.

**01_documentos/ — as cópias de trabalho.** Renomeadas de forma legível: DOC-01_CERTIDAO…, DOC-02…

**CASO.yaml — a FICHA (o coração).** As partes (PT01…); os fatos (F01…) com selo de honestidade — provado, alegado, controverso, alegado pelo adversário — sendo que um fato pode agora ser provado pelos próprios autos anexados (campo "fonte_autos: fls. X-Y"); as provas (P01…); os **instrumentais** (INS01… — procuração assinada, RG, contrato de honorários, declaração de hipossuficiência: documentos que provam representação, não fato); os pedidos (PED01…); os prazos (PZ01…); as pendências (PEN01…); o **financeiro** (contrato de honorários, custas, recebimentos); as **audiências**; a **fase processual** (pré-protocolo → postulatória → instrutória → decisória → recursal → cumprimento → encerrado), que os gatilhos do roteador atualizam sozinhos; as **propostas de colaborador** (PC01… — aguardando a sua ratificação); o bloco **autos** (o índice e o cache de leitura do processo anexado); e o estado dos portões.

**DIARIO.md — o livro de atas.** Entradas numeradas, datadas e com **origem** (titular / sistema / colaborador). Decisão que não está no diário não existe.

**INTAKE.md e ESTRATEGIA.md** — a história e o plano de batalha, com a simulação do adversário e o juiz rigoroso.

**MINUTA_v01, v02… — o produto.** Versões que nunca se sobrescrevem, cada parágrafo etiquetado. Minuta importada de colaborador nasce com um aviso no topo: "confiança zero — nada aqui foi verificado ainda".

**AUDIENCIAS/** — uma pasta por audiência, com o roteiro (perguntas por testemunha, pontos de ataque, provas a exibir, logística) preparado para a SUA revisão.

**_views/ — os painéis impressos.** STATUS, rastreabilidade, rol de documentos, checklist do cliente, pendências, resumo de decisões, FINANCEIRO — e os novos: **AUTOS_INDICE** (o mapa do processo anexado, com o plano de leitura e o cache) e **REVISAO_COLABORADOR** (o raio-X da peça importada). Se está em _views, foi gerado: editar à mão é violação.

**_efemeros/ — a bancada de rascunhos.** Inclui o texto extraído dos autos (regenerável de graça) e os rascunhos vindos de importação.

**PROTOCOLO/ — o pacote final.**

## 7. Quem decide o quê (D11 e a governança de autoria)

O sistema decide as questões técnico-jurídicas como um advogado sênior decidiria, aplicando a árvore de decisão do módulo, e registra cada decisão com justificativa, alternativa descartada e grau de confiança.

**Nível A (praxe pacífica):** o sistema decide e segue. Você lê depois o resumo de decisões (1 página) e ratifica em bloco, com veto pontual.

**Nível B (alta consequência):** o sistema decide, recomenda e espera o "ok". Exemplos: prisão civil, quantum fora do padrão, protocolar com pendência, recorrer ou não, praxe local divergindo da nacional.

**A novidade — governança de autoria:** toda entrada do diário e toda decisão agora registram QUEM originou: o titular, o sistema ou um colaborador nominado. E vale uma regra de ferro: **nada que veio de colaborador vira decisão sem a ratificação do titular** — as escolhas embutidas numa minuta importada (percentual, foro, tutela) viram "propostas de colaborador" (PC01…) que ficam paradas aguardando o seu carimbo, e o portão G2 trava enquanto houver proposta pendente.

O irredutível continua o mesmo: a peça sai com a sua assinatura e sob a sua responsabilidade perante a OAB. O sistema é autossuficiente até a porta do protocolo; a porta é sua.

## 8. Os três portões (G1, G2 e G3)

Portão é um checklist objetivo. Reprovado = caminho travado + lista exata do que falta. Todo resultado vira entrada no diário e fotografia no histórico. Os portões leem campos da ficha, nunca interpretam frases.

**G1 — Entrada completa (7 itens):** originais lacrados e todo documento registrado — como prova OU como instrumental; partes qualificadas ou com pendência; fatos com selo honesto (provado exige prova P## ou folha dos autos); prazos identificados ou declaração de "sem prazos"; pendências críticas com responsável e trava; complexidade e módulo definidos; checklist do cliente gerado. **Em modo defesa, o item zero vem antes de tudo: o prazo de resposta identificado, calculado e no vigia.**

**G2 — Pronto para escrever (7 itens):** estratégia completa com simulação adversária e juiz rigoroso; decisões com justificativa/alternativa/confiança; nível B com "ok" expresso; ratificação em bloco; todo pedido com fato vinculado; nenhuma pendência travando; riscos com contramedida ou aceite registrado; e **nenhuma proposta de colaborador aguardando ratificação**.

**G3 — Pronto para protocolar (9 itens, o mais rigoroso):** zero marcadores pendentes; etiquetas válidas; circuito pedido↔fato↔prova↔parágrafo↔lei fechado; toda lei dentro da validade e o núcleo reconferido na véspera; anti-erro fatal da área executado; rol de documentos batendo com a pasta e a peça; checagem cruzada — todo valor e percentual da peça bate com a decisão registrada que o originou (o valor da causa é conferido mecanicamente); nenhuma pendência bloqueadora; e a revisão humana integral assinada.

## 9. Os guardiões automáticos

**O vigia de prazos.** Toda sessão, sobre qualquer caso, começa varrendo os prazos de todos os casos. Vencido ou a 7 dias = alerta no diário + destaque no PAINEL. Prazos são espelhados no Google Calendar com rótulos anonimizados ("SOJ 2026-0002 · PZ01") — nunca nomes de partes.

**A cadeia de custódia (novo).** Todo original recebe o hash SHA-256 na entrada. Auditar é trivial: recalcule a impressão digital do arquivo e compare com a ficha — se um byte tiver mudado, o hash denuncia. Conversas de WhatsApp e autos têm manifesto arquivo por arquivo.

**O ritual mensal da biblioteca (novo).** Na primeira sessão do mês, o vigia lembra: verbetes vencidos são reverificados NA FONTE, com a lista dos casos ativos afetados por cada um. O PAINEL ainda mostra o radar do que vence nos próximos 15 dias.

**O git — a máquina de fotografias.** A cada portão e a cada entrega, uma foto inviolável e datada da pasta inteira. Qualquer adulteração de registro antigo aparece na comparação entre fotos.

**A nuvem (OneDrive).** Cópia contínua. Regra de ouro: uma pasta, uma nuvem só.

**O laboratório (TESTE_FICTICIO).** Todo script alterado roda nele antes de tocar caso real. O placar da casa até aqui: quatro falsos positivos de portão, um defeito que derrubava a porta única, um fatiador de autos que fragmentava peças e um deduplicador que guardava o nome errado — todos pegos no boneco, nenhum em caso real.

## 10. A biblioteca do escritório

**BASE_LEGAL — a lei conferida.** Um verbete por dispositivo: texto literal + fonte oficial + data + validade (90/30 dias) + situação + os casos que citam. Cada área tem a seção "antíteses — nunca usar": o conhecimento negativo (revogados, redações superadas, fontes inexistentes). A minuta de colaborador também passa por aqui: a varredura da porta de importação marca na hora o que é lei morta.

**ACERVO — os modelos de inspiração.** Anonimizados na entrada, com ficha de curadoria. Regra de ferro: modelo é professor de estilo e técnica, nunca de lei. Autos sigilosos são recusados.

**MÓDULOS — os livros de receitas.** Família: completo (árvore com 11 ramos, 9 decisões reservadas, anti-erro fatal de véspera, checklist com as 7 perguntas do atendimento, teses T1–T8 com antíteses, molde de peça). Consumidor/Águas do Pará: negativação indevida no JEC, com as teses e antíteses herdadas do trabalho validado. Bancário/CCB: defesa em execução movida por cooperativas — módulo que já NASCE em modo defesa (caso novo da área nasce como réu). Trabalhista e previdenciário: esqueletos de propósito — nascem do primeiro caso real.

**A camada de praxe local (novo).** Cada sentença e decisão dos próprios processos alimenta anotações por juízo: o que o juízo da comarca costuma deferir, em que patamar. Uma anotação só vira recomendação com 3 ou mais amostras consistentes do MESMO juízo — e praxe local divergindo da nacional é sempre decisão sua (nível B).

---

# PARTE II — MANUAL DE USO (o dia a dia)

## 11. A vida de um caso, do início ao fim

Exemplo com uma cliente fictícia, dona Maria, que quer cobrar pensão do ex-companheiro.

1. **Atendimento.** Converse normalmente. Anote a história num arquivo de texto ou Word. Se preferir gravar, registre o consentimento dela primeiro — vira entrada no diário — e o transcritor local converte o áudio em texto dentro do computador.
2. **A pasta bagunçada.** Crie CASOS/MARIA e jogue tudo dentro, como veio. A bagunça é sua, a ordem é do sistema.
3. **"Novo caso da Maria."** O sistema lacra os originais (com hash), cria as cópias DOC-01…, monta a ficha — já com a pendência padrão do contrato de honorários (que NÃO trava protocolo: regulariza-se em qualquer fase) —, identifica área e módulo, escreve a história limpa e gera o checklist para o WhatsApp da cliente.
4. **Portão 1.** Reprovou? Sai a lista exata. Aprovou? Estratégia.
5. **Estratégia e decisões.** Diagnóstico, simulação da defesa, juiz rigoroso, decisões pela árvore — nível B chega para você com recomendação.
6. **Ratificação em bloco.** Leia o resumo (1 página) e diga "ratifico".
7. **Portão 2 e minuta.** "Gerar minuta": a peça nasce do molde, ~70% pronta, etiquetada e com leis verificadas.
8. **Melhorar a peça** (capítulo 17) — ou editar você mesmo e devolver ("absorver minha versão").
9. **Documentos no meio do caminho.** "Chegou o extrato da Maria" — a corrente inteira roda sozinha: lacra com hash, registra, muda o fato para provado, baixa a pendência, anota no diário, reimprime os painéis, avisa o que ainda trava.
10. **Véspera.** "Preparar protocolo": anti-erro fatal + conferência final (com a checagem cruzada peça↔decisões) + relatório de revisão.
11. **A assinatura.** Leia a peça inteira — o único item que nenhum robô audita por você. Declare a revisão; o G3 fecha e o Word no timbrado é gerado.
12. **Protocolo.** Ato físico seu, com certificado digital. Volte e diga: "protocolado, processo nº X" — o sistema registra o evento, cadastra os prazos reais no vigia e no Calendar, muda a fase processual e dispara a primeira colheita.
13. **Vida do processo.** Toda novidade entra pela mesma porta. Decisão judicial? Prazo extraído ANTES de qualquer análise. Contestação chegou? O sistema propõe a réplica e muda a fase. Sentença? Propõe o recurso (decisão sua) ou o cumprimento. Ata de audiência? Baixa a audiência e colhe os aprendizados.
14. **Colheita.** O que o caso ensinou vira proposta de 1 página. Você ratifica — o próximo caso nasce sabendo.

## 12. Modo defesa (quando o cliente é o réu)

Se o que chega é uma peça adversária — a inicial de uma execução de cooperativa, por exemplo — o sistema entra em modo defesa:

1. **O prazo vem primeiro.** Antes de qualquer análise: prazo de resposta identificado, calculado, no vigia e no Calendar. Prazo de defesa é fatal; tudo o mais espera. O G1 ganha um item zero que trava tudo sem isso.
2. **As alegações do adversário entram com selo próprio** (alegado pelo adversário / controverso) e o sistema faz a análise adversarial: as teses deles, as fraquezas deles, os pontos de ataque. Toda lei citada pelo adversário também passa pela BASE_LEGAL — adversário também cita lei velha.
3. **O produto é a peça de defesa do módulo**, e a simulação se inverte: simula-se a réplica do autor contra a sua defesa.

O módulo bancário/CCB já nasce assim: caso novo da área entra automaticamente como réu/executado.

## 13. A porta de importação (trabalho de colaborador)

Um sócio ou estagiário te entrega um caso pré-trabalhado: minuta pronta, provas, procuração. O que fazer com isso? A resposta errada é "adotar a peça". A resposta do sistema é **importar com confiança zero**: aproveita-se o trabalho, desconfia-se de cada afirmação.

Diga **"importar caso trabalhado: [pasta]"** e o sistema:

1. **Deduplica por hash** — arquivos repetidos ("comprovante (1).pdf") são detectados pela impressão digital; fica o melhor nome, as cópias ficam lacradas mas fora da ficha.
2. **Separa provas de instrumentais.** Procuração ASSINADA, RG/CNH, contrato de honorários e declaração de hipossuficiência viram a classe INS## (provam representação, não fato). A "procuração revisada" em Word — rascunho, não assinada — vai para os efêmeros.
3. **Se houver DUAS minutas na pasta, o sistema PARA sem criar nada** e pergunta: são versões da mesma ação (qual vale?) ou ações distintas (importar separado)?
4. **A minuta vira MINUTA_v01 com aviso de confiança zero** e passa pela engenharia reversa: fatos afirmados viram F## cruzados com as provas anexas — afirmação sem prova fica "alegado" + pendência; pedidos viram PED##; TODA citação de lei é conferida na BASE_LEGAL (a varredura marca na hora: verificada, vencida, NÃO verificada ou REVOGADA — lei morta).
5. **As decisões embutidas na peça** (quantum, foro, tutelas) viram propostas PC## aguardando a sua ratificação. O G2 trava até você decidir cada uma.
6. **Sai o Relatório de Revisão do Colaborador** (_views/REVISAO_COLABORADOR.md): o que está bom — com crédito nominal —, o que cita lei morta, o que afirma sem prova, o juiz rigoroso e o adversário contra a peça dele. É, na prática, a avaliação de desempenho do colaborador, feita em minutos e por escrito.

No teste de aprovação, o sistema pegou: a citação dos artigos revogados da Lei de Alimentos, o fato sem nenhuma prova anexa, a contradição de pedir desconto em folha de um réu descrito como autônomo — e deu o crédito: o valor da causa do colaborador estava matematicamente exato.

## 14. O motor de mídia (WhatsApp, áudios e o transcritor local)

**Conversa de WhatsApp como prova.** Exporte a conversa no celular ("Exportar conversa", com mídias), jogue a pasta no computador e diga **"chegou export de conversa do WhatsApp"**. O sistema lacra TODOS os arquivos com manifesto de hashes e monta a **cronologia unificada**: mensagens e áudios na ordem em que aconteceram, cada fala degravada apontando o arquivo de origem. A conversa vira prova P## — com a fragilidade anotada com honestidade: prova eletrônica é indiciária; se a autenticidade virar ponto controverso, o sistema manda providenciar perícia ou ata notarial.

**O transcritor local.** Instalado com o "ok" do advogado após relatório técnico: roda 100% dentro do computador — nenhum áudio de cliente sai da máquina. Comandos: **"degravar a pasta do export"** (antes de receber a conversa — cria as degravações que entram inline na cronologia) e **"degravar o áudio X"** (atendimento gravado, áudio avulso).

**As três regras da mídia:** (1) toda degravação sai rotulada — *"degravação de trabalho — não substitui perícia nem ata notarial"*; (2) gravação de atendimento exige consentimento do cliente registrado no diário ANTES; (3) transcrição pronta que o cliente mandou do celular entra como RELATO dele, não como degravação do sistema.

## 15. O motor de autos (o processo que chega de fora)

Você assume um caso em andamento e baixa os autos do PJe: 60, 200, 500 páginas. Ler tudo com inteligência artificial custaria caro — e reler toda sessão custaria sempre. O motor de autos resolve com uma regra: **paga-se a leitura UMA vez, e só do que vale a pena.**

Diga **"anexar autos do caso X"** e o sistema:

1. **Lacra o PDF** (e as mídias que vierem junto — gravação de audiência, por exemplo) com manifesto de hashes.
2. **Extrai o texto de graça** — por script, sem gastar um centavo de IA. Páginas digitalizadas (pura imagem) passam pelo **OCR local do próprio Windows, em português** — nada sai da máquina.
3. **Fatia os autos por documento** (petição inicial, contestação, despacho, sentença, certidões…) e gera o **índice** (_views/AUTOS_INDICE.md): uma linha por peça, com tipo, folhas, data e custo estimado de leitura.
4. **Apresenta o plano de leitura com orçamento** — a pirâmide: peças das partes, decisões e atas se leem **integrais**; certidões de praxe, ARs e guias de custas **nunca** (lixo processual não consome orçamento); todo o resto fica **sob demanda**. Autos com mais de 100 folhas: é decisão sua — **nada é lido antes do seu "ok" ao plano**, como um orçamento de obra.
5. **Destila UMA vez.** O que foi lido vira registro na ficha com referência por folha: linha do tempo do processo, fatos ("o réu confessou renda de R$ 3-4 mil em audiência — fls. 24-25"), teses de cada parte, e os prazos de decisões e sentenças direto no vigia — prazo antes de tudo, como sempre.
6. **Nunca relê.** O que foi destilado fica marcado no índice (o cache). Reanexar o mesmo PDF responde "[CACHE] — nada foi re-extraído nem relido". Sessões futuras trabalham com a ficha e o índice, jamais reabrem o PDF. É a diferença entre pagar a leitura dos autos uma vez e pagá-la toda sessão, para sempre.

## 16. Dicionário de comandos

Todos os comandos se falam em português normal. A grafia exata não importa — o sentido importa.

| Comando | O que faz | Quando usar |
|---|---|---|
| "novo caso da [cliente]" | Pasta bagunçada → caso estruturado: lacra com hash, renomeia, ficha, história, checklist, G1 | Todo caso novo |
| "chegou [documento] do caso [X]" | A porta única com roteador: lacra, registra, atualiza fatos/pendências/fase, reimprime painéis; decisão judicial = prazo primeiro | Sempre que QUALQUER coisa chegar |
| "chegou export de conversa do WhatsApp" | Conversa vira cronologia unificada lacrada com manifesto de hashes + prova P## | Conversa como prova |
| "degravar o áudio X / a pasta do export" | Transcritor 100% local; degravação rotulada | Áudio de WhatsApp; atendimento gravado |
| "anexar autos do caso [X]" | Motor de autos: lacre, extração, OCR local, índice, plano com orçamento, cache | Assumiu processo em andamento |
| "importar caso trabalhado: [pasta]" | Porta de importação com confiança zero + Relatório de Revisão do Colaborador | Sócio/estagiário entregou caso pronto |
| "status do caso [X]" / "status do escritório" | Painel do caso ou PAINEL geral | Início do dia |
| "contextualizar caso [X]" | A IA lê ficha + fim do diário e entra no caso | Início de sessão sobre um caso |
| "rodar G1 / G2 / G3" | Executa o portão | Fim de etapa |
| "registrar decisão: …" | Grava decisão SUA no diário | Sempre que decidir algo |
| "ratifico o resumo de decisões" | Ratificação em bloco (nível A) | Depois de ler o resumo |
| "ratifico/veto a proposta PC01" | Decide proposta de colaborador (destrava o G2) | Após importação |
| "gerar minuta" | Peça nasce do molde, etiquetada | Após G2 |
| "revisar peça" (+ "juiz rigoroso na vNN", "adversário contra a vNN") | Ciclo de melhoria: diagnóstico → reescrita → comparativo | Quando a peça pode melhorar |
| "absorver minha versão da peça" | Porta de retorno: compara, classifica, verifica, reetiqueta, re-roda portão | Sempre que a SUA caneta melhorar a peça |
| "guardar modelo: [arquivo]" | Anonimiza, analisa e arquiva no Acervo (M-NN) | Peça/decisão inspiradora |
| "preparar audiência do caso [X]" | Pasta da audiência + roteiro para sua revisão + prazo no vigia | Audiência designada |
| "preparar protocolo" | Anti-erro + conferência final + relatório; após assinatura, Word no timbrado | Véspera |
| "protocolado, processo nº [N]" | Evento + prazos reais + fase + colheita | Logo após o PJe |
| "relatório do mês" | Retrato mensal do escritório | Fim do mês |
| "colher aprendizados / encerrar caso [X]" | Proposta de 1 página do que o caso ensinou | Automático; manual quando quiser |

## 17. Como melhorar uma peça (o ciclo de revisão)

O comando fraco é "melhore a peça" — genérico entra, polimento genérico sai. O ciclo certo tem quatro tempos: **diagnóstico → alvo → reescrita dirigida → comparativo para aprovar.**

**Diagnóstico:** "Rode o juiz rigoroso na v02 e liste o que ele cortaria"; "Vista a toga do advogado do réu e me mostre onde a peça sangra"; "Aponte os 3 parágrafos mais fracos e diga por quê".

**Estilo (liberdade total):** "Reescreva o capítulo da urgência com mais força, mantendo fatos e etiquetas"; "Enxugue 20% sem perder fundamento".

**Substância (passa pelos portões):** "Aprofunde a guarda com a jurisprudência verificada da biblioteca"; "Quero incluir [fato X] — antes de escrever, diga o que isso exige: prova? decisão? verificação?".

**Variantes e o comando de ouro:** "Gere duas versões do capítulo III — sóbria e incisiva"; "Mostre o comparativo da v03 contra a v02"; e o mais poderoso: **"Absorva este parágrafo que EU reescrevi e nivele o resto da peça pelo padrão dele"** — a sua melhor caneta vira a régua da peça inteira.

Formato que sempre funciona: **objetivo + restrição**. Critério de parada: quando o juiz rigoroso e o adversário voltarem magros, a peça está pronta. Toda revisão gera versão nova; melhorias aprovadas viram candidatas de colheita.

## 18. Os ciclos de aprendizado (a catraca)

O sistema fica mais inteligente a cada caso — por um mecanismo de catraca: avança um dente por vez, cada dente só encaixa com um clique humano, nunca desliza para trás. São quatro vias:

1. **A biblioteca acumula sozinha:** verificação paga no caso 2 é usada de graça no caso 15.
2. **A colheita propõe:** decisões viram ramos de árvore, quase-erros viram anti-erro, fontes falsas viram antíteses, melhorias de texto viram o molde novo. Nada é promovido sem ratificação — um erro capturado num caso é um arranhão; promovido ao módulo seria uma epidemia.
3. **A porta de retorno injeta ofício:** sua caneta ensina o molde. Regra de ouro: a versão protocolada é sempre a última que o sistema conhece.
4. **A praxe local acumula resultados (novo):** cada sentença dos próprios processos vira anotação por juízo; com 3+ amostras consistentes do mesmo juízo, vira recomendação calibrada para a comarca. Nenhuma ferramenta de mercado tem isso — é acúmulo puro do escritório.

Detalhe que vale saber: a inteligência artificial em si não aprende — o modelo de amanhã não lembra da conversa de hoje. Quem aprende são os arquivos. O cérebro é alugado; a biblioteca é do escritório.

## 19. O que o sistema NUNCA faz

- Não protocola nada sozinho — o protocolo é ato físico do advogado.
- Não assina, não substitui o advogado, não dispensa a revisão humana integral.
- Não inventa fato: diante de lacuna, para e pergunta. Fato sem prova carrega o selo de "alegado".
- Não cita lei de memória — nem de modelo, nem de colaborador, nem sua.
- Não decide nível B sem "ok", não promove nada ao módulo sem ratificação, e **não transforma proposta de colaborador em decisão sem o carimbo do titular**.
- Não apaga histórico: diário só cresce, versões não se sobrescrevem, originais intocáveis — agora com a impressão digital que prova.
- Não manda dado de cliente para fora: transcrição e OCR rodam NA máquina; agenda e Acervo só trabalham anonimizados.
- **Não grava atendimento sem consentimento registrado antes**, e não apresenta degravação como se fosse perícia — o rótulo é obrigatório.
- **Não lê autos grandes sem orçamento aprovado**: acima de 100 folhas, nada é lido antes do seu "ok" ao plano.
- Não instala nada novo no computador sem avaliar, reportar e receber o seu "ok".

---

# PARTE III — AUDITORIA, PROBLEMAS E SEGURANÇA

## 20. Como auditar o sistema — oito testes que qualquer pessoa faz

Os testes levam de 2 a 10 minutos cada e não exigem formação jurídica. Se todos passarem, o sistema está dizendo a verdade.

1. **O fio da meada (rastreabilidade).** Abra a última minuta, escolha QUALQUER parágrafo que afirme um fato, olhe a etiqueta (ex.: F04 | P11). Abra a ficha: o F04 existe e diz aquilo? A P11 aponta um DOC? O DOC prova mesmo aquilo? Siga até o original lacrado. Falhou = etiqueta órfã ou prova que não prova: pare e apure.

2. **Toda decisão tem ata.** Escolha qualquer número da peça (percentual, valor). Procure no diário a DECISAO que o originou: justificativa, alternativa, confiança, ratificação — e origem. Número "contrabandeado" é violação (e o G3 pega sozinho).

3. **Painel bate com a ficha.** STATUS.md deve ser espelho do CASO.yaml. Divergiu: painéis são gerados — peça "regenerar as views" e compare de novo.

4. **A lei confere na fonte.** Escolha um artigo citado. O verbete tem texto literal, endereço oficial, data dentro da validade? Clique e compare palavra por palavra.

5. **As fotografias não mentem.** "Mostre o histórico de fotos (commits) do caso X." Uma foto por portão, datas coerentes com o diário. Histórico com buraco = apure imediatamente.

6. **O portão reprova quando deve.** Rode o G3 num caso sabidamente incompleto. Portão saudável reprova com lista específica. Aprovação genérica em caso incompleto = portão quebrado.

7. **A impressão digital confere (novo).** Escolha qualquer original lacrado. Peça: "recalcule o hash do arquivo X e compare com a ficha". Os dois códigos devem ser idênticos, caractere por caractere. Divergiu = o arquivo foi alterado depois da entrada — gravíssimo; a cadeia de custódia existe exatamente para isto.

8. **O colaborador não passa sem carimbo (novo).** Num caso importado, confira se existe proposta PC## "aguardando ratificação" e rode o G2: ele DEVE reprovar citando a proposta. Depois confira no diário: as entradas da importação dizem a origem ("colaborador Fulano")? Ratificação sem registro ou proposta que virou decisão sozinha = violação da governança de autoria.

## 21. Sinais de alerta (o que indicaria problema)

- Arquivo em 00_originais com data de modificação posterior à entrada — ou com hash divergente da ficha. Gravíssimo.
- Painel em _views editado à mão.
- Entrada antiga do diário diferente entre duas fotografias do git.
- Citação de lei sem verbete, ou verbete vencido em peça protocolada.
- Etiqueta apontando fato ou prova que não existe.
- Prazo mencionado em texto sem PZ## no vigia.
- Peça protocolada diferente da última versão que o sistema conhece.
- Degravação circulando SEM o rótulo "de trabalho — não substitui perícia".
- Decisão no diário sem origem, ou proposta de colaborador executada sem ratificação.
- O mesmo trecho dos autos sendo relido em sessões diferentes (o cache existe para impedir isso — releitura é desperdício e sinal de defeito).

## 22. Problemas comuns e o que fazer

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| A IA de uma sessão nova "não lembra" do caso | Sessões não têm memória — a memória é a pasta | "Contextualizar caso X" |
| Arquivo "cópia em conflito" na pasta | Duas nuvens ou edição simultânea | UMA nuvem só; peça para reconciliar indicando qual vale |
| Portão reprovou e você discorda | Falta algo mesmo, ou check com defeito | Leia a lista item a item; discordou, teste no LABORATÓRIO |
| Prazo não apareceu no Calendar | Falha no espelhamento | O vigia interno é a fonte da verdade; peça "reespelhar prazos" |
| Documento entrou com tipo errado | Roteador classificou mal | "Reclassificar o DOC-NN como [tipo]" — correção vira entrada nova |
| Quero desfazer mudança na peça | Nada se perde | "Voltar a trabalhar sobre a vNN" |
| Protocolei versão editada por fora | Quebra da regra de ouro | Devolva JÁ por "absorver minha versão" |
| O sistema pediu um dado que você não sabe | Fato que só o cliente tem | Nunca chute: vira pendência + checklist do cliente |
| A degravação veio com erros | Áudio ruim ou modelo pequeno no limite | Confira contra o áudio; se repetir, peça o upgrade do modelo (o sistema propõe, você aprova o download) |
| Página dos autos ficou "OCR pendente" | Imagem ilegível para o OCR | Abra a página no PDF e leia manualmente; anote o conteúdo por "registrar decisão"/nota no diário |
| Import de colaborador PAROU com duas minutas | Proteção proposital | Responda: versões (diga qual vale) ou ações distintas (pastas separadas) |
| Autos novos do mesmo processo (volume 2) | Hash diferente do anexado | O sistema pede sua palavra antes de substituir — fale com o titular |

## 23. Segurança, sigilo e ética

**Sigilo e LGPD.** A pasta contém dados sensíveis — inclusive de menores sob segredo de justiça. Disco criptografado (BitLocker); nuvem com senha forte e duas etapas; nunca colar dados identificados fora do ambiente; agenda e Acervo só anonimizados. **Reforço da 2ª edição: áudio de cliente e página de processo NUNCA saem da máquina** — o transcritor e o OCR são locais por decisão de projeto, não por acaso.

**Prova digital com lastro.** A cadeia de custódia (hash na entrada + manifesto por arquivo + rótulo honesto nas degravações) foi desenhada para o dia em que a parte contrária impugnar a conversa de WhatsApp: o escritório mostra o export lacrado, a impressão digital de cada arquivo e a data de entrada — e sabe, desde o primeiro dia, que degravação de trabalho não substitui perícia.

**Responsabilidade profissional.** A IA prepara; o advogado decide o reservado, ratifica e assina. O diário fundamentado — agora com autor em cada entrada — é a prova documental de supervisão humana: a melhor defesa num questionamento perante a OAB e o antídoto à lógica antilitigância-predatória (Recomendação CNJ 159/2024). Volume aqui é consequência de qualidade replicável, nunca o contrário.

**Backup em três camadas.** Nuvem contínua + fotografias do git + recomenda-se um arquivo frio (zip) mensal fora do computador.

**Disciplina inegociável:** originais intocáveis; diário só cresce; painéis nunca à mão; lei nunca de memória; prazo antes de tudo; laboratório antes de caso real; consentimento antes de gravar; e a leitura final do advogado jamais vira cerimônia.

---

# PARTE IV — O FUTURO DO SISTEMA

## 24. O que a 1ª edição prometia — e o que já foi entregue

A 1ª edição listava doze melhorias futuras. Em uma semana de ondas auditadas, oito saíram do papel:

| Promessa da 1ª edição | Situação |
|---|---|
| Painel financeiro | ENTREGUE (Onda 1) — contrato, custas, recebimentos, visão no PAINEL |
| Higiene automatizada da biblioteca | ENTREGUE (Onda 1) — revalidação mensal com casos afetados |
| Relatório mensal do escritório | ENTREGUE (Onda 2) |
| Preparação de audiência | ENTREGUE (Onda 2) — roteiro para sua revisão + ata pela porta única |
| Ciclo de vida processual | PARCIAL (Onda 2) — gatilhos de fase automáticos; moldes das peças intermediárias nascem do 1º caso que precisar |
| Módulos novos por gatilho | ENTREGUE (Onda 3) — Águas do Pará e CCB adaptados; esqueletos prontos |
| Praxe local calibrada | ENTREGUE na fundação (Onda 3) — camada criada; calibra com 3+ amostras por juízo |
| Atendimento vira RELATO sozinho | ENTREGUE na essência (Onda 4) — transcritor local instalado; falta só virar hábito |
| Publicações/andamentos automáticos | NO RADAR — gatilho: mais de ~10 processos ativos |
| Backup frio com teste de restauração | NO RADAR — zip mensal + ensaio anual |
| Multiusuário com papéis | FUNDAÇÃO PRONTA — a governança de autoria (origem em tudo) e a porta de importação já são o alicerce; papéis formais quando houver equipe |
| Modo consultivo | HORIZONTE — pareceres e contratos, conscientemente fora do alvo atual |

E duas capacidades que a 1ª edição nem sonhava foram entregues por cima: o **motor de autos** (processo de fora vira índice com leitura orçada e cache) e a **cadeia de custódia** com hash em todo original.

## 25. O que permanece no radar

1. **Publicações e andamentos automáticos.** O sistema buscar as intimações no Diário de Justiça eletrônico e alimentar a porta única sozinho — cada publicação virando evento + prazo sem ação humana. Elimina o último risco de prazo por esquecimento. Gatilho: volume acima de ~10 processos ativos.
2. **Moldes das peças intermediárias** (réplica, contrarrazões, apelação, cumprimento) — cada um nasce do primeiro caso que precisar, pela regra de sempre.
3. **Backup frio testado.** Zip mensal fora do computador + um ensaio anual de restauração (backup nunca testado é uma esperança, não um backup).
4. **Multiusuário com papéis formais.** Estagiário opera rotina; decisão, ratificação e assinatura permanecem do advogado. O diário já registra quem fez o quê.
5. **Modo consultivo** (horizonte): pareceres e contratos como módulo próprio.

## 26. Glossário

- **Ficha (CASO.yaml):** o prontuário estruturado do caso — a única fonte da verdade.
- **Diário (DIARIO.md):** livro de atas append-only; cada entrada com data, número e origem.
- **Origem:** quem originou a entrada/decisão — titular, sistema ou colaborador (governança de autoria).
- **View / painel (_views):** documento gerado da ficha. Nunca se edita à mão.
- **Portão (G1/G2/G3):** checklist objetivo que trava o avanço.
- **Etiqueta / tag:** marca invisível ligando parágrafo a fato, prova e lei.
- **Verbete:** lei/julgado verificado na fonte, com data e validade.
- **Antítese:** conhecimento negativo — o que NUNCA usar.
- **Árvore de decisão (praxe):** as regras de decidir da área, com fontes.
- **Praxe local:** anotações por juízo da comarca; vira recomendação com 3+ amostras.
- **Nível A / Nível B:** sistema decide e você ratifica em bloco / espera seu "ok".
- **Porta única:** por onde entra qualquer documento, com o roteador de tipos.
- **Porta de retorno:** devolver ao sistema a peça melhorada pela sua caneta.
- **Porta de importação:** entrada de caso pré-trabalhado por colaborador, com confiança zero.
- **Instrumental (INS##):** documento que prova representação (procuração, RG, honorários, hipossuficiência), não fato.
- **Proposta de colaborador (PC##):** decisão embutida em peça importada, aguardando sua ratificação — trava o G2.
- **Cadeia de custódia / hash:** impressão digital SHA-256 de cada original, anotada na entrada.
- **Manifesto:** a lista de arquivos de um export/autos, cada um com seu hash.
- **Degravação de trabalho:** transcrição local rotulada — não substitui perícia nem ata notarial.
- **Sidecar:** arquivo de texto com a degravação de um áudio, gravado ao lado dele.
- **Fatia:** um documento dos autos (inicial, contestação, sentença…) delimitado por folhas.
- **Plano de leitura com orçamento:** ler integral / nunca ler / sob demanda, com custo estimado — acima de 100 fls., só com seu "ok".
- **Cache de leitura:** o registro do que já foi destilado — nada se relê.
- **fonte_autos:** campo do fato provado pelos próprios autos ("fls. X-Y").
- **Modo defesa:** cliente réu/executado — prazo de resposta primeiro (item zero do G1).
- **Vigia de prazos:** varredura de todos os prazos em toda sessão.
- **Colheita:** proposta do que o caso ensinou, mediante ratificação.
- **Acervo (M-##):** modelos de inspiração anonimizados e curados.
- **Laboratório (TESTE_FICTICIO):** caso falso permanente onde toda mudança é testada antes.
- **Git / fotografia / commit:** retrato inviolável e datado da pasta, a cada portão.
- **Kernel / módulo:** o núcleo igual para todas as áreas / o livro de receitas de cada uma.

## 27. Ficha técnica do sistema

Construído a partir de 04/07/2026 por três camadas que se auditam mutuamente: o advogado (decide e assina), o arquiteto (a planta — Blueprint v1.1 a v1.10) e o construtor (Claude Code, que ergueu e testou tudo dentro da pasta).

Evolução da planta: v1.1 ambiente local; v1.2 contrato da entrada bagunçada; v1.3 autonomia decisória D11; v1.4 obra entregue (Fases 1–4); v1.5 ciclos de mão dupla (colheita e porta de retorno); v1.6 Acervo; v1.7 roteador de tipos e modo defesa; **v1.8 as cinco ondas da expansão F6 aprovadas; v1.9 motores de mídia e de autos especificados; v1.10 porta de importação e governança de autoria** — estas três versões editadas pelo próprio advogado, que assumiu a manutenção da planta.

Placar do laboratório até esta edição: um prazo que o método antigo perdeu, pego no primeiro dia; quatro leis desatualizadas e uma resolução inexistente barradas antes de entrar em peça; quatro falsos positivos de portão que motivaram a regra "portão lê campo, não frase"; um defeito que derrubava a porta única por um símbolo de porcentagem; um fatiador de autos e um deduplicador corrigidos no boneco de teste; e uma peça real levada a nove verificações verdes — a última delas, a assinatura humana.

Dúvidas que este manual não responder: pergunte ao próprio sistema ("explique como funciona [X]") ou consulte o Blueprint v1.10, que é a planta completa.
