# -*- coding: utf-8 -*-
"""
gerar_views.py — regenera _views/ a partir da fonte da verdade (blueprint, seção 5).
Views por script = zero token e consistência garantida. NUNCA editar _views/ à mão.

Gera por caso: STATUS.md, rastreabilidade.md, rol_documentos.md,
checklist_cliente.md, pendencias.md, resumo_decisoes.md — e o PAINEL.md da raiz.

Uso:
  python gerar_views.py CLIENTE        # um caso (e o painel)
  python gerar_views.py --todos        # todos os casos (e o painel)
"""
import argparse
import re

import soj_lib as soj

PRIORIDADES = ["critica", "alta", "media", "baixa"]


def _fmt_gate(g):
    status = str(g.get("status", "pendente"))
    data = g.get("data")
    return f"{status} ({data})" if data else status


def _prazos_ordenados(dados):
    prazos = list(dados.get("prazos") or [])
    return sorted(prazos, key=lambda p: str(p.get("data", "9999")))


def _escrever(pasta_views, nome, texto):
    (pasta_views / nome).write_text(texto, encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ STATUS
def _view_status(nome, pasta, dados, entradas):
    caso = dados["caso"]
    gates = caso.get("gates") or {}
    prazos = _prazos_ordenados(dados)
    pend_criticas = [p for p in soj.pendencias_abertas(dados)
                     if str(p.get("prioridade")) == "critica"]
    proximo_prazo = ""
    if prazos:
        p0 = prazos[0]
        proximo_prazo = f"{p0.get('data')} — {p0.get('descricao')}"

    fatos = dados.get("fatos") or []
    contagem = {"provado": 0, "alegado": 0, "controverso": 0}
    for f in fatos:
        s = str(f.get("status", ""))
        if s in contagem:
            contagem[s] += 1

    fm = [
        "---",
        f"caso_id: {caso.get('id')}",
        f"cliente: {nome}",
        f"titulo: \"{caso.get('titulo')}\"",
        f"area: {caso.get('area')}",
        f"fase: {caso.get('fase')}",
        f"complexidade: {caso.get('complexidade')}",
        f"g1: {(gates.get('G1') or {}).get('status', 'pendente')}",
        f"g2: {(gates.get('G2') or {}).get('status', 'pendente')}",
        f"g3: {(gates.get('G3') or {}).get('status', 'pendente')}",
        f"proximo_prazo: \"{proximo_prazo}\"",
        f"pendencias_criticas_abertas: {len(pend_criticas)}",
        f"atualizado: {soj.agora()}",
        "---",
    ]

    corpo = [
        "",
        f"# STATUS — {caso.get('titulo')}",
        "",
        f"**Cliente/pasta:** {nome} · **Caso:** {caso.get('id')} · "
        f"**Área:** {caso.get('area')} · **Módulo:** {caso.get('modulo')}",
        f"**Fase:** {caso.get('fase')} · **Complexidade:** {caso.get('complexidade')} · "
        f"**Segredo de justiça:** {'sim' if caso.get('segredo_justica') else 'não'}",
        f"**Gates:** G1 {_fmt_gate(gates.get('G1') or {})} · "
        f"G2 {_fmt_gate(gates.get('G2') or {})} · G3 {_fmt_gate(gates.get('G3') or {})}",
        "",
        "## Próximos prazos",
    ]
    if prazos:
        for p in prazos[:3]:
            corpo.append(f"- {p.get('id')} — **{p.get('data')}** "
                         f"({p.get('criticidade')}): {p.get('descricao')}")
    else:
        corpo.append("- Nenhum prazo registrado.")

    corpo += ["", "## Pendências críticas abertas"]
    if pend_criticas:
        for p in pend_criticas:
            bloqueia = ", ".join(str(b) for b in (p.get("bloqueia") or [])) or "—"
            corpo.append(f"- {p.get('id')} ({p.get('responsavel')}): "
                         f"{p.get('descricao')} — bloqueia {bloqueia}")
    else:
        corpo.append("- Nenhuma.")

    abertas = soj.pendencias_abertas(dados)
    corpo += [
        "",
        "## Números do caso",
        f"- Partes: {len(dados.get('partes') or [])} · "
        f"Fatos: {len(fatos)} (provados {contagem['provado']} / "
        f"alegados {contagem['alegado']} / controversos {contagem['controverso']}) · "
        f"Provas: {len(dados.get('provas') or [])} · "
        f"Pedidos: {len(dados.get('pedidos') or [])} · "
        f"Pendências abertas: {len(abertas)}",
        "",
        "## Últimas entradas do diário",
    ]
    if entradas:
        for e in entradas[-5:][::-1]:
            primeira = (e["corpo"].splitlines() or [""])[0]
            corpo.append(f"- #{e['num']:03d} | {e['datahora']} | {e['tipo']} — {primeira}")
    else:
        corpo.append("- (diário vazio)")

    corpo += ["", "_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(fm + corpo)


# --------------------------------------------------------- rastreabilidade
def _view_rastreabilidade(pasta, dados):
    minuta = soj.minuta_atual(pasta)
    tags = soj.tags_da_minuta(minuta)
    fatos = dados.get("fatos") or []
    provas = dados.get("provas") or []
    pedidos = dados.get("pedidos") or []
    ids_fatos = {str(f.get("id")) for f in fatos}
    ids_provas = {str(p.get("id")) for p in provas}
    ids_pedidos = {str(p.get("id")) for p in pedidos}

    linhas_por_fato = {}
    for t in tags:
        for f in t["fatos"]:
            linhas_por_fato.setdefault(f, []).append(t["linha"])

    tags_por_pedido = {}
    for t in tags:
        for pd in t["pedidos"]:
            tags_por_pedido.setdefault(pd, []).append(t["linha"])

    out = [
        "# RASTREABILIDADE — fato × prova × pedido × parágrafo × fundamento",
        "",
        f"Minuta lida: {minuta.name if minuta else 'nenhuma minuta ainda'}",
        "",
        "| Fato | Status | Provas | Pedidos | Minuta (linhas) |",
        "|---|---|---|---|---|",
    ]
    for f in fatos:
        fid = str(f.get("id"))
        provas_f = ", ".join(str(x) for x in (f.get("provas") or [])) or "—"
        peds = [str(p.get("id")) for p in pedidos
                if fid in [str(x) for x in (p.get("fatos") or [])]]
        linhas = ", ".join(str(n) for n in linhas_por_fato.get(fid, [])) or "—"
        out.append(f"| {fid} | {f.get('status')} | {provas_f} | "
                   f"{', '.join(peds) or '—'} | {linhas} |")
    if not fatos:
        out.append("| (nenhum fato registrado) | | | | |")

    out += ["", "## Pedidos", "",
            "| Pedido | Tipo | Fatos | Fundamentos | Tags na minuta |",
            "|---|---|---|---|---|"]
    for p in pedidos:
        pid = str(p.get("id"))
        out.append(f"| {pid} | {p.get('tipo')} | "
                   f"{', '.join(str(x) for x in (p.get('fatos') or [])) or '—'} | "
                   f"{', '.join(str(x) for x in (p.get('fundamentos') or [])) or '—'} | "
                   f"{len(tags_por_pedido.get(pid, []))} |")
    if not pedidos:
        out.append("| (nenhum pedido registrado) | | | | |")

    alertas = []
    for f in fatos:
        sem_prova = not (f.get("provas") or [])
        sem_pend = not (f.get("pendencias") or [])
        sem_just = not f.get("justificativa")
        if sem_prova and sem_pend and sem_just:
            alertas.append(f"- {f.get('id')} ({f.get('status')}) sem prova, "
                           "sem pendência e sem justificativa.")
    for p in pedidos:
        if minuta and not tags_por_pedido.get(str(p.get("id"))):
            alertas.append(f"- {p.get('id')} sem nenhuma tag na minuta.")
    for t in tags:
        for fid in t["fatos"]:
            if fid not in ids_fatos:
                alertas.append(f"- Tag na linha {t['linha']} cita fato inexistente: {fid}")
        for pv in t["provas"]:
            if pv not in ids_provas:
                alertas.append(f"- Tag na linha {t['linha']} cita prova inexistente: {pv}")
        for pd in t["pedidos"]:
            if pd not in ids_pedidos:
                alertas.append(f"- Tag na linha {t['linha']} cita pedido inexistente: {pd}")

    out += ["", "## Alertas de cobertura", ""]
    out += alertas if alertas else ["- Nenhum alerta."]
    out += ["", "_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(out)


# ------------------------------------------------------------ rol de docs
def _view_rol(dados):
    provas = dados.get("provas") or []

    def chave(p):
        m = re.search(r"DOC-(\d+)", str(p.get("doc", "")))
        return int(m.group(1)) if m else 999

    out = ["# ROL DE DOCUMENTOS", "",
           "| Nº | Arquivo | O que prova | Força | Original |",
           "|---|---|---|---|---|"]
    for p in sorted(provas, key=chave):
        doc = str(p.get("doc", "")).replace("01_documentos/", "")
        out.append(f"| {p.get('id')} | {doc} | {p.get('o_que_prova')} | "
                   f"{p.get('forca')} | {str(p.get('original', '')).replace('00_originais/', '')} |")
    if not provas:
        out.append("| (nenhum documento registrado) | | | | |")
    out += ["", "_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(out)


# --------------------------------------------------- checklist do cliente
def _view_checklist_cliente(nome, dados):
    pendentes = [p for p in soj.pendencias_abertas(dados)
                 if str(p.get("responsavel")) == "cliente"]
    ordem = {p: i for i, p in enumerate(PRIORIDADES)}
    pendentes.sort(key=lambda p: ordem.get(str(p.get("prioridade")), 9))

    primeiro_nome = nome.title()
    for parte in (dados.get("partes") or []):
        papel = str(parte.get("papel", ""))
        if "autor" in papel or "representante" in papel:
            primeiro_nome = str(parte.get("nome", nome)).split()[0].title()
            break

    out = ["# CHECKLIST DO CLIENTE — pronto para WhatsApp", "",
           "Gerado das pendências abertas com responsável = cliente. "
           "Copie o bloco entre as linhas:", "",
           "```", ]
    if pendentes:
        out.append(f"Olá, {primeiro_nome}! Tudo bem? Para avançarmos com o seu caso, "
                   "preciso que você me envie:")
        out.append("")
        for i, p in enumerate(pendentes, 1):
            texto = p.get("mensagem_cliente") or p.get("descricao")
            out.append(f"{i}. {texto}")
        out += ["", "Pode mandar foto ou PDF por aqui mesmo. "
                    "Qualquer dúvida, me chame!"]
    else:
        out.append(f"Olá, {primeiro_nome}! Por enquanto não falta nenhum documento "
                   "seu — assim que houver novidade eu aviso.")
    out += ["```", "", "_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(out)


# ------------------------------------------------------------- pendências
def _view_pendencias(dados):
    todas = dados.get("pendencias") or []
    out = ["# PENDÊNCIAS", ""]
    abertas = [p for p in todas if soj.pendencia_aberta(p)]
    for prio in PRIORIDADES:
        grupo = [p for p in abertas if str(p.get("prioridade")) == prio]
        if not grupo:
            continue
        out.append(f"## {prio.upper()}")
        for p in grupo:
            bloqueia = ", ".join(str(b) for b in (p.get("bloqueia") or [])) or "nada"
            out.append(f"- **{p.get('id')}** ({p.get('responsavel')}): "
                       f"{p.get('descricao')} — bloqueia: {bloqueia}")
        out.append("")
    if not abertas:
        out += ["Nenhuma pendência aberta.", ""]
    resolvidas = [p for p in todas if not soj.pendencia_aberta(p)]
    if resolvidas:
        out.append("## Resolvidas")
        for p in resolvidas:
            out.append(f"- {p.get('id')}: {p.get('descricao')} "
                       f"(resolvida em {p.get('resolvida_em', '?')})")
        out.append("")
    out += ["_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(out)


# ------------------------------------------------------ resumo de decisões
def _view_resumo_decisoes(entradas):
    decisoes = [e for e in entradas if e["tipo"] == "DECISAO_SISTEMA"]
    ratif_e_vetos = [e for e in entradas
                     if e["tipo"] in ("RATIFICACAO", "DECISAO_ADVOGADO")]

    def campo(corpo, padrao):
        m = re.search(padrao, corpo, re.IGNORECASE)
        return m.group(1) if m else "?"

    out = ["# RESUMO DE DECISÕES — folha de ratificação (1 página)", "",
           "Decisões DECISAO_SISTEMA do DIARIO (D11). Para ratificar em bloco, "
           "registre uma entrada RATIFICACAO no DIARIO citando os números; para "
           "vetar, uma DECISAO_ADVOGADO citando o número vetado.", "",
           "| # | Data | Decisão | Tier | Confiança | Situação |",
           "|---|---|---|---|---|---|"]
    for d in decisoes:
        primeira = (d["corpo"].splitlines() or [""])[0]
        tier = "B" if re.search(r"tier\s*b", d["corpo"], re.IGNORECASE) else "A"
        conf = campo(d["corpo"], r"confian[cç]a:\s*(\w+)")
        ref = f"#{d['num']:03d}"
        situacao = "aguardando ratificação"
        for r in ratif_e_vetos:
            if r["num"] > d["num"] and (ref in r["corpo"] or "em bloco" in r["corpo"].lower()):
                situacao = ("vetada/ajustada" if r["tipo"] == "DECISAO_ADVOGADO"
                            else "ratificada") + f" (#{r['num']:03d})"
        out.append(f"| {ref} | {d['datahora']} | {primeira} | {tier} | {conf} | {situacao} |")
    if not decisoes:
        out.append("| (nenhuma decisão do sistema registrada ainda) | | | | | |")
    out += ["", "_Gerado por gerar_views.py — não editar._", ""]
    return "\n".join(out)


# ---------------------------------------------------------------- PAINEL
def _radar_de_prazos():
    """Seção 'PRAZOS NO RADAR' do painel (vigia de prazos — Adendo A1)."""
    linhas = ["## ⚠️ PRAZOS NO RADAR (vencidos ou a 7 dias)", ""]
    achados = 0
    if soj.CASOS.exists():
        for pasta in sorted(soj.CASOS.iterdir()):
            if not (pasta / "CASO.yaml").exists():
                continue
            dados = soj.load_caso(pasta)
            for prazo, dias in soj.prazos_em_alerta(dados):
                situacao = (f"**VENCIDO há {-dias} dia(s)**" if dias < 0
                            else f"vence em **{dias} dia(s)**")
                linhas.append(f"- 🔴 **{pasta.name}** · {prazo.get('id')} · "
                              f"{prazo.get('data')} · {situacao} "
                              f"({prazo.get('criticidade')}): {prazo.get('descricao')}")
                achados += 1
    if achados == 0:
        linhas.append("- Nenhum. Tudo em dia.")
    linhas.append("")
    return linhas


def atualizar_painel():
    linhas = ["# PAINEL DO ESCRITÓRIO", "",
              f"Gerado em {soj.agora()} por gerar_views.py — não editar. "
              "Fonte: frontmatter dos STATUS.md de cada caso.", ""]
    linhas += _radar_de_prazos()
    linhas += [
              "| Cliente | Caso | Título | Fase | G1 | G2 | G3 | Próximo prazo | Pend. críticas |",
              "|---|---|---|---|---|---|---|---|---|"]
    casos = 0
    if soj.CASOS.exists():
        for pasta in sorted(soj.CASOS.iterdir()):
            status = pasta / "_views" / "STATUS.md"
            if not status.exists():
                continue
            fm = {}
            dentro = False
            for linha in status.read_text(encoding="utf-8").splitlines():
                if linha.strip() == "---":
                    if dentro:
                        break
                    dentro = True
                    continue
                if dentro and ":" in linha:
                    k, v = linha.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            linhas.append(
                f"| {fm.get('cliente', pasta.name)} | {fm.get('caso_id', '?')} | "
                f"{fm.get('titulo', '?')} | {fm.get('fase', '?')} | {fm.get('g1', '?')} | "
                f"{fm.get('g2', '?')} | {fm.get('g3', '?')} | "
                f"{fm.get('proximo_prazo') or '—'} | "
                f"{fm.get('pendencias_criticas_abertas', '0')} |")
            casos += 1
    if casos == 0:
        linhas.append("| (nenhum caso ainda) | | | | | | | | |")
    linhas.append("")
    (soj.ROOT / "PAINEL.md").write_text("\n".join(linhas), encoding="utf-8", newline="\n")


# ----------------------------------------------------------------- driver
def gerar_views(nome):
    """Regenera todas as views de um caso + o painel. Devolve a pasta _views."""
    pasta = soj.caso_dir(nome)
    dados = soj.load_caso(pasta)
    entradas = soj.parse_diario(pasta)
    views = pasta / "_views"
    views.mkdir(exist_ok=True)

    _escrever(views, "STATUS.md", _view_status(nome, pasta, dados, entradas))
    _escrever(views, "rastreabilidade.md", _view_rastreabilidade(pasta, dados))
    _escrever(views, "rol_documentos.md", _view_rol(dados))
    _escrever(views, "checklist_cliente.md", _view_checklist_cliente(nome, dados))
    _escrever(views, "pendencias.md", _view_pendencias(dados))
    _escrever(views, "resumo_decisoes.md", _view_resumo_decisoes(entradas))
    atualizar_painel()
    return views


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Regenera as views (SOJ).")
    ap.add_argument("cliente", nargs="?")
    ap.add_argument("--todos", action="store_true")
    args = ap.parse_args()

    if args.todos:
        gerados = []
        for pasta in sorted(soj.CASOS.iterdir()) if soj.CASOS.exists() else []:
            if (pasta / "CASO.yaml").exists():
                gerar_views(pasta.name)
                gerados.append(pasta.name)
        atualizar_painel()
        print(f"[OK] Views regeneradas para {len(gerados)} caso(s): "
              f"{', '.join(gerados) or 'nenhum'} + PAINEL.md")
    elif args.cliente:
        gerar_views(args.cliente)
        print(f"[OK] Views de {args.cliente} regeneradas + PAINEL.md atualizado.")
    else:
        ap.error("informe o CLIENTE ou use --todos")


if __name__ == "__main__":
    main()
