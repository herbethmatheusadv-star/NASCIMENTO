# -*- coding: utf-8 -*-
"""
receber_documento.py — o PONTO ÚNICO DE ENTRADA (blueprint, seção 7).
Uma ação, consistência total:
  copia p/ 00_originais (intocado) -> renomeia p/ 01_documentos (DOC-NN)
  -> registra P## no CASO.yaml -> vincula a fato -> baixa pendência
  -> entrada DOC_RECEBIDO no DIARIO -> regenera views -> reporta bloqueios.

Uso:
  python receber_documento.py CLIENTE CAMINHO_DO_ARQUIVO
         --descricao "CERTIDAO NASCIMENTO JULLIA"
         [--o-que-prova "Filiacao e idade da menor"]
         [--forca plena|relativa|indiciaria]
         [--fato F04] [--marca-provado]
         [--resolve PEN01]
"""
import argparse
import shutil
import sys
from pathlib import Path

import soj_lib as soj


def destino_livre(pasta, nome):
    """Se já existir arquivo com esse nome, acrescenta _2, _3… (nunca sobrescreve)."""
    destino = pasta / nome
    i = 2
    while destino.exists():
        destino = pasta / f"{Path(nome).stem}_{i}{Path(nome).suffix}"
        i += 1
    return destino


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Ponto unico de entrada de documentos (SOJ).")
    ap.add_argument("cliente")
    ap.add_argument("arquivo", help="Caminho do arquivo recebido (como veio do cliente)")
    ap.add_argument("--descricao", required=True,
                    help='Nome curto do documento, ex.: "CERTIDAO NASCIMENTO JULLIA"')
    ap.add_argument("--o-que-prova", dest="o_que_prova", default="(a preencher)")
    ap.add_argument("--forca", default="plena",
                    choices=["plena", "relativa", "indiciaria"])
    ap.add_argument("--fato", help="Vincula a prova a um fato existente, ex.: F04")
    ap.add_argument("--marca-provado", action="store_true",
                    help="Muda o status do fato vinculado para 'provado'")
    ap.add_argument("--resolve", help="Baixa uma pendencia, ex.: PEN01")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)

    origem = Path(args.arquivo)
    if not origem.is_file():
        sys.exit(f"[ERRO] Arquivo nao encontrado: {origem}")

    # valida referencias ANTES de mexer em qualquer coisa
    fato = None
    if args.fato:
        fato = soj.por_id(dados.get("fatos"), args.fato)
        if fato is None:
            sys.exit(f"[ERRO] Fato {args.fato} nao existe no CASO.yaml. "
                     "Registre o fato primeiro (ou confira o id).")
    pendencia = None
    if args.resolve:
        pendencia = soj.por_id(dados.get("pendencias"), args.resolve)
        if pendencia is None:
            sys.exit(f"[ERRO] Pendencia {args.resolve} nao existe no CASO.yaml.")

    # 1. lacra o original em 00_originais/ (nome intocado; nunca sobrescreve)
    dest_orig = destino_livre(pasta / "00_originais", origem.name)
    shutil.copy2(origem, dest_orig)

    # 2. copia renomeada em 01_documentos/ (padrao DOC-NN das skills)
    num = soj.proximo_doc_num(dados)
    ext = origem.suffix.lower()
    nome_doc = f"DOC-{num:02d}_{soj.slug(args.descricao)}{ext}"
    shutil.copy2(origem, pasta / "01_documentos" / nome_doc)
    aviso_pdf = ""
    if ext != ".pdf":
        aviso_pdf = (f"[AVISO] O arquivo nao e PDF ({ext}). O padrao de 01_documentos/ "
                     "e PDF — converta a copia quando possivel (o original fica como esta).")

    # 3. registra a prova P## no CASO.yaml
    pid = soj.proximo_prova_id(dados)
    soj.lista_de(dados, "provas").append({
        "id": pid,
        "doc": f"01_documentos/{nome_doc}",
        "original": f"00_originais/{dest_orig.name}",
        "o_que_prova": args.o_que_prova,
        "forca": args.forca,
        "fragilidade": None,
    })

    # 4. vincula ao fato (e opcionalmente muda o status)
    mudanca_status = ""
    if fato is not None:
        if fato.get("provas") is None:
            fato["provas"] = []
        fato["provas"].append(pid)
        if args.marca_provado:
            antes = fato.get("status", "alegado")
            fato["status"] = "provado"
            mudanca_status = f" (status alterado: {antes} -> provado)"

    # 5. baixa a pendencia
    if pendencia is not None:
        pendencia["status"] = "resolvida"
        pendencia["resolvida_em"] = str(soj.hoje())

    soj.save_caso(pasta, dados)

    # 6. entrada no DIARIO
    corpo = (f"Recebido {args.descricao} -> 00_originais/{dest_orig.name} -> {nome_doc}.\n"
             f"Registrado como {pid}"
             + (f", vinculado a {args.fato}{mudanca_status}" if fato is not None else "")
             + ".")
    if pendencia is not None:
        corpo += f"\nResolve: {args.resolve}"
    num_diario = soj.append_diario(pasta, "DOC_RECEBIDO", corpo)

    # 7. regenera as views
    import gerar_views
    gerar_views.gerar_views(args.cliente)

    # 8. relatorio
    print(f"[OK] {args.descricao}: original lacrado, copia {nome_doc}, prova {pid} "
          f"registrada. DIARIO #{num_diario:03d}.")
    if aviso_pdf:
        print(aviso_pdf)
    for gate in ("G2", "G3"):
        travas = soj.pendencias_abertas(dados, bloqueia=gate)
        if travas:
            ids = ", ".join(str(p.get("id")) for p in travas)
            print(f"     {gate} ainda bloqueado por: {ids}")
    if not soj.pendencias_abertas(dados):
        print("     Nenhuma pendencia aberta.")


if __name__ == "__main__":
    main()
