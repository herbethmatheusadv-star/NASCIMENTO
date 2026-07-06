# -*- coding: utf-8 -*-
"""
colher_aprendizados.py — CICLO DE COLHEITA (blueprint, seção 7).
Disparado no "protocolado, processo nº X" e no "encerrar caso" (ou à mão).

Varre o DIARIO do caso e gera _views/PROPOSTA_DE_APRENDIZADO.md com os
CANDIDATOS a evolução do módulo da área. Este script NÃO altera nenhum
arquivo de módulo: **nada é promovido sem RATIFICACAO em bloco do advogado**
(entrada RATIFICACAO no DIARIO citando a proposta; a promoção é feita na
sessão, item a item, depois do ok).

Uso:
  python colher_aprendizados.py CLIENTE [--evento "protocolado processo N"]
"""
import argparse
import re

import soj_lib as soj


def _resumo(e, largura=180):
    primeira = (e["corpo"].splitlines() or [""])[0]
    return primeira[:largura]


BALDES = [
    ("Decisões Tier B e vetos → candidatos a RAMO DA ÁRVORE (praxe_decisoria) "
     "ou a DECISÃO RESERVADA",
     lambda e, t: e["tipo"] == "DECISAO_ADVOGADO"
     or (e["tipo"] == "DECISAO_SISTEMA" and re.search(r"tier\s*b", t))),
    ("Quase-erros e falso-positivos → candidatos ao ANTI-ERRO FATAL",
     lambda e, t: e["tipo"] == "ALERTA"
     or re.search(r"falso.?positivo|quase.?erro|divergenc", t)),
    ("Fontes inexistentes/revogadas → candidatos a ANTITESES (teses.md)",
     lambda e, t: re.search(r"revogad|inexistent|nao existe|"
                            r"redacao (anterior|superada)|nunca citar", t)),
    ("Desvios de template → candidatos a VARIANTES do template",
     lambda e, t: re.search(r"desvio de template|variante do template|"
                            r"fora do template", t)),
    ("Marcadas explicitamente com COLHEITA:",
     lambda e, t: "colheita:" in t),
    ("Verbetes novos (já vivem na BASE_LEGAL — apenas inventário)",
     lambda e, t: e["tipo"] == "PESQUISA"),
]


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Ciclo de colheita do SOJ.")
    ap.add_argument("cliente")
    ap.add_argument("--evento", default="colheita manual",
                    help='Gatilho, ex.: "protocolado processo N" | "encerramento"')
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)
    entradas = soj.parse_diario(pasta)
    modulo = dados["caso"].get("modulo", "?")

    out = [f"# PROPOSTA DE APRENDIZADO — {args.cliente} "
           f"({dados['caso'].get('id')})",
           "",
           f"Colheita gerada em {soj.agora()} · gatilho: {args.evento} · "
           f"módulo alvo: {modulo}",
           "",
           "> **NADA daqui foi promovido ao módulo.** Para promover: o advogado",
           "> registra RATIFICACAO em bloco no DIARIO citando esta proposta",
           "> (com vetos pontuais, se quiser) e a sessão executa item a item.",
           ""]

    total = 0
    ja_no_balde_verbetes = set()
    for titulo, pertence in BALDES:
        achados = []
        for e in entradas:
            t = soj.normaliza(e["corpo"])
            if "proposta de aprendizado" in t:      # não colher a si mesma
                continue
            if pertence(e, t):
                achados.append(e)
        out.append(f"## {titulo}")
        out.append("")
        if achados:
            for e in achados:
                out.append(f"- **#{e['num']:03d}** ({e['tipo']}, {e['datahora']}): "
                           f"{_resumo(e)}")
                total += 1
        else:
            out.append("- (nenhum candidato)")
        out.append("")

    out += ["---",
            "## Como ratificar",
            "",
            "Diga ao Claude: *\"ratifico a proposta de aprendizado do caso "
            f"{args.cliente}\"* (ou liste vetos). Será registrada RATIFICACAO "
            "no DIARIO e só então os itens aprovados entram em "
            f"ESCRITORIO/MODULOS/{str(modulo).split('/')[0]}/.", ""]

    (pasta / "_views").mkdir(exist_ok=True)
    destino = pasta / "_views" / "PROPOSTA_DE_APRENDIZADO.md"
    destino.write_text("\n".join(out), encoding="utf-8", newline="\n")

    num = soj.append_diario(
        pasta, "NOTA",
        f"CICLO DE COLHEITA executado (gatilho: {args.evento}): proposta de "
        f"aprendizado gerada em _views/PROPOSTA_DE_APRENDIZADO.md com {total} "
        "candidato(s). Nenhum arquivo de modulo alterado — aguarda RATIFICACAO "
        "em bloco do advogado.")

    print(f"[OK] Proposta de aprendizado: {total} candidato(s) -> "
          f"_views/PROPOSTA_DE_APRENDIZADO.md (DIARIO #{num:03d}).")
    print("     Nada foi promovido ao modulo — aguarda a sua ratificacao.")


if __name__ == "__main__":
    main()
