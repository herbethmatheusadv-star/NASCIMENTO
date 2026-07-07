# -*- coding: utf-8 -*-
"""
preparar_protocolo.py — Etapa 4 (blueprint, seções 2 e 7).
Exige G3 APROVADO (bloqueia sem ele). Faz:
  1. remove as tags SOJ da minuta final (strip);
  2. monta CASOS/<cliente>/PROTOCOLO/ com a peça limpa + DOC-01..NN + índice;
  3. registra entrada no DIARIO e commita no git.
A formatação final em DOCX timbrado é feita pela skill
`formatacao-peticoes-nascimento` (D10) a partir da peça limpa gerada aqui.

Uso:
  python preparar_protocolo.py CLIENTE [--minuta MINUTA_v03.md]
"""
import argparse
import re
import shutil
import sys

import soj_lib as soj

TAG_LINHA_RE = re.compile(r"^\s*<!--\s*SOJ:.*?-->\s*$")


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Monta o pacote de protocolo (SOJ).")
    ap.add_argument("cliente")
    ap.add_argument("--minuta", help="Nome do arquivo da minuta aprovada "
                                     "(padrao: a mais recente)")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)

    # trava dura: sem G3 aprovado nao ha protocolo (D8)
    g3 = ((dados["caso"].get("gates") or {}).get("G3") or {})
    if str(g3.get("status")) != "aprovado":
        sys.exit(f"[BLOQUEADO] O G3 deste caso esta '{g3.get('status', 'pendente')}'. "
                 "Rode 'python gate_check.py {0} G3' e resolva o que faltar antes "
                 "de preparar o protocolo.".format(args.cliente))

    if args.minuta:
        minuta = pasta / args.minuta
        if not minuta.exists():
            sys.exit(f"[ERRO] Minuta nao encontrada: {args.minuta}")
    else:
        minuta = soj.minuta_atual(pasta)
        if minuta is None:
            sys.exit("[ERRO] Nenhuma MINUTA_v*.md encontrada no caso.")

    protocolo = pasta / "PROTOCOLO"
    protocolo.mkdir(exist_ok=True)

    # 1. peça limpa (strip das tags SOJ, linha a linha)
    linhas = minuta.read_text(encoding="utf-8").splitlines()
    limpas = [l for l in linhas if not TAG_LINHA_RE.match(l)]
    peca = protocolo / "PETICAO_FINAL_para_timbrado.md"
    peca.write_text("\n".join(limpas) + "\n", encoding="utf-8", newline="\n")

    # 2. copia dos documentos DOC-01..NN — RESPEITANDO a valoracao de provas
    #    (aprendizado do caso 2026-0004): prova com categoria 'nao_juntar'
    #    fica integra no acervo do caso, mas NAO entra no pacote de protocolo.
    fora_do_rol = {str(p.get("doc", "")).replace("01_documentos/", "")
                   for p in (dados.get("provas") or [])
                   if soj.normaliza(str(p.get("categoria", ""))) == "nao_juntar"}
    docs_dir = pasta / "01_documentos"
    copiados = []
    if docs_dir.exists():
        for a in sorted(docs_dir.iterdir()):
            if a.is_file() and a.name not in fora_do_rol:
                shutil.copy2(a, protocolo / a.name)
                copiados.append(a.name)

    # 3. indice do pacote (tambem sem as 'nao_juntar')
    provas = [p for p in (dados.get("provas") or [])
              if soj.normaliza(str(p.get("categoria", ""))) != "nao_juntar"]
    idx = [f"# ÍNDICE DO PROTOCOLO — {dados['caso'].get('titulo')}",
           f"Caso {dados['caso'].get('id')} · montado em {soj.agora()} "
           f"a partir de {minuta.name}", "",
           "1. PETICAO_FINAL_para_timbrado.md (formatar em DOCX timbrado com a "
           "skill formatacao-peticoes-nascimento antes de protocolar)"]
    for i, p in enumerate(sorted(provas,
                                 key=lambda x: str(x.get("doc", ""))), start=2):
        doc = str(p.get("doc", "")).replace("01_documentos/", "")
        idx.append(f"{i}. {doc} — {p.get('o_que_prova')}")
    idx.append("")
    (protocolo / "INDICE.md").write_text("\n".join(idx), encoding="utf-8",
                                         newline="\n")

    # 4. DIARIO + git
    num = soj.append_diario(
        pasta, "NOTA",
        f"Pacote de protocolo montado em PROTOCOLO/ a partir de {minuta.name} "
        f"({len(copiados)} documento(s), tags SOJ removidas). Proximo passo: "
        "formatar em DOCX timbrado (skill formatacao-peticoes-nascimento), "
        "protocolar e registrar EVENTO_PROCESSUAL.")
    import gerar_views
    gerar_views.gerar_views(args.cliente)
    soj.git_commit(f"protocolo {args.cliente}: pacote montado (DIARIO #{num:03d})")

    print(f"[OK] Pacote montado em CASOS/{args.cliente}/PROTOCOLO/ "
          f"({len(copiados)} documento(s) + peca limpa + indice). DIARIO #{num:03d}.")
    print("     Proximo passo: gerar o DOCX timbrado com a skill "
          "formatacao-peticoes-nascimento e, apos protocolar, registrar "
          "EVENTO_PROCESSUAL no DIARIO.")


if __name__ == "__main__":
    main()
