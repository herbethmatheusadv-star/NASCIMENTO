# -*- coding: utf-8 -*-
"""
gate_check.py — executa os gates G1/G2/G3 (blueprint, seções 6 e 1/D8).
Gate reprovado = etapa seguinte BLOQUEADA. Todo gate: relatório em _views/,
entrada GATE no DIARIO e commit automático no git (D2) — aprovado ou não.

Os itens objetivos são verificados aqui; os itens de juízo (qualidade da
estratégia, revisão da peça) são verificados por convenções registradas no
DIARIO — ver ESCRITORIO/MODELOS/DIARIO.formato.md, "Convenções que os gates leem".

Uso:
  python gate_check.py CLIENTE G1|G2|G3
Sai com código 0 se aprovado, 2 se reprovado.
"""
import argparse
import datetime
import re
import sys

import soj_lib as soj

# ------------------------------------------------------------------ helpers

def _tem_entrada(entradas, tipos=None, contendo=None):
    for e in entradas:
        if tipos and e["tipo"] not in tipos:
            continue
        if contendo and contendo.lower() not in soj.normaliza(e["corpo"]):
            continue
        return True
    return False


def _pendencias_refs_da_parte(parte):
    """Procura, em qualquer nível da parte, campos 'pendencia: PEN##'."""
    refs = []

    def anda(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if str(k) == "pendencia":
                    refs.append(str(v))
                else:
                    anda(v)
        elif isinstance(obj, list):
            for x in obj:
                anda(x)

    anda(parte)
    return refs


def _data(valor):
    """Converte campo YAML (date ou string) para datetime.date, ou None."""
    if isinstance(valor, datetime.date):
        return valor
    try:
        return datetime.date.fromisoformat(str(valor))
    except Exception:
        return None


# ------------------------------------------------------------------ G1
def checar_g1(pasta, dados, entradas):
    itens = []
    provas = dados.get("provas") or []
    docs_dir = pasta / "01_documentos"
    arquivos = sorted(a.name for a in docs_dir.iterdir() if a.is_file()) \
        if docs_dir.exists() else []

    # 1. originais preservados + todo doc registrado como P## com original
    problemas = []
    registrados = {str(p.get("doc", "")).replace("01_documentos/", "") for p in provas}
    for a in arquivos:
        if a not in registrados:
            problemas.append(f"{a} esta em 01_documentos/ mas nao registrado como prova")
    for p in provas:
        orig = str(p.get("original", ""))
        if not orig:
            problemas.append(f"{p.get('id')} sem campo 'original'")
        elif not (pasta / orig).exists():
            problemas.append(f"{p.get('id')}: original nao encontrado ({orig})")
        doc = str(p.get("doc", ""))
        if doc and not (pasta / doc).exists():
            problemas.append(f"{p.get('id')}: copia nao encontrada ({doc})")
    if not provas:
        problemas.append("nenhum documento/prova registrado")
    itens.append(("Originais preservados e documentos registrados (P## com original)",
                  not problemas, "; ".join(problemas)))

    # 2. partes com qualificacao completa OU pendencia aberta
    problemas = []
    partes = dados.get("partes") or []
    if not partes:
        problemas.append("nenhuma parte registrada")
    for parte in partes:
        completa = soj.normaliza(parte.get("qualificacao", "")) == "completa"
        refs = _pendencias_refs_da_parte(parte)
        refs_validas = [r for r in refs
                        if soj.por_id(dados.get("pendencias"), r) is not None]
        if not completa and not refs_validas:
            problemas.append(f"{parte.get('id')} sem qualificacao completa e sem "
                             "pendencia apontando o que falta")
    itens.append(("Toda parte com qualificacao completa OU pendencia aberta",
                  not problemas, "; ".join(problemas)))

    # 3. fatos com status honesto
    problemas = []
    fatos = dados.get("fatos") or []
    if not fatos:
        problemas.append("nenhum fato registrado")
    for f in fatos:
        s = str(f.get("status", ""))
        if s not in ("provado", "alegado", "controverso"):
            problemas.append(f"{f.get('id')} com status invalido: '{s}'")
        if s == "provado" and not (f.get("provas") or []):
            problemas.append(f"{f.get('id')} marcado 'provado' sem nenhuma prova")
    itens.append(("Fatos essenciais com status honesto (provado/alegado/controverso)",
                  not problemas, "; ".join(problemas)))

    # 4. prazos identificados (ou NOTA "SEM PRAZOS" justificando)
    ok = bool(dados.get("prazos")) or _tem_entrada(entradas, ["NOTA"], "sem prazos")
    itens.append(("Prazos identificados (PZ##) ou NOTA 'SEM PRAZOS' no DIARIO",
                  ok, "" if ok else "nenhum prazo registrado e nenhuma justificativa"))

    # 5. pendencias com responsavel; criticas dizem o que bloqueiam
    problemas = []
    for p in (dados.get("pendencias") or []):
        if str(p.get("responsavel")) not in ("cliente", "advogado", "terceiro"):
            problemas.append(f"{p.get('id')} sem responsavel valido")
        if str(p.get("prioridade")) == "critica" and not (p.get("bloqueia") or []):
            problemas.append(f"{p.get('id')} critica sem campo 'bloqueia'")
    itens.append(("Pendencias com responsavel; criticas com 'bloqueia'",
                  not problemas, "; ".join(problemas)))

    # 6. complexidade classificada e modulo definido
    caso = dados["caso"]
    ok = (str(caso.get("complexidade")) in ("simples", "padrao", "complexo")
          and str(caso.get("modulo", "")) not in ("", "a_definir", "None"))
    itens.append(("Complexidade classificada (D9) e modulo definido",
                  ok, "" if ok else f"complexidade='{caso.get('complexidade')}', "
                                    f"modulo='{caso.get('modulo')}'"))

    # 7. checklist do cliente gerado e enviado
    view_ok = (pasta / "_views" / "checklist_cliente.md").exists()
    envio_ok = _tem_entrada(entradas, ["CONTATO_CLIENTE"], "checklist")
    detalhe = []
    if not view_ok:
        detalhe.append("view checklist_cliente.md nao gerada")
    if not envio_ok:
        detalhe.append("sem entrada CONTATO_CLIENTE contendo 'checklist' no DIARIO")
    itens.append(("Checklist do cliente gerado e enviado",
                  view_ok and envio_ok, "; ".join(detalhe)))
    return itens


# ------------------------------------------------------------------ G2
def checar_g2(pasta, dados, entradas):
    itens = []

    # 1. ESTRATEGIA.md completo
    est = pasta / "ESTRATEGIA.md"
    texto = soj.normaliza(est.read_text(encoding="utf-8")) if est.exists() else ""
    secoes = ["diagn", "estrat", "simula", "juiz"]
    faltam = [s for s in secoes if s not in texto]
    preenchida = est.exists() and "(a preencher" not in texto and len(texto) > 800
    ok = preenchida and not faltam
    detalhe = ("ESTRATEGIA.md inexistente" if not est.exists() else
               "ainda com marcadores '(a preencher)' ou curta demais" if not preenchida
               else f"secoes ausentes: {', '.join(faltam)}")
    itens.append(("ESTRATEGIA.md completo (diagnostico, estrategia, simulacao "
                  "adversaria, juiz rigoroso)", ok, "" if ok else detalhe))

    # 2. decisoes da arvore tomadas e fundamentadas (DECISAO_SISTEMA)
    decisoes = [e for e in entradas if e["tipo"] == "DECISAO_SISTEMA"]
    problemas = []
    if not decisoes:
        problemas.append("nenhuma DECISAO_SISTEMA no DIARIO")
    for d in decisoes:
        corpo = soj.normaliza(d["corpo"])
        for exigido in ("fundamento", "alternativa", "confianca"):
            if exigido not in corpo.replace("ç", "c"):
                problemas.append(f"#{d['num']:03d} sem campo '{exigido}'")
    itens.append(("Decisoes da arvore tomadas com fundamento, alternativa "
                  "descartada e confianca (D11)", not problemas, "; ".join(problemas)))

    # 3. ratificacao em bloco + 'ok' expresso nas Tier B
    problemas = []
    ratificacoes = [e for e in entradas if e["tipo"] == "RATIFICACAO"]
    if not ratificacoes:
        problemas.append("nenhuma entrada RATIFICACAO no DIARIO")
    for d in decisoes:
        if re.search(r"tier\s*b", d["corpo"], re.IGNORECASE):
            ref = f"#{d['num']:03d}"
            respondida = any(e["num"] > d["num"] and ref in e["corpo"]
                             for e in entradas
                             if e["tipo"] in ("DECISAO_ADVOGADO", "RATIFICACAO"))
            if not respondida:
                problemas.append(f"decisao Tier B {ref} sem 'ok' expresso "
                                 "(DECISAO_ADVOGADO/RATIFICACAO citando o numero)")
    itens.append(("Ratificacao em bloco registrada; Tier B com 'ok' expresso",
                  not problemas, "; ".join(problemas)))

    # 4. pedidos ancorados em fatos; fatos sem prova tem pendencia/justificativa
    problemas = []
    pedidos = dados.get("pedidos") or []
    if not pedidos:
        problemas.append("nenhum pedido registrado")
    for p in pedidos:
        fatos_ref = [str(x) for x in (p.get("fatos") or [])]
        if not fatos_ref:
            problemas.append(f"{p.get('id')} sem nenhum fato vinculado")
        for fid in fatos_ref:
            f = soj.por_id(dados.get("fatos"), fid)
            if f is None:
                problemas.append(f"{p.get('id')} cita fato inexistente {fid}")
            elif not (f.get("provas") or []) and not (f.get("pendencias") or []) \
                    and not f.get("justificativa"):
                problemas.append(f"fato {fid} (de {p.get('id')}) sem prova, sem "
                                 "pendencia e sem justificativa estrategica")
    itens.append(("Todo pedido com >=1 fato; fatos-chave sem prova tem pendencia "
                  "ou justificativa", not problemas, "; ".join(problemas)))

    # 5. nenhuma pendencia bloqueando o G2
    travas = soj.pendencias_abertas(dados, bloqueia="G2")
    itens.append(("Nenhuma pendencia aberta com bloqueia: [G2]", not travas,
                  ", ".join(str(p.get("id")) for p in travas)))

    # 6. riscos com contramedida ou aceitacao expressa
    tem_riscos = "risco" in texto
    tem_resposta = ("contramedida" in texto
                    or _tem_entrada(entradas, ["DECISAO_ADVOGADO"], "aceito o risco"))
    ok = tem_riscos and tem_resposta
    itens.append(("Riscos da simulacao com contramedida na estrategia ou aceitacao "
                  "expressa no DIARIO", ok,
                  "" if ok else "secao de riscos ausente ou sem contramedida/aceitacao"))
    return itens


# ------------------------------------------------------------------ G3
def checar_g3(pasta, dados, entradas):
    itens = []
    minuta = soj.minuta_atual(pasta)
    texto_minuta = minuta.read_text(encoding="utf-8") if minuta else ""
    tags = soj.tags_da_minuta(minuta)

    # 1. zero marcadores [VALIDAR]/[PESQUISAR]
    marcadores = re.findall(r"\[(?:VALIDAR|PESQUISAR)[^\]]*\]", texto_minuta,
                            re.IGNORECASE)
    ok = minuta is not None and not marcadores
    itens.append(("Zero marcadores [VALIDAR]/[PESQUISAR] na minuta", ok,
                  "minuta inexistente" if minuta is None else
                  f"{len(marcadores)} marcador(es): {', '.join(marcadores[:5])}"))

    # 2. tags SOJ validas (fatos e provas existentes)
    problemas = []
    ids_fatos = {str(f.get("id")) for f in (dados.get("fatos") or [])}
    ids_provas = {str(p.get("id")) for p in (dados.get("provas") or [])}
    ids_pedidos = {str(p.get("id")) for p in (dados.get("pedidos") or [])}
    if not tags:
        problemas.append("minuta sem nenhuma tag SOJ")
    for t in tags:
        for fid in t["fatos"]:
            if fid not in ids_fatos:
                problemas.append(f"linha {t['linha']}: fato inexistente {fid}")
        for pv in t["provas"]:
            if pv not in ids_provas:
                problemas.append(f"linha {t['linha']}: prova inexistente {pv}")
        for pd in t["pedidos"]:
            if pd not in ids_pedidos:
                problemas.append(f"linha {t['linha']}: pedido inexistente {pd}")
    itens.append(("Tags SOJ validas em toda a minuta (fato/prova/pedido existentes)",
                  not problemas, "; ".join(problemas[:8])))

    # 3. todo PED fecha o circuito pedido<->fato<->prova<->paragrafo<->fundamento
    problemas = []
    peds_com_tag = set()
    for t in tags:
        peds_com_tag.update(t["pedidos"])
    for p in (dados.get("pedidos") or []):
        pid = str(p.get("id"))
        excecao = any(pid in e["corpo"] and "exce" in soj.normaliza(e["corpo"])
                      for e in entradas)
        if excecao:
            continue
        if not (p.get("fatos") or []):
            problemas.append(f"{pid} sem fato")
        for fid in [str(x) for x in (p.get("fatos") or [])]:
            f = soj.por_id(dados.get("fatos"), fid)
            if f is not None and not (f.get("provas") or []):
                problemas.append(f"{pid}: fato {fid} sem prova")
        if not (p.get("fundamentos") or []):
            problemas.append(f"{pid} sem fundamento")
        if pid not in peds_com_tag:
            problemas.append(f"{pid} sem paragrafo na minuta (nenhuma tag)")
    itens.append(("Todo pedido fecha o circuito (fato-prova-paragrafo-fundamento) "
                  "ou tem excecao no DIARIO", not problemas, "; ".join(problemas[:8])))

    # 4. fundamentos verificados dentro da validade; nucleo rechecado na vespera
    problemas = []
    citados = dados.get("fundamentos_citados") or []
    usados = set()
    for p in (dados.get("pedidos") or []):
        usados.update(soj.normaliza_ref(r) for r in (p.get("fundamentos") or []))
    for t in tags:
        usados.update(soj.normaliza_ref(r) for r in t["fundamentos"])
    mapa = {soj.normaliza_ref(c.get("ref")): c for c in citados}
    area = str(dados["caso"].get("area", ""))
    arq_base = soj.ESCRITORIO / "BASE_LEGAL" / f"{area}.md"
    base = soj.normaliza_ref(arq_base.read_text(encoding="utf-8")) \
        if arq_base.exists() else ""
    for ref in sorted(usados):
        c = mapa.get(ref)
        if c is None:
            problemas.append(f"{ref} usado mas ausente de fundamentos_citados")
            continue
        dt = _data(c.get("verificado_em"))
        if dt is None:
            problemas.append(f"{c.get('ref')} sem data de verificacao")
            continue
        validade = int(c.get("validade_dias")
                       or (30 if "alteracao" in soj.normaliza(c.get("status", "")) else 90))
        idade = (soj.hoje() - dt).days
        if idade > validade:
            problemas.append(f"{c.get('ref')} vencido ({idade}d > {validade}d)")
        if c.get("nucleo") and idade > 2:
            problemas.append(f"{c.get('ref')} e nucleo: rechecagem na vespera "
                             f"obrigatoria (verificado ha {idade}d)")
        if base and soj.normaliza_ref(c.get("ref")) not in base:
            problemas.append(f"{c.get('ref')} sem verbete em BASE_LEGAL/{area}.md")
    if not usados:
        problemas.append("nenhum fundamento citado nos pedidos/tags")
    itens.append(("Fundamentos na BASE_LEGAL, dentro da validade; nucleo rechecado "
                  "na vespera", not problemas, "; ".join(problemas[:8])))

    # 5. checklist anti-erro fatal do modulo
    # (so vale registro em entrada humana — NOTA/DECISAO_ADVOGADO/RATIFICACAO;
    #  entradas GATE sao excluidas para o texto de uma reprovacao anterior
    #  nao satisfazer a checagem seguinte)
    TIPOS_HUMANOS = ["NOTA", "DECISAO_ADVOGADO", "RATIFICACAO"]
    modulo = str(dados["caso"].get("modulo", ""))
    area_mod = modulo.split("/")[0] if "/" in modulo else modulo
    arq_anti = soj.ESCRITORIO / "MODULOS" / area_mod / "anti_erro_fatal.md"
    ok = _tem_entrada(entradas, TIPOS_HUMANOS, "anti-erro")
    if arq_anti.exists() and "(a completar" not in arq_anti.read_text(encoding="utf-8") \
            and "esqueleto" not in soj.normaliza(arq_anti.read_text(encoding="utf-8")):
        itens.append(("Checklist anti-erro fatal do modulo executado", ok,
                      "" if ok else "sem entrada no DIARIO registrando a execucao"))
    else:
        itens.append(("Checklist anti-erro fatal (modulo ainda em construcao — "
                      "rodar o generico e registrar 'anti-erro' no DIARIO)", ok,
                      "" if ok else "sem entrada no DIARIO registrando a revisao anti-erro"))

    # 6. rol = arquivos da pasta = referencias DOC-NN na peca
    problemas = []
    docs_dir = pasta / "01_documentos"
    arquivos = {a.name for a in docs_dir.iterdir() if a.is_file()} \
        if docs_dir.exists() else set()
    registrados = {str(p.get("doc", "")).replace("01_documentos/", "")
                   for p in (dados.get("provas") or [])}
    for a in sorted(arquivos - registrados):
        problemas.append(f"arquivo sem registro: {a}")
    for r in sorted(registrados - arquivos):
        problemas.append(f"registrado sem arquivo: {r}")
    docs_citados = set(re.findall(r"DOC-\d+", texto_minuta))
    docs_existentes = {m.group(0) for a in arquivos
                       if (m := re.match(r"DOC-\d+", a))}
    for d in sorted(docs_citados - docs_existentes):
        problemas.append(f"minuta cita {d} que nao existe na pasta")
    itens.append(("Rol = arquivos da pasta = referencias DOC-NN na peca",
                  not problemas, "; ".join(problemas[:8])))

    # 7. nenhuma pendencia bloqueando o G3
    travas = soj.pendencias_abertas(dados, bloqueia="G3")
    itens.append(("Nenhuma pendencia aberta com bloqueia: [G3]", not travas,
                  ", ".join(str(p.get("id")) for p in travas)))

    # 8. conferencia FINAL de valores, datas, nomes e CPFs registrada
    # (exige 'conferencia' E 'valores' na mesma entrada, para nao confundir com
    #  conferencias parciais historicas — convencao no DIARIO.formato.md)
    ok = any(e["tipo"] in ("NOTA", "DECISAO_ADVOGADO")
             and "conferencia" in soj.normaliza(e["corpo"])
             and "valores" in soj.normaliza(e["corpo"])
             for e in entradas)
    itens.append(("Conferencia final de valores/datas/nomes/CPFs registrada no "
                  "DIARIO (entrada com 'CONFERENCIA' + 'valores')", ok,
                  "" if ok else "sem entrada de conferencia final"))

    # 9. revisao humana integral declarada pelo advogado
    ok = _tem_entrada(entradas, ["DECISAO_ADVOGADO", "RATIFICACAO"],
                      "revisao humana integral")
    itens.append(("Advogado declarou revisao humana integral da peca (DIARIO)",
                  ok, "" if ok else "sem declaracao de revisao humana integral"))
    return itens


# ------------------------------------------------------------------ driver
CHECKS = {"G1": checar_g1, "G2": checar_g2, "G3": checar_g3}
PRE_REQUISITO = {"G2": "G1", "G3": "G2"}
FASE_APOS = {"G1": "E2_estrategia", "G2": "E3_minuta", "G3": "E4_protocolo"}


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Executa os gates do SOJ.")
    ap.add_argument("cliente")
    ap.add_argument("gate", choices=["G1", "G2", "G3"])
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)
    entradas = soj.parse_diario(pasta)

    # bloqueio de sequencia: G2 exige G1 aprovado; G3 exige G2 aprovado
    anterior = PRE_REQUISITO.get(args.gate)
    if anterior:
        st = ((dados["caso"].get("gates") or {}).get(anterior) or {}).get("status")
        if str(st) != "aprovado":
            sys.exit(f"[BLOQUEADO] O {args.gate} so roda com o {anterior} aprovado "
                     f"(status atual do {anterior}: {st}).")

    itens = CHECKS[args.gate](pasta, dados, entradas)
    aprovados = sum(1 for _, ok, _ in itens if ok)
    total = len(itens)
    aprovado = aprovados == total
    resultado = "APROVADO" if aprovado else "REPROVADO"
    data = str(soj.hoje())

    # relatorio em _views/
    rel = [f"# GATE {args.gate} — {resultado} ({aprovados}/{total})",
           f"Caso: {args.cliente} ({dados['caso'].get('id')}) · Executado em {soj.agora()}",
           ""]
    for descricao, ok, detalhe in itens:
        rel.append(f"- [{'OK' if ok else 'FALHOU'}] {descricao}")
        if not ok and detalhe:
            rel.append(f"  - Falta: {detalhe}")
    rel += ["", "_Gerado por gate_check.py — nao editar._", ""]
    nome_rel = f"gate_{args.gate}_{data}.md"
    (pasta / "_views").mkdir(exist_ok=True)
    (pasta / "_views" / nome_rel).write_text("\n".join(rel), encoding="utf-8",
                                             newline="\n")

    # entrada no DIARIO
    corpo = f"{args.gate} executado: {resultado}. {aprovados}/{total} itens. " \
            f"Relatorio: _views/{nome_rel}"
    if not aprovado:
        faltas = [d for d, ok, _ in itens if not ok]
        corpo += "\nItens reprovados: " + "; ".join(faltas)
    num = soj.append_diario(pasta, "GATE", corpo)

    # atualiza a fonte da verdade
    gates = dados["caso"].setdefault("gates", {})
    gates[args.gate] = {"status": "aprovado" if aprovado else "reprovado",
                        "data": data, "diario": f"#{num:03d}"}
    if aprovado:
        dados["caso"]["fase"] = FASE_APOS[args.gate]
    soj.save_caso(pasta, dados)

    # regenera views e commita (D2: commit automatico a cada gate)
    import gerar_views
    gerar_views.gerar_views(args.cliente)
    soj.git_commit(f"gate {args.gate} {args.cliente}: {resultado} (DIARIO #{num:03d})")

    print(f"[{resultado}] Gate {args.gate} de {args.cliente}: {aprovados}/{total} itens.")
    for descricao, ok, detalhe in itens:
        print(f"  [{'OK' if ok else 'X '}] {descricao}")
        if not ok and detalhe:
            print(f"       -> {detalhe}")
    print(f"  Relatorio: _views/{nome_rel} · DIARIO #{num:03d} · commit git feito.")
    sys.exit(0 if aprovado else 2)


if __name__ == "__main__":
    main()
