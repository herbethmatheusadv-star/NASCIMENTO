# Bugs do radar encontrados com dados reais — fila da Etapa 2

> Regra da casa: bug achado com dado real vira teste antes de virar correção
> (`RADAR/teste_*.py`). Nenhum destes foi corrigido ainda — o radar segue
> rodando às 07h com estas limitações conhecidas.

---

## BUG-01 · 🔴 CRÍTICO · prazo do recurso confundido com prazo de arquivamento

**Descoberto:** 15/07/2026, na triagem TJPA do PROC-0006
(0808637-09.2026.8.14.0040).

**O que aconteceu:** a sentença extintiva do JEC diz, em cláusulas diferentes:
- *"em caso de interposição de recurso inominado no prazo legal (**10 dias**)"*
  → este é o prazo do cliente;
- *"decorrido o prazo de **15 dias** sem manifestação das partes, arquive-se"*
  e *"aguarde-se o prazo de **15 (quinze) dias** para cumprimento voluntário"*
  → estes **não são** prazo do cliente.

O `detectar_prazo()` pegou **15 dias** e reportou *"detectado no texto"* —
rótulo que transmite confiança alta. Resultado: vencimento estimado em
**28/07** quando o real é **21/07**. **Erro de 7 dias, na direção perigosa**
(mais tempo do que existe).

**Por que é grave:** é o mesmo padrão do bug já corrigido "narrativa do acórdão
virando ordem" — o classificador lê o texto todo e não distingue *o prazo que
me obriga* de *prazos que a decisão menciona*. Um erro para mais é o que faz
perder prazo; e o rótulo "detectado no texto" desarma a desconfiança do leitor.

**Correção proposta (Etapa 2):**
1. Extrair prazo **só da vizinhança de gatilhos de recurso/providência da
   parte** ("interposição de", "recorrer", "interpor", "prazo para
   apresentar/manifestar"), nunca de "arquive-se", "cumprimento voluntário",
   "sob pena de arquivamento".
2. Quando o texto contiver **mais de um prazo distinto**, não escolher em
   silêncio: reportar **todos**, adotar o **menor** e marcar
   `confianca: baixa` + fila vermelha do briefing.
3. Tabela por rito (Motor v2): sentença em JEC → recurso inominado 10 dias;
   ED 5 dias. A tabela deve **prevalecer sobre a captura textual quando esta
   for maior que a tabela** — o inverso do que ocorreu aqui.
4. Teste de regressão com o teor real desta sentença (guardar amostra).

---

## BUG-02 · 🟡 falso positivo: termo de audiência vira prazo de 15 dias

**Descoberto:** mesma triagem, mesmo processo.

**O que aconteceu:** o **termo de audiência de conciliação** (sem acordo,
disp. 26/06) foi tratado como ato que abre prazo, com *"15 dias, padrão
assumido"* → alerta `[ATENCAO]` de vencimento em 20/07. **Não existe esse
prazo:** o termo apenas registra que a conciliação foi infrutífera.

**Efeito colateral perigoso:** ruído. Um alerta falso de 20/07 competindo com
o prazo verdadeiro de 21/07 embaralha a leitura — exatamente o mecanismo que o
`resolvidos.txt` foi criado para combater ("alerta que grita sem motivo faz
parar de ler o relatório").

**Correção proposta (Etapa 2):** classificar "termo/ata de audiência" como
informativo por padrão (como já se faz com "lista de distribuição"), **exceto**
quando o texto contiver ordem expressa com prazo à parte. Prazo "padrão
assumido" em ato informativo não deve virar `[ATENCAO]`.

---

## BUG-03 · 🟡 DJEN: bloco em HTTP 500 persistente esconde processo inteiro

**Descoberto:** 15/07/2026 (o processo PROC-0005 só apareceu porque o advogado
entregou os autos).

**O que aconteceu:** a janela **28/09→11/11/2025** respondeu 500 em ~28
tentativas ao longo do dia. A fatia **28/09→12/10** falha em **todos** os
tamanhos de página (5, 10, 20, 25, 30, 50, 75, 100) — não é o `itensPorPagina`
(hipótese testada e **descartada**). É intermitência com ponto quente: a mesma
janela respondeu uma vez com `pp=5`, e a **paginação recupera parte dos itens
mesmo quando a consulta cheia falha** (10 de 14 comunicações recuperadas
assim).

**Correção proposta (Etapa 2):**
1. **Fila de re-tentativa persistente entre execuções**: bloco falho é gravado
   em `_SISTEMA/logs/` e re-tentado nos dias seguintes até responder — avisar
   uma vez não basta (o aviso apareceu, e ainda assim o processo ficou 8 meses
   fora do radar).
2. **Sub-fatiamento adaptativo:** ao falhar, quebrar o bloco em fatias menores
   (15 → 7 → 3 → 1 dia) antes de desistir; e **paginar mesmo assim**, guardando
   o que vier.
3. **Vigilância por número** dos processos já cadastrados (`numeroProcesso=`),
   como segunda camada independente da busca por OAB.

---

## BUG-04 · 🟢 "De quem é" fica INCERTO em processo do próprio cliente

**Descoberto:** mesma triagem (PROC-0006 e TJMA 0805885-75).

**O que aconteceu:** o veredito saiu `INCERTO` mesmo com o termo de audiência
nomeando "AUTOR: DANIEL ... acompanhado de seu advogado Herbeth Matheus
Mendonça do Nascimento, OAB/PA 39.261" — o dado necessário estava no texto.

**Correção proposta (Etapa 2):** quando as fichas de PROCESSOS/ existirem
(agora existem), o polo do cliente vem da **ficha**, não da adivinhação
textual. O `INCERTO` deve ser exceção, não regra. Enquanto isso: usar o nome
do próprio advogado no texto como pista do polo.
