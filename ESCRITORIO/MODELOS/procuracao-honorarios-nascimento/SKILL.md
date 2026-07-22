---
name: procuracao-honorarios-nascimento
description: "Gera PROCURAÇÃO (ad judicia et extra) e CONTRATO DE HONORÁRIOS no padrão do Juizado Especial Cível do escritório NASCIMENTO ADVOGADOS, dentro do timbrado oficial e SEMPRE em .docx. Use SEMPRE que o usuário pedir para 'fazer/gerar/montar a procuração', 'fazer o contrato de honorários', 'procuração e contrato pro cliente X', 'gerar procuração', 'contrato de honorários do JEC', 'documentos para o cliente assinar', ou entregar/apontar uma pasta de caso pedindo a procuração e/ou o contrato. Só muda a QUALIFICAÇÃO do cliente, o OBJETO (nome da ação) e o(s) RÉU(S); o resto (poderes, cláusulas 2ª–11ª, advogado/contratado, foro de Parauapebas/PA) é padrão e já vem pronto. Acione mesmo sem a palavra 'skill'."
license: Uso interno do escritório Nascimento Advocacia.
---

# Procuração + Contrato de Honorários (JEC) — Nascimento Advocacia

Gera dois documentos prontos para o cliente assinar, no **timbrado oficial**
(logo no cabeçalho, contatos no rodapé) e no padrão de formatação do escritório
(Century Gothic 11, justificado, margens 3/2/2/2):

1. **PROCURAÇÃO** — *ad judicia et extra*, poderes gerais e especiais.
2. **CONTRATO DE PRESTAÇÃO DE SERVIÇOS ADVOCATÍCIOS** — padrão **Juizado Especial
   Cível** (11 cláusulas: objeto, obrigações, honorários de êxito 50%, sucumbência,
   custas/gratuidade, tutelas, desistência, revogação, LGPD, foro).

## 1. O que VARIA por caso × o que é FIXO

**Varia (você preenche):**
- `cliente` — a **qualificação completa** do outorgante/contratante.
- `objeto` — o nome da ação (só p/ o contrato).
- `reus` — o(s) réu(s) qualificado(s) (só p/ o contrato).
- `data` — opcional; se não passar, entra a **data de hoje** automaticamente.

**Fixo (já embutido, NÃO mexer sem o titular pedir):**
- Todos os **poderes** da procuração.
- As **cláusulas 2ª a 11ª** do contrato e o **Parágrafo Único** da 1ª.
- O **CONTRATADO/advogado**: Dr. Herbeth Matheus Mendonça do Nascimento, OAB/PA 39.261.
- **Honorários de êxito: 50%** (mude só via campo `honorarios` se o titular decidir).
- **Foro: Comarca de Parauapebas/PA.**

## 2. Regras de ouro

- **Saída SEMPRE em `.docx`.** NUNCA entregue PDF: a conversão troca a fonte
  Century Gothic por uma substituta e o documento sai visualmente diferente. O
  advogado imprime direto do Word.
- **Salve os arquivos na PASTA DO CASO** (`CASOS/<CLIENTE>/…`) e entregue o link.
- **Confirme a qualificação com o cliente** antes de assinar (nome, estado civil,
  RG e órgão, CPF, endereço). Puxe os dados dos documentos do caso; havendo
  divergência entre fontes (ex.: B.O. × contrato), **pergunte** — nunca invente dado.
- O 1º trecho de `cliente` (antes da 1ª vírgula) vira o **nome** na assinatura e no
  nome do arquivo. O CPF sob a assinatura é extraído do texto (ou passe `cliente_cpf`).

## 3. Fluxo

**Passo 1 — Reunir os dados.** Monte um `dados.json` (modelo em
`referencias/dados.exemplo.json`). Exemplo mínimo p/ só a procuração: apenas
`cliente`. Para o contrato, inclua também `objeto` e `reus`.

**Passo 2 — Gerar.**
```
pip install python-docx --break-system-packages   # se necessário
python scripts/gerar_procuracao_contrato.py --dados dados.json --saida-dir "<pasta do caso>"
```
Opções: `--so procuracao` ou `--so contrato` (padrão: `ambos`); `--data "22 de
julho de 2026"` para fixar a data; `--template` para outro timbrado.

**Passo 3 — Conferir e entregar.** Confira o `.docx` (qualificação, objeto, réus,
assinatura) e entregue o link ao usuário. Se pedir, grave também na pasta do caso
do dispositivo. **Não gere PDF.**

## 4. Preset — golpe de consórcio (J Ferreira / Lima Financeira)

Litígio de massa recorrente (vítimas de falsa contemplação de consórcio). Use como
`objeto` e `reus`:
- **objeto:** `AÇÃO DE RESCISÃO CONTRATUAL POR VÍCIO DE CONSENTIMENTO C/C RESTITUIÇÃO INTEGRAL DE VALORES, INDENIZAÇÃO POR DANOS MORAIS`
- **reus:**
  - `**J. FERREIRA REPRESENTAÇÕES LTDA**, pessoa jurídica de direito privado, inscrita no CNPJ/ME nº 43.674.644/0001-78, situada na Avenida Rio Grande, nº 155, Bairro Beiro Rio, Parauapebas – PA, CEP 68515-000; e`
  - `**LIMA FINANCEIRA LTDA**, pessoa jurídica de direito privado, inscrita no CNPJ/ME nº 46.603.969/0001-58, situada na Avenida Rio Grande, nº 155, Bairro Beiro Rio, Parauapebas – PA, CEP 68515-000`

> Envolva o **nome da empresa ré em `**negrito**`** dentro do texto de cada réu.

## 5. Arquivos da skill
- `scripts/gerar_procuracao_contrato.py` — gerador (Python + python-docx). É o motor.
- `assets/Timbrado Oficial Nascimento.docx` — timbrado base (logo + rodapé).
- `referencias/modelo-procuracao.md` — texto integral da procuração (poderes fixos).
- `referencias/modelo-contrato-honorarios-jec.md` — texto integral do contrato.
- `referencias/dados.exemplo.json` — exemplo de entrada (caso Edson).
