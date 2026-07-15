#!/usr/bin/env python3
"""
git_health.py — verificacao de saude do git no ritual diario (SOJ).

Diretiva do advogado (15/07/2026), motivada pelo incidente do index.lock
que ficou 6 dias travando commits (09-15/07/2026):
  (i)   index.lock com idade > 30 min sem processo git ativo  -> ALERTA
  (ii)  mudancas nao commitadas ha > 24h                      -> ALERTA
  (iii) commits sem push ha > 24h (quando ha remoto)          -> ALERTA

Cada execucao e registrada (append) em _SISTEMA/logs/git_health.md.
Saida: codigo 0 (saudavel) ou 1 (ha alertas) — o briefing/vigia consome.
"""
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
LOG = RAIZ / "_SISTEMA" / "logs" / "git_health.md"
LOCK_LIMITE_SEG = 30 * 60
PENDENCIA_LIMITE_SEG = 24 * 3600


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True,
                       text=True, timeout=60)
    return r.stdout.strip()


def _tem_processo_git() -> bool:
    saida = subprocess.run(["tasklist", "/FI", "IMAGENAME eq git.exe"],
                           capture_output=True, text=True, timeout=30).stdout
    return "git.exe" in saida


def verificar() -> list[str]:
    alertas: list[str] = []

    # (i) index.lock orfao
    lock = RAIZ / ".git" / "index.lock"
    if lock.exists():
        idade = time.time() - lock.stat().st_mtime
        if idade > LOCK_LIMITE_SEG and not _tem_processo_git():
            alertas.append(
                f"index.lock orfao ha {idade/3600:.1f}h sem processo git ativo "
                f"— commits estao TRAVADOS (remover apos confirmar; ver "
                f"_SISTEMA/config/repositorio.md)")

    # (ii) mudancas nao commitadas ha mais de 24h
    status = _git("status", "--porcelain")
    if status:
        mais_antiga = None
        for linha in status.splitlines():
            caminho = linha[3:].split(" -> ")[-1].strip().strip('"')
            p = RAIZ / caminho
            if p.exists():
                m = p.stat().st_mtime
                mais_antiga = m if mais_antiga is None else min(mais_antiga, m)
        if mais_antiga and (time.time() - mais_antiga) > PENDENCIA_LIMITE_SEG:
            horas = (time.time() - mais_antiga) / 3600
            alertas.append(
                f"{len(status.splitlines())} arquivo(s) modificados sem commit; "
                f"o mais antigo ha {horas:.0f}h (regra da casa: sessao termina "
                f"com commit+push)")

    # (iii) commits sem push ha mais de 24h
    if _git("remote"):
        upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name",
                        "@{u}")
        if upstream:
            pendentes = _git("rev-list", f"{upstream}..HEAD", "--format=%ct",
                             "--no-commit-header")
            if pendentes:
                mais_antigo = min(int(t) for t in pendentes.splitlines() if t)
                if (time.time() - mais_antigo) > PENDENCIA_LIMITE_SEG:
                    n = len(pendentes.splitlines())
                    alertas.append(
                        f"{n} commit(s) sem push ha mais de 24h — o remoto "
                        f"privado e a rede de seguranca real")
    return alertas


def main() -> None:
    alertas = verificar()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    if not LOG.exists():
        LOG.write_text("# Log do git health check (diretiva de 15/07/2026)\n\n",
                       encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        if alertas:
            f.write(f"- {agora} — **ALERTA**: " + " · ".join(alertas) + "\n")
        else:
            f.write(f"- {agora} — ok\n")

    if alertas:
        print("[GIT-HEALTH] ALERTAS:")
        for a in alertas:
            print(f"  [!] {a}")
        sys.exit(1)
    print("[GIT-HEALTH] ok — sem pendencias de lock, commit ou push.")


if __name__ == "__main__":
    main()
