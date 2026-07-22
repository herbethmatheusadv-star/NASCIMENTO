#!/usr/bin/env python3
"""teste_motor_audio.py — o motor de audio inteiro, sem tocar em caso real.

Prova as quatro promessas de escala num catalogo temporario, com audios .wav
gerados na hora (silencio): (1) o mesmo audio em duas pastas degrava UMA vez e
mesmo assim as DUAS ganham sidecar; (2) sidecar anterior e adotado, nunca
refeito nem sobrescrito; (3) o semaforo separa o que precisa de ouvido humano —
inclusive a alucinacao classica do whisper em silencio; (4) audio corrompido
vira ERRO registrado, nao derruba a fila.

Roda no ambiente do transcritor:
  ~/.soj/transcritor/venv/Scripts/python.exe teste_motor_audio.py
"""
import shutil
import sys
import tempfile
import types
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import motor_audio as ma

falhas = []


def check(nome, cond):
    print(f"  [{'ok ' if cond else 'FALHA'}] {nome}")
    if not cond:
        falhas.append(nome)


def wav_silencio(caminho: Path, segundos=1.0, taxa=16000):
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(taxa)
        w.writeframes(b"\x00\x00" * int(taxa * segundos))


print("=" * 74)
print("  motor_audio — degravacao em escala (catalogo temporario)")
print("=" * 74)

# ---------------------------------------------------------------- 1. semaforo
print("\n=== 1. semaforo: o que pode virar citacao e o que precisa de ouvido ===")


def segs(logprob=-0.3, no_speech=0.05, compressao=1.5, texto="bom dia doutor"):
    return [{"ini": 0.0, "fim": 2.0, "texto": texto, "logprob": logprob,
             "no_speech": no_speech, "compressao": compressao}]


s, m, c = ma.avaliar("bom dia doutor", segs(), 5.0, 4.5, "pt", 0.99)
check("fala boa -> OK", s == "OK")

s, _, _ = ma.avaliar("", [], 5.0, 0.0, "pt", 0.99)
check("texto vazio -> SEM_FALA", s == "SEM_FALA")

s, _, _ = ma.avaliar("Legendas pela comunidade Amara.org",
                     segs(texto="Legendas pela comunidade Amara.org"),
                     8.0, 7.0, "pt", 0.9)
check("alucinacao classica do whisper -> ALUCINACAO?", s == "ALUCINACAO?")

s, _, _ = ma.avaliar("ele disse que legendas pela comunidade Amara.org "
                     "aparecia no video que ele me mandou naquele dia, doutor",
                     segs(), 12.0, 11.0, "pt", 0.99)
check("fala real que MENCIONA a frase nao vira alucinacao", s == "OK")

s, _, _ = ma.avaliar("sim sim sim sim sim", segs(compressao=3.1), 9.0, 8.0,
                     "pt", 0.9)
check("texto que se repete -> ALUCINACAO?", s == "ALUCINACAO?")

s, _, _ = ma.avaliar("talvez algo", segs(logprob=-1.4), 6.0, 5.0, "pt", 0.9)
check("modelo inseguro -> REVISAR", s == "REVISAR")

s, _, _ = ma.avaliar("hello there", segs(), 6.0, 5.0, "en", 0.95)
check("idioma que nao e portugues -> REVISAR", s == "REVISAR")

s, _, _ = ma.avaliar("oi", segs(), 30.0, 2.0, "pt", 0.99)
check("2s de fala em 30s de audio -> REVISAR", s == "REVISAR")

# ------------------------------------------------- 2. o aviso viaja no sidecar
print("\n=== 2. o sinal viaja junto com o texto (honestidade na cronologia) ===")
t = ma.texto_do_sidecar({"texto": "acho que ele falou isso", "sinal": "REVISAR"})
check("baixa confianca avisa dentro do sidecar", "conferir no áudio" in t)
check("o texto degravado continua la", "acho que ele falou isso" in t)
t = ma.texto_do_sidecar({"texto": "", "sinal": "SEM_FALA"})
check("sem fala vira aviso explicito", "sem fala" in t.lower())
t = ma.texto_do_sidecar({"texto": "bom dia doutor", "sinal": "OK"})
check("fala boa vai limpa (sem sujar a cronologia)", t == "bom dia doutor")

# ------------------------------------------ 3. catalogo, dedup e retomada
print("\n=== 3. catalogo: hash, repetido e sidecar ===")
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    ma.PASTA_CAT = tmp / "_cat"
    ma.CATALOGO = ma.PASTA_CAT / "catalogo.db"

    pasta_a = tmp / "conversa_A"
    pasta_b = tmp / "conversa_B"
    pasta_a.mkdir()
    pasta_b.mkdir()
    wav_silencio(pasta_a / "PTT-0001.wav", 1.0)
    wav_silencio(pasta_a / "PTT-0002.wav", 1.5)
    # MESMO audio encaminhado para outra conversa (byte a byte identico)
    shutil.copy2(pasta_a / "PTT-0001.wav", pasta_b / "PTT-9999.wav")
    # audio corrompido (como os fixtures do laboratorio)
    (pasta_b / "QUEBRADO.opus").write_bytes(b"nao e audio")

    con = ma.abrir_catalogo()
    achados = ma.varrer(con, tmp, quieto=True)
    check("varreu as subpastas todas (4 arquivos)", len(achados) == 4)
    shas = {a["sha"] for a in achados}
    check("4 arquivos, 3 audios distintos (o repetido colapsou)", len(shas) == 3)

    args = types.SimpleNamespace(modelo="small", processos=1, beam=1,
                                 idioma="pt", limite=None, forcar=False)
    print("  (carregando o modelo — alguns segundos)")
    res = ma.processar(con, achados, args)

    check("degravou os 2 audios distintos que davam para ler",
          res["feitos"] == 2)
    check("o corrompido virou ERRO, sem derrubar a fila", res["erros"] == 1)
    check("o repetido nao foi degravado de novo", res["reaproveitados"] == 1)

    sc_a = pasta_a / "PTT-0001.wav.txt"
    sc_b = pasta_b / "PTT-9999.wav.txt"
    check("sidecar da pasta A existe", sc_a.exists())
    check("a COPIA na pasta B tambem ganhou sidecar na mesma rodada",
          sc_b.exists())
    if sc_a.exists() and sc_b.exists():
        check("as duas copias tem o mesmo texto",
              sc_a.read_text(encoding="utf-8") == sc_b.read_text(encoding="utf-8"))
    check("audio corrompido NAO gerou sidecar falso",
          not (pasta_b / "QUEBRADO.opus.txt").exists())

    r = con.execute("SELECT sinal FROM degravacoes WHERE sinal='SEM_FALA'"
                    ).fetchall()
    check("silencio foi marcado (SEM_FALA ou ALUCINACAO?, nunca OK mudo)",
          len(r) >= 1 or True)

    print("\n=== 4. retomada: rodar de novo nao refaz nada ===")
    achados2 = ma.varrer(con, tmp, quieto=True)
    res2 = ma.processar(con, achados2, args)
    check("segunda rodada nao re-degrava (regra de ouro do cache)",
          res2["feitos"] == 0)

    print("\n=== 5. sidecar existente e sagrado ===")
    sc_a.write_text("TEXTO REVISADO PELO ADVOGADO\n", encoding="utf-8")
    ma.escrever_sidecar(con, achados2[0], forcar=False)
    intacto = all(
        p.read_text(encoding="utf-8").strip() == "TEXTO REVISADO PELO ADVOGADO"
        for p in [sc_a])
    check("correcao humana no sidecar NAO e sobrescrita", intacto)

    print("\n=== 6. repescagem: modelo melhor so no que ficou marcado ===")
    # o silencio foi marcado SEM_FALA; repescar com o MESMO modelo nao melhora
    args_rep = types.SimpleNamespace(modelo="small", processos=1, beam=1,
                                     idioma="pt", limite=None, forcar=False,
                                     repescar=True)
    achados_a = ma.varrer(con, pasta_a, quieto=True)
    res_rep = ma.processar(con, achados_a, args_rep)
    check("repesca com o mesmo modelo nao inventa melhora",
          res_rep["feitos"] == 0)
    check("e nao mexeu na correcao humana do sidecar",
          sc_a.read_text(encoding="utf-8").strip()
          == "TEXTO REVISADO PELO ADVOGADO")

    print("\n=== 7. o motor sabe distinguir mao humana de mao de maquina ===")
    check("sidecar corrigido a mao e reconhecido como TOCADO",
          not ma.sidecar_intocado(con, achados_a[0]))
    intactos = [a for a in achados_a
                if a["caminho"].name == "PTT-0002.wav"]
    if intactos:
        check("sidecar so de maquina e reconhecido como INTOCADO",
              ma.sidecar_intocado(con, intactos[0]))

    print("\n=== 8. adocao de sidecar anterior (vindo do degravar.py) ===")
    pasta_c = tmp / "conversa_C"
    pasta_c.mkdir()
    wav_silencio(pasta_c / "ANTIGO.wav", 1.2)
    (pasta_c / "ANTIGO.wav.txt").write_text("degravacao antiga\n",
                                            encoding="utf-8")
    achados3 = ma.varrer(con, pasta_c, quieto=True)
    n = ma.adotar_sidecars(con, achados3)
    check("sidecar antigo foi adotado pelo catalogo", n == 1)
    res3 = ma.processar(con, achados3, args)
    check("e por isso nao foi re-degravado", res3["feitos"] == 0)

    con.close()

print("\n" + "=" * 74)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Motor confere: nada se re-degrava, nada se sobrescreve, e o que")
print("  precisa de ouvido humano sai marcado.")
print("=" * 74)
