#!/usr/bin/env python3
"""
sessao.py — o navegador do robo. EFEMERO, com humano no portao.

Desenho aprovado pelo titular em 15/07/2026 ("certificado com humano no
portao" — ver _SISTEMA/emendas.md, Emenda 02):

  * perfil DESCARTAVEL: o Chromium sobe SEM nenhuma flag de perfil e sem
    exportar estado. E o comportamento padrao do Playwright — perfil temporario
    do proprio SO, apagado quando o navegador fecha. Nenhum cookie sobrevive ao
    processo. (A flag que apontaria um perfil fixo, e a chamada que exportaria
    o estado da sessao, estao no vocabulario proibido de regras.py: se alguem
    as escrever aqui, o teste quebra o build. Foi o que aconteceu na 1a versao
    deste arquivo, em 15/07/2026 — eu mesmo as tinha posto por reflexo.)
  * o robo abre a tela de login e PARA. Quem digita o PIN/senha do certificado
    e o titular, na janela, com as proprias maos. O robo nao le o campo, nao
    preenche, nao guarda.
  * a sessao morre com o processo. Amanha, PIN de novo — 30 segundos dele.

O que este modulo NAO faz, por ausencia (R7): nao clica em nada que aja, nao
navega para tela de ato, nao chama operacao de escrita. Toda navegacao passa
por regras.guarda_de_url; todo clique, por regras.guarda_de_clique.

Uso:
    python CONECTOR/sessao.py --checar        # so verifica o ambiente
    python CONECTOR/sessao.py --login         # abre e espera o titular logar
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import regras

RAIZ = Path(__file__).resolve().parents[1]

URL_LOGIN_TJPA = "https://pje.tjpa.jus.br/pje/login.seam"

# Marcadores de que a sessao esta ativa (o titular passou do portao).
# Sao trechos que so aparecem DEPOIS do login, em tela de leitura.
MARCAS_LOGADO = ("Painel", "Acervo", "Expedientes", "Quadro de Avisos",
                 "Consulta Processual", "Sair")


def ambiente_ok() -> tuple[bool, list[str]]:
    """Diz se da para rodar, sem esconder o que falta."""
    faltas: list[str] = []
    try:
        import playwright  # noqa: F401
    except ImportError:
        faltas.append(
            "playwright nao instalado. Instale com:\n"
            "        pip install playwright\n"
            "        python -m playwright install chromium")
    else:
        # Nao checamos o Chromium empacotado de proposito: ele existe nesta
        # maquina mas NAO SOBE (falta o Visual C++ Redistributable). Quem vale
        # e o Chrome do sistema, via channel="chrome".
        chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        chrome_x86 = Path(
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe")
        if not (chrome.exists() or chrome_x86.exists()):
            faltas.append("Chrome do sistema nao encontrado — o conector usa "
                          "channel='chrome' (o Chromium do Playwright nao sobe "
                          "nesta maquina).")
    # PJeOffice precisa estar rodando para o certificado A1 funcionar
    import socket
    with socket.socket() as s:
        s.settimeout(1.5)
        if s.connect_ex(("127.0.0.1", 8800)) != 0:
            faltas.append("PJeOffice nao esta escutando na porta 8800. "
                          "Abra o PJeOffice Pro antes de logar.")
    return (not faltas), faltas


class SessaoEfemera:
    """
    Context manager do navegador. Perfil temporario, apagado na saida.

    Nao ha `try/finally` opcional aqui: a limpeza acontece mesmo se estourar
    excecao, porque perfil que sobrevive a um crash e exatamente o cookie
    persistente que o titular vetou.
    """

    def __init__(self, headless: bool = False):
        self.headless = headless
        self._tmp: str | None = None
        self._pw = None
        self.contexto = None
        self.pagina = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        # Pasta so para downloads (autos). O PERFIL nao mora aqui: o navegador
        # sobe sem flag de perfil nenhuma, e o Playwright o cria e destroi
        # sozinho num temporario proprio.
        self._tmp = tempfile.mkdtemp(prefix="soj_pje_efemero_")
        self._pw = sync_playwright().start()
        # channel="chrome" = usa o Chrome JA INSTALADO na maquina, nao o
        # Chromium empacotado pelo Playwright — que nesta maquina nao sobe
        # ("configuracao lado a lado incorreta": falta o Visual C++
        # Redistributable). Diagnosticado em 15/07/2026; o Chrome do sistema
        # (v150) abre normal.
        #
        # IMPORTANTE: usar o Chrome do sistema NAO significa usar o PERFIL dele.
        # launch() sobe um perfil temporario proprio, vazio, que o Playwright
        # apaga ao fechar. As abas, cookies, senhas e sessoes pessoais do
        # titular NAO sao tocados nem herdados — a janela nasce em branco.
        self._navegador = self._pw.chromium.launch(
            headless=self.headless,
            channel="chrome",
            downloads_path=self._tmp,   # autos baixados vao para o temporario
        )
        # contexto novo = isolado, nada herdado, nada exportado ao fechar
        self.contexto = self._navegador.new_context(accept_downloads=True)
        self.pagina = self.contexto.new_page()
        return self

    def __exit__(self, *exc):
        try:
            if self.contexto:
                self.contexto.close()
            if getattr(self, "_navegador", None):
                self._navegador.close()
            if self._pw:
                self._pw.stop()
        finally:
            if self._tmp:
                shutil.rmtree(self._tmp, ignore_errors=True)
                print(f"[sessao] perfil efemero apagado: {self._tmp}")
        return False

    # -- navegacao guardada ------------------------------------------------
    def ir_para(self, url: str):
        regras.guarda_de_url(url)
        self.pagina.goto(url, wait_until="domcontentloaded")
        return self.pagina

    def clicar(self, seletor: str):
        alvo = self.pagina.locator(seletor)
        regras.guarda_de_clique(alvo.first.inner_text(timeout=5000) or seletor)
        alvo.first.click()

    # -- o portao ----------------------------------------------------------
    def esperar_login_humano(self, timeout_min: int = 12) -> bool:
        """
        Abre a tela de login e ESPERA o titular. Nao digita nada.

        SAO DOIS PASSOS (informado pelo titular em 15/07/2026):
          1. certificado A1 via PJeOffice (dialogo Java, fora do navegador)
          2. autenticador / 2FA

        Por isso a espera e generosa e a deteccao e ESTRITA: exigir apenas as
        palavras do painel no texto era falso positivo esperando para acontecer
        — o menu da propria tela de login pode conter "Painel"/"Sair", e o robo
        declararia sessao ativa no meio do 2FA. Agora sao tres condicoes
        simultaneas: saiu da URL de login + tem marca de painel + nao ha mais
        campo de senha na tela.

        O 2FA e o controle que protege o titular: o robo espera, nunca ajuda a
        contorna-lo, e a sessao morre com o processo — amanha, os dois passos
        de novo.
        """
        self.ir_para(URL_LOGIN_TJPA)
        print()
        print("=" * 70)
        print("  O ROBO PAROU NO PORTAO — E A SUA VEZ (2 PASSOS)")
        print("=" * 70)
        print("  A janela do Chrome esta aberta no login do PJe/TJPA.")
        print()
        print("    PASSO 1 — certificado A1 (PJeOffice pede o PIN numa janela")
        print("              Java, FORA do navegador: o robo nao alcanca).")
        print("    PASSO 2 — autenticador / 2FA.")
        print()
        print("  Os dois sao seus. O robo nao digita, nao le e nao guarda nada")
        print("  — e nao existe codigo aqui para contornar o 2FA.")
        print()
        print(f"  Aguardando ate {timeout_min} min. Sem pressa. Ctrl+C cancela.")
        print("=" * 70)
        js = """
        () => {
          const fora_do_login = !location.href.toLowerCase().includes('login');
          const txt = document.body ? document.body.innerText : '';
          const tem_painel = %s.some(m => txt.includes(m));
          const sem_campo_senha =
            document.querySelectorAll('input[type=password]').length === 0;
          return fora_do_login && tem_painel && sem_campo_senha;
        }
        """ % list(MARCAS_LOGADO)
        try:
            self.pagina.wait_for_function(js, timeout=timeout_min * 60_000)
        except Exception:  # noqa: BLE001
            print("\n[sessao] nao identifiquei o painel (talvez o 2FA nao tenha "
                  "concluido). Sessao encerrada sem ler nada — perfil apagado.")
            return False
        print(f"\n[sessao] painel detectado em {self.pagina.url[:70]}")
        print("[sessao] sessao ativa — modo SOMENTE LEITURA.")
        return True


def mapear_enquanto_voce_navega(s: SessaoEfemera) -> Path:
    """
    Spike, item 2 — na forma mais segura que existe: O ROBO NAO CLICA EM NADA.

    O titular navega (Expedientes, Acervo); o robo so escuta o trafego e salva
    o que a pagina pediu ao servidor. Zero risco de ciencia acidental: nao ha
    clique automatico para dar errado.

    Salva em _efemeros/mapeamento_pje/ (fora do git — tem dado de cliente).
    """
    destino = RAIZ / "_efemeros" / "mapeamento_pje"
    destino.mkdir(parents=True, exist_ok=True)
    carimbo = datetime.now().strftime("%Y-%m-%d_%H%M")

    import re
    import time

    chamadas: list[dict] = []
    telas: list[dict] = []
    paginas = [s.pagina]     # inclui novas abas: os autos abrem em nova janela

    def anotar_resposta(resp):
        try:
            req = resp.request
            if req.resource_type not in ("xhr", "fetch", "document"):
                return
            chamadas.append({
                "quando": datetime.now().strftime("%H:%M:%S"),
                "metodo": req.method,
                "url": resp.url,
                "status": resp.status,
                "tipo": req.resource_type,
                "content_type": (resp.header_value("content-type") or "")[:60],
            })
        except Exception:  # noqa: BLE001
            pass

    def _slug(url: str) -> str:
        m = re.search(r"/([A-Za-z]+)\.seam", url)
        return (m.group(1) if m else "tela")[:28]

    # Leitura pura do DOM: nomes/ids/rotulos dos elementos clicaveis, para eu
    # descobrir os seletores das abas e do download integral (acao 14 do §7.1).
    # NAO interage — so lê. Por isso a query cobre a,button,input e [role=tab].
    JS_ELEMENTOS = """
    () => {
      const out = [];
      const sel = 'a,button,input,[role=tab],[role=button]';
      for (const el of document.querySelectorAll(sel)) {
        const t = (el.innerText || el.value || el.title ||
                   el.getAttribute('aria-label') || '').trim().slice(0, 60);
        const id = el.id || '';
        if (!t && !id) continue;
        out.push({tag: el.tagName, id: id, name: el.name || '',
                  role: el.getAttribute('role') || '',
                  href: (el.getAttribute('href') || '').slice(0, 90), txt: t});
        if (out.length >= 140) break;
      }
      return out;
    }"""

    def capturar(pagina, motivo: str):
        """Salva um retrato da tela quando ela muda. Observacao, nunca acao."""
        try:
            if pagina.is_closed():
                return
            url = pagina.url
            html = pagina.content()
        except Exception:  # noqa: BLE001
            return
        assinatura = (_slug(url), round(len(html), -3))  # dedupe grosso
        if any(t["assinatura"] == assinatura for t in telas):
            return
        n = len(telas) + 1
        arquivo = f"tela_{n:02d}_{_slug(url)}.html"
        try:
            (destino / arquivo).write_text(html, encoding="utf-8")
        except Exception:  # noqa: BLE001
            return
        try:
            elems = pagina.evaluate(JS_ELEMENTOS)
        except Exception:  # noqa: BLE001
            elems = []
        telas.append({"assinatura": assinatura, "n": n, "url": url,
                      "arquivo": arquivo, "motivo": motivo, "elems": elems})
        print(f"[mapeamento] tela {n}: {_slug(url)}  "
              f"({len(elems)} elementos clicaveis catalogados)")

    def nova_aba(pag):
        # os autos digitais abrem em nova janela — capturo tambem, so leitura
        paginas.append(pag)
        pag.on("response", anotar_resposta)
        print("[mapeamento] nova aba detectada (os autos?) — vou retratar tambem")

    s.pagina.on("response", anotar_resposta)
    s.contexto.on("page", nova_aba)

    print()
    print("=" * 70)
    print("  MODO MAPEAMENTO — VOCE DIRIGE, EU ANOTO")
    print("=" * 70)
    print("  O robo NAO clica em nada. Ele so retrata cada tela que VOCE abre.")
    print()
    print("  Roteiro (com calma, na ordem que preferir):")
    print("    1. ACERVO       — a lista dos seus processos")
    print("    2. EXPEDIENTES  — a lista (NAO abra expediente pendente!)")
    print("    3. Pela ACERVO, clique no NUMERO de um processo qualquer para")
    print("       abrir os AUTOS digitais (isso e leitura, e seguro).")
    print()
    print("  A regra de ouro: NAO abra expediente marcado 'pendente de ciencia'.")
    print("  Abrir os autos pela ACERVO e leitura — pode. Expediente pendente,")
    print("  nao — porque o proprio ato de abrir pode disparar o prazo.")
    print()
    print("  Eu percebo sozinho quando voce passar pelas telas e encerro.")
    print("  Terminou antes? Feche a janela do Chrome que eu paro.")
    print("=" * 70)

    limite = time.time() + 10 * 60
    viu = {"acervo": False, "expediente": False, "autos": False}
    while time.time() < limite:
        for pag in list(paginas):
            capturar(pag, "navegacao")
        for c in chamadas:
            u = c["url"].lower()
            if "acervo" in u or "consultaprocesso" in u:
                viu["acervo"] = True
            if "expediente" in u or "aviso" in u or "painel" in u:
                viu["expediente"] = True
            if "consultadocumento" in u or "autosdigitais" in u \
                    or "detalheprocesso" in u:
                viu["autos"] = True
        vivas = [p for p in paginas if not _fechada(p)]
        if not vivas:
            print("\n[mapeamento] voce fechou a janela. Encerrando.")
            break
        if all(viu.values()):
            print("\n[mapeamento] retratei as tres telas (acervo, expedientes, "
                  "autos). Encerro em 20s — pode seguir navegando se quiser.")
            time.sleep(20)
            for pag in list(paginas):
                capturar(pag, "final")
            break
        time.sleep(3)
    else:
        print("\n[mapeamento] tempo limite. Salvo o que retratei ate aqui.")

    relatorio = destino / f"mapa_{carimbo}.md"
    with relatorio.open("w", encoding="utf-8") as f:
        f.write(f"# Mapeamento do painel PJe/TJPA — {carimbo}\n\n")
        f.write(f"{len(telas)} tela(s) retratada(s), {len(chamadas)} chamada(s) "
                f"de rede. O robo nao clicou em nada — so leu.\n\n")
        for t in telas:
            f.write(f"\n## Tela {t['n']} · `{_slug(t['url'])}` "
                    f"· [{t['motivo']}]\n\n")
            f.write(f"- HTML: `{t['arquivo']}`\n- URL: `{t['url'][:150]}`\n")
            f.write(f"- {len(t['elems'])} elementos clicaveis:\n\n")
            f.write("| tag | id | name | role | texto | href |\n")
            f.write("|---|---|---|---|---|---|\n")
            for e in t["elems"]:
                f.write(f"| {e['tag']} | `{e['id']}` | {e['name']} | {e['role']}"
                        f" | {e['txt']} | {e['href']} |\n")
        f.write("\n\n## Chamadas de rede (endpoints do painel)\n\n")
        f.write("| hora | metodo | status | tipo | content-type | url |\n")
        f.write("|---|---|---|---|---|---|\n")
        for c in chamadas:
            f.write(f"| {c['quando']} | {c['metodo']} | {c['status']} | "
                    f"{c['tipo']} | {c['content_type']} | `{c['url'][:150]}` |\n")
    print(f"\n[mapeamento] {len(telas)} telas + {len(chamadas)} chamadas "
          f"salvas em {relatorio}")
    return relatorio


def _fechada(pag) -> bool:
    try:
        return pag.is_closed()
    except Exception:  # noqa: BLE001
        return True


def main() -> None:
    ap = argparse.ArgumentParser(description="Sessao efemera do Conector PJe")
    ap.add_argument("--checar", action="store_true",
                    help="so verifica o ambiente e sai")
    ap.add_argument("--login", action="store_true",
                    help="abre o navegador e espera o login do titular")
    ap.add_argument("--mapear", action="store_true",
                    help="apos o login, anota o trafego enquanto VOCE navega")
    args = ap.parse_args()

    ok, faltas = ambiente_ok()
    print("[ambiente]", "pronto" if ok else "INCOMPLETO")
    for f in faltas:
        print("  -", f)
    if args.checar or not ok:
        sys.exit(0 if ok else 1)

    if args.login or args.mapear:
        with SessaoEfemera() as s:
            if not s.esperar_login_humano():
                return
            if args.mapear:
                mapear_enquanto_voce_navega(s)
            else:
                print("[sessao] portao validado. Nada foi lido (era so o "
                      "teste do login). Encerrando e apagando o perfil.")


if __name__ == "__main__":
    main()
