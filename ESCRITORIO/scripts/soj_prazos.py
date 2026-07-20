# -*- coding: utf-8 -*-
"""
soj_prazos.py — O MOTOR DE PRAZOS do SOJ (o watchdog).

Lê os prazos ESTRUTURADOS das fichas (campo `prazos:` no cabeçalho YAML),
calcula o vencimento com a regra certa (dias úteis × corridos, feriados
nacionais + móveis da Páscoa + recesso forense do art. 220 do CPC, + feriados
LOCAIS do config), e classifica por urgência. É o que existe para achar o prazo
ANTES — não depois.

  python soj_prazos.py                 # relatório de prazos, por urgência
  python soj_prazos.py --json          # grava index/prazos.json (para o painel)
  python soj_prazos.py --cnj <n>       # só um processo

Schema do campo `prazos:` na ficha (lista; dois formatos):
  # (a) prazo processual computado (termo + dias):
  - tipo: agravo            # rótulo livre (agravo, apelação, contrarrazões, ...)
    termo: 2026-06-04       # data do gatilho (intimação/publicação já considerada)
    dias: 15
    base: uteis             # uteis | corridos
    tribunal: tjpa          # p/ feriados locais (tjpa|tjma|trt8|parauapebas)
    status: aberto          # aberto | cumprido | perdido | suspenso | conferido
    obs: "contra a decisão de prisão"
  # (b) evento com data fixa (audiência, sessão):
  - tipo: audiência
    data: 2026-07-21
    hora: "08:30"
    status: aberto

REGRA DE FERRO: o motor CALCULA e ALERTA; a folha exata do prazo é sempre
conferida no PJe (feriados locais podem faltar). Vencimento nunca vira "fato"
sem `status: conferido` pelo advogado.
"""
import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import soj_lib as soj

try:
    import yaml
except ImportError:
    sys.exit("[prazos] falta pyyaml: pip install pyyaml")

PROCESSOS = soj.ROOT / "PROCESSOS"
CONFIG = soj.ROOT / "_SISTEMA" / "config" / "feriados.yaml"
SAIDA = soj.ROOT / "index" / "prazos.json"
HOJE = date.today()


# --------------------------------------------------------------- feriados
def pascoa(ano: int) -> date:
    """Domingo de Páscoa (algoritmo de Meeus/Butcher, calendário gregoriano)."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(ano, mes, dia)


def feriados_nacionais(ano: int) -> set:
    """Fixos + móveis (derivados da Páscoa). Não inclui locais nem recesso."""
    p = pascoa(ano)
    fixos = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15),
             (11, 20), (12, 25)]           # 20/11: Consciência Negra (Lei 14.759/2023)
    dias = {date(ano, m, d) for m, d in fixos}
    dias |= {
        p - timedelta(days=2),   # Sexta-feira Santa
        p - timedelta(days=48),  # Carnaval (segunda)
        p - timedelta(days=47),  # Carnaval (terça)
        p + timedelta(days=60),  # Corpus Christi
    }
    return dias


def _carregar_locais() -> dict:
    if not CONFIG.exists():
        return {}
    try:
        d = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        out = {}
        for trib, lista in (d.get("local") or {}).items():
            out[trib] = {_data(x) for x in (lista or []) if _data(x)}
        return out
    except Exception:  # noqa: BLE001
        return {}


LOCAIS = _carregar_locais()
_cache_nac = {}


def _nac(ano: int) -> set:
    if ano not in _cache_nac:
        _cache_nac[ano] = feriados_nacionais(ano)
    return _cache_nac[ano]


def em_recesso(d: date) -> bool:
    """Recesso forense do art. 220 do CPC: 20/12 a 20/01 (prazos suspensos)."""
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)


def eh_util(d: date, tribunal: str = "", com_recesso: bool = True) -> bool:
    if d.weekday() >= 5:                 # 5=sáb, 6=dom
        return False
    if d in _nac(d.year):
        return False
    if com_recesso and em_recesso(d):
        return False
    if tribunal and d in LOCAIS.get(tribunal, set()):
        return False
    return True


# --------------------------------------------------------------- cálculo
def _data(v):
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


def vencimento(termo: date, dias: int, base: str, tribunal: str = "") -> date:
    """Vencimento de um prazo. `uteis`: exclui o dia do começo (art. 224) e conta
    só dias úteis (art. 219), pulando recesso e feriados. `corridos`: soma
    corrida, protraindo o vencimento para o próximo dia útil se cair em não-útil."""
    if base == "corridos":
        # material (ex.: prescrição): recesso NÃO suspende; só protrai de
        # fim de semana / feriado (art. 224 §1º).
        d = termo + timedelta(days=dias)
        while not eh_util(d, tribunal, com_recesso=False):
            d += timedelta(days=1)
        return d
    # uteis (padrão dos prazos processuais)
    d = termo
    contados = 0
    while contados < dias:
        d += timedelta(days=1)
        if eh_util(d, tribunal):
            contados += 1
    return d


def calcular(pz: dict, proc: dict) -> dict | None:
    """Transforma um item `prazos:` da ficha num prazo calculado (ou None)."""
    tipo = str(pz.get("tipo") or "prazo")
    status = str(pz.get("status") or "aberto").lower()
    base = str(pz.get("base") or "uteis").lower()
    trib = str(pz.get("tribunal") or proc.get("tribunal_slug") or "").lower()
    obs = str(pz.get("obs") or "")
    conferido = status == "conferido"

    if pz.get("data"):                    # evento com data fixa (audiência)
        venc = _data(pz["data"])
        base = "data"
        if pz.get("hora"):
            obs = (f"{pz['hora']} " + obs).strip()
    elif pz.get("termo") and pz.get("dias"):
        termo = _data(pz["termo"])
        if not termo:
            return None
        venc = vencimento(termo, int(pz["dias"]), base, trib)
    else:
        return None
    if not venc:
        return None

    return {
        "proc": proc["id"], "numero": proc["numero"], "cliente": proc["cliente"],
        "adverso": proc["adverso"], "tipo": tipo, "obs": obs, "status": status,
        "base": base, "conferido": conferido,
        "vencimento": venc.isoformat(), "dias": (venc - HOJE).days,
        "local_faltando": bool(trib) and not LOCAIS.get(trib),
    }


# --------------------------------------------------------------- fichas
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


def _cliente(v) -> str:
    import re
    s = str(v or "").strip().strip('"')
    m = re.search(r"CLI-\d+", s)
    return m.group(0) if m else (s or "—")


def prazos_do_acervo(cnj: str = "") -> list:
    """Todos os prazos calculados do acervo, ordenados por vencimento.
    Ignora status cumprido/perdido/suspenso (só mostra o que ainda corre)."""
    out = []
    for f in sorted(PROCESSOS.glob("PROC-*.md")):
        fm = _fm(f)
        if "_audiencia" in f.stem or not fm.get("prazos"):
            continue
        numero = str(fm.get("numero") or "").strip().strip('"')
        if cnj and cnj not in numero:
            continue
        trib = str(fm.get("tribunal") or "").lower()
        proc = {"id": fm.get("id") or f.stem, "numero": numero,
                "cliente": _cliente(fm.get("cliente")),
                "adverso": str(fm.get("parte_adversa") or "?")[:44],
                "tribunal_slug": trib}
        for pz in fm["prazos"]:
            if not isinstance(pz, dict):
                continue
            calc = calcular(pz, proc)
            if calc and calc["status"] in ("aberto", "conferido"):
                out.append(calc)
    out.sort(key=lambda x: x["dias"])
    return out


# --------------------------------------------------------------- CLI
def _rotulo(dias: int) -> str:
    if dias < 0:
        return f"VENCIDO há {-dias}d"
    if dias == 0:
        return "HOJE"
    if dias == 1:
        return "amanhã"
    return f"em {dias} dias"


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Motor de prazos do SOJ.")
    ap.add_argument("--json", action="store_true", help="grava index/prazos.json")
    ap.add_argument("--cnj", default="", help="restringe a um processo")
    args = ap.parse_args()

    prazos = prazos_do_acervo(args.cnj)

    if args.json:
        SAIDA.parent.mkdir(parents=True, exist_ok=True)
        SAIDA.write_text(json.dumps(prazos, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        print(f"[prazos] {len(prazos)} prazo(s) → {SAIDA}")
        return

    print("=" * 70)
    print(f"  PRAZOS DO ACERVO — {HOJE:%d/%m/%Y}  ({len(prazos)} em curso)")
    print("=" * 70)
    if not prazos:
        print("  Nenhum prazo estruturado nas fichas ainda (campo `prazos:`).")
        print("  Adicione prazos ao cabeçalho das fichas para o motor vigiá-los.")
        return
    for p in prazos:
        venc = date.fromisoformat(p["vencimento"])
        selo = "⚠️ " if not p["conferido"] else "✓ "
        flag = " [feriados locais a configurar]" if p["local_faltando"] else ""
        print(f"\n  {selo}{_rotulo(p['dias']).ljust(14)} {venc:%d/%m/%Y}  "
              f"{p['tipo'].upper()}")
        print(f"     {p['proc']} · {p['cliente']} × {p['adverso']}")
        if p["obs"]:
            print(f"     {p['obs']}")
        print(f"     ({p['base']}{flag}; status: {p['status']})")
    print("\n" + "=" * 70)
    print("  ⚠️ = vencimento CALCULADO, a conferir no PJe (vire `status: conferido`).")
    print("  Prazos processuais em dias úteis; recesso 20/12–20/01 suspenso (art. 220).")
    print("=" * 70)


if __name__ == "__main__":
    main()
