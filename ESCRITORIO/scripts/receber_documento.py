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
import re
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
    # ROTEADOR DE TIPOS (blueprint §7, v1.7) + GATILHOS DE FASE (Onda 2/F6)
    ap.add_argument("--tipo", default="prova",
                    choices=["prova", "peca_adversaria", "contestacao",
                             "decisao", "sentenca", "sentenca_favoravel",
                             "transito", "ata_audiencia"],
                    help="Rota do documento na porta unica")
    ap.add_argument("--audiencia-data", dest="audiencia_data",
                    help="(ata_audiencia) data da audiencia a que a ata se "
                         "refere (YYYY-MM-DD) — marca status: realizada")
    ap.add_argument("--prazo-data", help="(decisao/sentenca) data do prazo extraido, YYYY-MM-DD")
    ap.add_argument("--prazo-descricao", help="(decisao/sentenca) descricao do prazo")
    ap.add_argument("--prazo-criticidade", default="alta",
                    choices=["alta", "media", "baixa"])
    ap.add_argument("--prazo-resposta", action="store_true",
                    help="Marca o prazo como prazo de RESPOSTA (item zero do G1 em polo passivo)")
    ap.add_argument("--sem-prazo", metavar="MOTIVO",
                    help="(decisao/sentenca) declara que a decisao NAO abre prazo, com motivo")
    # Onda 1/F6: metadados da decisao judicial
    ap.add_argument("--juizo", help="(decisao/sentenca) juizo prolator, ex.: 'Vara de Familia de Parauapebas'")
    ap.add_argument("--resultado", help="(decisao/sentenca) resultado em uma linha, ex.: 'liminar deferida — provisorios em 30 por cento do SM'")
    args = ap.parse_args()

    # REGRA DURA do roteador: TODO documento processual (decisao, sentenca,
    # contestacao, transito, ata) so entra com o prazo extraido (ou a
    # declaracao fundamentada de que nao ha prazo) — ANTES de qualquer outra
    # analise (blueprint §7, v1.7 + gatilhos de fase da Onda 2/F6).
    TIPOS_PROCESSUAIS = ("decisao", "sentenca", "sentenca_favoravel",
                         "contestacao", "transito", "ata_audiencia")
    if args.tipo in TIPOS_PROCESSUAIS:
        tem_prazo = args.prazo_data and args.prazo_descricao
        if not tem_prazo and not args.sem_prazo:
            sys.exit("[BLOQUEADO] Documento processual exige a EXTRACAO DO "
                     "PRAZO antes de qualquer outra analise: informe "
                     "--prazo-data e --prazo-descricao, ou declare "
                     "--sem-prazo \"motivo\".")

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
    #    + CADEIA DE CUSTODIA (Onda 4/F6): hash SHA-256 registrado na ficha
    dest_orig = destino_livre(pasta / "00_originais", origem.name)
    shutil.copy2(origem, dest_orig)
    hash_original = soj.sha256_arquivo(dest_orig)

    # 2. copia renomeada em 01_documentos/ (padrao DOC-NN das skills)
    num = soj.proximo_doc_num(dados)
    ext = origem.suffix.lower()
    nome_doc = f"DOC-{num:02d}_{soj.slug(args.descricao)}{ext}"
    shutil.copy2(origem, pasta / "01_documentos" / nome_doc)
    aviso_pdf = ""
    if ext != ".pdf":
        aviso_pdf = (f"[AVISO] O arquivo nao e PDF ({ext}). O padrao de 01_documentos/ "
                     "e PDF — converta a copia quando possivel (o original fica como esta).")

    # 3. registra a prova P## no CASO.yaml (com a categoria da rota)
    pid = soj.proximo_prova_id(dados)
    registro = {
        "id": pid,
        "doc": f"01_documentos/{nome_doc}",
        "original": f"00_originais/{dest_orig.name}",
        "o_que_prova": args.o_que_prova,
        "forca": args.forca,
        "fragilidade": None,
        "sha256": hash_original,
    }
    if args.tipo != "prova":
        registro["categoria"] = args.tipo
    if args.tipo in ("decisao", "sentenca", "sentenca_favoravel", "transito",
                     "ata_audiencia"):
        registro["juizo"] = args.juizo or "(a preencher)"
        registro["comarca"] = str(dados["caso"].get("comarca", ""))
        registro["resultado"] = args.resultado or "(a preencher)"
    soj.lista_de(dados, "provas").append(registro)

    # 3b. ROTAS PROCESSUAIS: PZ## criado ANTES de qualquer outra analise
    prazo_id = None
    if args.tipo in TIPOS_PROCESSUAIS and args.prazo_data:
        maior = 0
        for pz in (dados.get("prazos") or []):
            m = re.match(r"PZ(\d+)", str(pz.get("id", "")))
            if m:
                maior = max(maior, int(m.group(1)))
        prazo_id = f"PZ{maior + 1:02d}"
        novo_prazo = {"id": prazo_id, "descricao": args.prazo_descricao,
                      "data": args.prazo_data,
                      "criticidade": args.prazo_criticidade,
                      "origem": f"{nome_doc} ({pid})"}
        if args.prazo_resposta:
            novo_prazo["resposta"] = True
        soj.lista_de(dados, "prazos").append(novo_prazo)

    # 3c. GATILHOS DE FASE (Onda 2/F6): fase_processual + proposta de peca
    NOVA_FASE = {"contestacao": "postulatoria", "sentenca": "decisoria",
                 "sentenca_favoravel": "decisoria", "transito": "cumprimento",
                 "ata_audiencia": "instrutoria"}
    PROPOSTA_FASE = {
        "contestacao": ("PROPOSTA DE FASE: elaborar REPLICA (impugnacao a "
                        "contestacao) dentro do prazo{PZ}. Modulo sem template "
                        "de replica: gerar do zero e marcar o texto aprovado "
                        "com COLHEITA: (candidato a template)."),
        "sentenca": ("PROPOSTA DE FASE: avaliar EMBARGOS DE DECLARACAO e/ou "
                     "APELACAO dentro do prazo{PZ} — decisao reservada do "
                     "advogado (recurso = Tier B)."),
        "sentenca_favoravel": ("PROPOSTA DE FASE: (a) avaliar embargos/"
                               "contrarrazoes dentro do prazo{PZ}; (b) apos "
                               "anonimizar, guardar no ACERVO (praxe local)."),
        "transito": ("PROPOSTA DE FASE: iniciar CUMPRIMENTO DE SENTENCA "
                     "(modulo sem template: gerar do zero e marcar COLHEITA:)."),
        "ata_audiencia": ("COLHEITA DE AUDIENCIA: registrar no DIARIO o que o "
                          "juizo valorizou/perguntou (marcar COLHEITA:), "
                          "atualizar fatos controversos e cumprir os prazos "
                          "fixados na ata."),
    }
    proposta = ""
    if args.tipo in NOVA_FASE:
        fase_ant = dados["caso"].get("fase_processual", "pre_protocolo")
        dados["caso"]["fase_processual"] = NOVA_FASE[args.tipo]
        proposta = PROPOSTA_FASE[args.tipo].replace(
            "{PZ}", f" {prazo_id}" if prazo_id else " (sem prazo aberto)")
        proposta += (f" [fase_processual: {fase_ant} -> "
                     f"{NOVA_FASE[args.tipo]}]")

    # 3d. ata vinculada a audiencia designada -> status: realizada
    if args.tipo == "ata_audiencia" and args.audiencia_data:
        for aud in (dados.get("audiencias") or []):
            if str(aud.get("data")) == args.audiencia_data:
                aud["status"] = "realizada"
                aud["ata"] = pid

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

    # 6. entrada no DIARIO (tipo conforme a rota)
    corpo = (f"Recebido {args.descricao} [rota: {args.tipo}] -> "
             f"00_originais/{dest_orig.name} -> {nome_doc}.\n"
             f"Cadeia de custodia: SHA-256 {hash_original}.\n"
             f"Registrado como {pid}"
             + (f", vinculado a {args.fato}{mudanca_status}" if fato is not None else "")
             + ".")
    if pendencia is not None:
        corpo += f"\nResolve: {args.resolve}"
    tipo_entrada = "DOC_RECEBIDO"
    if args.tipo in TIPOS_PROCESSUAIS:
        tipo_entrada = "EVENTO_PROCESSUAL"
        if prazo_id:
            corpo += (f"\nPRAZO EXTRAIDO ANTES DE QUALQUER ANALISE: {prazo_id} "
                      f"— {args.prazo_descricao} ({args.prazo_data}, "
                      f"{args.prazo_criticidade}"
                      + (", PRAZO DE RESPOSTA" if args.prazo_resposta else "") + ").")
        else:
            corpo += f"\nSem prazo aberto — motivo declarado: {args.sem_prazo}"
    if proposta:
        corpo += "\n" + proposta
    num_diario = soj.append_diario(pasta, tipo_entrada, corpo)

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

    # 9. checklist da rota para a SESSAO (blueprint §7, v1.7 + Onda 2/F6)
    if proposta:
        print(f"     [GATILHO DE FASE] {proposta}")
    if args.tipo in ("peca_adversaria", "contestacao"):
        print(f"     [ROTA {args.tipo}] Agora a sessao DEVE: (1) analise "
              "adversarial -> ESTRATEGIA.md (teses deles, fraquezas, pontos "
              "de ataque); (2) alegacoes deles como fatos com status "
              "alegado_pelo_adversario/controverso; (3) TODA lei citada por "
              "eles: verificar na BASE_LEGAL antes de entrar em qualquer "
              "defesa; (4) rodar o vigia (prazo ja registrado pela rota).")
    elif args.tipo in ("decisao", "sentenca", "sentenca_favoravel",
                       "transito", "ata_audiencia"):
        print(f"     [ROTA {args.tipo}] Rodar o vigia AGORA "
              "(python ESCRITORIO/scripts/vigia_prazos.py) e espelhar o prazo "
              "no Calendar; so depois analisar o merito da decisao.")
        if args.tipo == "sentenca_favoravel":
            print("     Candidata ao ACERVO (praxe local): apos anonimizar, "
                  "rodar guardar_modelo --proprio (pendente a decisao do "
                  "advogado sobre autos sigilosos).")


if __name__ == "__main__":
    main()
