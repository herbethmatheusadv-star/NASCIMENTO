# -*- coding: utf-8 -*-
"""
soj_lib.py — funções compartilhadas do kernel SOJ.
Não é executado diretamente: os 5 scripts importam daqui.
Referência: SOJ_BLUEPRINT_v1.md (v1.3), seções 2-7.
"""
import datetime
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

try:
    from ruamel.yaml import YAML   # round-trip do CASO.yaml (v1) — opcional
except ImportError:                # kernel carrega sem ruamel (ex.: tarefa agendada,
    YAML = None                    # onde o user site-packages pode não estar no path)

# ----------------------------------------------------------------- caminhos
ROOT = Path(__file__).resolve().parents[2]          # .../NASCIMENTO
CASOS = ROOT / "CASOS"
ESCRITORIO = ROOT / "ESCRITORIO"

if YAML is not None:
    _yaml = YAML()                # modo round-trip: preserva comentários do CASO.yaml
    _yaml.preserve_quotes = True
    _yaml.width = 4096
else:
    _yaml = None                  # sem ruamel: só as funções de CASO.yaml ficam indisponíveis


def console_utf8():
    """Evita erro de acentuação no terminal do Windows."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def agora():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def hoje():
    return datetime.date.today()


def normaliza(texto):
    """minúsculas + sem acentos, para buscas tolerantes em textos."""
    t = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode("ascii")
    return t.lower()


def sha256_arquivo(caminho):
    """Hash SHA-256 do arquivo (cadeia de custodia — Onda 4/F6)."""
    import hashlib
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


ROTULO_DEGRAVACAO = ("DEGRAVAÇÃO DE TRABALHO — não substitui perícia nem ata "
                     "notarial; se a autenticidade for ponto controverso, "
                     "providenciar prova técnica.")


def slug(texto):
    """'Certidão de nascimento' -> 'CERTIDAO_DE_NASCIMENTO' (nomes de arquivo)."""
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^A-Za-z0-9]+", "_", t).strip("_")
    return t.upper()


# ----------------------------------------------------------------- caso
def caso_dir(nome_cliente):
    """Localiza a pasta do caso; encerra com mensagem clara se não existir."""
    p = CASOS / nome_cliente
    if not (p / "CASO.yaml").exists():
        existentes = []
        if CASOS.exists():
            existentes = sorted(d.name for d in CASOS.iterdir()
                                if (d / "CASO.yaml").exists())
        sys.exit(f"[ERRO] Caso '{nome_cliente}' nao encontrado em CASOS/. "
                 f"Casos existentes: {', '.join(existentes) or 'nenhum'}")
    return p


def _exige_ruamel():
    if _yaml is None:
        raise RuntimeError("ruamel.yaml é necessário para o CASO.yaml (v1). "
                           "Instale: pip install ruamel.yaml")


def load_caso(pasta):
    _exige_ruamel()
    with open(pasta / "CASO.yaml", encoding="utf-8") as f:
        return _yaml.load(f)


def save_caso(pasta, dados):
    _exige_ruamel()
    with open(pasta / "CASO.yaml", "w", encoding="utf-8", newline="\n") as f:
        _yaml.dump(dados, f)


def por_id(lista, id_procurado):
    for item in (lista or []):
        if str(item.get("id")) == str(id_procurado):
            return item
    return None


def lista_de(dados, chave):
    """Garante que dados[chave] é uma lista utilizável (YAML pode trazer None)."""
    if dados.get(chave) is None:
        dados[chave] = []
    return dados[chave]


# ----------------------------------------------------------------- DIARIO
_ENTRADA_RE = re.compile(r"^## #(\d+) \| ([^|]+?) \| ([A-Z_]+)\s*$")


def parse_diario(pasta):
    """Lê o DIARIO.md e devolve a lista de entradas: num, datahora, tipo, corpo."""
    arq = pasta / "DIARIO.md"
    entradas = []
    if not arq.exists():
        return entradas
    atual = None
    for linha in arq.read_text(encoding="utf-8").splitlines():
        m = _ENTRADA_RE.match(linha)
        if m:
            atual = {"num": int(m.group(1)), "datahora": m.group(2).strip(),
                     "tipo": m.group(3), "corpo": []}
            entradas.append(atual)
        elif atual is not None and linha.strip() != "---":
            atual["corpo"].append(linha)
    for e in entradas:
        e["corpo"] = "\n".join(e["corpo"]).strip()
    return entradas


def append_diario(pasta, tipo, corpo, origem=None):
    """Acrescenta uma entrada ao FIM do DIARIO (append-only). Devolve o número.

    origem (governanca de autoria, blueprint v1.10 secao 7): "titular",
    "sistema" ou "colaborador <NOME>" — vira a primeira linha do corpo.
    Entradas antigas sem o campo permanecem validas (origem implicita).
    """
    entradas = parse_diario(pasta)
    num = (entradas[-1]["num"] + 1) if entradas else 1
    if origem:
        corpo = f"Origem: {origem}.\n" + corpo.strip()
    bloco = f"## #{num:03d} | {agora()} | {tipo}\n{corpo.strip()}\n---\n"
    with open(pasta / "DIARIO.md", "a", encoding="utf-8", newline="\n") as f:
        f.write(bloco)
    return num


# ----------------------------------------------------------------- git (D2)
def git_commit(mensagem):
    """Commit automático da pasta inteira. Nunca derruba o script se falhar."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=ROOT, capture_output=True)
        r = subprocess.run(["git", "commit", "-m", mensagem], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode == 0:
            return True
        saida = (r.stdout or "") + (r.stderr or "")
        if "nothing to commit" in saida:
            return False
        print(f"[AVISO] git commit falhou: {saida.strip()[:300]}")
    except FileNotFoundError:
        print("[AVISO] git nao instalado — commit automatico pulado.")
    return False


# ----------------------------------------------------------------- minuta
_TAG_RE = re.compile(r"<!--\s*SOJ:\s*(.*?)\s*-->")


def minuta_atual(pasta):
    """Minuta mais recente: MINUTA_v_final > maior número de versão. None se não há."""
    arquivos = sorted(pasta.glob("MINUTA_v*.md"))
    if not arquivos:
        return None
    finais = [a for a in arquivos if "final" in a.name.lower()]
    return finais[-1] if finais else arquivos[-1]


def tags_da_minuta(caminho):
    """Lê tags <!-- SOJ: F04 | P03,P05 | PED01 | CC:1694 --> com nº da linha."""
    tags = []
    if caminho is None or not caminho.exists():
        return tags

    def ids(campo):
        return [x.strip() for x in campo.split(",") if x.strip() and x.strip() != "-"]

    for n, linha in enumerate(caminho.read_text(encoding="utf-8").splitlines(), 1):
        m = _TAG_RE.search(linha)
        if m:
            campos = [c.strip() for c in m.group(1).split("|")]
            campos += [""] * (4 - len(campos))
            tags.append({"linha": n,
                         "fatos": ids(campos[0]), "provas": ids(campos[1]),
                         "pedidos": ids(campos[2]), "fundamentos": ids(campos[3])})
    return tags


def normaliza_ref(ref):
    """'CC:art1694' e 'CC:1694' -> 'CC1694' (compara fundamentos com tolerância)."""
    return re.sub(r"[^A-Z0-9]", "", str(ref).upper().replace("ART", ""))


# ----------------------------------------------------------------- pendências
def pendencia_aberta(p):
    return normaliza(p.get("status", "aberta")) != "resolvida"


def pendencias_abertas(dados, bloqueia=None):
    """Pendências abertas; se bloqueia='G3', só as que travam aquele gate."""
    resultado = []
    for p in (dados.get("pendencias") or []):
        if not pendencia_aberta(p):
            continue
        if bloqueia and bloqueia not in [str(b) for b in (p.get("bloqueia") or [])]:
            continue
        resultado.append(p)
    return resultado


# ------------------------------------------------- declarações estruturadas
def ref_diario_ok(entradas, ref):
    """'#012' -> True se a entrada 012 existe no DIARIO (referencia valida)."""
    m = re.match(r"#?(\d+)$", str(ref).strip())
    if not m:
        return False
    n = int(m.group(1))
    return any(e["num"] == n for e in entradas)


def declaracao_ok(dados, entradas, chave):
    """Le dados['declaracoes'][chave] (Adendo A2): exige dict com campo
    'diario' apontando entrada existente. Devolve (ok, detalhe)."""
    d = (dados.get("declaracoes") or {}).get(chave)
    if not isinstance(d, dict):
        return False, (f"campo declaracoes.{chave} ausente no CASO.yaml "
                       "(registrar a entrada no DIARIO e apontar o numero)")
    if not ref_diario_ok(entradas, d.get("diario", "")):
        return False, (f"declaracoes.{chave}.diario = '{d.get('diario')}' "
                       "nao aponta para entrada existente do DIARIO")
    return True, ""


# ----------------------------------------------------------------- prazos
def prazo_ativo(p):
    """status: ativo (padrao) | cumprido | prejudicado — o vigia so olha ativos."""
    return normaliza(p.get("status", "ativo")) == "ativo"


def prazos_em_alerta(dados, janela_dias=7):
    """Prazos ATIVOS vencidos ou a <= janela_dias.
    Devolve lista de (prazo, dias) — dias negativo = vencido ha N dias."""
    resultado = []
    for p in (dados.get("prazos") or []):
        if not prazo_ativo(p):
            continue
        d = p.get("data")
        if isinstance(d, datetime.date):
            data = d
        else:
            try:
                data = datetime.date.fromisoformat(str(d))
            except Exception:
                continue
        dias = (data - hoje()).days
        if dias <= janela_dias:
            resultado.append((p, dias))
    return resultado


# ----------------------------------------------------------------- numeração
def proximo_id_caso():
    """Id sequencial ANO-NNNN varrendo todos os CASO.yaml existentes."""
    ano = hoje().year
    maior = 0
    if CASOS.exists():
        for arq in CASOS.glob("*/CASO.yaml"):
            try:
                dados = _yaml.load(arq.read_text(encoding="utf-8"))
                a, n = str(dados["caso"]["id"]).split("-")
                if int(a) == ano:
                    maior = max(maior, int(n))
            except Exception:
                continue
    return f"{ano}-{maior + 1:04d}"


def proximo_doc_num(dados):
    maior = 0
    for p in (dados.get("provas") or []):
        m = re.search(r"DOC-(\d+)", str(p.get("doc", "")))
        if m:
            maior = max(maior, int(m.group(1)))
    return maior + 1


def proximo_prova_id(dados):
    maior = 0
    for p in (dados.get("provas") or []):
        m = re.match(r"P(\d+)$", str(p.get("id", "")))
        if m:
            maior = max(maior, int(m.group(1)))
    return f"P{maior + 1:02d}"
