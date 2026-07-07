# REVISÃO DO COLABORADOR — DR. COLABORADOR FICTICIO
Caso 2026-0003 · importado em 2026-07-06 22:59 pela porta de importação (blueprint v1.10, §7)

> Relatório CONGELADO da importação (não se regenera). Parte mecânica: script.
> Seções semânticas: preenchidas pelo sistema NA SESSÃO de importação, antes do fechamento.

## 1. Inventário e rotas (dedupe por SHA-256)

- `COMPROVANTE PIX PENSAO.pdf` → **prova** · prova P01 (DOC-01_COMPROVANTE_PIX_PENSAO.pdf)
- `PETICAO INICIAL - ALIMENTOS.md` → **minuta** · MINUTA_v01.md (importada)
- `PROCURACAO ASSINADA.pdf` → **instrumental** · instrumental INS01 (DOC-02_PROCURACAO_ASSINADA.pdf)
- `PROCURACAO revisada final.docx` → **rascunho_instrumental** · _efemeros/importacao (rascunho de instrumental — nao e o assinado)
- `RG DA CLIENTE.jpg` → **instrumental** · instrumental INS02 (DOC-03_RG_DA_CLIENTE.jpg)

## 2. Duplicatas eliminadas do roteamento

- `COMPROVANTE PIX PENSAO (1).pdf` = cópia exata de `COMPROVANTE PIX PENSAO.pdf` (mesmo hash; lacrada, não roteada)

## 3. Verificação de fontes da minuta (BASE_LEGAL)

- 🔴 **REVOGADA (LEI MORTA)** — “arts. 16 a 18 da Lei nº 5.478” · verbete LEI5478:art16a18: REVOGADOS pelo CPC/2015
- 🟢 **verificada** — “art. 1.694 do Código Civil” · verbete CC:art1694
- 🟢 **verificada** — “art. 529 do Código de Processo Civil quanto ao desconto em” · verbete CPC:art529
- 🟡 **NAO VERIFICADA** — “art. 85 do CPC quanto aos honorários sucumbenciais” · sem verbete na BASE_LEGAL — verificar NA FONTE antes de qualquer uso

_Detecção heurística: a revisão semântica abaixo cobre o que a varredura não pegou._

## 4. O que está bom (crédito ao colaborador)

- Estrutura correta (fatos → direito → pedidos) e redação limpa.
- O fundamento central está certo e vigente: CC art. 1.694 (verbete válido).
- O **valor da causa está matematicamente exato** para o pedido que ele
  formulou: 12 × 2 filhos × 40% do SM 2026 (R$ 1.621,00) = R$ 15.561,60.
- Anexou o comprovante PIX que ancora o fato dos pagamentos parciais (F02 —
  único fato da peça que já nasce provado).
- Lembrou da gratuidade da justiça e do desconto em folha como garantia.

## 5. Fatos afirmados sem prova (órfãos)

- **F03 — renda de ~R$ 8.000,00 e "padrão de vida incompatível": ÓRFÃO.**
  Nenhum documento na pasta sustenta a afirmação. Ficou `alegado` + PEN03
  (prova da renda: CNIS, ofícios, redes sociais, diligência).
- **F01 — filiação e abandono do lar:** afirmado sem as certidões de
  nascimento (documento essencial do módulo família). `alegado` + PEN02
  (crítica, bloqueia G3).

## 6. Juiz rigoroso sobre a peça importada

1. **Fundamento revogado**: pede desconto em folha "na forma dos arts. 16 a
   18 da Lei 5.478/68" — revogados EXPRESSAMENTE pelo CPC/2015, art. 1.072,
   V (verbete LEI5478:art16a18). Citação que fulmina a credibilidade da
   peça; o fundamento vigente é o CPC art. 529 (que a própria peça também
   cita — bastava cortar a lei morta).
2. **Citação "no endereço declinado"** — mas endereço nenhum foi declinado
   na peça (CPC art. 319 exige qualificação). PEN05.
3. **Qualificação incompleta** da autora (sem CPF/endereço). PEN04.
4. **Quantum sem parâmetro fundamentado**: 40% do SM por filho sem uma linha
   de justificativa; a praxe do módulo trabalha com 30% do SM por filho como
   piso objetivo. Desvio não é proibido — mas exige fundamento (virou PC01).
5. Sem certidões de nascimento, a legitimidade/filiação fica descoberta
   (PEN02 bloqueia G3).

## 7. Adversário contra a peça importada

- Atacaria de imediato a **renda alegada de R$ 8.000,00**: zero lastro
  documental; pediria fixação pelo mínimo diante da ausência de prova.
- Usaria os **pagamentos parciais via PIX contra a autora**: "pago o que
  posso, não houve abandono material" — a peça não neutraliza esse uso.
- Impugnaria o **desconto em folha por fundamento revogado** — e o réu é
  descrito como AUTÔNOMO na própria peça: desconto em folha de quem não tem
  folha. Contradição interna grave.
- Contestaria a gratuidade — mitigável: em favor do alimentando menor a
  presunção o socorre (verbete STJ na BASE_LEGAL), mas a declaração de
  hipossuficiência NÃO veio na pasta do colaborador.

## 8. Decisões embutidas → propostas do colaborador

| ID | Tema | Proposta dele | Situação |
|---|---|---|---|
| PC01 | Quantum | 40% do SM por filho (80% total) | `aguardando_ratificacao` — diverge do piso da praxe (30%/filho) sem justificativa |
| PC02 | Valor da causa | R$ 15.561,60 (matemática exata) | `aguardando_ratificacao` — depende do PC01 |

**O G2 deste caso fica bloqueado até o titular ratificar ou vetar cada uma
(governança de autoria, blueprint v1.10 §7).** Registro: DIARIO #003.
