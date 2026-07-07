# -*- coding: utf-8 -*-
"""
importar_caso.py — PORTA DE IMPORTAÇÃO (blueprint v1.10, seção 7).
Caso pré-trabalhado por colaborador (minuta pronta + provas + instrumentais)
entra por ENGENHARIA REVERSA COM CONFIANÇA ZERO:

  1. Inventaria a pasta do colaborador; DEDUPLICA por hash SHA-256
     (mantém o melhor nome; as cópias são lacradas mas não roteadas).
  2. Se houver MAIS DE UMA minuta candidata: PARA antes de tocar em
     qualquer coisa e manda perguntar ao titular (versões da mesma ação
     ou ações distintas?). Reexecutar com --minuta "NOME" após a resposta.
  3. Roteia: provas -> P## (com hash) · INSTRUMENTAIS (procuração
     ASSINADA, RG/CNH, contrato de honorários, hipossuficiência) -> classe
     própria `instrumentais:` na ficha (provam representação, não fato) ·
     rascunho de instrumental em formato editável -> _efemeros.
  4. A minuta vira MINUTA_v01.md (IMPORTADA, com aviso de confiança zero);
     TODA citação de lei detectada é conferida contra a BASE_LEGAL
     (verificada / vencida / REVOGADA / não verificada).
  5. Gera _views/REVISAO_COLABORADOR.md (parte mecânica; as seções de
     juiz rigoroso/adversário/fatos órfãos são preenchidas pelo sistema
     NA MESMA SESSÃO de importação — relatório congelado depois).
  6. DIARIO tipo IMPORTACAO com origem (governança de autoria); decisões
     embutidas na peça viram propostas_colaborador aguardando ratificação
     (o G2 bloqueia enquanto houver proposta pendente).

Uso:
  python importar_caso.py CLIENTE PASTA --colaborador "NOME"
         [--area familia] [--titulo ...] [--comarca ...] [--polo ativo]
         [--segredo] [--probono] [--minuta "ARQUIVO ESCOLHIDO"]
"""
import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import soj_lib as soj

BASE_LEGAL = soj.ESCRITORIO / "BASE_LEGAL"

EXT_EDITAVEL = {".docx", ".doc", ".odt", ".rtf", ".txt", ".md"}
EXT_ASSINAVEL = {".pdf", ".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff"}
EXT_MINUTA = {".docx", ".doc", ".md", ".txt", ".odt"}

INSTRUMENTAL_RE = re.compile(
    r"procura[cç][aã]o|(?:^|[\s_\-])rg(?:[\s_\-]|\.|$)|cnh|identidade|"
    r"honorari|hipossufici|declara[cç][aã]o de pobreza|gratuidade", re.I)
MINUTA_RE = re.compile(
    r"peti[cç][aã]o|pe[cç]a|minuta|inicial|contesta[cç][aã]o|defesa|"
    r"r[eé]plica|recurso|apela[cç][aã]o|agravo|embargos|a[cç][aã]o de", re.I)
TIPOS_INSTRUMENTAL = [
    (re.compile(r"procura[cç][aã]o", re.I), "procuracao"),
    (re.compile(r"(?:^|[\s_\-])rg(?:[\s_\-]|\.|$)|cnh|identidade", re.I), "identidade"),
    (re.compile(r"honorari", re.I), "contrato_honorarios"),
    (re.compile(r"hipossufici|pobreza|gratuidade", re.I), "hipossuficiencia"),
]

# ---------------------------------------------------------------- citações
DIPLOMA_MAP = [
    (re.compile(r"c[oó]digo\s+de\s+processo\s+civil|(?<![A-Za-z])CPC(?![A-Za-z0-9])",
                re.I), "CPC"),
    (re.compile(r"c[oó]digo\s+civil|(?<![A-Za-z])CC(?![A-Za-z0-9])", re.I), "CC"),
    (re.compile(r"constitui[cç][aã]o|(?<![A-Za-z])CF(?![A-Za-z0-9])", re.I), "CF"),
    (re.compile(r"estatuto\s+da\s+crian[cç]a|(?<![A-Za-z])ECA(?![A-Za-z0-9])",
                re.I), "ECA"),
]
CIT_ART_DIPLOMA = re.compile(
    r"art(?:igo)?s?\.?\s*([\d\.]+)\s*(?:(?:a|e)\s*([\d\.]+))?[ºo°]?"
    r"[^,;.\n]{0,20}?\s(?:do|da|de o|de a)?\s*([^,;.\n]{2,60})", re.I)
CIT_LEI_ART = re.compile(
    r"Lei\s+n?[ºo°.\s]*([\d\.]+)(?:\s*/\s*\d{2,4})?\s*,?\s*"
    r"art(?:igo)?s?\.?\s*([\d\.]+)\s*(?:(?:a|e)\s*([\d\.]+))?", re.I)
CIT_ART_LEI = re.compile(
    r"art(?:igo)?s?\.?\s*([\d\.]+)\s*(?:(?:a|e)\s*([\d\.]+))?[ºo°]?\s*"
    r"(?:do|da|de)\s+Lei\s+n?[ºo°.\s]*([\d\.]+)", re.I)


def _num(s):
    return int(re.sub(r"\D", "", s)) if s and re.sub(r"\D", "", s) else None


def carrega_verbetes():
    """[(prefixo, art_lo, art_hi, ref, situacao, vencido_bool)] da BASE_LEGAL."""
    out = []
    hoje = date.today()
    for arq in sorted(BASE_LEGAL.glob("*.md")):
        for bloco in re.split(r"(?m)^## ", arq.read_text(encoding="utf-8"))[1:]:
            titulo = bloco.splitlines()[0].strip()
            ref = titulo.split(" —")[0].split(" -")[0].strip()
            if ":" not in ref:
                continue
            prefixo, _, resto = ref.partition(":")
            m = re.match(r"art(\d+)(?:a(\d+))?", resto.strip(), re.I)
            if not m:
                continue
            lo = int(m.group(1))
            hi = int(m.group(2)) if m.group(2) else lo
            m_sit = re.search(r"\*\*Situa[cç][aã]o:\*\*\s*([^·\n]+)", bloco)
            situacao = m_sit.group(1).strip() if m_sit else "?"
            m_ver = re.search(r"\*\*Verificado em:\*\*\s*(\d{4})-(\d{2})-(\d{2})", bloco)
            m_val = re.search(r"\*\*Validade:\*\*\s*(\d+)\s*dias", bloco)
            vencido = False
            if m_ver and m_val:
                dv = date(int(m_ver.group(1)), int(m_ver.group(2)), int(m_ver.group(3)))
                vencido = (hoje - dv).days > int(m_val.group(1))
            out.append((prefixo.upper(), lo, hi, ref, situacao, vencido))
    return out


def extrai_citacoes(texto):
    """[(trecho, prefixo, art_lo, art_hi)] — heurístico; a revisão semântica
    da sessão cobre o que a regex não pegar (confiança zero dos dois lados)."""
    achadas = []

    def add(trecho, prefixo, a1, a2):
        lo = _num(a1)
        if lo is None or prefixo is None:
            return
        hi = _num(a2) or lo
        item = (trecho.strip()[:90], prefixo, lo, hi)
        if item not in achadas:
            achadas.append(item)

    for m in CIT_LEI_ART.finditer(texto):
        add(m.group(0), "LEI" + re.sub(r"\D", "", m.group(1)), m.group(2), m.group(3))
    for m in CIT_ART_LEI.finditer(texto):
        add(m.group(0), "LEI" + re.sub(r"\D", "", m.group(3)), m.group(1), m.group(2))
    for m in CIT_ART_DIPLOMA.finditer(texto):
        cauda = m.group(3) or ""
        if re.match(r"Lei\b", cauda, re.I):
            continue                       # já coberto pelos padrões de Lei
        prefixo = None
        for rx, sigla in DIPLOMA_MAP:
            if rx.search(cauda):
                prefixo = sigla
                break
        if prefixo:
            add(m.group(0), prefixo, m.group(1), m.group(2))
    return achadas


def confere_citacoes(texto):
    """[(trecho, veredicto, detalhe)] contra os verbetes da BASE_LEGAL."""
    verbetes = carrega_verbetes()
    resultado = []
    for trecho, prefixo, lo, hi in extrai_citacoes(texto):
        matches = [v for v in verbetes
                   if v[0] == prefixo and not (hi < v[1] or lo > v[2])]
        if not matches:
            resultado.append((trecho, "NAO VERIFICADA",
                              "sem verbete na BASE_LEGAL — verificar NA FONTE "
                              "antes de qualquer uso"))
            continue
        for _, _, _, ref, situacao, vencido in matches:
            if "revog" in situacao.lower():
                resultado.append((trecho, "REVOGADA (LEI MORTA)",
                                  f"verbete {ref}: {situacao}"))
            elif vencido:
                resultado.append((trecho, "VENCIDA",
                                  f"verbete {ref} fora da validade — revalidar"))
            else:
                resultado.append((trecho, "verificada", f"verbete {ref}"))
    return resultado


# ---------------------------------------------------------------- utilidades
def texto_da_minuta(arq):
    if arq.suffix.lower() == ".docx":
        try:
            with zipfile.ZipFile(arq) as z:
                xml = z.read("word/document.xml").decode("utf-8", "replace")
            xml = re.sub(r"</w:p>", "\n\n", xml)
            txt = re.sub(r"<[^>]+>", "", xml)
            return (txt.replace("&amp;", "&").replace("&lt;", "<")
                       .replace("&gt;", ">").replace("&quot;", '"'))
        except Exception as e:
            sys.exit(f"[ERRO] Nao consegui extrair texto de {arq.name}: {e}")
    return arq.read_text(encoding="utf-8", errors="replace")


def melhor_nome(arquivos):
    """Entre duplicatas de mesmo hash: o melhor nome e o mais curto
    (o sufixo ' (1)' de copia so faz o nome crescer)."""
    return sorted(arquivos, key=lambda a: (len(a.name), a.name))[0]


def classifica(arq):
    nome, ext = arq.name, arq.suffix.lower()
    if INSTRUMENTAL_RE.search(nome):
        return "rascunho_instrumental" if ext in EXT_EDITAVEL else "instrumental"
    if ext in EXT_MINUTA and MINUTA_RE.search(nome):
        return "minuta"
    return "prova"


def tipo_instrumental(nome):
    for rx, tipo in TIPOS_INSTRUMENTAL:
        if rx.search(nome):
            return tipo
    return "outro"


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Porta de importacao (SOJ v1.10).")
    ap.add_argument("cliente")
    ap.add_argument("pasta_colaborador")
    ap.add_argument("--colaborador", required=True,
                    help='Quem trabalhou o caso (ex.: "DR. FULANO — estagiario")')
    ap.add_argument("--area", default="a_definir")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--comarca", default="a_definir")
    ap.add_argument("--polo", default="ativo", choices=["ativo", "passivo"])
    ap.add_argument("--segredo", action="store_true")
    ap.add_argument("--probono", action="store_true")
    ap.add_argument("--minuta", default=None,
                    help="Nome do arquivo-minuta escolhido pelo titular quando "
                         "houver mais de um candidato (resposta ao PARE)")
    args = ap.parse_args()

    origem_pasta = Path(args.pasta_colaborador)
    if not origem_pasta.is_dir():
        sys.exit(f"[ERRO] Pasta do colaborador nao encontrada: {origem_pasta}")

    # 1. inventario + hash + dedupe (ANTES de criar/tocar qualquer coisa)
    arquivos = sorted(a for a in origem_pasta.rglob("*") if a.is_file())
    if not arquivos:
        sys.exit("[ERRO] Pasta do colaborador vazia.")
    por_hash = {}
    hashes = {}
    for a in arquivos:
        h = soj.sha256_arquivo(a)
        hashes[a] = h
        por_hash.setdefault(h, []).append(a)
    mantidos, duplicatas = [], []
    for h, grupo in por_hash.items():
        best = melhor_nome(grupo)
        mantidos.append(best)
        duplicatas += [(d.name, best.name) for d in grupo if d is not best]
    mantidos.sort(key=lambda a: a.name.lower())

    # 2. classificacao + trava das duas minutas (PARE antes de qualquer efeito)
    rotas = {a: classifica(a) for a in mantidos}
    candidatas = [a for a, r in rotas.items() if r == "minuta"]
    minuta_arq = None
    if len(candidatas) > 1 and not args.minuta:
        print("[PARE] Ha MAIS DE UMA minuta candidata na pasta do colaborador:")
        for c in candidatas:
            print(f"       - {c.name}")
        print("       PERGUNTAR AO TITULAR: sao VERSOES da mesma acao (qual e a")
        print("       atual?) ou ACOES DISTINTAS (importar em casos separados)?")
        print('       Depois: reexecutar com --minuta "NOME DO ARQUIVO".')
        print("       NADA foi criado ou copiado.")
        sys.exit(2)
    if candidatas:
        if args.minuta:
            escolhidas = [c for c in candidatas if c.name == args.minuta]
            if not escolhidas:
                sys.exit(f"[ERRO] --minuta '{args.minuta}' nao esta entre as "
                         f"candidatas: {', '.join(c.name for c in candidatas)}")
            minuta_arq = escolhidas[0]
            for c in candidatas:
                if c is not minuta_arq:
                    rotas[c] = "rascunho_minuta"   # versao preterida -> _efemeros
        else:
            minuta_arq = candidatas[0]

    # 3. caso (cria se nao existir)
    pasta = soj.CASOS / args.cliente.strip()
    if not pasta.exists():
        cmd = [sys.executable, str(Path(__file__).parent / "novo_caso.py"),
               args.cliente, "--area", args.area, "--comarca", args.comarca,
               "--polo", args.polo]
        if args.titulo:
            cmd += ["--titulo", args.titulo]
        if args.segredo:
            cmd.append("--segredo")
        if args.probono:
            cmd.append("--probono")
        r = subprocess.run(cmd, cwd=str(Path(__file__).parent))
        if r.returncode != 0:
            sys.exit("[ERRO] novo_caso.py falhou — importacao abortada.")
    dados = soj.load_caso(pasta)

    # 4. lacre integral (00_originais e a foto fiel: TUDO, inclusive duplicatas)
    slug_colab = soj.slug(args.colaborador)[:30]
    destino_orig = pasta / "00_originais" / f"importacao_{slug_colab}"
    if destino_orig.exists():
        sys.exit(f"[ERRO] {destino_orig} ja existe — nao sobrescrevo originais.")
    destino_orig.mkdir(parents=True)
    for a in arquivos:
        shutil.copy2(a, destino_orig / a.name)

    # 5. roteamento dos mantidos
    efemeros = pasta / "_efemeros" / "importacao"
    linhas_rotas, num_doc = [], soj.proximo_doc_num(dados)
    provas_novas, instrumentais_novos = [], []
    ja = dados.get("instrumentais") or []
    prox_ins = max([int(str(i.get("id", "INS00"))[3:]) for i in ja] or [0]) + 1
    for a in mantidos:
        rota, rel_orig = rotas[a], f"00_originais/importacao_{slug_colab}/{a.name}"
        if rota in ("rascunho_instrumental", "rascunho_minuta"):
            efemeros.mkdir(parents=True, exist_ok=True)
            shutil.copy2(a, efemeros / a.name)
            destino = ("_efemeros/importacao (rascunho de instrumental — nao e "
                       "o assinado)" if rota == "rascunho_instrumental" else
                       "_efemeros/importacao (versao preterida da minuta)")
        elif rota == "instrumental":
            nome_doc = f"DOC-{num_doc:02d}_{soj.slug(a.stem)[:40]}{a.suffix.lower()}"
            shutil.copy2(a, pasta / "01_documentos" / nome_doc)
            instrumentais_novos.append({
                "id": f"INS{prox_ins:02d}", "tipo": tipo_instrumental(a.name),
                "doc": f"01_documentos/{nome_doc}", "original": rel_orig,
                "sha256": hashes[a], "origem": f"colaborador {args.colaborador}"})
            destino = f"instrumental {instrumentais_novos[-1]['id']} ({nome_doc})"
            num_doc += 1
            prox_ins += 1
        elif rota == "prova":
            nome_doc = f"DOC-{num_doc:02d}_{soj.slug(a.stem)[:40]}{a.suffix.lower()}"
            shutil.copy2(a, pasta / "01_documentos" / nome_doc)
            pid = soj.proximo_prova_id(dados)
            soj.lista_de(dados, "provas").append({
                "id": pid, "doc": f"01_documentos/{nome_doc}",
                "original": rel_orig, "sha256": hashes[a],
                "o_que_prova": "(importada do colaborador — revisar na "
                               "engenharia reversa)",
                "forca": "relativa",
                "fragilidade": "importada sem analise propria; forca a "
                               "confirmar na revisao do titular"})
            provas_novas.append(pid)
            destino = f"prova {pid} ({nome_doc})"
            num_doc += 1
        else:  # minuta
            destino = "MINUTA_v01.md (importada)"
        linhas_rotas.append((a.name, rota, destino))
    if instrumentais_novos:
        soj.lista_de(dados, "instrumentais").extend(instrumentais_novos)

    # 6. minuta importada + conferencia de citacoes
    citacoes = []
    if minuta_arq:
        texto = texto_da_minuta(minuta_arq)
        citacoes = confere_citacoes(texto)
        alvo = pasta / "MINUTA_v01.md"
        if alvo.exists():
            sys.exit("[ERRO] MINUTA_v01.md ja existe neste caso — porta de "
                     "importacao e para caso pre-trabalhado NOVO.")
        alvo.write_text(
            "> ⚠️ **MINUTA IMPORTADA — CONFIANÇA ZERO** · origem: colaborador "
            f"{args.colaborador} · importada em {soj.agora()} de "
            f"`{rel_dado(minuta_arq, origem_pasta)}` (hash "
            f"{hashes[minuta_arq][:16]}…)\n"
            "> Nada aqui foi verificado pelo sistema: fatos, pedidos e "
            "citações passam pela engenharia reversa\n"
            "> (ver `_views/REVISAO_COLABORADOR.md`) e pelos gates normais "
            "antes de qualquer uso.\n\n---\n\n"
            + texto.strip() + "\n",
            encoding="utf-8", newline="\n")

    # 7. relatorio de revisao do colaborador (parte mecanica)
    rel = [f"# REVISÃO DO COLABORADOR — {args.colaborador}",
           f"Caso {dados['caso']['id']} · importado em {soj.agora()} pela "
           "porta de importação (blueprint v1.10, §7)",
           "",
           "> Relatório CONGELADO da importação (não se regenera). Parte "
           "mecânica: script.",
           "> Seções semânticas: preenchidas pelo sistema NA SESSÃO de "
           "importação, antes do fechamento.",
           "",
           "## 1. Inventário e rotas (dedupe por SHA-256)", ""]
    rel += [f"- `{n}` → **{r}** · {d}" for n, r, d in linhas_rotas]
    rel += ["", "## 2. Duplicatas eliminadas do roteamento", ""]
    rel += ([f"- `{d}` = cópia exata de `{b}` (mesmo hash; lacrada, não roteada)"
             for d, b in duplicatas] or ["- (nenhuma)"])
    rel += ["", "## 3. Verificação de fontes da minuta (BASE_LEGAL)", ""]
    if citacoes:
        for trecho, veredicto, detalhe in citacoes:
            marca = "🔴" if "REVOGADA" in veredicto else \
                    ("🟡" if veredicto in ("VENCIDA", "NAO VERIFICADA") else "🟢")
            rel.append(f"- {marca} **{veredicto}** — “{trecho}” · {detalhe}")
        rel.append("")
        rel.append("_Detecção heurística: a revisão semântica abaixo cobre o "
                   "que a varredura não pegou._")
    else:
        rel.append("- (nenhuma minuta importada ou nenhuma citação detectada)")
    rel += ["", "## 4. O que está bom (crédito ao colaborador)", "",
            "_(preenchido pelo sistema na sessão de importação)_", "",
            "## 5. Fatos afirmados sem prova (órfãos)", "",
            "_(preenchido pelo sistema na sessão de importação)_", "",
            "## 6. Juiz rigoroso sobre a peça importada", "",
            "_(preenchido pelo sistema na sessão de importação)_", "",
            "## 7. Adversário contra a peça importada", "",
            "_(preenchido pelo sistema na sessão de importação)_", "",
            "## 8. Decisões embutidas → propostas do colaborador", "",
            "_(cada uma vira item em `propostas_colaborador:` aguardando "
            "ratificação — o G2 bloqueia enquanto houver pendente)_", ""]
    (pasta / "_views" / "REVISAO_COLABORADOR.md").write_text(
        "\n".join(rel), encoding="utf-8", newline="\n")

    soj.save_caso(pasta, dados)

    # 8. DIARIO (origem = governanca de autoria)
    corpo = (f"PORTA DE IMPORTACAO: pasta do colaborador {args.colaborador} "
             f"({len(arquivos)} arquivos, todos lacrados com SHA-256 em "
             f"00_originais/importacao_{slug_colab}/). Roteados: "
             f"{len(provas_novas)} prova(s) [{', '.join(provas_novas) or '-'}], "
             f"{len(instrumentais_novos)} instrumental(is) "
             f"[{', '.join(i['id'] for i in instrumentais_novos) or '-'}], "
             f"{len(duplicatas)} duplicata(s) fora do roteamento, "
             f"{sum(1 for _, r, _ in linhas_rotas if r.startswith('rascunho'))} "
             "rascunho(s) em _efemeros. "
             + (f"Minuta '{minuta_arq.name}' importada como MINUTA_v01 "
                "(confianca zero); " if minuta_arq else "Sem minuta; ")
             + "relatorio em _views/REVISAO_COLABORADOR.md. Engenharia reversa "
               "(F##/PED##/propostas do colaborador) segue na sessao.")
    num_d = soj.append_diario(pasta, "IMPORTACAO", corpo,
                              origem=f"colaborador {args.colaborador} "
                                     "(importado pelo sistema)")

    import gerar_views
    gerar_views.gerar_views(args.cliente)

    print(f"[OK] Importacao concluida (DIARIO #{num_d:03d}).")
    for n, r, d in linhas_rotas:
        print(f"     {n}  ->  {d}")
    if duplicatas:
        for dnome, bnome in duplicatas:
            print(f"     {dnome}  ->  duplicata de {bnome} (nao roteada)")
    graves = [c for c in citacoes if "REVOGADA" in c[1] or c[1] != "verificada"]
    if graves:
        print(f"     ATENCAO: {len(graves)} citacao(oes) da minuta exigem acao "
              "(ver _views/REVISAO_COLABORADOR.md).")
    print("     PROXIMO PASSO (sessao): engenharia reversa — fatos/pedidos/"
          "propostas do colaborador + secoes semanticas do relatorio.")


def rel_dado(arq, base):
    try:
        return str(arq.relative_to(base))
    except ValueError:
        return arq.name


if __name__ == "__main__":
    main()
