---
name: soj-kernel
description: >-
  Opera o Sistema Operacional Jurídico (SOJ) do escritório NASCIMENTO. Use
  quando o advogado disser qualquer comando do kernel: "novo caso", "chegou
  documento/extrato/certidão de X", "registrar decisão", "rodar G1/G2/G3",
  "status do caso X", "status do escritório", "gerar minuta", "preparar
  protocolo", "vigia de prazos" — ou qualquer pedido de trabalho sobre um
  caso em CASOS/. Encapsula os scripts de ESCRITORIO/scripts/ e as regras do
  SOJ_BLUEPRINT_v1.md para que toda sessão opere igual.
---

# SOJ Kernel — comandos padrão (blueprint, seção 7)

O dono é advogado e NÃO programa: explique em português simples, pergunte
antes de decisões importantes, e NUNCA invente fato ou lei (diante de lacuna,
pare e pergunte). Regras completas: `CLAUDE.md` da raiz + `SOJ_BLUEPRINT_v1.md`.

## Antes de qualquer comando (TODA sessão)

1. `python ESCRITORIO/scripts/vigia_prazos.py` — vigia de prazos, sempre primeiro.
2. Para trabalhar um caso: leia `CASOS/<X>/CASO.yaml` + `_views/STATUS.md` +
   cauda do `DIARIO.md`. NÃO releia a pasta inteira (Princípio: contexto mínimo).

## Comandos → o que fazer

| O advogado diz | Você faz |
|---|---|
| "novo caso" (+ pasta bagunçada) | `novo_caso.py NOME --titulo --area --modulo --comarca [--segredo]`; identifique a área sozinho (anuncie; pergunte só se ambíguo); lacre originais e registre cada documento via `receber_documento.py`; povoe CASO.yaml + INTAKE.md usando `MODULOS/<area>/checklist_documental.md` para abrir pendências; gere views; rode G1 |
| "chegou <documento> do caso X" | `receber_documento.py X <arquivo> --descricao ... [--o-que-prova ...] [--fato F## --marca-provado] [--resolve PEN##]` — ponto ÚNICO de entrada; nunca copie arquivo à mão |
| "registrar decisão" | Decida pela árvore `MODULOS/<area>/praxe_decisoria.md`: DECISAO_SISTEMA no DIARIO com fundamento + alternativa descartada + confiança + Tier; se estiver em `decisoes_reservadas.md` (Tier B) → recomende e AGUARDE o "ok" (DECISAO_ADVOGADO) |
| "rodar G1/G2/G3" | `gate_check.py X G#` — reprovado bloqueia; gates leem CAMPOS (`excecao_prova`, bloco `declaracoes:` com ref ao DIARIO), não texto livre |
| "status do caso X" | Leia e resuma `_views/STATUS.md` (se suspeitar de desatualização: `gerar_views.py X` antes) |
| "status do escritório" | Leia `PAINEL.md` (radar de prazos no topo) |
| "gerar minuta" | Parta de `MODULOS/<area>/templates/*.md` (v1 = template preenchido do CASO.yaml); tags SOJ por parágrafo; fundamentos SÓ com verbete válido na BASE_LEGAL — pesquise apenas o que falta/venceu e vire verbete |
| "preparar protocolo" | Véspera: anti-erro fatal (`MODULOS/<area>/anti_erro_fatal.md`) + conferência final com checagem cruzada peça↔decisões → declaracoes no CASO.yaml → G3 → revisão humana assinada do advogado → `preparar_protocolo.py X` → DOCX pela skill formatacao-peticoes-nascimento (NUNCA antes da assinatura) |
| "protocolado, processo nº N" | DIARIO: EVENTO_PROCESSUAL com o número; cadastrar prazos reais (PZ##); espelhar no Calendar (anonimizado: "[SOJ] <id> · PZ##"; laboratório = "[SOJ·TESTE]") |

## Regras duras (não negociar)

- `00_originais/` imutável · `DIARIO.md` append-only (corrigir = nova entrada)
  · `_views/` nunca à mão (`gerar_views.py`).
- Verificação com validade: verbete vencido não passa no G3; SM e afins pelo
  decreto vigente (verbete PARAM), nunca de notícia/memória.
- Alterou script? Teste TUDO em `CASOS/TESTE_FICTICIO` (laboratório
  permanente) ANTES de tocar caso real.
- `segredo_justica: true` = dados de menores: nada identificado sai deste
  ambiente; serviços externos só com id do caso + PZ##.
- Commits: automáticos a cada gate; não fazer push sem ordem.
