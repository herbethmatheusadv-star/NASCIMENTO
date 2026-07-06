# -*- coding: utf-8 -*-
"""
receber_whatsapp.py — rota "export de conversa do WhatsApp" (Onda 4/F6).
Recebe a PASTA do export (o .txt + as midias .opus/.jpg/...) e:

  1. LACRA tudo em 00_originais/<slug>/ com hash SHA-256 por arquivo
     (manifesto de cadeia de custodia);
  2. PARSEIA o .txt (formato de export do WhatsApp) e monta a CRONOLOGIA
     UNIFICADA em 01_documentos/DOC-NN_<slug>.md: mensagens + falas inline —
     cada fala aponta o arquivo de origem;
  3. Degravacoes: se existir <audio>.txt ao lado do .opus (sidecar), a fala
     entra inline JA ROTULADA; sem sidecar, entra como [degravacao pendente]
     (o transcritor local aguarda aprovacao do advogado — Onda 4);
  4. Registra a conversa como prova P## (categoria conversa_whatsapp) e
     escreve o DIARIO com o resumo + alerta de autenticidade.

ROTULO OBRIGATORIO em toda degravacao: trabalho, nao substitui pericia/ata
notarial — se a autenticidade for controversa, prova tecnica.

Uso:
  python receber_whatsapp.py CLIENTE PASTA_DO_EXPORT --descricao "CONVERSA COM FULANO"
         [--o-que-prova "..."] [--fato F##]
"""
import argparse
import re
import shutil
import sys
from pathlib import Path

import soj_lib as soj

# "12/05/2026 14:03 - Nome: mensagem"  (variantes com virgula tambem)
MSG_RE = re.compile(r"^(\d{2}/\d{2}/\d{4})[,]?\s+(\d{2}:\d{2})\s+-\s+([^:]+?):\s?(.*)$")
ANEXO_RE = re.compile(r"([\w\-\.]+\.(?:opus|ogg|mp3|m4a|jpg|jpeg|png|mp4|pdf))\s*\(arquivo anexado\)", re.I)
AUDIO_EXT = (".opus", ".ogg", ".mp3", ".m4a")


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Export de conversa do WhatsApp (SOJ).")
    ap.add_argument("cliente")
    ap.add_argument("pasta_export", help="Pasta com o .txt do export + midias")
    ap.add_argument("--descricao", required=True)
    ap.add_argument("--o-que-prova", dest="o_que_prova", default="(a preencher)")
    ap.add_argument("--fato", help="Vincula a conversa a um fato existente")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    export = Path(args.pasta_export)
    if not export.is_dir():
        sys.exit(f"[ERRO] Pasta do export nao encontrada: {export}")
    txts = sorted(export.glob("*.txt"))
    principais = [t for t in txts if not any(
        t.name.lower().endswith(e + ".txt") for e in AUDIO_EXT)]
    if not principais:
        sys.exit("[ERRO] Nenhum .txt de conversa na pasta do export.")
    txt = principais[0]

    dados = soj.load_caso(pasta)
    fato = None
    if args.fato:
        fato = soj.por_id(dados.get("fatos"), args.fato)
        if fato is None:
            sys.exit(f"[ERRO] Fato {args.fato} nao existe.")

    # 1. LACRE + MANIFESTO DE CUSTODIA (hash por arquivo)
    slugname = soj.slug(args.descricao)[:40]
    destino_orig = pasta / "00_originais" / f"whatsapp_{slugname}"
    if destino_orig.exists():
        sys.exit(f"[ERRO] {destino_orig} ja existe — nao sobrescrevo originais.")
    destino_orig.mkdir(parents=True)
    manifesto = []
    for arq in sorted(export.iterdir()):
        if arq.is_file():
            shutil.copy2(arq, destino_orig / arq.name)
            manifesto.append((arq.name, soj.sha256_arquivo(destino_orig / arq.name)))
    hash_txt = dict(manifesto).get(txt.name, "?")

    # 2. PARSE do .txt -> cronologia
    audios_total = audios_transcritos = mensagens = 0
    linhas_cron = []
    for linha in txt.read_text(encoding="utf-8", errors="replace").splitlines():
        m = MSG_RE.match(linha.strip())
        if not m:
            if linhas_cron and linha.strip():
                linhas_cron[-1] += " " + linha.strip()      # continuacao
            continue
        data, hora, autor, msg = m.groups()
        anexo = ANEXO_RE.search(msg)
        if anexo:
            nome_arq = anexo.group(1)
            origem_rel = f"00_originais/whatsapp_{slugname}/{nome_arq}"
            if nome_arq.lower().endswith(AUDIO_EXT):
                audios_total += 1
                sidecar = export / (nome_arq + ".txt")
                if sidecar.exists():
                    audios_transcritos += 1
                    fala = sidecar.read_text(encoding="utf-8",
                                             errors="replace").strip()
                    linhas_cron.append(
                        f"- **{data} {hora} — {autor.strip()}** 🎙️ *fala "
                        f"degravada* [origem: `{origem_rel}`]: “{fala}” "
                        f"*( {soj.ROTULO_DEGRAVACAO} )*")
                else:
                    linhas_cron.append(
                        f"- **{data} {hora} — {autor.strip()}** 🎙️ [ÁUDIO: "
                        f"`{origem_rel}` — **degravação pendente** (transcritor "
                        "local aguardando aprovação do advogado)]")
            else:
                linhas_cron.append(f"- **{data} {hora} — {autor.strip()}** 📎 "
                                   f"[anexo: `{origem_rel}`]")
        else:
            mensagens += 1
            linhas_cron.append(f"- **{data} {hora} — {autor.strip()}:** {msg}")

    # 3. DOC-NN da cronologia
    num = soj.proximo_doc_num(dados)
    nome_doc = f"DOC-{num:02d}_CONVERSA_WHATSAPP_{slugname}.md"
    cab = ["# CRONOLOGIA UNIFICADA — CONVERSA DE WHATSAPP",
           f"**{args.descricao}** · montada em {soj.agora()} pela porta única",
           "",
           f"> ⚖️ {soj.ROTULO_DEGRAVACAO}",
           "> Cronologia de TRABALHO gerada do export; os ORIGINAIS lacrados",
           f"> (com hash) estão em `00_originais/whatsapp_{slugname}/`.",
           "",
           "## Manifesto de custódia (SHA-256 na entrada)",
           ""]
    cab += [f"- `{n}` — `{h}`" for n, h in manifesto]
    cab += ["", "## Cronologia", ""]
    (pasta / "01_documentos" / nome_doc).write_text(
        "\n".join(cab + linhas_cron) + "\n", encoding="utf-8", newline="\n")

    # 4. prova P## + DIARIO
    pid = soj.proximo_prova_id(dados)
    soj.lista_de(dados, "provas").append({
        "id": pid, "doc": f"01_documentos/{nome_doc}",
        "original": f"00_originais/whatsapp_{slugname}",
        "nota": f"{len(manifesto)} arquivos originais lacrados; manifesto SHA-256 dentro do DOC",
        "o_que_prova": args.o_que_prova, "forca": "indiciaria",
        "fragilidade": "conversa eletronica — se a autenticidade for controvertida, exige pericia/ata notarial (degravacao e de trabalho)",
        "categoria": "conversa_whatsapp", "sha256": hash_txt})
    if fato is not None:
        if fato.get("provas") is None:
            fato["provas"] = []
        fato["provas"].append(pid)
    soj.save_caso(pasta, dados)

    num_d = soj.append_diario(
        pasta, "DOC_RECEBIDO",
        f"Export de conversa do WhatsApp recebido: {args.descricao} -> "
        f"00_originais/whatsapp_{slugname}/ ({len(manifesto)} arquivos com "
        f"SHA-256 no manifesto) -> {nome_doc} (cronologia unificada). "
        f"Registrado como {pid}"
        + (f", vinculado a {args.fato}" if fato is not None else "") + ". "
        f"Mensagens: {mensagens}; audios: {audios_total} "
        f"({audios_transcritos} degravados via sidecar, "
        f"{audios_total - audios_transcritos} pendentes). "
        f"{soj.ROTULO_DEGRAVACAO}")

    import gerar_views
    gerar_views.gerar_views(args.cliente)

    print(f"[OK] Conversa lacrada e cronologiada: {pid} / {nome_doc} "
          f"(DIARIO #{num_d:03d}).")
    print(f"     {len(manifesto)} originais com SHA-256; {mensagens} mensagens; "
          f"{audios_total} audio(s), {audios_transcritos} degravado(s), "
          f"{audios_total - audios_transcritos} pendente(s).")
    print(f"     ALERTA: {soj.ROTULO_DEGRAVACAO}")


if __name__ == "__main__":
    main()
