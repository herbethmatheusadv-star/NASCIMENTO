#!/usr/bin/env python3
"""
organizar_provas.py — Organiza a pasta de protocolo para ações contra a ÁGUAS DO PARÁ.

O que faz:
  - Cria a pasta PROTOCOLO - <CLIENTE>/ no destino.
  - Copia/renomeia as provas como DOC-01 ... DOC-NN, na ordem fornecida.
  - Converte imagens (.jpeg/.jpg/.png) em PDF (PJe só aceita PDF).
  - Une vários prints de uma mesma conversa em um único PDF.
  - Copia a petição (00 - PETICAO INICIAL.docx) para a pasta.

NÃO decide a ordem nem o conteúdo: a skill monta o "plano" (lista de itens) e chama este
script. Cada item do plano:
  {
    "id": "DOC-11",
    "nome": "Comprovante PIX 1 - R 45,13",
    "fontes": ["/caminho/foto1.jpeg"],          # 1+ arquivos; se imagens, viram 1 PDF
    "tipo": "pdf" | "imagem" | "audio" | "copia" # como tratar
  }

USO:
  pip install pillow --break-system-packages
  python organizar_provas.py plano.json "/destino/PROTOCOLO - NOME" "/caminho/peticao.docx"
"""
import json, os, shutil, sys

def to_pdf(imgs, out_path):
    from PIL import Image
    ims = [Image.open(p).convert("RGB") for p in imgs]
    ims[0].save(out_path, "PDF", resolution=200.0, save_all=True, append_images=ims[1:])

def main():
    plano_path, destino = sys.argv[1], sys.argv[2]
    peticao = sys.argv[3] if len(sys.argv) > 3 else None
    plano = json.load(open(plano_path, encoding="utf-8"))
    os.makedirs(destino, exist_ok=True)

    if peticao and os.path.exists(peticao):
        shutil.copy(peticao, os.path.join(destino, "00 - PETICAO INICIAL.docx"))

    indice = ["# ÍNDICE DE PROVAS", ""]
    for item in plano:
        doc_id = item["id"]
        nome = item.get("nome", "")
        fontes = item["fontes"]
        tipo = item.get("tipo", "copia")
        base = f"{doc_id} - {nome}".strip().rstrip(" -")

        if tipo == "imagem":
            out = os.path.join(destino, base + ".pdf")
            to_pdf(fontes, out)
        elif tipo == "audio":
            # mantém o áudio original; tenta também gerar .mp3 se ffmpeg existir
            for f in fontes:
                ext = os.path.splitext(f)[1]
                shutil.copy(f, os.path.join(destino, base + ext))
            try:
                import subprocess
                src = fontes[0]
                mp3 = os.path.join(destino, base + ".mp3")
                subprocess.run(["ffmpeg", "-i", src, "-y", "-loglevel", "error", mp3], check=False)
            except Exception:
                pass
        else:  # pdf / copia
            f = fontes[0]
            ext = os.path.splitext(f)[1] or ".pdf"
            shutil.copy(f, os.path.join(destino, base + ext))

        indice.append(f"- **{doc_id}** — {nome}")

    with open(os.path.join(destino, "INDICE DE PROVAS.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(indice) + "\n")
    print("OK ->", destino)

if __name__ == "__main__":
    main()
