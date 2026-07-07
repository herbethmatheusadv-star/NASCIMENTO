# -*- coding: utf-8 -*-
"""
degravar.py — transcritor LOCAL de audios (Onda 4/F6; instalado com ok do
advogado em 06/07/2026). Usa faster-whisper rodando 100% nesta maquina:
NENHUM audio sai do computador (sigilo preservado).

Dois modos:

  PASTA  → prepara um export de WhatsApp ANTES do receber_whatsapp.py:
           degrava cada audio da pasta e grava o sidecar <arquivo>.txt
           ao lado (o receber_whatsapp le o sidecar e poe a fala inline).
           Sidecar existente NUNCA e sobrescrito.

  ARQUIVO → degravacao avulsa (ex.: atendimento gravado): gera
           DEGRAVACAO_<nome>.md ao lado, com o rotulo obrigatorio e os
           metadados (modelo, duracao, tempo). Com --sidecar, gera o
           <arquivo>.txt puro em vez do .md.

O programa vive num ambiente proprio FORA do OneDrive
(C:/Users/<voce>/.soj/transcritor/venv); este script se relanca sozinho
com o Python certo — pode rodar com o Python normal do sistema.

Uso:
  python degravar.py CAMINHO [--modelo small|medium|large-v3-turbo]
                     [--sidecar] [--idioma pt]
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

VENV_PY = Path.home() / ".soj" / "transcritor" / "venv" / "Scripts" / "python.exe"
try:
    from faster_whisper import WhisperModel
except ImportError:
    if VENV_PY.exists() and Path(sys.executable) != VENV_PY:
        sys.exit(subprocess.call([str(VENV_PY)] + sys.argv))
    sys.exit("[ERRO] faster-whisper nao instalado e o ambiente do transcritor "
             f"nao existe em {VENV_PY}. Peca ao Claude para reinstalar.")

sys.path.insert(0, str(Path(__file__).parent))
import soj_lib as soj

AUDIO_EXT = (".opus", ".ogg", ".mp3", ".m4a", ".wav", ".aac", ".flac", ".wma")


def transcrever(model, arquivo, idioma):
    """Degrava um arquivo; devolve (texto, duracao_audio_s, tempo_gasto_s)."""
    t0 = time.time()
    segmentos, info = model.transcribe(str(arquivo), language=idioma,
                                       beam_size=5, vad_filter=True)
    texto = " ".join(s.text.strip() for s in segmentos).strip()
    return texto, info.duration, time.time() - t0


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Transcritor local do SOJ.")
    ap.add_argument("caminho", help="Audio unico OU pasta de export do WhatsApp")
    ap.add_argument("--modelo", default="small",
                    help="small (padrao) | medium | large-v3-turbo | large-v3")
    ap.add_argument("--sidecar", action="store_true",
                    help="Arquivo unico: gerar <audio>.txt puro em vez do .md")
    ap.add_argument("--idioma", default="pt")
    args = ap.parse_args()

    alvo = Path(args.caminho)
    if not alvo.exists():
        sys.exit(f"[ERRO] Nao encontrei: {alvo}")
    if alvo.is_dir():
        audios = sorted(a for a in alvo.iterdir()
                        if a.suffix.lower() in AUDIO_EXT)
        if not audios:
            sys.exit(f"[ERRO] Nenhum audio na pasta {alvo}.")
    else:
        audios = [alvo]

    print(f"[..] Carregando modelo '{args.modelo}' (primeira vez baixa da "
          "internet; depois e instantaneo)...")
    model = WhisperModel(args.modelo, device="cpu", compute_type="int8")

    ok = pulados = erros = 0
    for audio in audios:
        sidecar = audio.with_name(audio.name + ".txt")
        modo_pasta = alvo.is_dir()
        if modo_pasta and sidecar.exists():
            print(f"[--] {audio.name}: sidecar ja existe, nao sobrescrevo.")
            pulados += 1
            continue
        try:
            texto, dur, gasto = transcrever(model, audio, args.idioma)
        except Exception as e:
            print(f"[ERRO] {audio.name}: nao consegui decodificar ({e}).")
            erros += 1
            continue
        if modo_pasta or args.sidecar:
            sidecar.write_text(texto + "\n", encoding="utf-8", newline="\n")
            saida = sidecar.name
        else:
            saida_md = audio.with_name(f"DEGRAVACAO_{audio.stem}.md")
            saida_md.write_text(
                f"# DEGRAVAÇÃO — {audio.name}\n\n"
                f"> ⚖️ {soj.ROTULO_DEGRAVACAO}\n\n"
                f"- Gerada em {soj.agora()} · modelo `{args.modelo}` (local, "
                f"CPU) · áudio de {dur/60:.1f} min · processado em "
                f"{gasto/60:.1f} min\n\n---\n\n{texto}\n",
                encoding="utf-8", newline="\n")
            saida = saida_md.name
        ok += 1
        print(f"[OK] {audio.name} ({dur:.0f}s de audio em {gasto:.0f}s) -> {saida}")

    print(f"\n[FIM] {ok} degravado(s), {pulados} pulado(s), {erros} erro(s).")
    if ok:
        print(f"LEMBRETE: {soj.ROTULO_DEGRAVACAO}")


if __name__ == "__main__":
    main()
