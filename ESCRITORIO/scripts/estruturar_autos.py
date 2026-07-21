#!/usr/bin/env python3
"""
estruturar_autos.py — deixa os autos VIVOS (Fase A da "marcha processual viva").

A partir da TIMELINE de um processo (a lista de documentos do PJe-Kz: tipo, data,
id de cada peca), monta o INDICE CRONOLOGICO de pecas — peticoes, contestacoes,
manifestacoes, despachos, decisoes, sentencas, atas... — do mais ANTIGO ao mais
NOVO. E isso que torna os autos consultaveis por peca ("me mostra a inicial", "a
ultima manifestacao") e nao um bloco morto de PDF.

Serve tambem de BASELINE para o radar-delta (Fase B): a peca mais nova aqui e a
regua; amanha o radar compara a timeline nova com esta e captura SO o que entrou.

  Nao baixa nada, nao toca no tribunal — le uma timeline ja capturada. Leitura.

Uso:
  python ESCRITORIO/scripts/estruturar_autos.py <timeline.json> --cnj <CNJ>
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Pecas "estruturantes" — as que puxam a estrategia. Destacadas no indice.
DESTAQUE = {
    "peticao inicial", "peticao", "inicial", "contestacao", "replica",
    "manifestacao", "sentenca", "decisao", "despacho", "acordao", "acordo",
    "ata da audiencia", "recurso", "embargos", "alegacoes finais",
    "impugnacao", "agravo", "laudo",
}


def _sem_acento(t: str) -> str:
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", t or "")
                   if unicodedata.category(c) != "Mn").lower()


def carregar_timeline(caminho: Path) -> list[dict]:
    """Le a timeline (JSON do Kz) e normaliza os campos que o indice usa."""
    docs = json.loads(caminho.read_text(encoding="utf-8"))
    out = []
    for d in docs:
        if not d.get("documento", True):
            continue
        out.append({
            "id": d.get("id"),
            "id_unico": d.get("idUnicoDocumento"),
            "tipo": (d.get("tipo") or "").strip(),
            "titulo": (d.get("titulo") or "").strip(),
            "data": (d.get("data") or "")[:19],
            "responsavel": d.get("nomeSignatario") or d.get("nomeResponsavel") or "",
            "sigiloso": bool(d.get("documentoSigiloso")),
        })
    out.sort(key=lambda x: x["data"])  # cronologico: antigo -> novo
    return out


def _eh_destaque(tipo: str, titulo: str) -> bool:
    alvo = _sem_acento(tipo + " " + titulo)
    return any(d in alvo for d in DESTAQUE)


def render_md(cnj: str, pecas: list[dict]) -> str:
    linhas = [f"# Autos estruturados — {cnj}", ""]
    linhas.append(f"> Indice cronologico de pecas (mais antigo -> mais novo). "
                  f"{len(pecas)} pecas. Gerado {datetime.now():%d/%m/%Y %H:%M}.")
    linhas.append("> **Baseline do radar-delta:** a ultima peca abaixo e a regua; "
                  "o que entrar depois dela e novidade.")
    linhas.append("")
    tipos: dict[str, int] = {}
    for p in pecas:
        tipos[p["tipo"]] = tipos.get(p["tipo"], 0) + 1
    resumo = ", ".join(f"{t} ({n})" for t, n in sorted(tipos.items(), key=lambda x: -x[1]))
    linhas.append(f"**Composicao:** {resumo}")
    linhas.append("")
    linhas.append("| # | data | tipo | titulo | id |")
    linhas.append("|--:|------|------|--------|----|")
    for i, p in enumerate(pecas, 1):
        marca = "**" if _eh_destaque(p["tipo"], p["titulo"]) else ""
        dt = p["data"][:10] if p["data"] else "—"
        tit = (p["titulo"] or p["tipo"])[:48]
        seg = " 🔒" if p["sigiloso"] else ""
        linhas.append(f"| {i} | {dt} | {marca}{p['tipo']}{marca} | {tit}{seg} | "
                      f"`{p['id_unico'] or p['id']}` |")
    if pecas:
        ult = pecas[-1]
        linhas += ["", f"**Última peça (régua do delta):** {ult['data'][:10]} · "
                   f"{ult['tipo']} · `{ult['id_unico'] or ult['id']}`"]
    return "\n".join(linhas) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Indice cronologico de pecas (autos vivos).")
    ap.add_argument("timeline", help="JSON da timeline do processo (Kz)")
    ap.add_argument("--cnj", required=True, help="numero CNJ do processo")
    args = ap.parse_args()

    pecas = carregar_timeline(Path(args.timeline))
    if not pecas:
        raise SystemExit("  Timeline vazia — nada a estruturar.")

    destino = RAIZ / "AUTOS" / args.cnj
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "estrutura_cronologica.md").write_text(
        render_md(args.cnj, pecas), encoding="utf-8")
    # baseline para o radar-delta (Fase B): a lista de ids/datas de hoje
    (destino / "timeline_baseline.json").write_text(
        json.dumps({"cnj": args.cnj, "capturado_em": datetime.now().isoformat(timespec="seconds"),
                    "total_pecas": len(pecas), "pecas": pecas},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    ult = pecas[-1]
    print(f"  {len(pecas)} pecas estruturadas (cronologico) -> "
          f"AUTOS/{args.cnj}/estrutura_cronologica.md")
    print(f"  baseline do delta salvo. Ultima peca: {ult['data'][:10]} · {ult['tipo']}")


if __name__ == "__main__":
    main()
