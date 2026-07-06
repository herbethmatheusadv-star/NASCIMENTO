# MODELO E ESTRUTURA DA PETIÇÃO INICIAL

Formatação: **A4, Times New Roman 12, espaçamento 1,5, justificado, recuo de 1ª linha 1,25 cm,
paginação no rodapé.** Citações longas em recuo, fonte 11. Use `scripts/build_peticao.js` (parametrizável)
ou redija seguindo esta estrutura.

---

## ESTRUTURA (ordem fixa)

### 1. Endereçamento
`EXCELENTÍSSIMO(A) SENHOR(A) DOUTOR(A) JUIZ(ÍZA) DE DIREITO DO JUIZADO ESPECIAL CÍVEL DA COMARCA DE [COMARCA] — ESTADO DO PARÁ.`

### 2. Linha de flags
`Pedido de gratuidade da justiça: [SIM/NÃO]. Pedido de tutela de urgência inaudita altera parte: SIM.`

### 3. Qualificação da parte autora
Nome, nacionalidade, estado civil, profissão, CPF, (vulnerabilidade se houver), endereço, e-mail, "por seu advogado infra-assinado (procuração anexa)", com fulcro nos dispositivos (ver `teses-juridicas.md` › preâmbulo), "propor a presente".

### 4. Nome da ação
`AÇÃO DECLARATÓRIA DE INEXIGIBILIDADE DE DÉBITO C/C [REPETIÇÃO DE INDÉBITO EM DOBRO E] INDENIZAÇÃO POR DANOS MORAIS, COM PEDIDO DE TUTELA DE URGÊNCIA INAUDITA ALTERA PARTE`
(incluir "REPETIÇÃO DE INDÉBITO EM DOBRO" apenas nas sub-hipóteses A e D).

### 5. Qualificação da ré (FIXA)
`em face de ÁGUAS DO PARÁ D SPE S.A., concessionária de serviço público de abastecimento de água e esgotamento sanitário, CNPJ 61.067.904/0001-29, com endereço na Av. Potiguá, Galeria Diamond, Sala 05 / R.A-613, Primavera, Parauapebas/PA, CEP 68.515-000.`

### 6. I — DOS FATOS
Narrar em subitens, na ordem cronológica, ancorando CADA fato a um DOC:
- I.1 Relação de consumo / origem do débito (migração SAAEP→Águas do Pará, se aplicável; matrícula; consumo zero; lote alheio/vendido).
- I.2 (se houver pagamento) O pagamento — data, valor, ID PIX, titular (CC art. 304 se terceiro pagou).
- I.3 A negativação — data, contratos, valores, queda de score.
- I.4 Reclamação no PROCON / administrativa (se houver) e inércia da ré.
- I.5 Confissão escrita do erro (se houver protocolo).
- I.6 Danos / vulnerabilidade / dano à saúde / constrangimento (se houver).
> Adaptar os subitens à sub-hipótese (B/C: foco em "não é/não era o titular"; sem pagamento).

### 7. II — DO DIREITO
Selecionar as teses pertinentes de `teses-juridicas.md`:
- II.1 Incidência do CDC + responsabilidade objetiva (**sem Súmula 608**).
- II.2 Inexigibilidade do débito.
- II.3 (A/D) Repetição em dobro — Tema 929/STJ.
- II.4 Dano moral in re ipsa — Súmula 385 (a contrario) + REsp 2.282.338/MG + TJPA.
- II.5 Quantum (tabela) — proporcionalidade/razoabilidade + caráter pedagógico (CC art. 944).
- II.6 Tutela de urgência — CPC art. 300 c/c CDC art. 84 (fumus + periculum + reversibilidade).

### 8. III — DOS PEDIDOS
a) Tutela de urgência inaudita altera parte: exclusão do nome dos cadastros (Serasa/SPC/Boa Vista/Quod) em 48h, sob astreintes (R$ 500/dia);
b) Abstenção de nova inscrição pelos mesmos débitos, sob multa;
c) Citação da ré para audiência de conciliação (art. 16, Lei 9.099/95) e contestação;
d) Inversão do ônus da prova (CDC art. 6º, VIII);
e) Gratuidade da justiça (se hipossuficiência juntada);
f) No mérito, procedência para: (i) DECLARAR a inexigibilidade dos débitos [identificar]; (ii) [A/D] CONDENAR à repetição em dobro de R$ [X]; (iii) CONDENAR a danos morais de R$ [Y]; (iv) honorários em caso de recurso; (v) oficiar aos órgãos de proteção ao crédito.

### 9. III.A — Rol probatório
Protesto por provas; depoimento pessoal do representante da ré; testemunhas (se houver), independentemente de prévio rol (art. 34, Lei 9.099/95).

### 10. III.B — Valor da causa
`R$ [valor] (por extenso)` = dano moral + repetição (se houver). Dentro do limite do JEC.

### 11. Fecho
"Termos em que, pede e espera deferimento." + local/data + bloco de assinatura (de `ADVOGADO.md`).

### 12. ANEXO ÚNICO — Rol de documentos
Lista DOC-01…DOC-NN na MESMA ordem e numeração da pasta de protocolo.

---

## REGRAS DE REDAÇÃO
- Toda afirmação de fato deve apontar o DOC correspondente.
- Citações de áudio: identificar arquivo + trecho transcrito + (DOC-XX).
- Não usar Súmula 608/STJ. Não citar precedente sem teor confirmado.
- Ajustar gênero/dados ao cliente. Remover seções inaplicáveis (ex.: repetição em dobro nas sub-hipóteses B/C/E).
- Linguagem técnica, objetiva, sem floreios excessivos.
