# SOJ v2 — ARQUITETURA UNIFICADA (proposta para aprovação)

> 15/07/2026 · Motivada pela ordem do titular ("nova arquitetura eliminando o
> SOJ original") e fundamentada na **AUDITORIA_2026-07-15** (7 vermelhos, 21
> amarelos). **Status: AGUARDANDO GO — ver Emenda 03 em `_SISTEMA/emendas.md`.**

## 1. O veredito da auditoria em uma frase

**O problema não é o SOJ v1 nem o Operacional: é existirem os dois.** Todos os
achados estruturais nascem da fronteira entre eles: 24/25 processos sem caso
(os casos "existem" no outro modelo), os 3 casos reais sem `proxima_acao`
(o campo é do modelo novo, nunca entrou no CASO.yaml), o GETULIO morando em
dois lugares (CASOS/GETULIO + PROC-0010), dois motores de prazo (vigia × radar),
duas numerações, dois pontos de entrada de documento. Cada dia de dualidade
fabrica divergência nova.

## 2. O princípio da v2

**Uma entidade, uma casa, um formato.** Markdown + frontmatter (o que o
Obsidian, o Auditor, o radar e o conector já leem), com o modelo do
prompt-mestre (§3) como canônico. O que o v1 tem de melhor **não é a
arquitetura — é a disciplina**: DIARIO append-only, gates executáveis, originais
imutáveis, colheita de aprendizados, módulos por área. **Isso migra. O resto
aposenta.**

## 3. Topologia v2

```
NASCIMENTO/
├── CLIENTES/CLI-####.md            # como hoje (§3.2)
├── CASOS/CASO-####_slug/           # UM DIRETÓRIO POR CASO
│   ├── CASO.md                     # ficha canônica (§3.3 + F##/P##/PED##/PZ## no corpo)
│   ├── DIARIO.md                   # append-only — HERDADO DO v1, formato intocado
│   ├── originais/  documentos/  minutas/  audiencias/  protocolo/  _efemeros/
├── PROCESSOS/PROC-####.md          # como hoje (§3.4); espelham prazos do caso
├── INBOX/  AUTOS/  FINANCEIRO/  BRIEFINGS/            # como hoje
├── CONHECIMENTO/                   # ESCRITORIO/ renomeado (git mv, histórico preservado)
│   ├── MODULOS/  BASE_LEGAL/  ACERVO/  APRENDIZADOS/  CHECKLISTS/
├── RADAR/   CONECTOR/              # inalterados (já são v2)
├── _SISTEMA/
│   ├── scripts/                    # scripts v2 (lib única lendo frontmatter)
│   ├── templates/  prompts/  config/  bases/  logs/
└── _ARQUIVO/soj_v1/                # o que for aposentado — ARQUIVADO, nunca apagado
```

## 4. Mapa de destino — cada peça do v1

| Peça v1 | Destino | Como |
|---|---|---|
| `CASO.yaml` (fonte da verdade) | **APOSENTADO** | conteúdo migra para `CASO.md` (frontmatter §3.3; F##/P##/PED##/PT## viram seções do corpo; PZ## viram blocos de memória de cálculo §4.2 com estado) |
| `DIARIO.md` por caso | **MANTIDO INTACTO** | é o ledger — copia byte a byte; corrigi-lo seria falsificar história |
| `00_originais/` (imutável) | **MANTIDO** | vira `originais/` dentro do diretório do caso; hashes preservados |
| `_views/` | regeneradas | `gerar_views` v2 lê CASO.md |
| Gates G1/G2/G3 (`gate_check.py`) | **MANTIDOS** (conceito) | reimplementados sobre frontmatter; mesmos critérios |
| 18 scripts (`vigia`, `receber_documento`, `anexar_autos`, `novo_caso`…) | reescritos 1-a-1 sobre `soj_lib` v2 | os v1 vão para `_ARQUIVO/soj_v1/scripts/` no desligamento |
| `SOJ_BLUEPRINT_v1.md`, `MANUAL_DO_OPERADOR_*` | **_ARQUIVO/** | substituídos por este documento + LEIA-ME v2 |
| skill `soj-kernel` | **REESCRITA** | comandos iguais, alvos v2 |
| `ESCRITORIO/` (módulos, base legal, acervo, aprendizados) | **RENOMEADO → CONHECIMENTO/** | é conteúdo, não arquitetura — intocado no mérito |
| `PAINEL.md` | **APOSENTADO** | substituído pelo briefing diário (Etapa 4) + bases do Obsidian |
| Numeração `2026-XXXX` | congelada | casos migrados ganham `CASO-####` novo e guardam `id_legado:` no frontmatter |
| `CASO_TESTE_001/` (pré-v1) | **_ARQUIVO/** | resquício apontado pela auditoria |

**Nada é apagado.** "Eliminar" = tirar de operação. Registro de caso é dever
profissional (responsabilidade do advogado + trilha de auditoria); o
`_ARQUIVO/soj_v1/` e o histórico git são a prova de como cada dado nasceu.

## 5. O que a v2 resolve no dia 1

- R1 estrutural: **todo processo nasce vinculado a um caso** (o `novo_caso` v2
  cria caso+processo juntos; o censo vincula na criação).
- Um único motor de prazos: PZ## com memória de cálculo e estado vive no
  CASO.md; radar detecta → INBOX → sugerido no caso → humano confirma → vigia
  v2 cobra. Fim do espelho manual.
- Auditor R1–R6 (já rodando) passa a ler **um** modelo — sem regras de exceção
  para a fronteira.
- Uma numeração viva, uma porta de entrada de documentos, um gerador de views.

## 6. Migração — 5 ondas, cada uma com demonstração real → aprovação → commit

**Regra de ouro: o v1 só desliga quando o v2 provar paridade.** O vigia v1 e o
v2 rodam LADO A LADO durante a transição; divergência entre eles = bug do v2.

- **Onda 0 — rede de segurança** (1 sessão): tag git `v1-final`; backup zipado
  do repositório; `_ARQUIVO/` criado. *DoD: restauração de 1 arquivo testada.*
- **Onda 1 — laboratório** (1–2 sessões): `soj_lib` v2 + template CASO.md +
  `vigia`/`gates`/`views` v2; migrar **TESTE_FICTICIO** (o caso-laboratório
  existe para isso). *DoD: os 4 scripts v2 rodam no lab; auditor sem vermelho
  no lab; vigia v2 reproduz o vigia v1 no lab.*
- **Onda 2 — casos reais em ordem de risco** (2–3 sessões):
  **TANIA** (gates aprovados, sem prazo vivo) → **GETULIO** (⚠️ PZ03 sugerido:
  migra com dupla execução do vigia no mesmo dia) → **DAIANE** (**por último —
  protocolo em curso**; opção: congelar até protocolar). Cada caso: CASO.md
  gerado do CASO.yaml por script + conferência humana da ficha + DIARIO copiado
  + views regeradas + PROC-#### vinculado. *DoD por caso: auditor zera os
  vermelhos dele; vigia v2 = vigia v1.*
- **Onda 3 — cérebro e kernel** (1 sessão): `ESCRITORIO/` → `CONHECIMENTO/`
  (git mv); skill soj-kernel v2; CLAUDE.md reescrito; scripts v1 →
  `_ARQUIVO/soj_v1/scripts/`. *DoD: sessão nova opera só com comandos v2.*
- **Onda 4 — fechamento** (1 sessão): blueprint/manual/PAINEL → `_ARQUIVO/`;
  os 18 processos do censo vinculados a casos (entrevista-relâmpago só para
  agrupar: quais processos são o mesmo caso — ex.: execução + embargos da
  COOPVALE); LEIA-ME v2; auditoria final. *DoD: auditor com ZERO vermelho —
  o critério objetivo de "migração concluída".*

## 7. Riscos nomeados

1. **GETULIO tem prazo vivo** (PZ03) e a sentença é de hoje — migra com
   paridade dupla no mesmo dia, nunca numa sexta.
2. **DAIANE tem protocolo em curso** — mexer no caso no meio do protocolo é
   pedir R4 quebrada. Recomendação: congelar; migrar após o protocolo.
3. **Scripts v1 durante a transição**: continuam operando os casos ainda não
   migrados. A skill/CLAUDE.md deixa explícito qual caso vive em qual mundo
   (o auditor lista).
4. **Custo**: ~5–8 sessões de trabalho mecânico + conferências suas. O ganho:
   cada dia de dualidade a menos é divergência a menos — a auditoria mostrou
   que ela já esconde informação de prazo.

## 8. Decisões que só o titular pode tomar (bloqueiam o GO)

1. **GO da Emenda 03** — confirmar que "eliminar" = aposentar para `_ARQUIVO/`
   (nunca apagar registro de caso).
2. **DAIANE**: congela até protocolar (recomendado) ou migra por último?
3. **Numeração**: adotar sequência única `CASO-####` com `id_legado` (recomendado)
   ou manter `2026-XXXX` como esquema vivo?
4. **Gates e DIARIO**: confirmo que ficam (recomendado — são a disciplina que
   funciona); ou a eliminação os inclui?
