# AUDITORIA SOJ — 2026-07-15

Universo: **25 processos** (fichas) · **5 casos v1** (CASO.yaml, 2 de laboratório) · **7 clientes**.

**7 VERMELHOS · 21 amarelos · 1 informativos**

## 🔴 VERMELHOS (violacao de regra — briefing)

- **[R1]** 24/25 processos SEM CASO vinculado: PROC-0001, PROC-0002, PROC-0003, PROC-0004, PROC-0005, PROC-0006, PROC-0007, PROC-0008, PROC-0009, PROC-0011, PROC-0012, PROC-0013, PROC-0014, PROC-0015, PROC-0016, PROC-0017, PROC-0018, PROC-0019, PROC-0020, PROC-0021, PROC-0022, PROC-0023, PROC-0024, PROC-0025 — 'um processo sem caso nao existe' (modelo de dados, §3)
- **[R1]** caso 2026-0004 (DAIANE): CASO.yaml sem campo proxima_acao
- **[R1]** caso 2026-0004 (DAIANE): CASO.yaml sem campo data_interna
- **[R1]** caso 2026-0005 (GETULIO): CASO.yaml sem campo proxima_acao
- **[R1]** caso 2026-0005 (GETULIO): CASO.yaml sem campo data_interna
- **[R1]** caso 2026-0002 (TANIA): CASO.yaml sem campo proxima_acao
- **[R1]** caso 2026-0002 (TANIA): CASO.yaml sem campo data_interna

## 🟡 Amarelos

- [R6] PROC-0002: encerrado sem R6 concluido (financeiro/resultado/aprendizado/comunicacao/arquivo)
- [R6] PROC-0004: encerrado sem R6 concluido (financeiro/resultado/aprendizado/comunicacao/arquivo)
- [R6] PROC-0005: encerrado sem R6 concluido (financeiro/resultado/aprendizado/comunicacao/arquivo)
- [R6] PROC-0008: encerrado sem R6 concluido (financeiro/resultado/aprendizado/comunicacao/arquivo)
- [R3] CLI-0001 (F A COMERCIO LTDA): faltam procuracao, cpf/cnpj, telefone, forma_pagamento
- [R3] CLI-0002 (ANDRE DE MOURA SOUSA): faltam contrato, procuracao, cpf/cnpj, telefone, forma_pagamento
- [R3] CLI-0003 (BEATRYZ CORREA OLIVEIRA): faltam contrato, procuracao, cpf/cnpj, telefone, forma_pagamento
- [R3] CLI-0004 (PERFIL COMERCIO E ENGENHARIA LTDA): faltam cpf/cnpj, telefone
- [R3] CLI-0005 (C E S NASCIMENTO SERVICOS LTDA): faltam contrato, cpf/cnpj, telefone, forma_pagamento
- [R3] CLI-0006 (DANIEL AUGUSTO PINHEIRO PINHEIRO): faltam contrato, cpf/cnpj, telefone, forma_pagamento
- [R3] CLI-0007 (VINICIUS FERNANDES DA SILVA): faltam contrato, cpf/cnpj, telefone, forma_pagamento
- [R2] caso 2026-0005: PZ03 SUGERIDO aguardando confirmacao humana
- [R1] caso 2026-0001 (TESTE_FICTICIO) [LAB]: CASO.yaml sem campo proxima_acao
- [R1] caso 2026-0001 (TESTE_FICTICIO) [LAB]: CASO.yaml sem campo data_interna
- [R2] caso 2026-0001: PZ01 sem estado nem status (modelo v1 legado — motor v2 exige estado)
- [R2] caso 2026-0001: PZ05 sem estado nem status (modelo v1 legado — motor v2 exige estado)
- [R1] caso 2026-0003 (TESTE_IMPORTACAO) [LAB]: CASO.yaml sem campo proxima_acao
- [R1] caso 2026-0003 (TESTE_IMPORTACAO) [LAB]: CASO.yaml sem campo data_interna
- [ESTRUTURA] PROC-0010 aponta para caso v1 2026-0005 (CASOS/GETULIO) — DUPLA ARQUITETURA no mesmo processo
- [ESTRUTURA] CASO_TESTE_001/ na raiz: resquicio do sistema pre-v1, fora de qualquer modelo
- [R5] APR-0002_competencia-territorial-jec.md: status=bruto — aguarda ratificacao do titular

## ℹ️ Informativos

- [ETAPA2] INBOX/ vazio — fluxo DJEN->INBOX ainda nao liga radar ao sistema (Etapa 2)

---
R4 (protocolo) ainda nao e verificavel mecanicamente neste modelo — entra com a migracao v2 (checklist de protocolo como campos).