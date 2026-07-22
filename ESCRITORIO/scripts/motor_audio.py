# -*- coding: utf-8 -*-
"""
motor_audio.py — MOTOR DE AUDIO do SOJ: degravacao em ESCALA (centenas,
milhares de audios de WhatsApp), 100% dentro desta maquina.

O degravar.py (Onda 4) resolve 1 audio ou 1 pasta pequena, do zero, toda vez.
Isso nao sobe para milhares: se cair a energia no audio 700, perde-se tudo; o
mesmo audio encaminhado em 3 conversas e degravado 3 vezes; e nada avisa que a
degravacao 412 saiu ruim. O MOTOR resolve os quatro problemas de escala:

  1. CATALOGO (SQLite, fora do git) com o SHA-256 de cada audio. Vale aqui a
     REGRA DE OURO DO CACHE do SOJ: nada se re-degrava. Mesmo hash = mesma
     fala, degravada UMA vez, ainda que o arquivo apareca em 10 pastas.
  2. RETOMADA: a fila e persistente e o sidecar e gravado assim que cada audio
     fica pronto. Ctrl+C, queda de energia ou reboot no meio de 2.000 audios
     custa, no maximo, o audio que estava na agulha.
  3. SEMAFORO DE CONFIANCA: whisper erra e, pior, ALUCINA em silencio
     ("Legendas pela comunidade Amara.org"). Degravacao e material de prova —
     entao cada audio sai com sinal OK / REVISAR / SEM_FALA / ALUCINACAO?, e o
     que nao for OK entra numa lista de conferencia humana.
  4. FITA DE TEMPO: cada trecho guarda inicio e fim, para citar a fala pelo
     minuto ("aos 1min12s do audio X") em peca e em audiencia.

Compativel com o que ja existe: escreve o mesmo sidecar `<audio>.txt` que o
receber_whatsapp.py le, e NUNCA sobrescreve sidecar existente (sem --forcar).
Sidecar antigo, feito pelo degravar.py, e ADOTADO pelo catalogo (nao se refaz).

Uso (roda com o Python normal; se relanca sozinho no ambiente do transcritor):
  python motor_audio.py CAMINHO                 # varre e degrava o que falta
  python motor_audio.py CAMINHO --status        # so o mapa: quanto falta e quanto demora
  python motor_audio.py CAMINHO --revisar       # lista o que precisa de ouvido humano
  python motor_audio.py CAMINHO --relatorio     # DEGRAVACAO_<pasta>.md com os minutos
  python motor_audio.py --catalogo              # estado geral do catalogo

  python motor_audio.py CAMINHO --buscar "pagamento"   # acha a fala e o MINUTO

Opcoes: --modelo large-v3-turbo|small|medium · --processos N · --limite N
        --forcar · --repescar · --idioma pt · --beam N

MODELO PADRAO: large-v3-turbo, por decisao do advogado em 22/07/2026. O small
e ~3x mais rapido, mas erra nome proprio COM CONFIANCA ("Edison" por "Edson") —
e erro confiante o semaforo nao pega. Como a degravacao vira citacao em peca,
aqui a precisao vale o tempo. Para triagem rapida de acervo, use --modelo small.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
import unicodedata
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path

VENV_PY = Path.home() / ".soj" / "transcritor" / "venv" / "Scripts" / "python.exe"

# O motor SO roda no ambiente do transcritor. Se foi chamado com outro Python,
# se relanca la (mesmo truque do degravar.py) — o advogado nao precisa saber.
try:
    import av  # noqa: F401  (usado para medir duracao sem ffmpeg)
    from faster_whisper import WhisperModel  # noqa: F401
except ImportError:
    if VENV_PY.exists() and Path(sys.executable) != VENV_PY:
        sys.exit(subprocess.call([str(VENV_PY)] + sys.argv))
    sys.exit("[ERRO] O ambiente do transcritor nao existe em "
             f"{VENV_PY}. Peca ao Claude para reinstalar.")

sys.path.insert(0, str(Path(__file__).parent))
import soj_lib as soj

RAIZ = soj.ROOT
PASTA_CAT = RAIZ / "_SISTEMA" / "audio"
CATALOGO = PASTA_CAT / "catalogo.db"

AUDIO_EXT = (".opus", ".ogg", ".mp3", ".m4a", ".wav", ".aac", ".flac", ".wma",
             ".amr", ".mp4a")

# Alucinacoes classicas do whisper em pt quando o audio e silencio/ruido.
# Aparecem inteiras e sozinhas — por isso a comparacao e do texto TODO.
ALUCINACOES = [
    "legendas pela comunidade amara.org", "amara.org",
    "legendado por", "subtitles by", "subtitulos por",
    "obrigado por assistir", "obrigada por assistir",
    "inscreva-se no canal", "ate o proximo video", "ate a proxima",
    "muito obrigado a todos", "compartilhe esse video",
]

# Limiares do semaforo. Calibrados para fala de WhatsApp (curta, com ruido).
LIM_LOGPROB = -1.0      # abaixo disso o modelo estava "chutando"
LIM_NO_SPEECH = 0.6     # acima disso provavelmente nao ha fala
LIM_COMPRESSAO = 2.4    # acima disso o texto se repete (sintoma de alucinacao)


# ----------------------------------------------------------------- catalogo
def abrir_catalogo() -> sqlite3.Connection:
    """Catalogo e CACHE: fica fora do git e se reconstroi dos sidecars."""
    PASTA_CAT.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(CATALOGO, timeout=30)
    con.execute("PRAGMA journal_mode=WAL")     # sobrevive a queda de energia
    con.executescript("""
    CREATE TABLE IF NOT EXISTS degravacoes (
        sha256      TEXT PRIMARY KEY,
        duracao_s   REAL,
        modelo      TEXT,
        idioma      TEXT,
        prob_idioma REAL,
        texto       TEXT,
        segmentos   TEXT,
        confianca   REAL,
        sinal       TEXT,
        motivo      TEXT,
        tempo_s     REAL,
        quando      TEXT
    );
    CREATE TABLE IF NOT EXISTS arquivos (
        caminho   TEXT PRIMARY KEY,
        sha256    TEXT,
        tamanho   INTEGER,
        duracao_s REAL,
        visto_em  TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_arq_sha ON arquivos(sha256);
    CREATE INDEX IF NOT EXISTS idx_deg_sinal ON degravacoes(sinal);
    """)
    return con


def rel(caminho: Path) -> str:
    """Caminho relativo a raiz — o catalogo nao guarda caminho absoluto."""
    try:
        return caminho.resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return caminho.resolve().as_posix()


def duracao_de(caminho: Path) -> float:
    """Duracao em segundos, lida do container (sem decodificar o audio todo)."""
    try:
        with av.open(str(caminho)) as c:
            if c.duration:
                return c.duration / 1_000_000
            for s in c.streams:
                if s.type == "audio" and s.duration and s.time_base:
                    return float(s.duration * s.time_base)
    except Exception:
        pass
    return 0.0


# ----------------------------------------------------------------- varredura
def varrer(con: sqlite3.Connection, alvo: Path, quieto=False) -> list[dict]:
    """Descobre os audios sob 'alvo' (recursivo), com hash e duracao.

    Hash e duracao so se recalculam se o arquivo mudou de tamanho — varrer
    2.000 audios ja catalogados custa segundos, nao minutos.
    """
    if alvo.is_file():
        candidatos = [alvo] if alvo.suffix.lower() in AUDIO_EXT else []
    else:
        candidatos = sorted(p for p in alvo.rglob("*")
                            if p.is_file() and p.suffix.lower() in AUDIO_EXT)
    if not candidatos:
        return []

    conhecidos = {r[0]: (r[1], r[2], r[3]) for r in con.execute(
        "SELECT caminho, sha256, tamanho, duracao_s FROM arquivos")}

    achados, novos = [], 0
    for i, arq in enumerate(candidatos, 1):
        chave = rel(arq)
        tam = arq.stat().st_size
        antigo = conhecidos.get(chave)
        if antigo and antigo[1] == tam:
            sha, dur = antigo[0], antigo[2]
        else:
            sha = soj.sha256_arquivo(arq)
            dur = duracao_de(arq)
            con.execute(
                "INSERT INTO arquivos(caminho,sha256,tamanho,duracao_s,visto_em)"
                " VALUES(?,?,?,?,?) ON CONFLICT(caminho) DO UPDATE SET"
                " sha256=excluded.sha256, tamanho=excluded.tamanho,"
                " duracao_s=excluded.duracao_s, visto_em=excluded.visto_em",
                (chave, sha, tam, dur, soj.agora()))
            novos += 1
            if not quieto and novos % 200 == 0:
                print(f"[..] catalogando... {novos} arquivos novos", flush=True)
        achados.append({"caminho": arq, "chave": chave, "sha": sha, "dur": dur})
    con.commit()
    if novos and not quieto:
        print(f"[OK] {novos} audio(s) novo(s) no catalogo "
              f"({len(achados)} no total sob o alvo).")
    return achados


def adotar_sidecars(con: sqlite3.Connection, achados: list[dict]) -> int:
    """Sidecar que ja existe (feito pelo degravar.py) entra no catalogo como
    IMPORTADO. Trabalho antigo nunca se refaz — e nunca se sobrescreve."""
    tem = {r[0] for r in con.execute("SELECT sha256 FROM degravacoes")}
    n = 0
    for a in achados:
        if a["sha"] in tem:
            continue
        sc = a["caminho"].with_name(a["caminho"].name + ".txt")
        if not sc.exists():
            continue
        texto = sc.read_text(encoding="utf-8", errors="replace").strip()
        con.execute(
            "INSERT OR IGNORE INTO degravacoes(sha256,duracao_s,modelo,idioma,"
            "prob_idioma,texto,segmentos,confianca,sinal,motivo,tempo_s,quando)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["sha"], a["dur"], "(sidecar anterior)", "pt", None, texto,
             "[]", None, "IMPORTADO",
             "degravacao anterior adotada do sidecar; sem fita de tempo",
             None, soj.agora()))
        tem.add(a["sha"])
        n += 1
    con.commit()
    return n


# ----------------------------------------------------------------- semaforo
def _normaliza(t: str) -> str:
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return " ".join(t.lower().split())


def avaliar(texto: str, segs: list[dict], dur: float, dur_vad: float,
            idioma: str, prob_idioma: float) -> tuple[str, str, float | None]:
    """Semaforo da degravacao: (sinal, motivo, confianca).

    Nao "conserta" nada — apenas diz, com honestidade, o que merece ouvido
    humano ANTES de virar citacao em peca.
    """
    if not texto.strip():
        return "SEM_FALA", "nenhuma fala reconhecida no audio", None

    conf = None
    if segs:
        conf = sum(s["logprob"] for s in segs) / len(segs)

    n = _normaliza(texto)
    for frase in ALUCINACOES:
        # alucinacao ocupa o audio inteiro; texto real que MENCIONA a frase e maior
        if frase in n and len(n) < len(frase) + 25:
            return ("ALUCINACAO?",
                    f"texto tipico de alucinacao em silencio ('{texto[:40]}')", conf)

    if dur_vad and dur and dur_vad < 0.35 * dur and dur > 3:
        return ("REVISAR", f"so {dur_vad:.1f}s de fala em {dur:.0f}s de audio "
                "(muito silencio/ruido)", conf)

    if segs:
        pior_ns = max(s["no_speech"] for s in segs)
        pior_cr = max(s["compressao"] for s in segs)
        if pior_cr > LIM_COMPRESSAO:
            return ("ALUCINACAO?", f"texto se repete (compressao {pior_cr:.1f})", conf)
        if pior_ns > LIM_NO_SPEECH:
            return ("REVISAR", f"trecho com alta chance de nao ser fala "
                    f"({pior_ns:.0%})", conf)
    if conf is not None and conf < LIM_LOGPROB:
        return "REVISAR", f"modelo pouco seguro (confianca {conf:.2f})", conf
    if idioma != "pt" and (prob_idioma or 0) > 0.5:
        return "REVISAR", f"detectou idioma '{idioma}', nao portugues", conf
    return "OK", "", conf


# ----------------------------------------------------------------- trabalho
_MODELO = None
_CFG: dict = {}


def _init_worker(modelo: str, threads: int, idioma: str, beam: int):
    global _MODELO, _CFG
    from faster_whisper import WhisperModel
    _MODELO = WhisperModel(modelo, device="cpu", compute_type="int8",
                           cpu_threads=threads)
    _CFG = {"idioma": idioma, "beam": beam, "nome": modelo}


def _degravar_um(tarefa: tuple[str, str, float]) -> dict:
    """Roda no processo filho. Nunca levanta excecao: erro vira registro."""
    sha, caminho, dur = tarefa
    t0 = time.time()
    try:
        segs_it, info = _MODELO.transcribe(
            caminho, language=_CFG["idioma"], beam_size=_CFG["beam"],
            vad_filter=True, condition_on_previous_text=False)
        segs = [{"ini": round(s.start, 2), "fim": round(s.end, 2),
                 "texto": s.text.strip(), "logprob": round(s.avg_logprob, 3),
                 "no_speech": round(s.no_speech_prob, 3),
                 "compressao": round(s.compression_ratio, 2)}
                for s in segs_it]
        texto = " ".join(s["texto"] for s in segs).strip()
        sinal, motivo, conf = avaliar(
            texto, segs, info.duration, getattr(info, "duration_after_vad", 0),
            info.language, info.language_probability)
        return {"sha": sha, "caminho": caminho, "ok": True, "texto": texto,
                "segmentos": segs, "duracao": info.duration or dur,
                "idioma": info.language, "prob_idioma": info.language_probability,
                "sinal": sinal, "motivo": motivo, "confianca": conf,
                "tempo": time.time() - t0, "modelo": _CFG["nome"]}
    except Exception as e:
        return {"sha": sha, "caminho": caminho, "ok": False,
                "erro": f"{type(e).__name__}: {e}", "tempo": time.time() - t0,
                "duracao": dur}


def texto_do_sidecar(r: dict) -> str:
    """O que vai para o `<audio>.txt`. O sinal viaja junto: quem ler a
    cronologia depois PRECISA saber que aquele trecho nao esta conferido."""
    if r["sinal"] == "SEM_FALA":
        return "[sem fala audível — áudio sem conteúdo de voz reconhecido]"
    if r["sinal"] in ("REVISAR", "ALUCINACAO?"):
        return f"{r['texto']} [degravação de baixa confiança — conferir no áudio]"
    return r["texto"]


def sidecar_intocado(con: sqlite3.Connection, a: dict) -> bool:
    """O sidecar ainda e o que a maquina escreveu, ou o advogado corrigiu?

    Se o conteudo bate com o que o motor gravou, e material de maquina e pode
    ser substituido por uma degravacao melhor. Se NAO bate, houve mao humana
    ali — e mao humana nunca se sobrescreve.
    """
    sc = a["caminho"].with_name(a["caminho"].name + ".txt")
    if not sc.exists():
        return True
    linha = con.execute(
        "SELECT texto, sinal, motivo FROM degravacoes WHERE sha256=?",
        (a["sha"],)).fetchone()
    if not linha:
        return False
    esperado = texto_do_sidecar({"texto": linha[0] or "", "sinal": linha[1],
                                 "motivo": linha[2]})
    return sc.read_text(encoding="utf-8", errors="replace").strip() == esperado.strip()


def processar(con: sqlite3.Connection, achados: list[dict], args) -> dict:
    """A fila: so entra audio sem degravacao no catalogo (ou com --forcar).

    Com --repescar, a fila e outra: sao os audios que o semaforo marcou, para
    uma segunda tentativa com modelo melhor.
    """
    if getattr(args, "repescar", False):
        return repescar(con, achados, args)

    feitos = {r[0] for r in con.execute(
        "SELECT sha256 FROM degravacoes WHERE sinal != 'ERRO'")}

    fila, vistos, reaproveitados = [], set(), 0
    for a in achados:
        if a["sha"] in feitos and not args.forcar:
            continue
        if a["sha"] in vistos:          # audio repetido DENTRO da mesma varredura
            reaproveitados += 1
            continue
        vistos.add(a["sha"])
        fila.append(a)

    # audios repetidos que ja tem texto: so falta escrever o sidecar
    for a in achados:
        if a["sha"] in feitos and not args.forcar:
            escrever_sidecar(con, a, args.forcar)

    if not fila:
        return {"feitos": 0, "erros": 0, "reaproveitados": reaproveitados}

    if args.limite:
        fila = fila[:args.limite]
    fila.sort(key=lambda a: -a["dur"])          # os longos primeiro: empacota melhor
    seg_total = sum(a["dur"] for a in fila)

    ritmo = ritmo_medido(con, args.modelo)
    print(f"\n[FILA] {len(fila)} audio(s) para degravar — "
          f"{seg_total/60:.1f} min de audio.")
    if reaproveitados:
        print(f"       {reaproveitados} repetido(s) aproveitado(s) do catalogo "
              "(mesmo hash, nao se re-degrava).")
    if ritmo:
        print(f"       Estimativa: ~{seg_total/ritmo/60:.0f} min "
              f"(ritmo medido: {ritmo:.1f}x tempo real).")
    print(f"       Modelo '{args.modelo}', {args.processos} processo(s), "
          "tudo dentro desta maquina.\n")

    tarefas = [(a["sha"], str(a["caminho"]), a["dur"]) for a in fila]
    por_sha = {a["sha"]: a for a in fila}
    # o mesmo audio pode estar em varias pastas: TODAS recebem o sidecar nesta
    # rodada (senao a copia so seria atendida na proxima vez que se rodasse)
    copias: dict[str, list[dict]] = {}
    for a in achados:
        copias.setdefault(a["sha"], []).append(a)
    t0 = time.time()
    n_ok = n_erro = n_atencao = 0
    seg_feito = 0.0

    def registrar(r):
        nonlocal n_ok, n_erro, n_atencao, seg_feito
        a = por_sha[r["sha"]]
        seg_feito += r.get("duracao", 0) or 0
        if not r["ok"]:
            n_erro += 1
            con.execute(
                "INSERT OR REPLACE INTO degravacoes(sha256,duracao_s,modelo,"
                "texto,segmentos,sinal,motivo,tempo_s,quando)"
                " VALUES(?,?,?,?,?,?,?,?,?)",
                (r["sha"], r.get("duracao"), args.modelo, "", "[]", "ERRO",
                 r["erro"], r["tempo"], soj.agora()))
            print(f"[ERRO] {a['caminho'].name}: {r['erro'][:90]}")
            return
        con.execute(
            "INSERT OR REPLACE INTO degravacoes(sha256,duracao_s,modelo,idioma,"
            "prob_idioma,texto,segmentos,confianca,sinal,motivo,tempo_s,quando)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["sha"], r["duracao"], r["modelo"], r["idioma"],
             r["prob_idioma"], r["texto"],
             json.dumps(r["segmentos"], ensure_ascii=False), r["confianca"],
             r["sinal"], r["motivo"], r["tempo"], soj.agora()))
        n_ok += 1
        if r["sinal"] != "OK":
            n_atencao += 1
        for copia in copias.get(r["sha"], [a]):
            escrever_sidecar(con, copia, args.forcar)

        feito = n_ok + n_erro
        el = time.time() - t0
        falta = (seg_total - seg_feito) / (seg_feito / el) if seg_feito else 0
        marca = "" if r["sinal"] == "OK" else f"  <{r['sinal']}>"
        print(f"[{feito:>4}/{len(fila)}] {a['caminho'].name[:44]:<44} "
              f"{r['duracao']:>5.0f}s em {r['tempo']:>5.1f}s"
              f"{marca}   falta ~{falta/60:.0f} min", flush=True)

    try:
        if args.processos <= 1:
            _init_worker(args.modelo, 0, args.idioma, args.beam)
            for t in tarefas:
                registrar(_degravar_um(t))
                con.commit()
        else:
            threads = max(1, (os.cpu_count() or 4) // args.processos)
            with ProcessPoolExecutor(
                    max_workers=args.processos, initializer=_init_worker,
                    initargs=(args.modelo, threads, args.idioma, args.beam)) as ex:
                for r in ex.map(_degravar_um, tarefas, chunksize=1):
                    registrar(r)
                    con.commit()
    except KeyboardInterrupt:
        con.commit()
        print("\n[PARADO] Interrompido pelo advogado. O que ja ficou pronto "
              "esta salvo — e so rodar de novo que ele continua daqui.")
    con.commit()
    return {"feitos": n_ok, "erros": n_erro, "atencao": n_atencao,
            "reaproveitados": reaproveitados}


RANK = {"OK": 3, "IMPORTADO": 3, "REVISAR": 2, "ALUCINACAO?": 1,
        "SEM_FALA": 1, "ERRO": 0}


def repescar(con: sqlite3.Connection, achados: list[dict], args) -> dict:
    """Segunda tentativa, com modelo melhor, SO no que o semaforo marcou.

    A economia do escritorio mora aqui: a varredura inteira roda no modelo
    rapido; o modelo caro (e lento) so trabalha nos poucos audios duvidosos —
    que sao, justamente, os que podem virar citacao errada numa peca.

    Troca o texto apenas se o resultado novo for MELHOR no semaforo, e apenas
    se o sidecar ainda for material de maquina. Sidecar corrigido pelo
    advogado e soberano: fica como esta, e o motor avisa.
    """
    alvos, vistos = [], set()
    for a in achados:
        if a["sha"] in vistos:
            continue
        r = con.execute("SELECT sinal FROM degravacoes WHERE sha256=?",
                        (a["sha"],)).fetchone()
        if r and r[0] not in ("OK", "IMPORTADO"):
            vistos.add(a["sha"])
            alvos.append(a)

    if not alvos:
        print("\n[OK] Nada a repescar: nenhum audio marcado pelo semaforo "
              "nesta pasta.")
        return {"feitos": 0, "erros": 0, "atencao": 0, "reaproveitados": 0}

    seg = sum(a["dur"] for a in alvos)
    print(f"\n[REPESCA] {len(alvos)} audio(s) marcado(s) — {seg/60:.1f} min — "
          f"agora no modelo '{args.modelo}'.")
    print("          Os que ja estavam OK nao se tocam.\n")

    _init_worker(args.modelo, 0, args.idioma, args.beam)
    melhorou = igual = protegido = erros = 0
    copias: dict[str, list[dict]] = {}
    for a in achados:
        copias.setdefault(a["sha"], []).append(a)

    for i, a in enumerate(alvos, 1):
        antes = con.execute(
            "SELECT sinal, texto FROM degravacoes WHERE sha256=?",
            (a["sha"],)).fetchone()
        intocado = sidecar_intocado(con, a)
        r = _degravar_um((a["sha"], str(a["caminho"]), a["dur"]))
        if not r["ok"]:
            erros += 1
            print(f"[{i:>3}/{len(alvos)}] {a['caminho'].name[:40]:<40} ERRO")
            continue
        if RANK.get(r["sinal"], 0) <= RANK.get(antes[0], 0):
            igual += 1
            print(f"[{i:>3}/{len(alvos)}] {a['caminho'].name[:40]:<40} "
                  f"{antes[0]} -> {r['sinal']} (nao melhorou, mantido)")
            continue
        con.execute(
            "INSERT OR REPLACE INTO degravacoes(sha256,duracao_s,modelo,idioma,"
            "prob_idioma,texto,segmentos,confianca,sinal,motivo,tempo_s,quando)"
            " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["sha"], r["duracao"], r["modelo"], r["idioma"], r["prob_idioma"],
             r["texto"], json.dumps(r["segmentos"], ensure_ascii=False),
             r["confianca"], r["sinal"], r["motivo"], r["tempo"], soj.agora()))
        con.commit()
        melhorou += 1
        if intocado:
            for copia in copias.get(a["sha"], [a]):
                escrever_sidecar(con, copia, forcar=True)
            print(f"[{i:>3}/{len(alvos)}] {a['caminho'].name[:40]:<40} "
                  f"{antes[0]} -> {r['sinal']}  ATUALIZADO")
        else:
            protegido += 1
            print(f"[{i:>3}/{len(alvos)}] {a['caminho'].name[:40]:<40} "
                  f"{antes[0]} -> {r['sinal']}  (sidecar corrigido a mao: "
                  "catalogo atualizado, arquivo PRESERVADO)")

    print(f"\n[FIM DA REPESCA] {melhorou} melhorou(aram), {igual} sem ganho, "
          f"{erros} erro(s).")
    if protegido:
        print(f"  {protegido} sidecar(es) tinham correcao humana e NAO foram "
              "tocados — confira se quer adotar a versao nova.")
    return {"feitos": melhorou, "erros": erros, "atencao": 0,
            "reaproveitados": 0}


def escrever_sidecar(con: sqlite3.Connection, a: dict, forcar: bool) -> bool:
    """Grava `<audio>.txt` — a porta pela qual o receber_whatsapp.py le a fala.
    Sidecar existente NUNCA e sobrescrito sem --forcar (regra da Onda 4)."""
    sc = a["caminho"].with_name(a["caminho"].name + ".txt")
    if sc.exists() and not forcar:
        return False
    linha = con.execute(
        "SELECT texto, sinal, motivo FROM degravacoes WHERE sha256=?",
        (a["sha"],)).fetchone()
    if not linha:
        return False
    texto, sinal, motivo = linha
    r = {"texto": texto or "", "sinal": sinal, "motivo": motivo}
    if sinal in ("ERRO",):
        return False
    sc.write_text(texto_do_sidecar(r) + "\n", encoding="utf-8", newline="\n")
    return True


def ritmo_medido(con: sqlite3.Connection, modelo: str) -> float | None:
    """Quantas vezes o tempo real esta maquina degrava — medido do proprio
    historico, entao a estimativa melhora sozinha a cada rodada."""
    r = con.execute(
        "SELECT SUM(duracao_s), SUM(tempo_s) FROM degravacoes "
        "WHERE modelo=? AND tempo_s IS NOT NULL AND tempo_s > 0",
        (modelo,)).fetchone()
    if r and r[0] and r[1]:
        return r[0] / r[1]
    return None


# ----------------------------------------------------------------- relatorios
def mmss(s: float) -> str:
    return f"{int(s)//60}min{int(s)%60:02d}s"


def mostrar_status(con, achados, args):
    tot = len(achados)
    seg = sum(a["dur"] for a in achados)
    unicos = {a["sha"] for a in achados}
    feitos = {r[0] for r in con.execute(
        "SELECT sha256 FROM degravacoes WHERE sinal != 'ERRO'")}
    prontos = unicos & feitos
    falta = unicos - feitos
    seg_falta = sum(a["dur"] for a in achados if a["sha"] in falta)

    print(f"\n=== MAPA DO AUDIO — {args.caminho} ===")
    print(f"  arquivos de audio ....... {tot}")
    print(f"  audios distintos ........ {len(unicos)}"
          + (f"  ({tot - len(unicos)} repetidos — degravam 1 vez so)"
             if tot != len(unicos) else ""))
    print(f"  duracao total ........... {seg/60:.1f} min")
    print(f"  ja degravados ........... {len(prontos)}")
    print(f"  faltando ................ {len(falta)}  ({seg_falta/60:.1f} min)")
    ritmo = ritmo_medido(con, args.modelo)
    if falta and ritmo:
        print(f"  tempo estimado .......... ~{seg_falta/ritmo/60:.0f} min "
              f"(ritmo medido: {ritmo:.1f}x tempo real)")
    elif falta:
        print("  tempo estimado .......... (ainda sem medicao desta maquina)")

    sinais = {}
    for a in achados:
        r = con.execute("SELECT sinal FROM degravacoes WHERE sha256=?",
                        (a["sha"],)).fetchone()
        if r:
            sinais[r[0]] = sinais.get(r[0], 0) + 1
    if sinais:
        print("\n  semaforo das degravacoes:")
        for s in ("OK", "IMPORTADO", "REVISAR", "ALUCINACAO?", "SEM_FALA", "ERRO"):
            if s in sinais:
                print(f"    {s:<12} {sinais[s]}")
    print()


def mostrar_revisar(con, achados, args):
    """A lista de conferencia: o que NAO pode virar citacao sem ouvir."""
    print(f"\n=== CONFERENCIA HUMANA — {args.caminho} ===")
    print(f"{soj.ROTULO_DEGRAVACAO}\n")
    n = 0
    for a in sorted(achados, key=lambda x: x["caminho"].name):
        r = con.execute(
            "SELECT sinal, motivo, texto, confianca FROM degravacoes "
            "WHERE sha256=? AND sinal NOT IN ('OK','IMPORTADO')",
            (a["sha"],)).fetchone()
        if not r:
            continue
        n += 1
        sinal, motivo, texto, conf = r
        print(f"[{sinal}] {a['caminho'].name}  ({a['dur']:.0f}s)")
        print(f"    por que: {motivo}")
        if texto:
            print(f"    saiu:    \"{texto[:110]}\"")
        print(f"    ouvir:   {a['chave']}\n")
    if not n:
        print("Nada a conferir: todas as degravacoes desta pasta passaram no "
              "semaforo.\n")
    else:
        print(f"{n} degravacao(oes) pedem ouvido humano antes de virar citacao.\n")


def gerar_relatorio(con, achados, args):
    """DEGRAVACAO_<pasta>.md — o produto de trabalho, com os minutos para citar."""
    alvo = Path(args.caminho)
    base = alvo if alvo.is_dir() else alvo.parent
    saida = base / f"DEGRAVACAO_{soj.slug(base.name)[:40]}.md"

    linhas = [f"# DEGRAVACAO — {base.name}", "",
              f"> ⚖️ {soj.ROTULO_DEGRAVACAO}", "",
              f"- Gerada em {soj.agora()} pelo motor de áudio do SOJ "
              f"(modelo `{args.modelo}`, 100% local — nenhum áudio saiu da máquina)",
              f"- {len(achados)} áudio(s) nesta pasta", "",
              "Cada fala traz o **minuto dentro do áudio** para citação direta "
              "em peça ou audiência.", "", "---", ""]
    n_at = 0
    for a in sorted(achados, key=lambda x: x["caminho"].name):
        r = con.execute(
            "SELECT texto, segmentos, sinal, motivo, duracao_s FROM degravacoes"
            " WHERE sha256=?", (a["sha"],)).fetchone()
        if not r:
            continue
        texto, segs_json, sinal, motivo, dur = r
        aviso = "" if sinal in ("OK", "IMPORTADO") else \
            f"  ⚠️ **{sinal}** — {motivo}"
        linhas.append(f"## {a['caminho'].name}  ({mmss(dur or 0)}){aviso}")
        linhas.append("")
        if sinal not in ("OK", "IMPORTADO"):
            n_at += 1
        try:
            segs = json.loads(segs_json or "[]")
        except json.JSONDecodeError:
            segs = []
        if segs:
            for s in segs:
                linhas.append(f"- `{mmss(s['ini'])}–{mmss(s['fim'])}` "
                              f"{s['texto']}")
        elif texto:
            linhas.append(f"- {texto}")
        else:
            linhas.append("- *(sem fala reconhecida)*")
        linhas.append("")
    if n_at:
        linhas += ["---", "",
                   f"**{n_at} áudio(s) marcados para conferência humana** — "
                   "rode `--revisar` para a lista.", ""]
    saida.write_text("\n".join(linhas), encoding="utf-8", newline="\n")
    print(f"\n[OK] Relatorio com a fita de tempo: {rel(saida)}")
    print(f"     {len(achados)} audio(s); {n_at} pedem conferencia.\n")


def buscar(con, termo: str, alvo: Path | None):
    """Procura uma palavra em TODAS as degravacoes e devolve o MINUTO exato.

    E isto que torna util ter mil audios: ninguem reouve mil audios para achar
    onde a parte falou em "pagamento". Aqui a resposta ja vem citavel —
    arquivo + minuto + o trecho.
    """
    alvo_rel = rel(alvo) + "/" if alvo and alvo.is_dir() else None
    caminhos: dict[str, list[str]] = {}
    for cam, sha in con.execute("SELECT caminho, sha256 FROM arquivos"):
        if alvo_rel and not cam.startswith(alvo_rel):
            continue
        caminhos.setdefault(sha, []).append(cam)

    alvo_n = _normaliza(termo)
    print(f"\n=== BUSCA NAS DEGRAVACOES: \"{termo}\" ===")
    if alvo_rel:
        print(f"    (limitada a {alvo_rel})")
    print()

    achou = 0
    for sha, texto, segs_json in con.execute(
            "SELECT sha256, texto, segmentos FROM degravacoes "
            "WHERE texto IS NOT NULL AND texto != ''"):
        if sha not in caminhos or alvo_n not in _normaliza(texto):
            continue
        try:
            segs = json.loads(segs_json or "[]")
        except json.JSONDecodeError:
            segs = []
        onde = [s for s in segs if alvo_n in _normaliza(s["texto"])]
        nome = Path(caminhos[sha][0]).name
        achou += 1
        if onde:
            for s in onde:
                print(f"  {nome}  aos {mmss(s['ini'])}")
                print(f"      \"{s['texto']}\"")
        else:
            print(f"  {nome}")
            print(f"      \"{texto[:150]}\"")
        for extra in caminhos[sha][1:]:
            print(f"      (o mesmo audio tambem esta em {extra})")
        print(f"      arquivo: {caminhos[sha][0]}")
        print()

    if not achou:
        print("  Nada encontrado. (Lembre: so procura no que ja foi degravado.)\n")
    else:
        print(f"  {achou} audio(s) com \"{termo}\".")
        print(f"  {soj.ROTULO_DEGRAVACAO}\n")


def mostrar_catalogo(con):
    print("\n=== CATALOGO DE AUDIO DO SOJ ===")
    r = con.execute("SELECT COUNT(*), SUM(duracao_s), SUM(tempo_s) "
                    "FROM degravacoes WHERE sinal != 'ERRO'").fetchone()
    n_arq, n_dist = con.execute(
        "SELECT COUNT(*), COUNT(DISTINCT sha256) FROM arquivos").fetchone()
    print(f"  audios distintos degravados ... {r[0] or 0}")
    print(f"  arquivos vistos no acervo ..... {n_arq}"
          + (f"  ({n_arq - n_dist} sao o mesmo audio repetido)"
             if n_arq > n_dist else ""))
    print(f"  audio processado .............. {(r[1] or 0)/60:.1f} min")
    if r[2]:
        print(f"  maquina gastou ................ {(r[2] or 0)/60:.1f} min "
              f"({(r[1] or 0)/r[2]:.1f}x tempo real)")
    print("\n  por sinal:")
    for s, n in con.execute("SELECT sinal, COUNT(*) FROM degravacoes "
                            "GROUP BY sinal ORDER BY COUNT(*) DESC"):
        print(f"    {s:<12} {n}")
    print("\n  por modelo:")
    for m, n in con.execute("SELECT modelo, COUNT(*) FROM degravacoes "
                            "GROUP BY modelo ORDER BY COUNT(*) DESC"):
        print(f"    {str(m):<22} {n}")
    print(f"\n  arquivo: {rel(CATALOGO)}  (fora do git — se reconstroi)\n")


# ----------------------------------------------------------------- principal
def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(
        description="Motor de audio do SOJ — degravacao em escala, 100% local.")
    ap.add_argument("caminho", nargs="?", help="Pasta (varre em profundidade) ou audio")
    ap.add_argument("--modelo", default="large-v3-turbo",
                    help="large-v3-turbo (padrao — decisao do advogado em "
                         "22/07/2026: precisao e o produto) | small (rapido, "
                         "para triagem) | medium")
    ap.add_argument("--processos", type=int, default=1,
                    help="Processos em paralelo (padrao 1: o ctranslate2 ja usa "
                         "todos os nucleos)")
    ap.add_argument("--beam", type=int, default=1,
                    help="1 (padrao, rapido) | 5 (mais lento, as vezes melhor)")
    ap.add_argument("--idioma", default="pt")
    ap.add_argument("--limite", type=int, help="Degrava so os N primeiros (teste)")
    ap.add_argument("--forcar", action="store_true",
                    help="Re-degrava e SOBRESCREVE sidecar (use com cuidado)")
    ap.add_argument("--repescar", action="store_true",
                    help="Segunda tentativa so nos audios marcados pelo "
                         "semaforo, com o --modelo indicado (ex.: large-v3-turbo)")
    ap.add_argument("--status", action="store_true", help="So o mapa, nao degrava")
    ap.add_argument("--revisar", action="store_true",
                    help="Lista o que precisa de conferencia humana")
    ap.add_argument("--relatorio", action="store_true",
                    help="Gera DEGRAVACAO_<pasta>.md com os minutos")
    ap.add_argument("--catalogo", action="store_true", help="Estado geral")
    ap.add_argument("--buscar", metavar="TERMO",
                    help="Procura a palavra nas degravacoes e mostra o MINUTO")
    args = ap.parse_args()

    con = abrir_catalogo()

    if args.catalogo and not args.caminho:
        mostrar_catalogo(con)
        return
    if args.buscar:
        alvo = Path(args.caminho) if args.caminho else None
        if alvo is not None and alvo.exists():
            varrer(con, alvo, quieto=True)
        buscar(con, args.buscar, alvo)
        return
    if not args.caminho:
        ap.error("informe o CAMINHO (pasta ou audio) — ou use --catalogo/--buscar")

    alvo = Path(args.caminho)
    if not alvo.exists():
        sys.exit(f"[ERRO] Nao encontrei: {alvo}")

    achados = varrer(con, alvo, quieto=args.status)
    if not achados:
        sys.exit(f"[ERRO] Nenhum audio em {alvo} "
                 f"(procuro {', '.join(AUDIO_EXT)}).")
    adotados = adotar_sidecars(con, achados)
    if adotados:
        print(f"[OK] {adotados} degravacao(oes) anterior(es) adotada(s) do "
              "sidecar — nao se refaz trabalho ja feito.")

    if args.status:
        mostrar_status(con, achados, args)
        return
    if args.revisar:
        mostrar_revisar(con, achados, args)
        return
    if args.relatorio:
        gerar_relatorio(con, achados, args)
        return

    res = processar(con, achados, args)
    if res["feitos"] or res["erros"]:
        print(f"\n[FIM] {res['feitos']} degravado(s), {res['erros']} erro(s), "
              f"{res.get('atencao', 0)} para conferir.")
        print(f"LEMBRETE: {soj.ROTULO_DEGRAVACAO}")
        if res.get("atencao"):
            print(f"Veja o que conferir:  python motor_audio.py "
                  f"\"{args.caminho}\" --revisar")
    else:
        print("\n[OK] Nada a fazer: todos os audios ja estao degravados no "
              "catalogo. (Regra de ouro: nada se re-degrava.)")
    mostrar_status(con, achados, args)


if __name__ == "__main__":
    main()
