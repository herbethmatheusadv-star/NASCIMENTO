# PRAXE DECISÓRIA — falso consórcio

> Árvore de decisão do módulo `consumidor_consorcio`. **Tier A** = a sessão
> decide e registra DECISAO_SISTEMA no DIARIO. **Tier B** = a sessão recomenda
> e AGUARDA o "ok" do advogado (ver `decisoes_reservadas.md`).
> n=1 (caso 2026-0006) — camada LOCAL ainda vazia.

## RAMO 0 — Triagem (Tier A)

```
Cliente relata compra de casa/carro que virou consórcio?
├── tem 4+ marcas da seção 4 da ANATOMIA? ──> é este módulo
└── senão ──> consumidor geral ou cível
```
**Primeira providência, sempre:** `motor_audio.py <pasta da conversa>` e depois
`--relatorio`. Sem os áudios degravados NÃO se opina sobre viabilidade (o papel
está todo contra o cliente). *Tier A, inegociável.*

## RAMO 1 — A bifurcação que decide tudo (Tier A para apurar, Tier B para concluir)

```
A cota existe? Em qual administradora? Qual grupo?
├── RAMO A — existe, administradora autorizada pelo BACEN
│      alvo: a VENDA (T2, T3, T4, T5). Réus: corretora + corretor conveniado.
│      pedido central: rescisão + devolução da CORRETAGEM + danos morais.
│      a administradora só entra com prova de que se beneficiou/tolerou (Tier B).
│
├── RAMO B — não existe / nunca cadastrada / administradora não autorizada
│      alvo: a INEXECUÇÃO (T1 na frente, T2-T5 em reforço).
│      é o ramo mais forte: não depende de vencer a blindagem documental.
│      avaliar comunicação ao MP/PROCON e a hipótese criminal (Tier B).
│
└── INDETERMINADO — não se protocola. Bloqueia G2.
```

## RAMO 2 — Ordem das teses na peça (Tier A)

1. **T1** se Ramo B (inexecução — terreno onde a blindagem não protege)
2. **T4** sempre logo cedo (nulidade das cláusulas de blindagem) — **é ela que
   abre caminho para a prova oral ser valorada**; deixar T4 para o fim é erro
   de arquitetura, porque o juiz lê as declarações de ciência antes.
3. **T2** (vício de consentimento), ancorada na contradição temporal
4. **T3** (oferta que vincula / prática enganosa)
5. **T5** (solidariedade) — no capítulo da legitimidade passiva
6. **T6** só se a apuração do portal trouxer fato — senão não entra

## RAMO 3 — Rito e foro (Tier A / Tier B)

- Foro: comarca do domicílio do consumidor. No caso-fonte coincide com o eleito
  no contrato (Parauapebas/PA) — sem disputa. *Tier A.*
- **JEC × Vara Cível: Tier B.** O contrato de honorários do caso-fonte menciona
  a Lei 9.099/95, mas a escolha depende do valor da causa (que depende do Ramo)
  e da complexidade probatória. Caso com necessidade de perícia em áudio **não
  cabe no JEC** — e a defesa desta área ataca justamente a autenticidade da
  gravação. Decidir com o valor fechado, nunca antes.

## RAMO 4 — Prova (Tier A)

- Degravação com o rótulo obrigatório + relatório com o minuto de cada fala
  (`motor_audio.py --relatorio`) — a citação por minuto é o padrão da área.
- Áudio marcado pelo semáforo **não vira citação** sem escuta humana.
- Pedir na inicial a **exibição** de: contrato de adesão, número de grupo/cota,
  comprovante do repasse da 1ª parcela, gravação da "checagem telefônica" que o
  próprio contrato diz existir (P01 p.7: *"autoriza a checagem telefônica
  gravada"* — se ela existe, é prova deles que pode ser nossa).
- Antecipar o ataque à autenticidade da conversa: a degravação é de trabalho;
  se a autenticidade for controvertida, ata notarial/perícia. *Avisar o cliente
  do custo ANTES.*

## CAMADA LOCAL (Parauapebas / TJPA)

> Regra da casa: anotação com contagem; vira recomendação só com **n≥3 do mesmo
> juízo**; divergência do entendimento nacional = Tier B.

- (vazio — n=1). Primeiro caso: 2026-0006, ainda não protocolado.
- A preencher: como o juízo local trata declaração de ciência assinada em
  contrato de adesão; se aceita degravação de WhatsApp sem ata notarial; faixa
  de dano moral praticada.
