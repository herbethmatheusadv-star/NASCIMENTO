# -*- coding: utf-8 -*-
"""
guardar_modelo.py — ACERVO DE MODELOS (blueprint, seção 9).
Guarda uma peça/decisão de referência no acervo do escritório, com:
  1. ANONIMIZAÇÃO na entrada: varredura mecânica (CPF, CNPJ, CEP, e-mail,
     telefone) + substituições nominais passadas pela sessão (--anon);
  2. RECUSA de autos sigilosos (detecção no texto; sem exceção);
  3. Ficha de curadoria M-NN (origem, área, tipo, ano, por quê, ressalvas,
     resultado) + índice regenerado.

O acervo armazena SEMPRE .md (texto extraído e anonimizado) — o valor do
modelo é estilo e técnica, nunca a lei nem o formato. PDFs: converter antes.

REGRA DE FERRO (skill soj-kernel): modelo é professor de ESTILO e TÉCNICA,
nunca de lei — citação vinda de modelo só entra em peça após verificação na
BASE_LEGAL.

Uso:
  python guardar_modelo.py ARQUIVO(.md|.txt|.docx) --area familia|consumidor|bancario|geral
     --tipo peca|decisao|sentenca --origem "..." --acao "..." --ano 2024
     --porque "a tecnica que interessa" [--ressalva "nao copiar X"]
     [--resultado "..."] [--proprio] [--anon "TEXTO=SUBSTITUTO"]...
"""
import argparse
import re
import sys
from pathlib import Path

import soj_lib as soj

ACERVO = soj.ESCRITORIO / "ACERVO"

PADROES_MECANICOS = [
    ("CPF", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b"), "[CPF-REMOVIDO]"),
    ("CNPJ", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b"), "[CNPJ-REMOVIDO]"),
    ("CEP", re.compile(r"\b\d{5}-\d{3}\b"), "[CEP-REMOVIDO]"),
    ("EMAIL", re.compile(r"\b[\w.\-]+@[\w\-]+\.[\w.\-]+\b"), "[EMAIL-REMOVIDO]"),
    ("TELEFONE", re.compile(r"\(\d{2}\)\s*9?\d{4}[-.\s]?\d{4}\b"), "[TEL-REMOVIDO]"),
]

MARCAS_SIGILO = ["segredo de justica", "tramitacao reservada", "autos sigilosos",
                 "processo sigiloso", "sigilo judicial"]


def extrair_texto(caminho):
    caminho = Path(caminho)
    ext = caminho.suffix.lower()
    if ext in (".md", ".txt"):
        return caminho.read_text(encoding="utf-8", errors="replace")
    if ext == ".docx":
        try:
            from docx import Document
        except ImportError:
            sys.exit("[ERRO] python-docx nao instalado.")
        return "\n\n".join(p.text for p in Document(str(caminho)).paragraphs
                           if p.text.strip())
    sys.exit(f"[RECUSADO] Formato {ext} nao aceito. PDFs e outros: converta "
             "para .md/.docx e anonimize os nomes ANTES de guardar.")


def proximo_m():
    maior = 0
    for f in ACERVO.glob("*/M-*_FICHA.md"):
        m = re.match(r"M-(\d+)_", f.name)
        if m:
            maior = max(maior, int(m.group(1)))
    return maior + 1


def regenerar_indice():
    linhas = ["# ÍNDICE DO ACERVO DE MODELOS", "",
              f"Gerado por guardar_modelo.py em {soj.agora()} — não editar.",
              "",
              "| M-NN | Área | Tipo | Ano | Por que foi guardado | Ressalvas |",
              "|---|---|---|---|---|---|"]
    fichas = sorted(ACERVO.glob("*/M-*_FICHA.md"))
    for f in fichas:
        t = f.read_text(encoding="utf-8")

        def campo(nome):
            m = re.search(rf"\*\*{nome}:\*\* (.+)", t)
            return m.group(1).strip() if m else "?"
        mid = f.name.split("_")[0]
        linhas.append(f"| {mid} | {f.parent.name} | {campo('Tipo')} | "
                      f"{campo('Ano')} | {campo('Por que guardado')} | "
                      f"{campo('Ressalvas')} |")
    if not fichas:
        linhas.append("| (acervo vazio) | | | | | |")
    linhas.append("")
    (ACERVO / "INDICE.md").write_text("\n".join(linhas), encoding="utf-8",
                                      newline="\n")


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Guarda um modelo no acervo (SOJ).")
    ap.add_argument("arquivo")
    ap.add_argument("--area", required=True,
                    choices=["familia", "consumidor", "bancario", "geral"])
    ap.add_argument("--tipo", required=True,
                    choices=["peca", "decisao", "sentenca"])
    ap.add_argument("--origem", required=True,
                    help='Ex.: "peticao de colega (anonima)", "sentenca da Vara de Familia de Parauapebas — processo do escritorio"')
    ap.add_argument("--acao", required=True, help="Tipo de acao")
    ap.add_argument("--ano", required=True)
    ap.add_argument("--porque", required=True,
                    help="ANALISE DO SISTEMA (curadoria autonoma, v1.7): tecnicas, "
                         "movimentos, estrutura, o que e copiavel e o que e datado "
                         "— a sessao analisa o modelo ANTES de rodar o comando")
    ap.add_argument("--nota-advogado", default="",
                    help="Nota do advogado (campo OPCIONAL)")
    ap.add_argument("--ressalva", default="nenhuma",
                    help='Ex.: "nao copiar o capitulo X — fundamento superado"')
    ap.add_argument("--resultado", default="desconhecido")
    ap.add_argument("--proprio", action="store_true",
                    help="Peca/decisao de processo do proprio escritorio")
    ap.add_argument("--anon", action="append", default=[],
                    metavar="TEXTO=SUBST",
                    help="Substituicao nominal identificada na sessao (repetivel)")
    args = ap.parse_args()

    texto = extrair_texto(args.arquivo)

    # 1. RECUSA de autos sigilosos — sem excecao (blueprint §9)
    tnorm = soj.normaliza(texto)
    for marca in MARCAS_SIGILO:
        if marca in tnorm:
            sys.exit(f"[RECUSADO] O texto contem indicio de autos sigilosos "
                     f"('{marca}'). Pecas de autos sigilosos NAO entram no "
                     "acervo — regra sem excecao.")

    # 2. ANONIMIZACAO: substituicoes nominais da sessao + varredura mecanica
    relatorio = []
    for par in args.anon:
        if "=" not in par:
            sys.exit(f"[ERRO] --anon invalido (use TEXTO=SUBSTITUTO): {par}")
        alvo, subst = par.split("=", 1)
        n = texto.count(alvo)
        if n == 0:
            print(f"[AVISO] --anon '{alvo}' nao encontrado no texto.")
        texto = texto.replace(alvo, subst)
        relatorio.append(f"nominal '{alvo}' -> '{subst}' ({n}x)")
    for nome, padrao, subst in PADROES_MECANICOS:
        texto, n = padrao.subn(subst, texto)
        if n:
            relatorio.append(f"{nome}: {n} ocorrencia(s) removida(s)")

    # 3. grava modelo + ficha + indice
    mid = f"M-{proximo_m():02d}"
    pasta = ACERVO / args.area
    pasta.mkdir(parents=True, exist_ok=True)
    slug = soj.slug(args.acao)[:40]
    destino = pasta / f"{mid}_{slug}.md"
    cab = (f"<!-- {mid} — MODELO DO ACERVO (anonimizado na entrada). "
           "REGRA DE FERRO: professor de ESTILO e TECNICA, nunca de lei — "
           "toda citacao juridica daqui so entra em peca apos verificacao na "
           "BASE_LEGAL. -->\n\n")
    destino.write_text(cab + texto, encoding="utf-8", newline="\n")

    ficha = pasta / f"{mid}_FICHA.md"
    ficha.write_text("\n".join([
        f"# {mid} — FICHA DE CURADORIA",
        "",
        f"**Arquivo:** {destino.name}",
        f"**Origem:** {args.origem}" + (" · PROCESSO DO ESCRITÓRIO" if args.proprio else ""),
        f"**Área:** {args.area}",
        f"**Tipo:** {args.tipo}",
        f"**Ação:** {args.acao}",
        f"**Ano:** {args.ano}",
        f"**Por que guardado:** {args.porque}",
        f"**Nota do advogado:** {args.nota_advogado or '(nenhuma — campo opcional)'}",
        f"**Ressalvas:** {args.ressalva}",
        f"**Resultado:** {args.resultado}",
        f"**Guardado em:** {soj.agora()}",
        f"**Anonimização na entrada:** {'; '.join(relatorio) or 'nada a substituir'}"
        " · Revisão nominal pela sessão: conferida antes do comando.",
        "",
        "> REGRA DE FERRO: modelo ensina ESTILO e TÉCNICA, nunca lei. Citação",
        "> jurídica vinda deste modelo só entra em peça após verificação na",
        "> BASE_LEGAL (verbete válido). Uso sob demanda — nunca automático.",
        "",
    ]), encoding="utf-8", newline="\n")

    regenerar_indice()
    print(f"[OK] {mid} guardado em ACERVO/{args.area}/ "
          f"({len(relatorio)} classe(s) de anonimizacao aplicadas).")
    print(f"     Ficha: {ficha.name} · Indice regenerado.")


if __name__ == "__main__":
    main()
