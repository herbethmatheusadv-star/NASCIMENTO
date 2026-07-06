---
name: peticao-negativacao-aguas-do-para
description: "Redige petições iniciais prontas para protocolo no Juizado Especial Cível contra a concessionária ÁGUAS DO PARÁ D SPE S.A. (CNPJ 61.067.904/0001-29), em casos de negativação indevida de consumidores (Serasa/SPC). Use quando o usuário apontar uma pasta de cliente com documentos do caso (faturas, comprovantes PIX, extrato Serasa, protocolos, laudos, prints) e pedir para 'redigir a petição', 'fazer a inicial', 'montar a ação contra a Águas do Pará', 'gerar peça de negativação', 'massificar' ou 'litigância de massa'. Diagnostica a sub-hipótese (pagou e foi negativado, negativado sem pagar, lote vendido, não-morador, cobrança em duplicidade), busca jurisprudência TJPA/STJ, redige em DOCX com tutela de urgência, inexigibilidade, repetição em dobro (quando cabível) e danos morais escalonados (piso R$ 10.000), revisa as citações e organiza a pasta de protocolo com a peça e as provas renomeadas (DOC-01...)."
license: Uso interno do escritório.
---

# Petição de Negativação Indevida — ÁGUAS DO PARÁ (JEC/PA)

## 1. O que esta skill faz

A partir de **uma pasta de cliente** contendo os documentos do caso, esta skill:

1. Lê e classifica todos os documentos (PDFs, imagens, áudios, transcrições).
2. **Diagnostica a sub-hipótese** do caso (ver seção 4).
3. Atualiza o banco de teses com uma **busca rápida na web** (TJPA/STJ).
4. **Redige a petição inicial em DOCX**, pronta para protocolo no PJe.
5. **Escalona o dano moral** conforme os agravantes presentes (piso R$ 10.000,00).
6. **Revisa** as citações jurisprudenciais (anti-erro fatal — ver seção 8).
7. **Organiza uma pasta única de protocolo** com a peça + provas renomeadas (DOC-01…).

> **Réu fixo:** AGUAS DO PARA D SPE S.A. — CNPJ 61.067.904/0001-29 — Av. Potiguá, Galeria Diamond, Sala 05 / R.A-613, Primavera, Parauapebas/PA, CEP 68.515-000 — tel. 0800 091 0091.
> **Foro padrão:** JEC da Comarca de Parauapebas/PA (CDC, art. 101, I — domicílio do consumidor). Confirmar se o cliente reside em outra comarca.

## 2. Arquivos da skill (leia conforme a etapa)

- `ADVOGADO.md` — dados fixos do advogado (cabeçalho/assinatura). **Leia sempre.**
- `referencias/modelo-peticao.md` — estrutura e redação-modelo da peça. **Leia antes de redigir.**
- `referencias/teses-juridicas.md` — banco de teses por matéria. **Leia antes de redigir.**
- `referencias/jurisprudencia.md` — precedentes TJPA/STJ verificados. **Leia antes de redigir.**
- `referencias/tabela-danos-morais.md` — escalonamento do quantum. **Leia ao calcular o pedido.**
- `referencias/checklist-protocolo.md` — conferência final. **Leia na revisão.**
- `scripts/build_peticao.js` — gerador do DOCX (Node + docx).
- `scripts/organizar_provas.py` — renomeia/organiza/converte as provas.

## 3. FLUXO OPERACIONAL (passo a passo)

### Passo 0 — Confirmar a pasta
Peça/confirme o caminho da pasta do cliente. Liste o conteúdo (recursivo). NÃO presuma.

### Passo 1 — Ler e classificar tudo
Leia cada documento e monte uma tabela: identidade do cliente (nome, CPF, endereço, e-mail), faturas (matrícula, valores, vencimentos, consumo m³), comprovantes de pagamento (PIX/boleto, datas, IDs, titular pagante), extrato Serasa (dívidas, datas, contratos, score antes/depois), protocolos da empresa, reclamação PROCON, laudos/atestados (vulnerabilidade/dano à saúde), prints e áudios.

### Passo 2 — Diagnosticar a sub-hipótese (seção 4)
Determine qual(is) sub-hipótese(s) se aplica(m). Isso define os pedidos.

### Passo 3 — PARAR e perguntar se houver lacuna
**Regra dura:** se faltar documento essencial ou houver ambiguidade que afete os fatos ou os pedidos (ex.: não dá para saber se houve pagamento; falta o extrato do Serasa; matrícula ilegível; dúvida sobre quem é o titular), **pare e pergunte ao usuário** antes de redigir. Liste objetivamente o que falta. Nunca invente fato.

### Passo 4 — Atualizar jurisprudência (web)
Faça 1–3 buscas rápidas para confirmar/atualizar precedentes do TJPA e valores recentes (ex.: "TJPA negativação indevida concessionária água dano moral", "TJPA Águas do Pará dano moral"). Acrescente o que achar de novo ao que já consta em `referencias/jurisprudencia.md`. **Nunca cite precedente cujo teor você não confirmou** (ver seção 8).

### Passo 5 — Calcular o dano moral (tabela)
Use `referencias/tabela-danos-morais.md`. Piso de R$ 10.000,00; somar agravantes; teto de alçada do JEC. Somar repetição em dobro ao valor da causa quando cabível.

### Passo 6 — Redigir a peça (DOCX)
Leia `referencias/modelo-peticao.md`, `teses-juridicas.md`, `jurisprudencia.md` e `ADVOGADO.md`. Gere o DOCX com `scripts/build_peticao.js` (ou redija seguindo o modelo). Formatação forense: A4, Times New Roman 12, espaçamento 1,5, justificado, paginação no rodapé.

### Passo 7 — Revisar (anti-erro fatal)
Rode o checklist da seção 8 e de `referencias/checklist-protocolo.md`. Valide o DOCX.

### Passo 8 — Organizar a pasta de protocolo
Rode `scripts/organizar_provas.py` (ou faça manualmente): crie `PROTOCOLO - [NOME DO CLIENTE]/`, renomeie provas como DOC-01…DOC-NN na ordem do rol, converta imagens JPEG/PNG → PDF (PJe só aceita PDF), una prints de uma mesma conversa em um único PDF, e coloque a petição (`00 - PETICAO INICIAL.docx`) e um `INDICE DE PROVAS.md`.

### Passo 9 — Entregar e reportar
Entregue a pasta e a peça com computer:// links. Reporte: sub-hipótese diagnosticada, valor da causa, pedidos, e pendências (dados a preencher, nova captura do Serasa na data do protocolo, etc.).

## 4. SUB-HIPÓTESES (o núcleo é SEMPRE negativação indevida)

| # | Situação | Pedidos típicos |
|---|---|---|
| **A** | Cliente PAGOU (ou terceiro pagou por ele) e mesmo assim foi negativado | Inexigibilidade + **repetição em dobro** (art. 42, § ún., CDC) + dano moral + tutela |
| **B** | Negativado SEM ter pago (cobrança de matrícula/lote que não é dele; não mora mais lá) | Inexigibilidade + dano moral + tutela (sem repetição) |
| **C** | Lote já VENDIDO há anos, cobrado e negativado no nome do antigo dono | Inexigibilidade + dano moral + tutela + (juntar contrato/escritura de venda) |
| **D** | Cobrança em DUPLICIDADE / a maior (pagou o de outro lote, pagou duas vezes) | Repetição em dobro + dano moral (se negativado) + inexigibilidade |
| **E** | Cobrança indevida ainda SEM negativação | Inexigibilidade + tutela preventiva (abster-se de negativar) + dano moral eventual |

> **Regra de ouro:** havendo pagamento de valor indevido → cabe **repetição em dobro** (Tema 929/STJ, para pagamentos após 30/03/2021). Não havendo pagamento → **não** se pede repetição. Em todas, se houve negativação → **dano moral in re ipsa**.

## 5. Diagnóstico de agravantes (para o quantum e a narrativa)
Verifique e documente, se presentes: (a) queda de score (print Serasa antes/depois); (b) vulnerabilidade — idoso, PcD, doença crônica (laudos); (c) dano à saúde com nexo (atestado/laudo pós-evento); (d) constrangimento a terceiros (prints/áudios); (e) inércia após PROCON/reclamação; (f) confissão escrita do erro pela ré (protocolos); (g) reincidência/tempo de negativação. Cada agravante entra na narrativa dos fatos E na dosimetria.

## 6. Valor da causa
`Valor da causa = dano moral (tabela) + repetição em dobro (se houver)`. Sempre ≤ 40 salários mínimos (limite do JEC; em 2026 ≈ R$ 60.720,00). Se ultrapassar, avisar o usuário e sugerir renúncia ao excedente ou rito comum.

## 7. Dados que a peça precisa (cheque na pasta; se faltar, PERGUNTE)
Cliente: nome completo, CPF, estado civil, profissão, endereço, e-mail. Réu: fixo (seção 1). Fatos: matrícula(s), faturas (nº, valor, vencimento, consumo), pagamento (data, valor, ID PIX, titular), negativação (data, contratos, valores, score antes/depois), PROCON (nº, data), protocolos da ré, vulnerabilidade/saúde. Advogado: `ADVOGADO.md`.

## 8. REVISÃO ANTI-ERRO FATAL (checklist jurídico obrigatório)
Antes de entregar, confirme **uma a uma**:
- [ ] Toda súmula citada corresponde ao tema certo. **Súmula 608/STJ é PLANO DE SAÚDE — NÃO usar para concessionária.** Aplicação do CDC à concessionária: CDC arts. 22 e 6º, X; Lei 8.987/95 art. 7º; Lei 13.460/2017.
- [ ] Nenhum REsp/acórdão citado sem teor confirmado. Em dúvida, use os precedentes verificados de `referencias/jurisprudencia.md` ou a tese genérica sem número.
- [ ] Repetição em dobro só se houve pagamento indevido (e após 30/03/2021 p/ Tema 929).
- [ ] Súmula 385/STJ — confirmar que NÃO há outras negativações legítimas (a contrario sensu). Se houver, ajustar a tese.
- [ ] Datas, valores, matrícula, CPF e nomes batem com os documentos.
- [ ] Referências cruzadas (DOC-XX) na peça batem com o rol/pasta.
- [ ] Valor da causa dentro do limite do JEC.
- [ ] Dados do advogado preenchidos (`ADVOGADO.md`); se faltarem, sinalizar pendência.
- [ ] Foro = domicílio do consumidor.
- [ ] Validar o DOCX.

## 9. Princípios de conduta
- **Pare e pergunte** diante de qualquer lacuna ou ambiguidade relevante.
- **Nunca invente** fatos, datas, valores ou jurisprudência.
- Entrega **apenas em DOCX** (peça) + provas em PDF; gere PDF da peça só se o usuário pedir.
- Mantenha a **numeração de provas coerente** entre peça e pasta.
- Linguagem jurídica forense, técnica e objetiva, em português do Brasil.
                                                                                                                                                                                                       