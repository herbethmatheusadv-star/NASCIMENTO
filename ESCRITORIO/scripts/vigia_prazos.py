# -*- coding: utf-8 -*-
"""
vigia_prazos.py — o VIGIA DE PRAZOS do escritório (Adendo A1 do blueprint).
Regra permanente do kernel (aprendida no piloto, quando o prazo de 11/06/2026
venceu sem que o sistema antigo desse alarme):

  TODA SESSÃO, sobre qualquer caso, começa rodando este script.

O que faz: varre os prazos de TODOS os casos contra a data de hoje.
Prazo ATIVO vencido ou a <= 7 dias:
  1. gera entrada ALERTA no DIARIO do caso (uma unica vez por estado,
     marcador VIGIA-PRAZO — sem duplicar em rodadas seguintes);
  2. ganha destaque no PAINEL.md (secao "PRAZOS NO RADAR", via gerar_views).

Prazos com status: cumprido | prejudicado sao ignorados.

Uso:
  python vigia_prazos.py            # varre tudo, alerta e atualiza o painel
  python vigia_prazos.py --so-ver   # so mostra, sem escrever nada
"""
import argparse

import soj_lib as soj


def marcador(pid, dias):
    estado = "VENCIDO" if dias < 0 else "PROXIMO"
    return f"VIGIA-PRAZO {pid} [{estado}]"


def ja_alertado(entradas, marca):
    return any(e["tipo"] == "ALERTA" and marca in e["corpo"] for e in entradas)


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Vigia de prazos do SOJ (Adendo A1).")
    ap.add_argument("--so-ver", action="store_true",
                    help="Apenas exibe, sem gravar ALERTA nem atualizar views")
    args = ap.parse_args()

    achados = []       # (cliente, prazo, dias, novo_alerta: bool)
    casos_alterados = []

    if soj.CASOS.exists():
        for pasta in sorted(soj.CASOS.iterdir()):
            if not (pasta / "CASO.yaml").exists():
                continue
            dados = soj.load_caso(pasta)
            alertas = soj.prazos_em_alerta(dados)
            if not alertas:
                continue
            entradas = soj.parse_diario(pasta)
            for prazo, dias in alertas:
                pid = str(prazo.get("id"))
                marca = marcador(pid, dias)
                novo = not ja_alertado(entradas, marca)
                achados.append((pasta.name, prazo, dias, novo))
                if novo and not args.so_ver:
                    if dias < 0:
                        corpo = (f"{marca}: '{prazo.get('descricao')}' VENCEU em "
                                 f"{prazo.get('data')} (ha {-dias} dia(s)). "
                                 "Providenciar imediatamente ou registrar no CASO.yaml "
                                 "o status cumprido/prejudicado com justificativa.")
                    else:
                        corpo = (f"{marca}: '{prazo.get('descricao')}' vence em "
                                 f"{prazo.get('data')} (em {dias} dia(s), "
                                 f"criticidade {prazo.get('criticidade')}).")
                    soj.append_diario(pasta, "ALERTA", corpo)
                    if pasta.name not in casos_alterados:
                        casos_alterados.append(pasta.name)

    if not args.so_ver:
        import gerar_views
        for nome in casos_alterados:
            gerar_views.gerar_views(nome)
        gerar_views.atualizar_painel()

    # Lembrete mensal da biblioteca (Onda 1/F6): dispara UMA vez por mes,
    # na primeira sessao em que o vigia roda no mes novo.
    if not args.so_ver:
        estado = soj.ESCRITORIO / ".lembrete_revalidacao"
        mes = soj.hoje().strftime("%Y-%m")
        anterior = estado.read_text(encoding="utf-8").strip() if estado.exists() else ""
        if anterior != mes:
            estado.write_text(mes, encoding="utf-8")
            print(f"[BIBLIOTECA] 1a sessao do mes {mes}: rode o ritual de "
                  "revalidacao — python ESCRITORIO/scripts/revalidar_biblioteca.py")

    if not achados:
        print("[VIGIA] Nenhum prazo vencido ou a 7 dias em nenhum caso. Tudo em dia.")
        return
    print(f"[VIGIA] {len(achados)} prazo(s) no radar:")
    for cliente, prazo, dias, novo in achados:
        situacao = f"VENCIDO ha {-dias}d" if dias < 0 else f"vence em {dias}d"
        etiqueta = "ALERTA NOVO no DIARIO" if (novo and not args.so_ver) else \
                   ("alerta novo (nao gravado — --so-ver)" if novo else "ja alertado antes")
        print(f"  [!] {cliente} · {prazo.get('id')} · {situacao} · "
              f"{prazo.get('descricao')}")
        print(f"      -> {etiqueta}")


if __name__ == "__main__":
    main()
