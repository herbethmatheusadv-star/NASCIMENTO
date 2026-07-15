# Fonte da verdade por campo — CASO.yaml × fichas markdown

> **STATUS: APROVADA pelo advogado em 15/07/2026**, com duas condições
> incorporadas abaixo (marcadas ★). Princípio: **uma verdade por campo**. Quem
> duplica, deriva por script; o Auditor confere a derivação e acusa divergência.

## Condições da aprovação (15/07/2026)

- **★(a)** Todo `PZ##` no CASO.yaml referencia **obrigatoriamente** o número
  do processo a que pertence (campo `processo:`) — casos com múltiplos
  processos exigem isso. Já aplicado no PZ02 do caso 2026-0005 (GETULIO).
- **★(b)** A partir da **Etapa 2**, o `PZ##` carrega os campos completos da
  memória de cálculo do §4.2 do prompt-mestre, incluindo o **estado**
  (`sugerido | confirmado | cumprido | perdido | cancelado`).

## Mapa de propriedade

| Campo | Fonte única | Quem espelha (por script) |
|---|---|---|
| Identidade do processo (número, tribunal, sistema, grau, órgão, classe, valor da causa, sigiloso) | `PROCESSOS/PROC-####.md` (frontmatter) | views/bases |
| Polo do cliente e parte adversa | `PROC-####.md` | views/bases |
| Vínculos processo→caso→cliente | `PROC-####.md` (campos `caso:`, `cliente:`) | views/bases |
| Fase/situação processual externa, última movimentação | `PROC-####.md` | views/bases |
| `proxima_acao` e `data_interna` **do processo** | `PROC-####.md` | briefing |
| `proxima_acao`, `data_interna`, `prescricao_ou_limite`, `impedimento` **do caso** | `CASO.yaml` (campos novos, extensão v1) | briefing |
| Fatos (F##), provas (P##), pedidos (PED##), partes (PT##), gates, decisões | `CASO.yaml` (modelo v1 intocado) | views |
| **Prazos (PZ##) + memória de cálculo** | `CASO.yaml` — todo prazo confirmado vira PZ## | ficha PROC exibe espelho gerado; vigia lê o CASO.yaml |
| Dados de relacionamento do cliente (contato, origem, docs pendentes, contrato/procuração/hipossuficiência, última atualização enviada) | `CLIENTES/CLI-####.md` | views/bases |
| Qualificação da parte **nos autos** (nome, CPF, endereço para a peça) | `CASO.yaml` (PT##) — *snapshot* copiado do CLI na criação do caso | — |
| Financeiro (lançamentos) | `FINANCEIRO/lancamentos.md` (append-only) | relatório mensal |

## Regras de fronteira

1. **Todo processo pertence a um caso** (R1). Enquanto o caso v1 não existe
   (cadastro em andamento), a ficha PROC pode carregar prazos *provisórios* em
   estado `sugerido`; ao criar o caso, migram para PZ## e a ficha passa a
   espelhar.
2. **PT## é snapshot, não referência viva** — e **CASO.yaml é o canônico**
   (determinação do advogado, 15/07/2026): mudança de contato/endereço se faz
   no CLI; se afetar peça em curso, a atualização do PT## é decisão registrada
   no DIARIO. **Auditor R2: snapshot PT## divergente na ficha PROC = ALERTA
   VERMELHO no briefing** (nunca correção automática).
3. **Views e bases nunca são fonte** (D5 do blueprint, mantida).
4. Conflito não previsto neste mapa → perguntar ao advogado e registrar aqui.
