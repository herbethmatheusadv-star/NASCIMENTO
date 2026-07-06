# -*- coding: utf-8 -*-
"""
diff_pecas.py — utilitário do MODO REVISÃO DE PEÇA (skill soj-kernel).
Compara DUAS versões de peça (qualquer combinação de .md/.docx) e imprime o
diff itemizado, mudança a mudança. SEM efeitos colaterais: não escreve no
DIARIO nem em views — serve para apresentar a proposta ao advogado ANTES da
aprovação (regra inegociável do modo revisão).

Uso:
  python diff_pecas.py ARQUIVO_BASE ARQUIVO_NOVO [--saida caminho.md]
"""
import argparse
import sys
from pathlib import Path

import soj_lib as soj
from absorver_versao import diff_itemizado, extrair_paragrafos


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Diff itemizado entre duas pecas.")
    ap.add_argument("base")
    ap.add_argument("nova")
    ap.add_argument("--saida", help="Se dado, grava o relatorio neste arquivo")
    args = ap.parse_args()

    for arq in (args.base, args.nova):
        if not Path(arq).is_file():
            sys.exit(f"[ERRO] Arquivo nao encontrado: {arq}")

    mudancas = diff_itemizado(extrair_paragrafos(args.base),
                              extrair_paragrafos(args.nova))

    out = [f"# DIFF DE PEÇAS — {Path(args.base).name} → {Path(args.nova).name}",
           f"Gerado em {soj.agora()} · {len(mudancas)} mudança(s) · "
           "sem efeitos colaterais (diff_pecas.py)", ""]
    for n, (op, antes, depois) in enumerate(mudancas, 1):
        out.append(f"## Mudança {n} ({op})")
        if antes:
            out.append(f"- ANTES: {antes[:400]}")
        if depois:
            out.append(f"+ DEPOIS: {depois[:400]}")
        out.append("")
    if not mudancas:
        out.append("(nenhuma diferença de conteúdo entre as versões)")

    texto = "\n".join(out)
    if args.saida:
        Path(args.saida).write_text(texto, encoding="utf-8", newline="\n")
        print(f"[OK] {len(mudancas)} mudanca(s) -> {args.saida}")
    else:
        print(texto)


if __name__ == "__main__":
    main()
