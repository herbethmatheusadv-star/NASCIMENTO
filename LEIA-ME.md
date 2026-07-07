# LEIA-ME — Sistema Operacional Jurídico NASCIMENTO (SOJ)

> Este arquivo explica o sistema em linguagem simples, para quem não é
> programador. A especificação técnica completa está em `SOJ_BLUEPRINT_v1.md`.

---

## O que é isto?

Esta pasta é o seu escritório digital. Ela funciona com uma regra de ouro:

**Cada informação vive em UM único lugar. Todo o resto é gerado automaticamente.**

No sistema antigo, o mesmo dado (um fato, uma prova, um prazo) era copiado em
vários arquivos — e quando um mudava, os outros ficavam desatualizados. Aqui
isso não acontece: os dados do caso vivem num único arquivo (`CASO.yaml`), e os
quadros, checklists e relatórios são produzidos por pequenos programas
("scripts") a partir dele. Se um quadro está errado, corrige-se a fonte e
gera-se de novo — nunca se edita o quadro.

## O mapa da pasta

```
NASCIMENTO/
├── LEIA-ME.md          ← você está aqui
├── SOJ_BLUEPRINT_v1.md ← a "lei" do sistema (especificação aprovada)
├── PAINEL.md           ← visão geral de TODOS os casos (gerado automaticamente)
│
├── ESCRITORIO/         ← o que é do escritório, não de um caso específico
│   ├── ADVOGADO.md     ← seus dados profissionais (fonte única da qualificação)
│   ├── BASE_LEGAL/     ← leis e jurisprudência verificadas, com data de validade
│   ├── MODULOS/        ← o "conhecimento" por área: familia, consumidor_aguas,
│   │                     bancario_ccb (defesa nativa) + esqueletos trab./prev.
│   ├── MODELOS/        ← modelos comentados do CASO.yaml e do DIARIO.md
│   └── scripts/        ← os 5 programas que operam o sistema
│
└── CASOS/
    └── NOME_DO_CLIENTE/       ← uma pasta por cliente
        ├── 00_originais/      ← documentos EXATAMENTE como recebidos. NUNCA mexer.
        ├── 01_documentos/     ← cópias renomeadas (DOC-01, DOC-02…)
        ├── CASO.yaml          ← A FONTE DA VERDADE: partes, fatos, provas, pedidos, prazos, pendências
        ├── DIARIO.md          ← o livro de registro: só se ACRESCENTA, nunca se edita
        ├── INTAKE.md          ← resumo do atendimento (texto)
        ├── ESTRATEGIA.md      ← diagnóstico e estratégia (texto)
        ├── MINUTA_v01.md      ← a petição em construção
        ├── _views/            ← relatórios GERADOS (status, pendências…). Nunca editar.
        ├── _efemeros/         ← rascunhos descartáveis
        └── PROTOCOLO/         ← o pacote final para protocolar (criado no fim)
```

## As 4 regras que nunca se quebram

1. **`00_originais/` é sagrado.** O que o cliente mandou fica lá intocado, para sempre.
2. **`DIARIO.md` só cresce.** Errou? Escreve-se uma NOVA entrada corrigindo — nunca se apaga a antiga. É isso que dá valor de prova ao registro.
3. **`_views/` nunca se edita à mão.** Está errado? A fonte (`CASO.yaml`) está errada — corrija lá e gere de novo.
4. **Nenhuma lei é citada de memória.** Todo artigo citado tem texto literal, fonte oficial e data de verificação na `BASE_LEGAL/`.

## Os 5 scripts (o que cada um faz)

Você normalmente NÃO roda os scripts sozinho — você pede ao Claude Code em
português ("chegou o extrato da Tânia", "rodar o G1") e ele roda por você.
Mas é bom saber o que existe:

| Script | O que faz | Quando |
|---|---|---|
| `novo_caso.py` | Cria a pasta do caso com tudo dentro | Cliente novo |
| `receber_documento.py` | Porta única de entrada: guarda o original, renomeia a cópia, registra a prova, baixa pendência, atualiza tudo | Chegou qualquer documento |
| `gerar_views.py` | Regenera os relatórios (status, pendências, checklist do cliente, painel) | Após qualquer mudança |
| `gate_check.py` | Roda os portões de qualidade G1/G2/G3 (checklists objetivos que BLOQUEIAM o avanço se algo falta) | Fim de cada etapa |
| `preparar_protocolo.py` | Monta o pacote final (petição limpa + documentos + índice) | Depois do G3 aprovado |
| `vigia_prazos.py` | Varre os prazos de TODOS os casos: vencido ou a ≤ 7 dias → ALERTA no diário + destaque no painel | **Início de toda sessão** |
| `colher_aprendizados.py` | Colhe do diário os aprendizados do caso (proposta que SÓ vira módulo com a sua ratificação) | Automático no protocolo e no encerramento |
| `absorver_versao.py` | Porta de retorno: compara a SUA versão da peça com a do sistema e prepara a absorção classificada | Quando você melhorar a peça por fora |
| `guardar_modelo.py` | Guarda peça/decisão de referência no ACERVO: anonimiza na entrada, recusa autos sigilosos, monta ficha de curadoria M-NN | Comando "guardar modelo" |
| `revalidar_biblioteca.py` | Ritual mensal da BASE_LEGAL: lista verbetes vencidos + casos ativos afetados; `--marcar` registra a revalidação | 1ª sessão do mês (o vigia lembra) |
| `preparar_audiencia.py` | Cria a pasta da audiência com roteiro (perguntas, ataques, provas, logística) para a SUA revisão + prazo no vigia | Comando "preparar audiência" |
| `relatorio_mensal.py` | Retrato do mês: casos, prazos, reprovações de gate e motivos, decisões, verbetes, pendências, horas (estimativa) | Fim do mês |
| `receber_whatsapp.py` | Export de conversa do WhatsApp: lacra tudo com hash SHA-256, monta a cronologia unificada (mensagens + falas), registra como prova | Chegou conversa como prova |
| `degravar.py` | Transcritor 100% local (nenhum áudio sai do computador): degrava os áudios de uma pasta de export (antes do receber_whatsapp) ou um áudio avulso de atendimento | Antes de receber conversa com áudios; atendimento gravado |

Exemplo de uso direto (numa janela do PowerShell, dentro desta pasta):

```
python ESCRITORIO\scripts\gate_check.py TANIA G1
```

## O caminho de um caso (as 4 etapas e os 3 portões)

```
E1 INTAKE ──G1──► E2 ESTRATÉGIA ──G2──► E3 MINUTA ──G3──► E4 PROTOCOLO
```

- **G1** — "o intake está completo?" (documentos guardados, partes, fatos, prazos e pendências registrados)
- **G2** — "estamos prontos para escrever a petição?" (estratégia feita, decisões tomadas e ratificadas)
- **G3** — "a peça pode ser protocolada?" (zero pendências bloqueantes, leis reverificadas, revisão humana declarada)

Portão reprovado = etapa seguinte **bloqueada**. É a sua proteção contra erro fatal.

## Quem decide o quê (D11 do blueprint)

O sistema decide as questões técnicas com praxe conhecida (percentuais,
regimes, competência…), sempre registrando no DIARIO **o fundamento, a
alternativa descartada e o grau de confiança**. Você não é consultado a cada
detalhe: **ratifica em bloco nos portões**, com direito de veto pontual.
O que é irredutivelmente seu: a revisão final e a assinatura — a peça só sai
com a sua declaração de revisão humana integral registrada no DIARIO.

## Git e backup (as suas redes de segurança)

- **Git** guarda uma "fotografia" de toda a pasta a cada portão executado —
  automático, você não faz nada. Serve para provar o que existia em cada
  momento e para recuperar qualquer estado passado.
- **Backup em nuvem** (Google Drive para desktop ou OneDrive) mantém uma cópia
  contínua fora do computador. Veja as instruções de ativação com o Claude.

## Dinheiro do caso (Onda 1 da expansão F6)

Cada caso tem o bloco `financeiro` no CASO.yaml (contrato de honorários,
custas, recebimentos) — o **contrato assinado é pendência padrão de todo caso
novo** (salvo pro bono), mas **não trava o protocolo**: regulariza-se em
qualquer fase. A view `_views/FINANCEIRO.md` mostra o caso; o
PAINEL soma o escritório (a receber, recebido no mês, custas). E o CASO.yaml
ganhou a `fase_processual` (pré-protocolo → postulatória → instrutória →
decisória → recursal → cumprimento → encerrado), visível no painel.

## Regra de ouro da peça

**A versão protocolada é SEMPRE a última que o sistema conhece.** Se você
melhorar a petição no Word ou em qualquer lugar fora daqui, ela volta pelo
comando *"absorver minha versão da peça"* — o sistema compara, classifica
cada mudança (estilo / fato novo / citação a verificar / valor a reconciliar),
salva como versão nova e re-roda o portão. Nunca protocole um texto que o
sistema não viu: a rastreabilidade morre ali.

## Se você se perder

Abra uma sessão do Claude Code nesta pasta e diga: *"status do escritório"* ou
*"status do caso FULANO"*. O sistema explica onde cada caso está e o que falta.
