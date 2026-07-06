# MÓDULO CONSUMIDOR / ÁGUAS DO PARÁ — contrato do módulo (Onda 3/F6, 2026-07-06)

> Adaptação da skill `peticao-negativacao-aguas-do-para` ao kernel (D10).
> **100% do conteúdo validado preservado por cópia íntegra** em
> `referencias/`, `scripts/` e `templates/` (integridade conferida).
> `SKILL_original.md` = a skill como era. Réu FIXO e dados do advogado agora
> vêm das fontes únicas do kernel (réu: abaixo; advogado: ESCRITORIO/ADVOGADO.md
> — o ADVOGADO.md da skill NÃO foi migrado de propósito).

## Núcleo da área

**Negativação indevida de consumidor** pela concessionária:
**AGUAS DO PARA D SPE S.A. — CNPJ 61.067.904/0001-29** — Av. Potiguá, Galeria
Diamond, Sala 05 / R.A-613, Primavera, Parauapebas/PA, CEP 68.515-000 —
0800 091 0091. **Foro padrão:** JEC de Parauapebas/PA (CDC art. 101, I —
domicílio do consumidor; conferir a comarca do cliente).

## Tipos de ação (sub-hipóteses A–E — SKILL_original §4)

| # | Situação | Pedidos típicos |
|---|---|---|
| A | Pagou e foi negativado | Inexigibilidade + repetição em DOBRO (art. 42 §ún. CDC; Tema 929 p/ pós-30/03/2021) + dano moral + tutela |
| B | Negativado sem dever (matrícula/lote alheio) | Inexigibilidade + dano moral + tutela |
| C | Lote vendido; cobrado o antigo dono | Idem B + contrato/escritura da venda |
| D | Duplicidade / cobrança a maior | Repetição em dobro + inexigibilidade (+ dano moral se negativado) |
| E | Cobrança indevida ainda SEM negativação | Inexigibilidade + tutela preventiva + dano moral eventual |

Regra de ouro preservada: pagamento indevido → dobro; sem pagamento → sem
dobro; negativação → dano moral **in re ipsa**.

## Rito e quantum

- JEC (Lei 9.099/95); valor da causa = dano moral + dobro, **≤ 40 SM** —
  estourou a alçada → DECISÃO RESERVADA (renúncia × rito comum).
- Dosimetria: `referencias/tabela-danos-morais.md` (piso R$ 10.000 +
  agravantes da §5 da skill: score, vulnerabilidade, saúde, constrangimento,
  inércia pós-PROCON, confissão, reincidência).

## Correspondências com o kernel

- Passos 0–2 da skill (ler pasta, classificar, diagnosticar) → E1/intake
  (porta única substitui `scripts/organizar_provas.py`, mantido como legado).
- Passo 3 ("parar e perguntar") → regra que o kernel já tem por princípio.
- Passo 4 (atualizar jurisprudência na web) → subordinado ao D6: o que se
  confirmar vira VERBETE datado em `BASE_LEGAL/consumidor.md`; nunca citar
  sem verbete.
- Passos 6–8 (DOCX, checklist, pasta de protocolo) → E3/G3/preparar_protocolo
  + skill de formatação (o gerador `scripts/build_peticao.js` fica como
  alternativa legada).
- Template da peça: `templates/negativacao_indevida.md` (cópia do
  modelo-peticao validado; ganhará tags SOJ no primeiro caso real da área).

## Estado do contrato (seção 9)

| Arquivo | Estado |
|---|---|
| MODULO.md · praxe_decisoria.md · decisoes_reservadas.md · checklist_documental.md · teses.md · anti_erro_fatal.md | ✅ (Onda 3) |
| templates/negativacao_indevida.md · referencias/ (5) · scripts/ (2, legados) | ✅ copiados íntegros |
| Tabela de quantum | ✅ referencias/tabela-danos-morais.md (validada em uso) |
