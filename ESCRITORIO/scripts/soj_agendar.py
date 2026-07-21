# -*- coding: utf-8 -*-
"""
soj_agendar.py — o DAEMON do SOJ (Tarefa Agendada do Windows).

Registra uma tarefa que roda `soj_atualizar.py` toda manhã: você acorda com o
painel, os prazos e as pendências já frescos do dia. Roda quando você está
logado; **NÃO baixa autos** (o download exige o seu login no PJe) — só regenera
as vistas.

  python soj_agendar.py --instalar [--hora 07:00]
  python soj_agendar.py --status
  python soj_agendar.py --remover

Sem senha e sem privilégio de administrador: a tarefa roda no seu usuário.
"""
import argparse
import subprocess
import sys

import soj_lib as soj

NOME = "SOJ - Atualizar painel do dia"
ALVO = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_atualizar.py"
WRAPPER = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_atualizar_agendado.cmd"


def _run(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _gerar_wrapper() -> None:
    """Gera o .cmd que a tarefa roda.

    Por que não é só `python soj_atualizar.py`: o Agendador roda num contexto de
    perfil onde o `AppData\\Roaming` (user site-packages) NÃO é o mesmo da sessão
    interativa — o mesmo caminho resolve para pastas diferentes, e o import de
    pyyaml/ruamel falha. Por isso as libs ficam em `_SISTEMA/pylibs` (dentro do
    repositório, que a tarefa lê igual aos scripts). O wrapper injeta ESSA pasta
    + a dos scripts no sys.path, força UTF-8 e registra a saída num log."""
    py = sys.executable
    linha_py = (
        "import sys,os; h=r\'%~dp0.\'; sys.path.insert(0, h); "
        "sys.path.insert(0, os.path.abspath(os.path.join(h,'..','..','_SISTEMA','pylibs'))); "
        "import soj_atualizar; soj_atualizar.main()"
    )
    conteudo = (
        "@echo off\r\n"
        "chcp 65001 >nul\r\n"
        'set "PYTHONUTF8=1"\r\n'
        f'"{py}" -c "{linha_py}" >> "%TEMP%\\soj_agendador.log" 2>&1\r\n'
    )
    WRAPPER.write_text(conteudo, encoding="utf-8")


def _corrigir_energia() -> None:
    """schtasks cria a tarefa com 'só iniciar na tomada' — num notebook na
    bateria ela nunca roda. Limpa essa condição (PowerShell)."""
    ps = (f'$t=Get-ScheduledTask -TaskName "{NOME}";'
          f'$t.Settings.DisallowStartIfOnBatteries=$false;'
          f'$t.Settings.StopIfGoingOnBatteries=$false;'
          f'Set-ScheduledTask -TaskName "{NOME}" -Settings $t.Settings | Out-Null')
    r = _run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps])
    if r.returncode == 0:
        print("[agendar] condição de bateria removida (roda na tomada ou na bateria).")
    else:
        print("[agendar] aviso: não consegui ajustar a condição de bateria — se a "
              "tarefa não rodar no notebook, desmarque 'só na tomada' no Agendador.")


def instalar(hora: str) -> int:
    _gerar_wrapper()
    r = _run(["schtasks", "/Create", "/TN", NOME, "/TR", str(WRAPPER),
              "/SC", "DAILY", "/ST", hora, "/F"])
    print((r.stdout or r.stderr).strip())
    if r.returncode == 0:
        _corrigir_energia()
        print(f"[agendar] ✅ tarefa criada — roda TODO DIA às {hora} (quando você"
              f" estiver logado).\n"
              f"          Ver:     python soj_agendar.py --status\n"
              f"          Remover: python soj_agendar.py --remover")
    else:
        print("[agendar] falhou ao criar a tarefa (veja a mensagem acima).")
    return r.returncode


def remover() -> None:
    r = _run(["schtasks", "/Delete", "/TN", NOME, "/F"])
    print((r.stdout or r.stderr).strip())


def status() -> None:
    r = _run(["schtasks", "/Query", "/TN", NOME, "/V", "/FO", "LIST"])
    saida = (r.stdout or "").strip()
    if r.returncode != 0 or not saida:
        print(f"[agendar] tarefa '{NOME}' NÃO está instalada.")
        return
    for linha in saida.splitlines():
        if any(linha.strip().startswith(k) for k in
               ("TaskName", "Next Run", "Status", "Schedule", "Start Time",
                "Próxima", "Estado", "Hora de")):
            print("  " + linha.strip())


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Agendador do SOJ (Windows).")
    ap.add_argument("--instalar", action="store_true", help="cria a tarefa diária")
    ap.add_argument("--remover", action="store_true", help="remove a tarefa")
    ap.add_argument("--status", action="store_true", help="mostra a tarefa")
    ap.add_argument("--hora", default="07:00", help="HH:MM (padrão 07:00)")
    a = ap.parse_args()
    if a.remover:
        remover()
    elif a.status:
        status()
    elif a.instalar:
        sys.exit(instalar(a.hora))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
