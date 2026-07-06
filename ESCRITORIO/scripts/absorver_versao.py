# -*- coding: utf-8 -*-
"""
absorver_versao.py — PORTA DE RETORNO (blueprint, seção 7).
O advogado devolveu a versão DELE da peça (.md ou .docx). Este script faz a
parte mecânica: extrai o texto, compara com a última minuta do sistema (sem
as tags SOJ) e gera o relatório de diferenças para a CLASSIFICAÇÃO na sessão:

  estilo          -> absorve e marca para colheita (COLHEITA: no DIARIO)
  fato novo       -> exige F## com prova ou status honesto de alegação
  citação nova    -> VERIFICAR NA FONTE antes de aceitar (verbete na BASE_LEGAL)
  quantum/pedido  -> reconciliar com as decisões (DECISAO_ADVOGADO com "ok")

Depois da classificação (sessão): re-taguear, salvar como vNN (NUNCA
sobrescrever), DIARIO, re-rodar o gate da fase, e só então regerar o DOCX.
Regra de ouro: a versão protocolada é SEMPRE a última que o sistema conhece.

Uso:
  python absorver_versao.py CLIENTE CAMINHO_DA_VERSAO_DO_ADVOGADO
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

import soj_lib as soj

TAG_LINHA_RE = re.compile(r"^\s*<!--\s*SOJ:.*?-->\s*$")


def paragrafos_md(texto):
    blocos, atual = [], []
    for linha in texto.splitlines():
        if TAG_LINHA_RE.match(linha):
            continue
        if linha.strip() == "" or linha.strip() == "---":
            if atual:
                blocos.append(" ".join(atual).strip())
                atual = []
        else:
            atual.append(linha.strip())
    if atual:
        blocos.append(" ".join(atual).strip())
    # descarta blocos de comentario interno
    return [b for b in blocos if not b.startswith("<!--")]


def paragrafos_docx(caminho):
    try:
        from docx import Document
    except ImportError:
        sys.exit("[ERRO] python-docx nao instalado (pip install python-docx).")
    return [p.text.strip() for p in Document(str(caminho)).paragraphs
            if p.text.strip()]


def extrair_paragrafos(caminho):
    """Extrai paragrafos de .md (sem tags SOJ/comentarios) ou .docx."""
    caminho = Path(caminho)
    if caminho.suffix.lower() == ".docx":
        return paragrafos_docx(caminho)
    return paragrafos_md(caminho.read_text(encoding="utf-8"))


def _itemiza(antes, depois):
    """Pareia paragrafos de um bloco alterado por similaridade, para que
    cada mudanca real vire UM item classificavel."""
    itens, usados = [], set()
    for d in depois:
        melhor, melhor_r = None, 0.0
        for i, a in enumerate(antes):
            if i in usados:
                continue
            r = difflib.SequenceMatcher(a=a, b=d).ratio()
            if r > melhor_r:
                melhor, melhor_r = i, r
        if melhor is not None and melhor_r >= 0.6:
            usados.add(melhor)
            if antes[melhor] != d:
                itens.append(("alterado", antes[melhor], d))
        else:
            itens.append(("acrescentado", None, d))
    for i, a in enumerate(antes):
        if i not in usados:
            itens.append(("removido", a, None))
    return itens


def diff_itemizado(base, nova):
    """Diff de listas de paragrafos, itemizado mudanca a mudanca.
    Devolve lista de (tipo, antes|None, depois|None). Sem efeitos colaterais."""
    sm = difflib.SequenceMatcher(a=base, b=nova, autojunk=False)
    mudancas = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        mudancas.extend(_itemiza(base[i1:i2], nova[j1:j2]))
    return mudancas


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Porta de retorno do SOJ.")
    ap.add_argument("cliente")
    ap.add_argument("arquivo", help="Versao do advogado (.md ou .docx)")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    origem = Path(args.arquivo)
    if not origem.is_file():
        sys.exit(f"[ERRO] Arquivo nao encontrado: {origem}")

    minuta = soj.minuta_atual(pasta)
    if minuta is None:
        sys.exit("[ERRO] O caso nao tem MINUTA_v*.md — nada com que comparar.")

    base = paragrafos_md(minuta.read_text(encoding="utf-8"))
    if origem.suffix.lower() == ".docx":
        nova = paragrafos_docx(origem)
    else:
        nova = paragrafos_md(origem.read_text(encoding="utf-8"))

    mudancas = diff_itemizado(base, nova)

    carimbo = soj.agora().replace(":", "").replace(" ", "_")
    (pasta / "_efemeros").mkdir(exist_ok=True)
    destino = pasta / "_efemeros" / f"ABSORCAO_{carimbo}.md"

    out = [f"# PORTA DE RETORNO — diff da versão do advogado ({origem.name}) "
           f"contra {minuta.name}",
           "",
           f"Gerado em {soj.agora()}. {len(mudancas)} bloco(s) de mudança.",
           "",
           "> CLASSIFICAR cada mudança na sessão: **estilo** (absorve + marca "
           "COLHEITA) · **fato novo** (exige F## com prova/alegação) · "
           "**citação nova** (VERIFICAR NA FONTE — verbete antes de aceitar) · "
           "**quantum/pedido** (reconciliar com DECISAO_SISTEMA; ok do "
           "advogado). Depois: re-taguear → salvar vNN → DIARIO → re-rodar o "
           "gate da fase → regerar DOCX.",
           ""]
    for n, (op, antes, depois) in enumerate(mudancas, 1):
        out.append(f"## Mudança {n} ({op})")
        out.append("")
        if antes:
            out.append(f"- ANTES: {antes[:400]}")
        if depois:
            out.append(f"+ DEPOIS: {depois[:400]}")
        out.append("")
        out.append("**Classificação:** [ ] estilo · [ ] fato novo · "
                   "[ ] citação nova · [ ] quantum/pedido")
        out.append("")

    destino.write_text("\n".join(out), encoding="utf-8", newline="\n")
    num = soj.append_diario(
        pasta, "NOTA",
        f"PORTA DE RETORNO: versao do advogado recebida ({origem.name}); diff "
        f"contra {minuta.name} com {len(mudancas)} bloco(s) de mudanca em "
        f"_efemeros/{destino.name}. Aguarda classificacao (estilo / fato novo "
        "/ citacao nova / quantum) antes de qualquer absorcao.")

    print(f"[OK] {len(mudancas)} bloco(s) de mudanca -> _efemeros/{destino.name} "
          f"(DIARIO #{num:03d}).")
    print("     Proximo passo: classificar cada mudanca na sessao (4 categorias) "
          "e so entao absorver em nova vNN.")


if __name__ == "__main__":
    main()
