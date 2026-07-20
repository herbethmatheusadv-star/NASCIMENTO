# -*- coding: utf-8 -*-
"""
soj_pendencias.py — O GESTOR DE PENDÊNCIAS do SOJ.

Reúne, num lugar só, as AÇÕES HUMANAS que o sistema não faz (R7): procurações a
assinar, petições prontas a protocolar, documentos a coletar, tarefas. Deriva a
maior parte do que JÁ está estruturado nas fichas — não pede recadastro:

  - procurações : CLIENTES cujo campo `procuracao` != assinada;
  - protocolos  : minutas prontas em AUTOS/<n>/inteligencia/minutas/*_RASCUNHO.md;
  - documentos  : campo `docs_pendentes` das fichas de cliente;
  - tarefas etc.: campo `pendencias:` (explícito) em PROCESSOS/ e CLIENTES/.

  python soj_pendencias.py            # relatório agrupado
  python soj_pendencias.py --json     # grava index/pendencias.json (para o painel)

Campo explícito `pendencias:` (lista) na ficha:
  - tipo: procuração | protocolo | documento | tarefa | contrato | assinatura
    o_que: "assinar a procuração ad judicia"
    quem: cliente | advogado | escritorio
    status: aberto | feito
    prazo: 2026-07-25        # opcional
    obs: "..."

R7: o gestor só ORGANIZA a fila de ações do titular. Assinar e protocolar são
sempre dele — o robô prepara, não age.
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
    sys.exit("[pendencias] falta pyyaml: pip install pyyaml")

PROCESSOS = soj.ROOT / "PROCESSOS"
CLIENTES = soj.ROOT / "CLIENTES"
AUTOS = soj.ROOT / "AUTOS"
SAIDA = soj.ROOT / "index" / "pendencias.json"


def _fm(caminho: Path) -> dict:
    txt = caminho.read_text(encoding="utf-8", errors="ignore")
    if not txt.startswith("---"):
        return {}
    fim = txt.find("\n---", 3)
    if fim < 0:
        return {}
    try:
        return yaml.safe_load(txt[3:fim]) or {}
    except Exception:  # noqa: BLE001
        return {}


def _proc_por_cnj() -> dict:
    """{cnj: {id, cliente}} — para ligar a minuta (em AUTOS/<cnj>) ao processo."""
    out = {}
    for f in PROCESSOS.glob("PROC-*.md"):
        if "_audiencia" in f.stem:
            continue
        fm = _fm(f)
        cnj = str(fm.get("numero") or "").strip().strip('"')
        if cnj:
            out[cnj] = {"id": fm.get("id") or f.stem,
                        "cliente": str(fm.get("cliente") or "")}
    return out


def _clientes_nome() -> dict:
    out = {}
    for f in CLIENTES.glob("CLI-*.md"):
        fm = _fm(f)
        out[str(fm.get("id") or f.stem)] = str(fm.get("nome") or f.stem)
    return out


def _norm(v) -> str:
    return str(v or "").strip().strip('"').lower()


def pendencias_do_acervo() -> list:
    """Todas as pendências abertas, derivadas + explícitas. Uma lista de dicts."""
    out = []
    nomes = _clientes_nome()

    # 1) PROCURAÇÕES — clientes cujo campo procuracao não é 'assinada'
    for f in sorted(CLIENTES.glob("CLI-*.md")):
        fm = _fm(f)
        cid = str(fm.get("id") or f.stem)
        proc = _norm(fm.get("procuracao"))
        if proc and proc != "assinada":
            out.append({"tipo": "procuração", "ref": cid,
                        "titulo": str(fm.get("nome") or cid),
                        "o_que": f"procuração {proc}", "quem": "cliente",
                        "status": "aberto", "prazo": None})
        # 2) DOCUMENTOS — docs_pendentes (lista) das fichas de cliente
        for d in (fm.get("docs_pendentes") or []):
            if str(d).strip():
                out.append({"tipo": "documento", "ref": cid,
                            "titulo": str(fm.get("nome") or cid),
                            "o_que": str(d)[:160], "quem": "escritório",
                            "status": "aberto", "prazo": None})

    # 3) PROTOCOLOS — minutas prontas em AUTOS (o robô preparou; você assina)
    mapa = _proc_por_cnj()
    for m in sorted(AUTOS.glob("*/inteligencia/minutas/*_RASCUNHO.md")):
        cnj = m.parents[2].name
        proc = mapa.get(cnj, {})
        pid = proc.get("id", cnj)
        cli = re.search(r"CLI-\d+", proc.get("cliente", ""))
        titulo = nomes.get(cli.group(0), pid) if cli else pid
        peca = m.stem.replace("_RASCUNHO", "").replace("_", " ")
        out.append({"tipo": "protocolo", "ref": pid, "titulo": titulo,
                    "o_que": f"protocolar: {peca} (rascunho pronto)",
                    "quem": "advogado", "status": "aberto", "prazo": None})

    # 4) EXPLÍCITAS — campo `pendencias:` em PROCESSOS/ e CLIENTES/
    for base in (PROCESSOS, CLIENTES):
        for f in sorted(base.glob("*-*.md")):
            if "_audiencia" in f.stem:
                continue
            fm = _fm(f)
            ref = str(fm.get("id") or f.stem)
            titulo = str(fm.get("nome") or fm.get("cliente") or ref)
            m = re.search(r"CLI-\d+", titulo)
            if m and m.group(0) in nomes:
                titulo = nomes[m.group(0)]
            for pz in (fm.get("pendencias") or []):
                if not isinstance(pz, dict) or _norm(pz.get("status")) == "feito":
                    continue
                out.append({
                    "tipo": _norm(pz.get("tipo")) or "tarefa", "ref": ref,
                    "titulo": titulo, "o_que": str(pz.get("o_que") or "")[:160],
                    "quem": _norm(pz.get("quem")) or "advogado",
                    "status": "aberto",
                    "prazo": str(pz.get("prazo")) if pz.get("prazo") else None,
                    "obs": str(pz.get("obs") or "")})

    ordem = {"protocolo": 0, "procuração": 1, "assinatura": 1, "contrato": 2,
             "documento": 3, "tarefa": 4}
    out.sort(key=lambda x: (ordem.get(x["tipo"], 9), x["ref"]))
    return out


def resumo(pend: list) -> dict:
    r = {}
    for p in pend:
        r[p["tipo"]] = r.get(p["tipo"], 0) + 1
    return r


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Gestor de pendências do SOJ.")
    ap.add_argument("--json", action="store_true", help="grava index/pendencias.json")
    args = ap.parse_args()

    pend = pendencias_do_acervo()

    if args.json:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(pend, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"[pendencias] {len(pend)} pendência(s) → {SAIDA}")
        return

    r = resumo(pend)
    print("=" * 68)
    print(f"  PENDÊNCIAS DO ESCRITÓRIO  ({len(pend)} abertas)")
    print("  " + " · ".join(f"{v} {k}" for k, v in r.items()))
    print("=" * 68)
    icone = {"protocolo": "📌", "procuração": "✍️ ", "documento": "📎",
             "contrato": "📄", "tarefa": "•", "assinatura": "✍️ "}
    atual = None
    for p in pend:
        if p["tipo"] != atual:
            atual = p["tipo"]
            print(f"\n  {icone.get(atual, '•')} {atual.upper()}")
        pz = f"  ⏰ {p['prazo']}" if p.get("prazo") else ""
        print(f"     [{p['ref']}] {p['titulo'][:38]} — {p['o_que']}{pz}")
    print("\n" + "=" * 68)
    print("  R7: o robô organiza a fila. Assinar e protocolar são só seus.")
    print("=" * 68)


if __name__ == "__main__":
    main()
