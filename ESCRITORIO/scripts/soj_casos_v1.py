# -*- coding: utf-8 -*-
"""
soj_casos_v1.py — A PONTE v1 (CASOS/) → v2 (o cockpit).

O SOJ tem duas ferramentas complementares, não redundantes:
  - v1  `CASOS/<NOME>/`  — a OFICINA DE PEÇAS (intake → estratégia → minuta →
        protocolo, com gates e DIÁRIO). Fonte da verdade: `CASO.yaml`.
  - v2  `PROCESSOS/` + `CLIENTES/` — o COCKPIT do acervo (painel, prazos,
        pendências, financeiro).

O buraco que esta ponte fecha: um caso que nasce e termina em v1 **não aparece
em v2** e some do radar diário. Ex. real: a Tânia (alimentos/guarda, petição
FINAL pronta) e a Daiane-cível (obrigação de fazer) — ambas prontas a protocolar
e invisíveis ao cockpit.

A ponte NÃO move nem duplica dados: ela LÊ o `CASO.yaml` de v1 e, para cada caso
com **petição final pronta e ainda não protocolado** (`fase_processual:
pre_protocolo`), devolve uma pendência de `protocolo` — que o `soj_pendencias`
funde na fila "Petições prontas a protocolar (você assina)".

  python soj_casos_v1.py            # relatório de todos os casos de v1
  python soj_casos_v1.py --json     # grava index/casos_v1.json

R7: a ponte só traz para o radar. Assinar e protocolar são sempre do titular.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import soj_lib as soj

try:
    import yaml
except ImportError:
    sys.exit("[casos_v1] falta pyyaml: pip install pyyaml")

CASOS = soj.ROOT / "CASOS"
SAIDA = soj.ROOT / "index" / "casos_v1.json"

# nomes de arquivo que indicam uma peça FINAL (não um DOC de prova)
_RX_PECA_FINAL = re.compile(r"(?i)(peticao|petição).*(final|timbrado|inicial)"
                            r"|(final|timbrado).*(peticao|petição)")


def _peticao_final(dir_caso: Path) -> str:
    """Devolve o nome da peça final em <dir>/PROTOCOLO/ (ou ''), se houver."""
    prot = dir_caso / "PROTOCOLO"
    if not prot.is_dir():
        return ""
    for f in sorted(prot.iterdir()):
        if f.is_file() and f.suffix.lower() in (".md", ".docx", ".pdf") \
                and _RX_PECA_FINAL.search(f.name):
            return f.name
    return ""


def _eh_teste(dir_nome: str, titulo: str) -> bool:
    """Fixtures de laboratório (TESTE_*, CASO_TESTE_*, 'ficticio') nunca entram
    na fila real — mesmo que ganhem uma peça depois."""
    alvo = f"{dir_nome} {titulo}".lower()
    return bool(re.search(r"\bteste\b|test[e_]|fict|lab importacao|importacao", alvo))


def _autor(caso_yaml: dict) -> str:
    """Nome da parte no polo ativo (papel começa com 'autor')."""
    for pt in (caso_yaml.get("partes") or []):
        if isinstance(pt, dict) and str(pt.get("papel") or "").startswith("autor"):
            return str(pt.get("nome") or "").strip()
    return ""


def casos_v1() -> list:
    """Todos os casos de v1 com CASO.yaml — o estado bruto, para o relatório."""
    out = []
    if not CASOS.is_dir():
        return out
    for d in sorted(p for p in CASOS.iterdir() if p.is_dir()):
        arq = d / "CASO.yaml"
        if not arq.exists():
            continue
        try:
            data = yaml.safe_load(arq.read_text(encoding="utf-8", errors="ignore"))
        except Exception:  # noqa: BLE001
            data = None
        if not isinstance(data, dict):
            continue
        caso = data.get("caso") or {}
        peca = _peticao_final(d)
        titulo = str(caso.get("titulo") or d.name)
        out.append({
            "dir": d.name,
            "id": str(caso.get("id") or d.name),
            "titulo": titulo,
            "area": str(caso.get("area") or ""),
            "comarca": str(caso.get("comarca") or ""),
            "fase": str(caso.get("fase") or ""),
            "fase_processual": str(caso.get("fase_processual") or "").strip(),
            "segredo": bool(caso.get("segredo_justica")),
            "autor": _autor(data),
            "peca_final": peca,
            "teste": _eh_teste(d.name, titulo),
        })
    return out


def pendentes_de_protocolo() -> list:
    """Casos de v1 prontos a protocolar (peça final + `pre_protocolo`), no
    formato de pendência que o soj_pendencias consome (tipo 'protocolo')."""
    out = []
    for c in casos_v1():
        if c["teste"]:
            continue
        if c["fase_processual"] == "pre_protocolo" and c["peca_final"]:
            seg = " · segredo de justiça" if c["segredo"] else ""
            out.append({
                "tipo": "protocolo",
                "ref": c["dir"],
                "titulo": (c["autor"] or c["titulo"])[:60],
                "o_que": f"protocolar: {c['titulo']} — petição final pronta "
                         f"(v1 CASOS/{c['dir']}/PROTOCOLO){seg}",
                "quem": "advogado", "status": "aberto", "prazo": None,
                "fonte": "v1"})
    return out


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Ponte v1 (CASOS/) → cockpit.")
    ap.add_argument("--json", action="store_true", help="grava index/casos_v1.json")
    args = ap.parse_args()
    casos = casos_v1()
    pend = pendentes_de_protocolo()

    if args.json:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps({"casos": casos, "pendentes": pend},
                                    ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[casos_v1] {len(casos)} caso(s), {len(pend)} pronto(s) → {SAIDA}")
        return

    print("=" * 70)
    print(f"  PONTE v1 → v2 · {len(casos)} caso(s) na oficina (CASOS/)")
    print("=" * 70)
    for c in casos:
        pronto = "  📌 PRONTO A PROTOCOLAR" if (
            c["fase_processual"] == "pre_protocolo" and c["peca_final"]) else ""
        print(f"\n  [{c['dir']}] {c['titulo'][:52]}")
        print(f"     área {c['area'] or '?'} · fase_proc {c['fase_processual'] or '?'}"
              f"{' · segredo' if c['segredo'] else ''}{pronto}")
        if c["peca_final"]:
            print(f"     peça final: {c['peca_final']}")
    print("\n" + "-" * 70)
    print(f"  {len(pend)} caso(s) prontos a protocolar entram na fila de pendências:")
    for p in pend:
        print(f"     [{p['ref']}] {p['titulo']}")
    print("=" * 70)
    print("  R7: a ponte só traz para o radar. Assinar/protocolar é do titular.")
    print("=" * 70)


if __name__ == "__main__":
    main()
