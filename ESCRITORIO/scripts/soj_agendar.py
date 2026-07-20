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


def _run(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def instalar(hora: str) -> int:
    tr = f'"{sys.executable}" "{ALVO}"'
    r = _run(["schtasks", "/Create", "/TN", NOME, "/TR", tr,
              "/SC", "DAILY", "/ST", hora, "/F"])
    print((r.stdout or r.stderr).strip())
    if r.returncode == 0:
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
