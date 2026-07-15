# Relatório do Spike — Conector PJe (PARCIAL)

> 15/07/2026. **Status: PARCIAL — os itens 1, 2 e 4 do spike não foram
> executados** (dependem de confirmação sua: ver `_SISTEMA/emendas.md`,
> Ressalvas 1–3). O que segue é o item 3 (MNI), que **não precisa de
> credencial** — e ele sozinho já muda o desenho do conector.

## 1. Resultado: existe porta oficial, e ela é boa (no TJPA)

O **MNI** (Modelo Nacional de Interoperabilidade, Res. CNJ 65/2008) é o
webservice oficial de intercomunicação do PJe. Testei os WSDLs — endpoints
**públicos**, sem login:

| Tribunal | Endpoint | Resultado |
|---|---|---|
| **TJPA 1º grau** | `pje.tjpa.jus.br/pje/intercomunicacao?wsdl` | ✅ **200 · WSDL completo (34.642 bytes)** |
| **TJPA 2º grau** | `pje.tjpa.jus.br/pje-2g/intercomunicacao?wsdl` | ✅ **200 · WSDL** |
| TJMA 1º grau | `pje.tjma.jus.br/pje/intercomunicacao?wsdl` | ⚠️ **403** (existe, mas barra a origem) |
| TRT-8 | 5 caminhos testados | ❌ 404 (caminho não descoberto) |
| PDPJ (Jus.br) | `portaldeservicos.pdpj.jus.br/api/v2/processos` | ⚠️ **403** (exige token) |

**Namespace confirmado:** `http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/`
— versão 2.2.2 do padrão nacional.

## 2. As 6 operações do MNI do TJPA — e as duas que o robô NUNCA pode chamar

```
consultarAvisosPendentes        ← a lista de EXPEDIENTES (o que o spike queria)
consultarProcesso               ← dados do processo + documentos (ACERVO/AUTOS)
consultarTeorComunicacao        ← ⚠️ teor da intimação — VER ALERTA
consultarAlteracao              ← mudanças desde uma data (ideal p/ radar diário)
confirmarRecebimento            ← 🔴 É "TOMAR CIÊNCIA". PROIBIDO.
entregarManifestacaoProcessual  ← 🔴 É PETICIONAR. PROIBIDO.
```

### 🔴 O achado que mais importa para a R7

**A porta oficial de leitura é a mesma porta de escrita.** O webservice que
lista os expedientes também tem `confirmarRecebimento` (dispara a ciência e o
prazo) e `entregarManifestacaoProcessual` (protocola peça). Isso reforça — e
muda o alvo — da sua R7-EXECUTÁVEL: a proibição não pode ser só "não clicar
no botão Responder" na interface; ela tem que ser **uma allowlist de operações
no código do cliente SOAP**, porque no MNI um `confirmarRecebimento` é uma
linha de código, indistinguível de um `consultarProcesso` para quem lê rápido.

**Proposta de implementação da R7 (código, não documento):**
- allowlist explícita: só `consultarAvisosPendentes`, `consultarProcesso`,
  `consultarAlteracao` são chamáveis;
- `confirmarRecebimento` e `entregarManifestacaoProcessual` **não existem** no
  cliente — não são "bloqueados por if", são **ausentes**; tentar chamá-los é
  `AttributeError`, não uma decisão de runtime;
- teste que falha se alguém adicionar essas operações ao cliente.

### ⚠️ `consultarTeorComunicacao` é zona cinzenta

Precisa de verificação empírica: **ler o teor de um aviso pendente pode
disparar a ciência** (é o que o botão da interface faz). Até que se prove o
contrário num aviso já ciente, ele entra na mesma allowlist negativa. A
quarentena que você desenhou cobre isto — e o MNI dá o dado de que ela precisa
(`consultarAvisosPendentes` diz **quais** estão pendentes, sem abrir nenhum).

## 3. Consequência para o desenho: rota por tribunal

| Tribunal | Rota provável | Observação |
|---|---|---|
| **TJPA** | **MNI** | WSDL público nos 2 graus. Se aceitar CPF+senha, o conector não precisa de navegador nenhum — nem de perfil persistente, nem de sessão. |
| **TJMA** | MNI (403 a resolver) | O 403 pode ser filtro de origem/user-agent; investigar antes de cair para navegador. |
| **TRT-8** | a descobrir | Caminho do WSDL não encontrado em 5 tentativas. A JT costuma expor o MNI; falta achar o path. |
| **PDPJ** | token | 403 sem credencial. É a porta do Jus.br. |

**Se o MNI atender, o item 1 do spike (Playwright + perfil persistente) fica
sem propósito no TJPA** — e com ele evapora a maior parte da Ressalva 2 das
emendas: sem navegador, não há cookie para persistir nem sessão para medir. O
que resta é **onde mora a credencial** — decisão sua, registrada nas emendas.

## 4. O que falta para o spike ficar completo

- **[bloqueado]** itens 1, 2 e 4 (navegador, Network, PDPJ) — aguardam sua
  confirmação nas emendas.
- **[bloqueado]** testar `consultarAvisosPendentes` com CPF+senha no TJPA —
  é o teste que decide tudo, e depende da sua decisão sobre credenciais.
- **[posso fazer já]** descobrir o path do MNI no TRT-8 e diagnosticar o 403
  do TJMA — ambos sem credencial.
- **[posso fazer já]** codificar as regras de ferro (R7 como allowlist,
  quarentena, watchdog, conduta) — você mesmo determinou que elas venham
  antes de qualquer leitura automática.

## 5. Nota sobre a fixture

Você citou *"os prints de hoje (10 expedientes; 19 processos = 16 Parauapebas
+ 3 Canaã)"* — **eles não chegaram nesta conversa.** Se puder anexá-los, viram
a fixture de teste do censo. Para calibrar: a varredura DJEN de hoje achou
**18 processos TJPA** (Parauapebas, Canaã e Turmas em Belém) — perto dos 19 que
você contou, o que é um bom sinal cruzado, e a diferença é exatamente o tipo de
coisa que o censo existe para resolver.
