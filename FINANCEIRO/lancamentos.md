# FINANCEIRO — lançamentos (razão append-only)

> Regra: linha lançada nunca se edita. Correção = novo lançamento de estorno
> com referência à linha corrigida. Tipos: entrada, parcela, ato, exito,
> consulta, despesa, reembolso, acordo, alvara.

| data | tipo | cliente | caso | descrição | valor | vencimento | status | obs |
|---|---|---|---|---|---|---|---|---|
| 2026-07-15 | entrada | CLI-0001 F A Comércio | PROC-0001 | honorários combinados (entrevista 15/07) — RECEBIMENTO A CONFIRMAR | R$ 900,00 | — | a-confirmar | processo encerrado 19/03/2026 |
| 2026-07-15 | acordo | CLI-0003 Beatryz | PROC-0003 | honorários líquidos do acordo homologado 03/03 (ata fls. 217) — fluxo via parcelas na conta do Dr. Fernando (Bradesco Ag 2008 CC 251259-9) | R$ 2.728,19 | conforme parcelas (última 10/08/2026) | a-receber | IRPF na fonte R$ 24,27; confirmar repasses por parcela |
| 2026-07-15 | despesa | CLI-0003 Beatryz | PROC-0003 | custas do acordo — DIVERGÊNCIA na ata (fls. 217: reclamada × fls. 219: reclamante, R$ 682,28, 30 dias após última parcela) — conferir no PJe antes de provisionar | R$ 682,28 | ~2026-09-10 | provisorio | ver PROC-0003 §2 |
