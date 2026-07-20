# -*- coding: utf-8 -*-
"""
soj_servidor.py — O PAINEL DO DIA, AO VIVO (servidor local, so na sua maquina).

Serve o painel em http://127.0.0.1:PORTA e deixa os botoes RODAREM os scripts de
leitura direto — sem copiar comando, sem terminal, sem se preocupar com a pasta.
Regenera o painel a cada carga (sempre fresco). Fecha com Ctrl+C ou fechando a
janela.

R7 — a REGRA DE FERRO vale aqui tambem, e com mais rigor, porque um servidor e
uma porta nova. As tres travas:
  * escuta SO em 127.0.0.1 — sua maquina; ninguem na rede alcanca;
  * so roda uma ALLOWLIST de acoes de LEITURA (buscar, resumo, linha do tempo,
    reindexar) — nada que assine, protocole, tome ciencia ou toque no PJe;
  * /ver serve arquivos SO de dentro de AUTOS/ e PROCESSOS/ (rejeita '..').
O download dos autos (unico ponto que fala com o PJe, e ja guardado pela R7 no
CONECTOR) fica de fora de proposito: exige o seu login no navegador, entao mora
na rotina do terminal, nao num botao.

Uso:
  python soj_servidor.py                 # sobe o servidor e abre o navegador
  python soj_servidor.py --porta 8787
  python soj_servidor.py --sem-abrir
"""
import argparse
import html as H
import json
import os
import re
import subprocess
import sys
import threading
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

import soj_lib as soj
import soj_painel as pn

SCRIPTS = soj.ROOT / "ESCRITORIO" / "scripts"
LIMITE_SAIDA = 20000     # corta a saida mostrada na gaveta (nao trava o navegador)


# --------------------------------------------------------------- ALLOWLIST (R7)
# So LEITURA/PREPARO. A chave e o nome que vem do botao; a funcao monta os
# argumentos (o primeiro item e o script). Qualquer acao fora deste dicionario e
# recusada. Aqui nao entra nada que escreva no processo — e proposital.
def _cmd_buscar(cnj, termo):
    return ["soj_search.py", termo] + (["--processo", cnj] if cnj else [])


def _cmd_resumo(cnj, termo):
    return ["soj_resumo.py", "--cnj", cnj]


def _cmd_inteligencia(cnj, termo):
    return ["soj_inteligencia.py"] + (["--cnj", cnj] if cnj else [])


def _cmd_reindexar(cnj, termo):
    return ["soj_reindex.py"]


ACOES = {
    "buscar":       ("Busca nos autos",   _cmd_buscar,       True),
    "resumo":       ("Preparo do dossie", _cmd_resumo,       False),
    "inteligencia": ("Linha do tempo",    _cmd_inteligencia, False),
    "reindexar":    ("Reindexacao FTS5",  _cmd_reindexar,    False),
}

# scripts que a allowlist tem direito de chamar (defesa em profundidade: mesmo
# que uma funcao acima fosse adulterada, so estes nomes rodam).
SCRIPTS_PERMITIDOS = {"soj_search.py", "soj_resumo.py", "soj_inteligencia.py",
                      "soj_reindex.py"}


# ----------------------------------------------------------- markdown -> html
def _md_para_html(md: str, titulo: str) -> str:
    """Renderizador minimo (titulos, negrito, listas, citacao, regua, codigo).
    Reaproveita o CSS do painel para manter o tema claro/escuro."""
    def inline(s: str) -> str:
        s = H.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
        return s

    out, in_ul = [], False

    def fecha_ul():
        nonlocal in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False

    for ln in md.splitlines():
        s = ln.rstrip()
        if not s.strip():
            fecha_ul()
            continue
        if re.match(r"^---+\s*$", s):
            fecha_ul(); out.append("<hr>"); continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            fecha_ul(); n = len(m.group(1))
            out.append(f"<h{n}>{inline(m.group(2))}</h{n}>"); continue
        corte = s.lstrip()
        if corte.startswith(("- ", "* ")):
            if not in_ul:
                out.append("<ul>"); in_ul = True
            out.append(f"<li>{inline(corte[2:])}</li>"); continue
        if corte.startswith("> "):
            fecha_ul(); out.append(f"<blockquote>{inline(corte[2:])}</blockquote>"); continue
        fecha_ul(); out.append(f"<p>{inline(s)}</p>")
    fecha_ul()
    corpo = "\n".join(out)
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H.escape(titulo)}</title><style>{pn.CSS}
body{{padding:0}}.doc{{max-width:820px;margin:0 auto;padding:26px 22px 60px}}
.doc h1{{font-size:22px}}.doc h2{{font-size:17px;margin-top:22px}}.doc h3{{font-size:15px}}
.doc blockquote{{border-left:3px solid var(--gold);margin:12px 0;padding:6px 14px;color:var(--tx2);background:var(--card);border-radius:0 8px 8px 0}}
.doc code{{background:var(--card);border:1px solid var(--ln);border-radius:5px;padding:1px 5px;font-size:.92em}}
.doc hr{{border:none;border-top:1px solid var(--ln);margin:18px 0}}
.doc a.volta{{display:inline-block;margin-bottom:14px;font-size:12px;color:var(--acc);text-decoration:none}}</style>
</head><body><div class="doc"><a class="volta" href="/">← voltar ao painel</a>
{corpo}</div></body></html>"""


# --------------------------------------------------------------------- servidor
class Painel(BaseHTTPRequestHandler):
    server_version = "SOJ/1.0"

    def log_message(self, *a):     # silencio no console (nao poluir a janela)
        pass

    # -- respostas ---------------------------------------------------------
    def _ok(self, corpo, ctype):
        if isinstance(corpo, str):
            corpo = corpo.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def _json(self, obj):
        self._ok(json.dumps(obj, ensure_ascii=False), "application/json; charset=utf-8")

    def _erro(self, code, msg):
        corpo = msg.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    # -- rotas -------------------------------------------------------------
    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ("/", "/index.html"):
            pn.HOJE = date.today()          # servidor de pe por dias: data fresca
            self._ok(pn.render(pn.carregar(), servidor=True), "text/html; charset=utf-8")
        elif u.path == "/ver":
            self._servir_arquivo((parse_qs(u.query).get("p") or [""])[0])
        elif u.path == "/saude":
            self._json({"ok": True, "root": str(soj.ROOT)})
        else:
            self._erro(404, "nao encontrado")

    def do_POST(self):
        if urlparse(self.path).path != "/acao":
            return self._erro(404, "nao encontrado")
        n = int(self.headers.get("Content-Length") or 0)
        if n > 10000:
            return self._erro(413, "pedido grande demais")
        try:
            req = json.loads(self.rfile.read(n) or b"{}")
        except Exception:  # noqa: BLE001
            return self._erro(400, "json invalido")
        self._rodar_acao(req)

    # -- /ver: arquivo renderizado, so de dentro de AUTOS/ e PROCESSOS/ ----
    def _servir_arquivo(self, rel):
        partes = [x for x in unquote(rel or "").replace("\\", "/").split("/")
                  if x not in ("", ".")]
        if any(x == ".." for x in partes) or not partes:
            return self._erro(400, "caminho invalido")
        alvo = soj.ROOT.joinpath(*partes).resolve()
        raizes = [(soj.ROOT / d).resolve() for d in ("AUTOS", "PROCESSOS")]
        dentro = any(str(alvo).startswith(str(r) + os.sep) for r in raizes)
        if not dentro or not alvo.is_file():
            return self._erro(404, "arquivo nao encontrado")
        if alvo.suffix.lower() in (".md", ".txt"):
            self._ok(_md_para_html(alvo.read_text(encoding="utf-8", errors="ignore"),
                                   alvo.name), "text/html; charset=utf-8")
        else:
            self._ok(alvo.read_bytes(), "application/octet-stream")

    # -- /acao: roda um script da allowlist e devolve a saida -------------
    def _rodar_acao(self, req):
        acao = str(req.get("acao", "")).strip()
        cnj = str(req.get("cnj", "")).strip()
        termo = str(req.get("termo", "")).strip()
        if acao not in ACOES:
            return self._json({"ok": False, "titulo": "Acao nao permitida",
                               "saida": f"'{acao}' nao esta na lista de acoes de "
                                        f"leitura. O painel so le e prepara (R7)."})
        titulo, monta, exige_termo = ACOES[acao]
        if cnj and not re.fullmatch(r"[0-9.\-]{5,30}", cnj):
            return self._json({"ok": False, "titulo": "CNJ invalido", "saida": cnj})
        if exige_termo and not termo:
            return self._json({"ok": False, "titulo": titulo, "saida": "faltou o termo."})
        partes = monta(cnj, termo)
        if partes[0] not in SCRIPTS_PERMITIDOS:      # defesa em profundidade
            return self._json({"ok": False, "titulo": "Bloqueado",
                               "saida": f"script fora da allowlist: {partes[0]}"})
        cmd = [sys.executable, str(SCRIPTS / partes[0]), *partes[1:]]
        try:
            p = subprocess.run(cmd, cwd=str(soj.ROOT), capture_output=True,
                               text=True, encoding="utf-8", errors="replace",
                               timeout=180)
            saida = (p.stdout or "")
            if p.stderr and p.stderr.strip():
                saida += "\n[mensagens]\n" + p.stderr
            self._json({"ok": p.returncode == 0, "titulo": titulo,
                        "saida": saida[:LIMITE_SAIDA] or "(sem saida)"})
        except subprocess.TimeoutExpired:
            self._json({"ok": False, "titulo": titulo,
                        "saida": "demorou demais (limite de 180s)."})
        except Exception as e:  # noqa: BLE001
            self._json({"ok": False, "titulo": titulo, "saida": f"erro: {e}"})


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Painel do dia AO VIVO (servidor local).")
    ap.add_argument("--porta", type=int, default=8777, help="porta (8777)")
    ap.add_argument("--sem-abrir", action="store_true", help="nao abre o navegador")
    args = ap.parse_args()

    if not pn.PROCESSOS.exists():
        sys.exit("[painel] PROCESSOS/ nao existe — rode dentro do repositorio do SOJ.")

    try:
        srv = ThreadingHTTPServer(("127.0.0.1", args.porta), Painel)
    except OSError as e:
        sys.exit(f"[painel] nao consegui abrir a porta {args.porta} ({e}).\n"
                 f"         Talvez o painel ja esteja no ar. Tente --porta 8787.")
    url = f"http://127.0.0.1:{args.porta}/"
    print("=" * 62)
    print("  SOJ · Painel do dia — AO VIVO")
    print(f"  {url}")
    print("  R7: so leitura, so nesta maquina. Ctrl+C para parar.")
    print("=" * 62)
    if not args.sem_abrir:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n[painel] encerrado.")
    finally:
        srv.server_close()


if __name__ == "__main__":
    main()
