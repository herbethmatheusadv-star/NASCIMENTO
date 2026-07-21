# -*- coding: utf-8 -*-
"""
soj_financeiro.py — O PULSO FINANCEIRO do SOJ.

Lê o razão append-only `FINANCEIRO/lancamentos.md` (a verdade do dinheiro) e
agrega: recebido, a receber, provisionado, e os vencimentos próximos. Cruza com
as fichas de cliente para listar os **contratos a formalizar** (R3 — honorários
sem contrato escrito é receita que escorre).

  python soj_financeiro.py            # relatório
  python soj_financeiro.py --json     # grava index/financeiro.json (painel)

Não inventa número: só soma o que está lançado. Lançamento não se edita (o razão
é append-only); correção = estorno com referência.
"""
import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

import soj_lib as soj

try:
    import yaml
except ImportError:
    sys.exit("[financeiro] falta pyyaml: pip install pyyaml")

FINANCEIRO = soj.ROOT / "FINANCEIRO"
CLIENTES = soj.ROOT / "CLIENTES"
SAIDA = soj.ROOT / "index" / "financeiro.json"
HOJE = date.today()


def _valor(s: str) -> float:
    """'R$ 2.728,19' -> 2728.19 ; '—'/'' -> 0.0"""
    s = re.sub(r"[^\d,]", "", str(s).replace(".", "")).replace(",", ".")
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def _norm(s) -> str:
    return str(s or "").strip().strip('"').lower()


def lancamentos() -> list:
    arq = FINANCEIRO / "lancamentos.md"
    if not arq.exists():
        return []
    out = []
    for ln in arq.read_text(encoding="utf-8", errors="ignore").splitlines():
        ln = ln.strip()
        if not ln.startswith("|"):
            continue
        cols = [c.strip() for c in ln.strip("|").split("|")]
        if len(cols) < 9 or cols[0].lower() == "data" or set(cols[0]) <= {"-", " "}:
            continue
        out.append({"data": cols[0], "tipo": cols[1].lower(), "cliente": cols[2],
                    "caso": cols[3], "descricao": cols[4], "valor": _valor(cols[5]),
                    "vencimento": cols[6], "status": _norm(cols[7]), "obs": cols[8]})
    return out


def _data(v):
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


def contratos_a_formalizar() -> list:
    """Clientes cujo contrato não é 'assinado' nem 'não-aplicável'."""
    out = []
    for f in sorted(CLIENTES.glob("CLI-*.md")):
        txt = f.read_text(encoding="utf-8", errors="ignore")
        fim = txt.find("\n---", 3)
        try:
            fm = yaml.safe_load(txt[3:fim]) if txt.startswith("---") and fim > 0 else {}
        except Exception:  # noqa: BLE001
            fm = {}
        c = _norm((fm or {}).get("contrato"))
        if c and c not in ("assinado", "assinada", "nao-aplicavel", "não-aplicável"):
            out.append({"ref": str((fm or {}).get("id") or f.stem),
                        "nome": str((fm or {}).get("nome") or f.stem), "estado": c})
    return out


def resumo() -> dict:
    lanc = lancamentos()
    por_status = {}
    for l in lanc:
        # despesa/provisório reduzem; entrada/parcela/acordo/exito somam a favor
        por_status[l["status"]] = por_status.get(l["status"], 0.0) + l["valor"]
    a_vencer = sorted(
        [l for l in lanc if l["status"] in ("a-receber", "a-confirmar", "provisorio")
         and _data(l["vencimento"])],
        key=lambda x: _data(x["vencimento"]))
    return {
        "recebido": round(por_status.get("recebido", 0.0), 2),
        "a_receber": round(por_status.get("a-receber", 0.0), 2),
        "provisorio": round(por_status.get("provisorio", 0.0), 2),
        "a_confirmar": round(por_status.get("a-confirmar", 0.0), 2),
        "lancamentos": len(lanc),
        "a_vencer": [{"cliente": l["cliente"][:32], "valor": l["valor"],
                      "vencimento": l["vencimento"], "status": l["status"]}
                     for l in a_vencer[:8]],
        "contratos_a_formalizar": contratos_a_formalizar(),
    }


def _r(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Pulso financeiro do SOJ.")
    ap.add_argument("--json", action="store_true", help="grava index/financeiro.json")
    args = ap.parse_args()
    r = resumo()

    if args.json:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[financeiro] → {SAIDA}")
        return

    print("=" * 66)
    print("  PULSO FINANCEIRO  (do razão FINANCEIRO/lancamentos.md)")
    print("=" * 66)
    print(f"  Recebido:     {_r(r['recebido'])}")
    print(f"  A receber:    {_r(r['a_receber'])}")
    print(f"  Provisório:   {_r(r['provisorio'])}   (despesas/custas a confirmar)")
    print(f"  A confirmar:  {_r(r['a_confirmar'])}")
    if r["a_vencer"]:
        print("\n  A vencer/confirmar:")
        for v in r["a_vencer"]:
            print(f"    {v['vencimento']}  {_r(v['valor'])}  {v['cliente']} ({v['status']})")
    caf = r["contratos_a_formalizar"]
    print(f"\n  📄 CONTRATOS A FORMALIZAR: {len(caf)}  (honorários sem contrato "
          f"escrito = R3 pendente)")
    for c in caf[:6]:
        print(f"    [{c['ref']}] {c['nome'][:40]} — contrato {c['estado']}")
    if len(caf) > 6:
        print(f"    … e mais {len(caf) - 6}.")
    print("\n" + "=" * 66)
    print("  Só soma o que está lançado. Razão é append-only (não se edita).")
    print("=" * 66)


if __name__ == "__main__":
    main()
