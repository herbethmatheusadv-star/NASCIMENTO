# -*- coding: utf-8 -*-
"""
soj_autos.py — a ROTINA de autos num comando so (Fase 3 do PLANO_SOJ).

Encadeia baixar -> importar -> reindexar: UM login e os autos de todo o acervo
viram texto pesquisavel e citavel. E o botao unico do dia a dia.

  PASSO 1  CONECTOR/baixar_autos.py --todos   (voce loga uma vez; reaproveita
           a sessao viva se ja houver — nao repete o login)
  PASSO 2  soj_import.py                      (PDF -> texto + manifesto)
  PASSO 3  soj_reindex.py                     (index FTS5)

Para em qualquer passo que falhe (nao reindexa em cima de importacao quebrada).

Uso:
  python soj_autos.py                 # baixa tudo, importa, reindexa
  python soj_autos.py --sem-baixar    # so importa + reindexa (PDFs ja em AUTOS/)
  python soj_autos.py --cnj 0805058-87.2025.8.14.0040
  python soj_autos.py --forcar        # re-extrai mesmo com cache
"""
import argparse
import subprocess
import sys

import soj_lib as soj

BAIXAR = soj.ROOT / "CONECTOR" / "baixar_autos.py"
IMPORTAR = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_import.py"
REINDEX = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_reindex.py"
INTEL = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_inteligencia.py"
RESUMO = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_resumo.py"
PAINEL = soj.ROOT / "ESCRITORIO" / "scripts" / "soj_painel.py"


def passo(n: int, titulo: str, args: list) -> int:
    # flush=True: senao o banner do pai (bufferizado) sai DEPOIS da saida do
    # filho e a ordem fica trocada.
    print("\n" + "#" * 68, flush=True)
    print(f"#  PASSO {n}: {titulo}", flush=True)
    print("#" * 68, flush=True)
    # stdio herdado: o passo 1 precisa que VOCE veja e responda o login.
    return subprocess.run([sys.executable, *map(str, args)],
                          cwd=str(soj.ROOT)).returncode


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(
        description="Rotina de autos: baixar + importar + reindexar.")
    ap.add_argument("--sem-baixar", action="store_true", help="pula o download")
    ap.add_argument("--cnj", default="", help="restringe a um processo")
    ap.add_argument("--forcar", action="store_true", help="re-extrai mesmo com cache")
    args = ap.parse_args()

    if not args.sem_baixar:
        alvo = ["--cnj", args.cnj] if args.cnj else ["--todos"]
        rc = passo(1, "BAIXAR autos (voce loga uma vez)", [BAIXAR, *alvo])
        if rc != 0:
            print(f"\n[rotina] o download saiu com codigo {rc}. Parei aqui — "
                  f"nada foi importado.")
            sys.exit(rc)
    else:
        print("[rotina] --sem-baixar: uso os PDFs que ja estao em AUTOS/.")

    imp = [IMPORTAR]
    if args.cnj:
        imp += ["--cnj", args.cnj]
    if args.forcar:
        imp += ["--forcar"]
    rc = passo(2, "IMPORTAR (PDF -> texto + manifesto)", imp)
    if rc != 0:
        print(f"\n[rotina] a importacao saiu com codigo {rc}. Nao reindexei.")
        sys.exit(rc)

    intel = [INTEL]
    if args.cnj:
        intel += ["--cnj", args.cnj]
    rc = passo(3, "LINHA DO TEMPO das pecas (inteligencia)", intel)
    if rc != 0:
        print(f"\n[rotina] a inteligencia saiu com codigo {rc}. Parei aqui.")
        sys.exit(rc)

    rc = passo(4, "REINDEXAR (index FTS5)", [REINDEX])
    if rc != 0:
        print(f"\n[rotina] a reindexacao saiu com codigo {rc}.")
        sys.exit(rc)

    # passo 5: prepara os dossies/esqueletos dos processos com audiencia/prazo
    # iminente (a IA preenche o resumo depois). Nao derruba a rotina se falhar —
    # e preparacao, nao coleta.
    passo(5, "PREPARAR resumos dos processos iminentes (audiencia/prazo)",
          [RESUMO, "--iminentes"])

    # passo 6: gera e ABRE o painel do dia (o cockpit). Nao derruba a rotina.
    passo(6, "PAINEL do dia (abre no navegador)", [PAINEL])

    print("\n" + "=" * 68)
    print("  ROTINA COMPLETA — o painel do dia abriu no navegador.")
    print('  Buscar:            python soj_search.py "termo"')
    print("  Resumo de 1 proc:  python soj_resumo.py --cnj <n>   (IA preenche)")
    print("  Conferir citacoes: python soj_verificar_citacoes.py MINUTA.md")
    print("=" * 68)


if __name__ == "__main__":
    main()
