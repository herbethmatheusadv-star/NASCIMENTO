# MODELO — formato do DIARIO.md (o ledger de cada caso)

> Blueprint v1.3, seção 4. O DIARIO é **append-only**: entradas numeradas em
> sequência, jamais editadas ou apagadas. Correção = nova entrada citando a
> antiga. O arquivo real é criado pelo `novo_caso.py`; os scripts acrescentam
> entradas automaticamente (recebimento de documento, gates); decisões e notas
> são acrescentadas pelo Claude/advogado sempre AO FIM do arquivo.

## Formato de cada entrada

```markdown
## #015 | 2026-06-27 16:40 | DECISAO_SISTEMA
Alimentos: 30% do salário mínimo por filho (60% total) + 50% das despesas
extraordinárias de saúde e educação mediante comprovação.
Fundamento: renda do réu não comprovada → ramo "renda desconhecida" da árvore
(praxe_decisoria.md §alimentos); praxe consolidada TJPA/STJ na BASE_LEGAL.
Alternativa descartada: % sobre rendimentos líquidos — inviável sem prova de renda.
Confiança: alta · Tier A (ratificação em bloco no G2) · Afeta: PED01
---
## #019 | 2026-06-28 10:12 | GATE
G2 executado: APROVADO. 9/9 itens. Relatório: _views/gate_G2_2026-06-28.md
---
## #021 | 2026-07-02 09:30 | DOC_RECEBIDO
Recebido extrato bancário Caixa 07/2025–06/2026 → 00_originais/E-01.pdf →
DOC-11. Registrado como P11, vinculado a F04 (status alterado: alegado → provado).
Resolve: PEN01
---
```

Anatomia da linha de cabeçalho: `## #NÚMERO | DATA HORA | TIPO`
Cada entrada termina com uma linha `---`.

## Tipos de entrada

| Tipo | Quando usar |
|---|---|
| `DECISAO_SISTEMA` | Decisão técnico-jurídica tomada pelo sistema (D11). SEMPRE com: fundamento, alternativa descartada, confiança (alta/média/baixa) e tier (A ou B) |
| `DECISAO_ADVOGADO` | Vetos e decisões reservadas (Tier B) do advogado |
| `RATIFICACAO` | Ratificação em bloco do resumo de decisões, nos gates |
| `DOC_RECEBIDO` | Documento novo (gerada pelo receber_documento.py) |
| `GATE` | Execução de G1/G2/G3, aprovado OU reprovado (gerada pelo gate_check.py) |
| `PESQUISA` | Pesquisa jurídica concluída (o resultado vai para a BASE_LEGAL) |
| `CONTATO_CLIENTE` | Contato relevante com o cliente (ex.: checklist enviado) |
| `EVENTO_PROCESSUAL` | Protocolo, citação, decisão, audiência… |
| `ALERTA` | Risco ou problema detectado |
| `NOTA` | Qualquer outro registro relevante |

## As três regras duras (seção 4 do blueprint)

1. **Entradas jamais são editadas** — correção é nova entrada referenciando a anterior. O git denuncia qualquer edição.
2. **Decisão sem registro não existe** — toda decisão do sistema entra como DECISAO_SISTEMA completa; vetos como DECISAO_ADVOGADO; ratificações como RATIFICACAO.
3. **Todo gate gera entrada**, aprovado ou não.

## Convenções que os gates leem (para o gate_check.py reconhecer)

- Checklist enviado ao cliente → entrada `CONTATO_CLIENTE` contendo a palavra "checklist" (G1).
- Caso sem prazos → entrada `NOTA` contendo "SEM PRAZOS" e a justificativa (G1).
- Aceitação de risco da simulação adversária → entrada `DECISAO_ADVOGADO` contendo "aceito o risco" (G2).
- Conferência final de dados → entrada `NOTA` contendo "CONFERÊNCIA" de valores/datas/nomes/CPFs (G3).
- Revisão final do advogado → entrada `DECISAO_ADVOGADO` contendo "revisão humana integral" (G3).
