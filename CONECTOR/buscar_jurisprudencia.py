# -*- coding: utf-8 -*-
"""
buscar_jurisprudencia.py — jurisprudencia NACIONAL por texto livre, sem login,
sem captcha, de graca. A porta que o Jusbrasil/Escavador usam.

O RACIOCINIO QUE LEVOU AQUI (registrar, porque e o metodo, nao o truque):
  - As consultas de jurisprudencia dos tribunais tem CAPTCHA (TJMG) ou sao
    SPA que nao respondem por URL (TJRS). Parecia bloqueado.
  - Mas Jusbrasil e Escavador tem TUDO. Logo NAO passam por ali.
  - Eles ingerem o DIARIO. E o diario publica ACORDAO COM EMENTA.
  - A API publica do DJEN (`comunicaapi.pje.jus.br`), que o SOJ ja usava so com
    `numeroOab`, aceita tambem o parametro **`texto`** — busca em TEXTO INTEGRAL
    de tudo que foi publicado por TODOS os tribunais do pais.
  - Testado em 22/07/2026: `texto="golpe do consorcio"` -> 625 publicacoes
    nacionais, entre elas acordaos do TJPA, TJCE, TJES, TJMA, TJBA, TJPB...
  (Os parametros `textoPesquisa`, `termo` e `q` sao IGNORADOS pela API — devolvem
   o total geral. So `texto` filtra de verdade. Nao confundir.)

LIMITE HONESTO: isto acha o que foi PUBLICADO NO DIARIO no periodo indexado —
nao e o acervo historico completo de um tribunal. Ementa antiga que nunca foi
republicada nao aparece. Para essas, ainda e preciso a consulta do tribunal
(com o captcha resolvido pelo advogado).

Uso:
  python CONECTOR/buscar_jurisprudencia.py "golpe do consorcio" --tribunal TJPA
  python CONECTOR/buscar_jurisprudencia.py "vicio de consentimento consorcio" --so-acordaos
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
SEG_GRAU = re.compile(r"C.mara|Turma|Desembargador|Relator|Se..o", re.I)
TEM_EMENTA = re.compile(r"EMENTA|AC.RD.O|Acordam", re.I)


def _get(params, tentativas=3):
    url = f"{API}?{urllib.parse.urlencode(params)}"
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except Exception as e:
            erro = e
            time.sleep(1.5 * (i + 1))
    print(f"[AVISO] {str(erro)[:80]}")
    return {}


def limpar(t):
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()


def main():
    ap = argparse.ArgumentParser(description="Jurisprudencia nacional pelo DJEN.")
    ap.add_argument("termo", help='Ex.: "golpe do consorcio"')
    ap.add_argument("--tribunal", help="Sigla (TJPA, TJSP...). Sem isso: o pais inteiro")
    ap.add_argument("--so-acordaos", action="store_true",
                    help="So orgaos de 2o grau com ementa/acordao no texto")
    ap.add_argument("--paginas", type=int, default=3, help="Paginas de 100 (padrao 3)")
    ap.add_argument("--saida", help="Arquivo .md de saida")
    args = ap.parse_args()

    itens = []
    for pag in range(1, args.paginas + 1):
        p = {"texto": args.termo, "itensPorPagina": 100, "pagina": pag}
        if args.tribunal:
            p["siglaTribunal"] = args.tribunal
        d = _get(p)
        lote = d.get("items") or []
        if pag == 1:
            print(f"[..] '{args.termo}'"
                  + (f" em {args.tribunal}" if args.tribunal else " no BRASIL")
                  + f": {d.get('count')} publicacao(oes)")
        itens.extend(lote)
        if len(lote) < 100:
            break

    vistos, sel = set(), []
    for i in itens:
        t = limpar(i.get("texto"))
        if args.so_acordaos and not (SEG_GRAU.search(str(i.get("nomeOrgao", "")))
                                     and TEM_EMENTA.search(t) and len(t) > 700):
            continue
        chave = (i.get("numeroprocessocommascara"), t[:120])
        if chave in vistos:
            continue
        vistos.add(chave)
        sel.append((i, t))

    print(f"[OK] {len(sel)} resultado(s)"
          + (" de 2o grau com ementa" if args.so_acordaos else "") + "\n")

    linhas = [f"# JURISPRUDÊNCIA — \"{args.termo}\"", "",
              f"- Fonte: **DJEN** (`comunicaapi.pje.jus.br`), publicação oficial — "
              f"sem login, sem captcha",
              f"- Escopo: {args.tribunal or 'BRASIL'} · {len(sel)} resultado(s)", "",
              "> ⚠️ A ementa abaixo vem da **publicação no diário**, que é fonte "
              "oficial do ato. Ainda assim, antes de citar em peça, conferir o "
              "**inteiro teor do acórdão** — a publicação pode vir truncada.", ""]
    for i, t in sel:
        linhas += [f"## {i.get('siglaTribunal')} · `{i.get('numeroprocessocommascara')}`",
                   f"- **Órgão:** {i.get('nomeOrgao')}",
                   f"- **Classe:** {i.get('nomeClasse')} · **Publicado:** {i.get('data_disponibilizacao')}",
                   ""]
        m = re.search(r"(EMENTA.{0,2500})", t, re.I | re.S)
        linhas += ["```", (m.group(1) if m else t[:1500]), "```", ""]
        print(f"  [{i.get('siglaTribunal')}] {i.get('numeroprocessocommascara')} — "
              f"{str(i.get('nomeOrgao'))[:55]}")

    destino = Path(args.saida) if args.saida else \
        RAIZ / "_efemeros" / f"JURIS_{re.sub(r'[^a-z0-9]+','_',args.termo.lower())[:40]}.md"
    if not destino.is_absolute():
        destino = RAIZ / destino
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas), encoding="utf-8", newline="\n")
    print(f"\n     {destino}")


if __name__ == "__main__":
    main()
