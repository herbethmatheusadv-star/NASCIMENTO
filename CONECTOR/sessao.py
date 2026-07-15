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
        from playwright.sync_api import sync_playwright
        try:
            with sync_playwright() as p:
                if not Path(p.chromium.executable_path).exists():
                    faltas.append("Chromium do Playwright ausente: "
                                  "python -m playwright install chromium")
        except Exception as e:  # noqa: BLE001
            faltas.append(f"Playwright presente mas nao inicializa: {e}")
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
        # launch() puro = perfil efemero por padrao. Nao passamos flag de
        # perfil: ela seria justamente o que o titular vetou, e e desnecessaria.
        self._navegador = self._pw.chromium.launch(headless=self.headless)
        # contexto novo = isolado, nada herdado, nada exportado ao fechar
        self.contexto = self._navegador.new_context(
            accept_downloads=True,
            downloads_path=self._tmp,
        )
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
    def esperar_login_humano(self, timeout_min: int = 10) -> bool:
        """
        Abre a tela de login e ESPERA o titular. Nao digita nada.

        Volta True quando a pagina mostrar sinal de sessao ativa.
        """
        self.ir_para(URL_LOGIN_TJPA)
        print()
        print("=" * 70)
        print("  O ROBO PAROU NO PORTAO — E A SUA VEZ")
        print("=" * 70)
        print("  1. A janela do Chromium esta aberta no login do PJe/TJPA.")
        print("  2. Faca login com o SEU certificado (PJeOffice ativo).")
        print("  3. O PIN e digitado por VOCE, na janela. O robo nao le esse")
        print("     campo, nao preenche e nao guarda nada.")
        print("  4. Assim que o painel abrir, o robo segue sozinho — so lendo.")
        print()
        print(f"  Aguardando ate {timeout_min} min. Ctrl+C cancela tudo.")
        print("=" * 70)
        try:
            self.pagina.wait_for_function(
                "() => %s.some(m => document.body.innerText.includes(m))"
                % list(MARCAS_LOGADO),
                timeout=timeout_min * 60_000,
            )
        except Exception:  # noqa: BLE001
            print("\n[sessao] nao identifiquei o painel. Sessao encerrada sem "
                  "ler nada — perfil apagado.")
            return False
        print("\n[sessao] painel detectado. Sessao ativa (so leitura).")
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

    chamadas: list[dict] = []

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

    s.pagina.on("response", anotar_resposta)

    print()
    print("=" * 70)
    print("  MODO MAPEAMENTO — VOCE DIRIGE, EU ANOTO")
    print("=" * 70)
    print("  O robo NAO vai clicar em nada. Ele so escuta o que a pagina pede")
    print("  ao servidor enquanto VOCE navega.")
    print()
    print("  Por favor, navegue com calma ate:")
    print("    1. EXPEDIENTES  (a lista — NAO abra nenhum expediente!)")
    print("    2. ACERVO       (a lista de processos)")
    print()
    print("  Se um expediente estiver 'pendente de ciencia', NAO clique nele.")
    print("  A lista basta — e dela que o censo precisa.")
    print()
    print("  Quando terminar, volte aqui e aperte ENTER.")
    print("=" * 70)
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print("\n[mapeamento] interrompido.")

    # HTML da ultima pagina que ele deixou aberta (para eu ver a estrutura)
    try:
        html = s.pagina.content()
        (destino / f"pagina_final_{carimbo}.html").write_text(html,
                                                              encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        print(f"[mapeamento] nao consegui salvar o HTML: {e}")

    relatorio = destino / f"chamadas_{carimbo}.md"
    with relatorio.open("w", encoding="utf-8") as f:
        f.write(f"# Mapeamento do painel PJe/TJPA — {carimbo}\n\n")
        f.write(f"{len(chamadas)} chamada(s) observada(s). "
                f"O robo nao clicou em nada.\n\n")
        f.write("| hora | metodo | status | tipo | content-type | url |\n")
        f.write("|---|---|---|---|---|---|\n")
        for c in chamadas:
            f.write(f"| {c['quando']} | {c['metodo']} | {c['status']} | "
                    f"{c['tipo']} | {c['content_type']} | `{c['url'][:150]}` |\n")
    print(f"\n[mapeamento] {len(chamadas)} chamadas salvas em {relatorio}")
    return relatorio


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
