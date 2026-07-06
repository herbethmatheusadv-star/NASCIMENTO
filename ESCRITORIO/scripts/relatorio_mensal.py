# -*- coding: utf-8 -*-
"""
relatorio_mensal.py — ESCRITORIO/RELATORIOS/AAAA-MM.md (Onda 2/F6).
Retrato do mes, gerado dos dados (DIARIO, CASO.yaml, BASE_LEGAL, git):
casos novos/protocolados/encerrados; prazos cumpridos e no radar;
REPROVACOES DE GATE E MOTIVOS; decisoes Tier B e vetos; verbetes
verificados/vencidos; pendencias de clientes; horas e custo de IA como
ESTIMATIVA (claramente marcada — nao ha medidor exato).

Uso:  python relatorio_mensal.py [--mes AAAA-MM]
"""
import argparse
import datetime
import re
import subprocess

import soj_lib as soj


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Relatorio mensal do SOJ.")
    ap.add_argument("--mes", default=soj.hoje().strftime("%Y-%m"),
                    help="AAAA-MM (padrao: mes corrente)")
    args = ap.parse_args()
    mes = args.mes

    novos, protocolados, encerrados = [], [], []
    reprovacoes, tier_b, decisoes_adv = [], [], []
    prazos_cumpridos, radar, pend_clientes = [], [], []

    if soj.CASOS.exists():
        for pasta in sorted(soj.CASOS.iterdir()):
            if not (pasta / "CASO.yaml").exists():
                continue
            nome = pasta.name
            dados = soj.load_caso(pasta)
            entradas = soj.parse_diario(pasta)
            no_mes = [e for e in entradas if e["datahora"].startswith(mes)]
            for e in no_mes:
                corpo_n = soj.normaliza(e["corpo"])
                primeira = (e["corpo"].splitlines() or [""])[0]
                if e["num"] == 1:
                    novos.append(f"{nome} — criado em {e['datahora']}")
                if e["tipo"] == "EVENTO_PROCESSUAL" and "protocolad" in corpo_n:
                    protocolados.append(f"{nome} — #{e['num']:03d} {primeira[:100]}")
                if "encerrad" in corpo_n and e["tipo"] in ("NOTA", "EVENTO_PROCESSUAL") \
                        and "encerramento do caso" in corpo_n:
                    encerrados.append(f"{nome} — #{e['num']:03d}")
                if e["tipo"] == "GATE" and "REPROVADO" in e["corpo"]:
                    m = re.search(r"Itens reprovados: (.+)", e["corpo"], re.S)
                    motivos = (m.group(1).strip()[:300] if m else "(sem detalhe)")
                    reprovacoes.append(f"**{nome}** #{e['num']:03d} — "
                                       f"{primeira[:60]}\n  - Motivos: {motivos}")
                if e["tipo"] == "DECISAO_SISTEMA" and re.search(r"tier\s*b", corpo_n):
                    tier_b.append(f"{nome} #{e['num']:03d} — {primeira[:110]}")
                if e["tipo"] == "DECISAO_ADVOGADO":
                    decisoes_adv.append(f"{nome} #{e['num']:03d} — {primeira[:110]}")
            for pz in (dados.get("prazos") or []):
                if soj.normaliza(pz.get("status", "")) == "cumprido" and \
                        str(pz.get("data", "")).startswith(mes):
                    prazos_cumpridos.append(f"{nome} {pz.get('id')} — {pz.get('descricao')}")
            for pz, dias in soj.prazos_em_alerta(dados):
                radar.append(f"{nome} {pz.get('id')} — {pz.get('data')} "
                             f"({'VENCIDO' if dias < 0 else f'{dias}d'}): "
                             f"{str(pz.get('descricao'))[:90]}")
            for p in soj.pendencias_abertas(dados):
                if str(p.get("responsavel")) == "cliente":
                    pend_clientes.append(f"{nome} {p.get('id')} — "
                                         f"{str(p.get('descricao'))[:90]}")

    # BASE_LEGAL: verificados no mes e vencidos hoje
    verificados, vencidos = [], []
    base = soj.ESCRITORIO / "BASE_LEGAL"
    for arq in sorted(base.glob("*.md")) if base.exists() else []:
        for bloco in re.split(r"(?m)^## ", arq.read_text(encoding="utf-8"))[1:]:
            ref = bloco.splitlines()[0].split(" —")[0].strip()
            m_ver = re.search(r"\*\*Verificado em:\*\*\s*(\d{4}-\d{2}-\d{2})", bloco)
            m_val = re.search(r"\*\*Validade:\*\*\s*(\d+)\s*dias", bloco)
            if m_ver and m_ver.group(1).startswith(mes):
                verificados.append(f"{ref} ({arq.name}) — verificado {m_ver.group(1)}")
            if m_ver and m_val:
                v = datetime.date.fromisoformat(m_ver.group(1)) + \
                    datetime.timedelta(days=int(m_val.group(1)))
                if v < soj.hoje():
                    vencidos.append(f"{ref} ({arq.name}) — venceu {v}")

    # horas via git (ESTIMATIVA: por dia trabalhado, ultimo - primeiro commit + 30min)
    horas_txt = "sem dados do git"
    commits = 0
    try:
        r = subprocess.run(["git", "log", f"--since={mes}-01",
                            f"--until={mes}-31 23:59", "--format=%ad",
                            "--date=format:%Y-%m-%d %H:%M"],
                           cwd=soj.ROOT, capture_output=True, text=True)
        stamps = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        commits = len(stamps)
        por_dia = {}
        for s in stamps:
            d, h = s.split(" ")
            por_dia.setdefault(d, []).append(h)
        total_min = 0
        for d, hs in por_dia.items():
            hs = sorted(hs)
            h0 = int(hs[0][:2]) * 60 + int(hs[0][3:5])
            h1 = int(hs[-1][:2]) * 60 + int(hs[-1][3:5])
            total_min += (h1 - h0) + 30
        horas_txt = (f"~{total_min / 60:.1f}h em {len(por_dia)} dia(s) de "
                     f"trabalho, {commits} commits")
    except Exception:
        pass

    def secao(titulo, itens, vazio="- (nenhum)"):
        s = [f"## {titulo}", ""]
        s += [f"- {i}" for i in itens] if itens else [vazio]
        s.append("")
        return s

    out = [f"# RELATÓRIO MENSAL — {mes}", "",
           f"Gerado em {soj.agora()} por relatorio_mensal.py — não editar.", ""]
    out += secao("Casos novos no mês", novos)
    out += secao("Protocolados no mês", protocolados)
    out += secao("Encerrados no mês", encerrados)
    out += secao("⚠️ REPROVAÇÕES DE GATE e motivos (o que os portões barraram)",
                 reprovacoes)
    out += secao("Decisões Tier B do sistema (no mês)", tier_b)
    out += secao("Decisões e vetos do advogado (no mês)", decisoes_adv)
    out += secao("Prazos cumpridos no mês", prazos_cumpridos)
    out += secao("Prazos no radar AGORA (vencidos ou ≤ 7 dias)", radar)
    out += secao("Verbetes verificados/revalidados no mês", verificados)
    out += secao("Verbetes VENCIDOS hoje (rodar revalidar biblioteca)", vencidos)
    out += secao("Pendências de clientes em aberto", pend_clientes)
    out += ["## Horas e custo de IA — **ESTIMATIVA** (sem medidor exato)", "",
            f"- Horas de operação (proxy: timestamps do git): **{horas_txt}**.",
            "  Método: por dia com commits, do primeiro ao último commit +30min.",
            "  É ESTIMATIVA de atividade no repositório, não ponto de trabalho.",
            "- Custo de IA: **não há medidor por sessão neste ambiente** — a",
            "  referência confiável é a fatura/uso do plano Claude. Proxy do mês:",
            f"  {commits} commits em {horas_txt.split(' em ')[-1] if ' em ' in horas_txt else '?'}.",
            "  Tratar QUALQUER número daqui como estimativa marcada.", ""]

    destino = soj.ESCRITORIO / "RELATORIOS"
    destino.mkdir(exist_ok=True)
    arq = destino / f"{mes}.md"
    arq.write_text("\n".join(out), encoding="utf-8", newline="\n")
    print(f"[OK] Relatorio mensal gerado: ESCRITORIO/RELATORIOS/{mes}.md")
    print(f"     Reprovacoes de gate no mes: {len(reprovacoes)} · Tier B: "
          f"{len(tier_b)} · Radar: {len(radar)} · Pend. clientes: {len(pend_clientes)}")


if __name__ == "__main__":
    main()
