# Relatório de Reconhecimento — Etapa 0 (SOJ Operacional, Fase 0)

> Gerado em 2026-07-15. Nenhum código foi escrito. Aguarda aprovação do advogado
> (PROMPT_MESTRE_SOJ_OPERACIONAL.md, §2.5).

---

## 1. O que existe

### 1.1 O MVP (radar DJEN) — `Brand Nascimento\monitor-prazos\`

| Peça | Onde | O que faz |
|---|---|---|
| Coleta DJEN | `monitor_prazos.py` (`consultar_djen`, `_requisitar`, `fatiar`) | consulta por OAB com retry (4x), fatiamento em blocos de 45 dias, janela `auto` que anda para trás até o prazo vivo mais antigo, aviso de relatório incompleto |
| Calendário e prazos | `monitor_prazos.py` (`Calendario`, `calcular_prazo`) | dias úteis (art. 219 CPC / 775 CLT), feriados nacionais + móveis (via Páscoa), recesso 20/12–20/01, feriados locais **por tribunal** |
| Leitura do teor | `classificador.py` | o que é (despacho/decisão/sentença…), o que pede (só em trecho de ordem), sob pena de quê, e de quem é o prazo (MEU / DA_OUTRA_PARTE / INCERTO) |
| Conciliação | `datajud.py` | petição no prazo × decurso certificado × sem sinal; cache 12h; chave pública CNJ |
| Relatório | `monitor_prazos.py` (`gerar_html`, `imprimir_console`) | HTML diário em `relatorios/`, ordenado por urgência (VENCIDO GRAVE no topo) |

- **Armazenamento: não há banco de dados.** Estado = `config.json` (OAB 39261/PA, prazo padrão 15), `feriados_locais.txt` (PA/MA/TRT8 já cadastrados), `resolvidos.txt`, `.cache_datajud.json`, HTMLs em `relatorios/`. O "banco do radar" citado no prompt-mestre é a própria consulta DJEN — os números de processo vêm dela.
- **Dependências: zero** — só stdlib do Python. ~110 testes em 4 arquivos (`teste_*.py`).
- **O TRT-8 já entra no radar hoje**: a consulta é por OAB, sem filtro de tribunal. O que falta é a **tabela de prazos por rito** (CLT: RO 8, ED 5…) — hoje, sem prazo no texto, assume 15.

### 1.2 A descoberta central: o SOJ v1 já existe — `OneDrive\Documentos\NASCIMENTO\`

Sistema maior do que o prompt-mestre supunha, **rodando com casos reais**:

- **Git próprio, 93 commits** (commits automáticos por gate). Sem remoto configurado.
- `SOJ_BLUEPRINT_v1.md` (v1.10) — decisões D1–D11: `CASO.yaml` como fonte da verdade, `DIARIO.md` append-only, views só por script, gates G1/G2/G3 executáveis.
- `.claude/skills/soj-kernel/SKILL.md` — kernel completo de comandos ("novo caso", "chegou documento", gates, colheita, importação, WhatsApp, autos, acervo).
- `ESCRITORIO/DOUTRINA_ANALISE.md` — **aprovada pelo titular em 07/07/2026**; será integrada como norma superior ao §1.3 do prompt (o próprio prompt manda).
- `ESCRITORIO/scripts/` — 18 scripts: `vigia_prazos`, `gate_check`, `gerar_views`, `receber_documento`, `novo_caso`, `importar_caso`, `anexar_autos`, `degravar`, `receber_whatsapp`, `guardar_modelo`, `colher_aprendizados`, `relatorio_mensal`, `preparar_protocolo`, `preparar_audiencia`, `absorver_versao`, `diff_pecas`, `revalidar_biblioteca`, `soj_lib`.
- `ESCRITORIO/MODULOS/` — 4 módulos plenos (família, consumidor_aguas, bancario_ccb, cível/honra digital) + 2 esqueletos (trabalhista, previdenciário).
- `ESCRITORIO/BASE_LEGAL/` (verbetes com validade), `ESCRITORIO/ACERVO/` (modelos M-##), `ESCRITORIO/MODELOS/` (schema do CASO.yaml).
- `CASOS/`: DAIANE (2026-0004, cível — em curso, com alterações não commitadas), TANIA (2026-0002, família — G1/G2/G3 aprovados), GETULIO, TESTE_FICTICIO (laboratório permanente), TESTE_IMPORTACAO.
- `CLAUDE.md`, `LEIA-ME.md`, `MANUAL_DO_OPERADOR_SOJ.md` (+2ª edição), `PAINEL.md`.

**O que o SOJ v1 NÃO tem — e o prompt-mestre traz:** entidade CLIENTE, entidade PROCESSO (pós-protocolo), INBOX de intimações, ligação radar→sistema, motor de prazos com estados (`sugerido→confirmado`) e memória de cálculo, decomposição D-8→D0, briefing diário 07h, Auditor R1–R6, FINANCEIRO, views em Obsidian Bases.

### 1.3 Vault Obsidian

Existe em `OneDrive\Documentos\Obsidian Vault` (com sub-vaults: Conhecimentos, Gestão CENTRAL, IA). **A pasta NASCIMENTO não é um vault hoje** (sem `.obsidian`) — mas o Obsidian abre qualquer pasta como vault sem mover nenhum arquivo.

### 1.4 Skills e peças de redação

- `soj-kernel` (repo NASCIMENTO) · `carrossel-juridico-nascimento` (repo Brand Nascimento).
- `formatacao-peticoes-nascimento`, `advogado-bancario-cooperativas`, `peticao-negativacao-aguas-do-para` — skills de usuário, presentes na sessão. As duas últimas **já foram absorvidas** pelos módulos `bancario_ccb` e `consumidor_aguas` (o `SKILL_original.md` está guardado dentro de cada módulo). A de formatação segue sendo o braço de DOCX final (regra dura do kernel).

### 1.5 API Comunica — verificação do TRT-8 (item 4 da Etapa 0) ✔

- **Sigla correta: `TRT8`** (sem hífen). Confirmado de duas formas: o filtro `siglaTribunal=TRT8` retornou 4.079 comunicações só em 14/07/2026 (a primeira delas da 3ª Vara do Trabalho de **Parauapebas**), e o próprio campo `siglaTribunal` dos itens vem como `TRT8`. A variação `TRT-8` respondeu "sistema ocupado" (inconclusivo e irrelevante — a forma canônica está confirmada).
- **OAB 39261/PA retorna resultados no TRT8: 16 comunicações desde 01/01/2026**, em pelo menos 2 processos (ex.: 0001766-17.2024.5.08.0126, 0000342-54.2026.5.08.0130).

---

## 2. O que será reaproveitado

| Ativo | Destino no SOJ Operacional |
|---|---|
| `monitor-prazos/` inteiro | vira o **radar** do sistema; motor de prazos **refatorado** (v2: estados + memória de cálculo + tabelas por rito), nunca reescrito |
| `feriados_locais.txt` | semente do `_SISTEMA/config/feriados.yaml` |
| `classificador.py` | base da triagem do INBOX (o que é, o que pede, de quem é) |
| `datajud.py` | conciliação mantida e ampliada (log em `_SISTEMA/logs/conciliacao.md`) |
| SOJ v1: kernel, gates, DIARIO, CASO.yaml, módulos, BASE_LEGAL, ACERVO | **espinha dorsal mantida** — o SOJ Operacional completa o v1, não o substitui |
| `DOUTRINA_ANALISE.md` | norma superior do modo analítico (Analista Processual das 12 saídas obedece a ela) |
| `vigia_prazos.py` | funde-se com o Motor de Prazos v2 (radar detecta e sugere; vigia cobra os confirmados) |
| `colher_aprendizados.py` | já implementa o espírito da R6 |
| `relatorio_mensal.py` | base do relatório financeiro mensal |
| Skills de redação | referenciadas na saída 10 do Analista; jamais duplicadas |

---

## 3. Morada proposta e árvore final

**Recomendação: o SOJ Operacional mora em `OneDrive\Documentos\NASCIMENTO\`** — é onde já estão o git ativo, o kernel, a doutrina e os casos reais. Abre-se essa pasta como vault no Obsidian ("Open folder as vault"; nada muda de lugar). O `monitor-prazos/` muda para dentro do repo.

```
NASCIMENTO/                        (vault Obsidian + repo git)
├── CLAUDE.md · SOJ_BLUEPRINT_v1.md · LEIA-ME.md · PAINEL.md
├── .claude/skills/soj-kernel/
├── CASOS/                         (mantém o modelo v1: CASO.yaml + DIARIO + _views)
├── CLIENTES/          [novo]      CLI-0001.md — frontmatter do prompt §3.2
├── PROCESSOS/         [novo]      PROC-0001.md — frontmatter do prompt §3.4
├── INBOX/             [novo]      1 nota por intimação; zerado diariamente
├── AUTOS/<numero>/    [novo]      PDFs fora do git; backup zipado+cifrado semanal
├── FINANCEIRO/        [novo]      contratos/ · lancamentos.md · RELATORIOS/
├── BRIEFINGS/         [novo]      AAAA-MM-DD.md (alimenta/substitui o PAINEL.md)
├── RADAR/             [movido]    o monitor-prazos, refatorado na Etapa 2
├── ESCRITORIO/        [existente] = o CONHECIMENTO/ do prompt
│   ├── MODULOS/ · BASE_LEGAL/ · ACERVO/ · MODELOS/ · RELATORIOS/ · scripts/
│   └── DOUTRINA_ANALISE.md
└── _SISTEMA/          [novo]      templates/ · prompts/ · config/ · bases/ · logs/
```

**Conciliações de projeto (as três decisões que evitam retrabalho):**

1. **Modelo de dados.** `CASO.yaml` continua a fonte da verdade do caso (D3/D5 do blueprint — mexer nisso agora quebraria gates, views e 93 commits de histórico). CLIENTE e PROCESSO nascem no formato do prompt (markdown+frontmatter, o que o Obsidian Bases lê). O espelhamento entre CASO.yaml e as views/bases é sempre por script, nunca à mão.
2. **`CONHECIMENTO/` não será criado.** `ESCRITORIO/` já cumpre o papel: TESES→`MODULOS/*/teses.md` · MODELOS→`ACERVO/`+`MODULOS/*/templates/` · PRECEDENTES→`BASE_LEGAL/`+referências dos módulos · CHECKLISTS/ESTRATEGIAS→dentro dos módulos · APRENDIZADOS→fluxo do `colher_aprendizados.py`.
3. **Dois vigias viram um.** Radar (DJEN, detecta e **sugere**) + vigia_prazos (cobra os **confirmados** PZ##). O estado `sugerido→confirmado` do prompt é exatamente a fronteira entre os dois.

---

## 4. Riscos

1. **Git órfão em `C:\Users\nasci`** — a pasta "Brand Nascimento" está sob um repo iniciado na raiz do perfil do Windows, com **zero commits** e sem remoto. Inútil (nada versionado) e perigoso (o git varre o perfil inteiro). Proposta: descartar esse `.git` (não toca em nenhum arquivo seu) e versionar o radar dentro do repo NASCIMENTO. **Só farei com o seu ok.**
2. **Sem remoto privado** — o prompt (§1.5) exige git com remoto privado; o repo NASCIMENTO não tem nenhum. Precisamos criar (ex.: GitHub privado).
3. **OneDrive + git** — NASCIMENTO sincroniza pelo OneDrive; sync de `.git` pode gerar conflito. O blueprint (D2) já aceitou esse trade-off; o remoto privado vira a rede de segurança real.
4. **Duas verdades sobre o mesmo caso** — CASO.yaml × fichas markdown. Mitigação: espelhamento só por script (D5), com o Auditor conferindo consistência.
5. **Feriados municipais ausentes** (Parauapebas, Marabá, Imperatriz, Belém) — causa nº 1 de erro de prazo. A tabela `prazos.yaml`/`feriados.yaml` será validada com você antes de ativar (§4.3).
6. **DJEN instável** — já mitigado no MVP (retry, fatiamento, aviso de incompleto). Manter no v2.
7. **DataJud** — rate limit agressivo, defasagem ~4 dias, não indexa advogado. Conciliação continua sendo sinal, nunca baixa automática de prazo.
8. **Trabalho não commitado no NASCIMENTO** (caso DAIANE em curso) — commit antes de qualquer mudança estrutural da Etapa 1.

---

## 5. Dúvidas — aguardando sua resposta

- **Q1 · Morada:** confirma NASCIMENTO como casa do SOJ, aberto como vault no Obsidian? (Alternativa: dentro do "Obsidian Vault" existente — não recomendo: separaria o sistema do git e dos casos.)
- **Q2 · Radar:** movo o `monitor-prazos/` para `NASCIMENTO/RADAR/`? (Recomendado — um repo só governa tudo. O agendamento diário do Windows seria atualizado junto.)
- **Q3 · Git órfão:** autoriza apagar o `.git` vazio de `C:\Users\nasci`? (Remove só a configuração do repo vazio; nenhum arquivo seu é tocado.)
- **Q4 · Remoto privado:** você tem conta no GitHub (ou prefere outro serviço) para criarmos o repositório privado do NASCIMENTO?
- **Q5 · Feriados municipais:** na Etapa 2 eu proponho a tabela das comarcas ativas (Parauapebas, Marabá, Imperatriz, Belém) e você valida item a item — de acordo? Alguma outra comarca ativa hoje?
- **Q6 · Backup dos AUTOS/:** qual pasta de nuvem recebe o zip cifrado semanal?
- **Q7 · Numeração:** casos mantêm os ids do v1 (`2026-0004`); `CLI-####`/`PROC-####` valem só para as entidades novas — confirma?

---

**PARADA OBRIGATÓRIA.** Nenhum código foi escrito. A Etapa 1 (Resgate operacional) só começa após a sua aprovação deste relatório — com as respostas acima ou os ajustes que você determinar.
