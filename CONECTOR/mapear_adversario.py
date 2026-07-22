# -*- coding: utf-8 -*-
"""
mapear_adversario.py — MAPA DO ADVERSARIO: todos os processos de uma empresa
(ou pessoa) num tribunal, sem login, sem captcha, de graca.

POR QUE ISTO EXISTE (e por que o caminho obvio nao funciona):

  - O DataJud publico NAO devolve parte nenhuma. Testado em 22/07/2026: o
    indice traz tribunal, grau, numeroProcesso, dataAjuizamento, nivelSigilo,
    orgaoJulgador, classe, assuntos, movimentos. Nome/CPF/CNPJ foram retirados.
    Logo, "buscar por CNPJ no DataJud" e impossivel — nao e limitacao nossa.
  - A consulta publica do TJPA busca por NOME (nao por CNPJ), exige CAPTCHA e
    tem teto de resultados. O robo nao resolve captcha.

  A porta que FUNCIONA e a mesma que Escavador e Jusbrasil usam: o DIARIO.
  Toda publicacao do DJEN traz o nome das partes, e a API publica
  `comunicaapi.pje.jus.br/api/v1/comunicacao` aceita o filtro `nomeParte`.
  Ingerindo o diario constroi-se o indice nome -> processo. E isso aqui.

O QUE ELE ENTREGA
  - a lista de processos DISTINTOS em que o alvo aparece, com vara, classe,
    data e as OUTRAS partes (co-reus, consumidores, administradoras);
  - o texto integral de cada publicacao (materia-prima da jurimetria);
  - o cruzamento com o DataJud por processo (assuntos + cadeia de movimentos),
    que e onde se le o DESFECHO sem abrir os autos.

AVISO DE PRECISAO — a busca e por NOME, entao ela erra para os dois lados:
  - homonimos entram ("J FERREIRA" traz 4.753 publicacoes do pais inteiro);
  - a razao social do contrato pode nao ser a usada no processo (no caso
    2026-0006, "J FERREIRA REPRESENTACOES" nao acha nada no TJPA, e
    "FERREIRA REPRESENTACOES" acha 58).
  Por isso: SEMPRE rodar variantes, SEMPRE filtrar por tribunal, e SEMPRE
  conferir na lista de partes antes de tratar um processo como do alvo.
  Este script NAO confirma identidade — ele levanta candidatos.

Uso:
  python CONECTOR/mapear_adversario.py "FERREIRA REPRESENTACOES" --tribunal TJPA
  python CONECTOR/mapear_adversario.py "FERREIRA REPRESENTACOES" "LIMA FINANCEIRA" \
         --tribunal TJPA --pasta ADVERSARIOS/jferreira --datajud
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DJEN = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
DATAJUD = "https://api-publica.datajud.cnj.jus.br/api_publica_{indice}/_search"
# chave PUBLICA que o CNJ divulga na documentacao (mesma ja usada pelo RADAR)
CHAVE_CNJ = ("cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw==")

UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}


def _get(url: str, timeout=90, tentativas=4):
    erro = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:                       # rede/HTTP: tenta de novo
            erro = e
            time.sleep(1.5 * (i + 1))
    print(f"[AVISO] falhou apos {tentativas} tentativas: {str(erro)[:90]}")
    return None


# ------------------------------------------------------------------ DJEN
def buscar_djen(nome: str, tribunal: str | None, por_pagina=100, max_paginas=40):
    """Todas as comunicacoes do DJEN em que 'nome' figura como parte."""
    itens, pagina = [], 1
    while pagina <= max_paginas:
        p = {"nomeParte": nome, "itensPorPagina": por_pagina, "pagina": pagina}
        if tribunal:
            p["siglaTribunal"] = tribunal
        d = _get(f"{DJEN}?{urllib.parse.urlencode(p)}")
        if not d:
            break
        lote = d.get("items") or []
        itens.extend(lote)
        total = d.get("count") or 0
        if len(lote) < por_pagina or len(itens) >= total:
            break
        pagina += 1
    return itens


def limpar(t: str) -> str:
    t = re.sub(r"<[^>]+>", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()


# --------------------------------------------------------------- DataJud
def datajud_processo(cnj_sem_mascara: str, sigla: str):
    """Metadados + cadeia de MOVIMENTOS (onde se le o desfecho)."""
    corpo = json.dumps({"query": {"match": {"numeroProcesso": cnj_sem_mascara}},
                        "size": 1}).encode()
    url = DATAJUD.format(indice=sigla.lower())
    req = urllib.request.Request(url, data=corpo, method="POST", headers={
        "Authorization": f"APIKey {CHAVE_CNJ}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
    except Exception:
        return None
    hits = d.get("hits", {}).get("hits", [])
    return hits[0]["_source"] if hits else None


def main():
    ap = argparse.ArgumentParser(description="Mapa do adversario via DJEN (sem login).")
    ap.add_argument("nomes", nargs="+", help="Variantes do nome da parte")
    ap.add_argument("--tribunal", help="Sigla, ex.: TJPA (recomendado: sem isso vem o pais inteiro)")
    ap.add_argument("--pasta", default=None, help="Pasta de saida (padrao: ADVERSARIOS/<slug>)")
    ap.add_argument("--datajud", action="store_true",
                    help="Cruza cada processo com o DataJud (classe, assuntos, movimentos)")
    args = ap.parse_args()

    slug = re.sub(r"[^A-Za-z0-9]+", "_", args.nomes[0]).strip("_").lower()
    pasta = Path(args.pasta) if args.pasta else RAIZ / "ADVERSARIOS" / slug
    if not pasta.is_absolute():
        pasta = RAIZ / pasta
    pasta.mkdir(parents=True, exist_ok=True)

    print(f"[..] DJEN: {len(args.nomes)} variante(s)"
          + (f", tribunal {args.tribunal}" if args.tribunal else " (BRASIL INTEIRO)"))

    todas, por_processo = [], {}
    for nome in args.nomes:
        itens = buscar_djen(nome, args.tribunal)
        print(f"     '{nome}': {len(itens)} publicacao(oes)")
        for i in itens:
            i["_busca"] = nome
            cnj = i.get("numeroprocessocommascara") or i.get("numero_processo")
            if not cnj:
                continue
            todas.append(i)
            por_processo.setdefault(cnj, []).append(i)

    if not por_processo:
        sys.exit("[ERRO] Nenhuma publicacao. Tente outra variante do nome "
                 "(no caso 2026-0006, 'J FERREIRA REPRESENTACOES' nao acha nada "
                 "no TJPA e 'FERREIRA REPRESENTACOES' acha 58).")

    # --- consolida por processo
    linhas = []
    for cnj, pubs in por_processo.items():
        pubs.sort(key=lambda x: x.get("data_disponibilizacao") or "")
        partes, orgaos, classes = set(), set(), set()
        for p in pubs:
            for d in (p.get("destinatarios") or []):
                n = d.get("nome") if isinstance(d, dict) else d
                if n:
                    partes.add(str(n).strip())
            if p.get("nomeOrgao"):
                orgaos.add(p["nomeOrgao"])
            if p.get("nomeClasse"):
                classes.add(p["nomeClasse"])
        linhas.append({
            "cnj": cnj,
            "tribunal": pubs[0].get("siglaTribunal"),
            "orgaos": sorted(orgaos),
            "classes": sorted(classes),
            "primeira_publicacao": pubs[0].get("data_disponibilizacao"),
            "ultima_publicacao": pubs[-1].get("data_disponibilizacao"),
            "n_publicacoes": len(pubs),
            "partes": sorted(partes),
            "publicacoes": [{"data": p.get("data_disponibilizacao"),
                             "orgao": p.get("nomeOrgao"),
                             "classe": p.get("nomeClasse"),
                             "tipo": p.get("tipoComunicacao"),
                             "texto": limpar(p.get("texto")),
                             "link": p.get("link")} for p in pubs],
        })
    linhas.sort(key=lambda x: x["primeira_publicacao"] or "")

    # --- cruza com DataJud (assuntos + movimentos = o desfecho)
    if args.datajud:
        print(f"[..] DataJud: cruzando {len(linhas)} processo(s)...")
        for n, L in enumerate(linhas, 1):
            sigla = L["tribunal"] or (args.tribunal or "")
            if not sigla:
                continue
            dj = datajud_processo(re.sub(r"\D", "", L["cnj"]), sigla)
            if dj:
                L["datajud"] = {
                    "classe": (dj.get("classe") or {}).get("nome"),
                    "assuntos": [a.get("nome") for a in (dj.get("assuntos") or [])],
                    "orgao": (dj.get("orgaoJulgador") or {}).get("nome"),
                    "ajuizamento": dj.get("dataAjuizamento"),
                    "grau": dj.get("grau"),
                    "movimentos": [{"data": m.get("dataHora"), "nome": m.get("nome"),
                                    "codigo": m.get("codigo")}
                                   for m in (dj.get("movimentos") or [])],
                }
            if n % 10 == 0:
                print(f"     {n}/{len(linhas)}")

    (pasta / "processos.json").write_text(
        json.dumps(linhas, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- relatorio legivel
    md = [f"# MAPA DO ADVERSARIO — {', '.join(args.nomes)}", "",
          f"- Gerado em {date.today().isoformat()} pelo DJEN "
          f"(`comunicaapi.pje.jus.br`) — sem login, sem captcha",
          f"- Tribunal: **{args.tribunal or 'TODOS'}** · "
          f"**{len(linhas)} processos** · {len(todas)} publicações", "",
          "> ⚠️ Busca por NOME: pode trazer homônimo e pode perder variação de "
          "razão social. **Conferir a lista de partes de cada processo antes de "
          "tratar como do alvo.**", "",
          "## Processos", "",
          "| # | Processo | Órgão | Classe | 1ª publ. | últ. publ. | publ. |",
          "|---|---|---|---|---|---|---|"]
    for n, L in enumerate(linhas, 1):
        md.append(f"| {n} | `{L['cnj']}` | {'; '.join(L['orgaos'])[:60]} | "
                  f"{'; '.join(L['classes'])[:40]} | {(L['primeira_publicacao'] or '')[:10]} | "
                  f"{(L['ultima_publicacao'] or '')[:10]} | {L['n_publicacoes']} |")
    md += ["", "## Partes por processo (quem litiga contra quem)", ""]
    for n, L in enumerate(linhas, 1):
        md.append(f"### {n}. `{L['cnj']}` — {'; '.join(L['classes'])}")
        md.append(f"- Órgão: {'; '.join(L['orgaos'])}")
        md.append(f"- Partes: {', '.join(L['partes']) or '(não informadas)'}")
        if L.get("datajud"):
            dj = L["datajud"]
            md.append(f"- Assuntos (DataJud): {', '.join(a for a in dj['assuntos'] if a)}")
            md.append(f"- Movimentos: {len(dj['movimentos'])}")
        md.append("")
    (pasta / "MAPA.md").write_text("\n".join(md), encoding="utf-8", newline="\n")

    print(f"\n[OK] {len(linhas)} processo(s) distinto(s), {len(todas)} publicacao(oes).")
    print(f"     {pasta / 'MAPA.md'}")
    print(f"     {pasta / 'processos.json'}  (texto integral das publicacoes)")
    print("\nLEMBRETE: busca por NOME — conferir as partes antes de tratar como do alvo.")


if __name__ == "__main__":
    main()
