# -*- coding: utf-8 -*-
"""
Le o teor da intimacao e responde tres perguntas:

  1. O que e isto?        despacho, decisao, sentenca, ato ordinatorio...
  2. O prazo e MEU?       ou e da parte contraria?
  3. Quao grave e?        "sob pena de desercao" nao e "sob pena de multa"

PRINCIPIO QUE RESOLVE TODO EMPATE: na duvida, mostrar. Este modulo so diz
"nao e seu" quando o texto e explicito e o polo do seu cliente e conhecido e
oposto. Qualquer ambiguidade vira INCERTO, e INCERTO aparece no relatorio.
Esconder por engano custa um prazo; mostrar a mais custa dez segundos de
leitura.
"""
from __future__ import annotations

import re
import unicodedata

# --------------------------------------------------------------------------

def normalizar(texto: str) -> str:
    """Minusculas, sem acento, espaco colapsado - para casar padrao sem sofrer."""
    t = unicodedata.normalize("NFKD", texto or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).lower()


# --------------------------------------------------------------------------
# 1. Que ato e este?
# --------------------------------------------------------------------------

# ordem importa: o mais especifico ganha
TIPOS_ATO = [
    ("acordao", r"\bacordao\b|\bementa\b.{0,400}?\bacordam\b|\bacordam\s+os\b"),
    ("sentenca", r"\bsentenca\b|\bjulgo\s+(?:procedente|improcedente|extinto)\b|"
                 r"\bhomologo\b.{0,80}\bacordo\b"),
    ("decisao", r"\bdecisao\s+interlocutoria\b|\bdecisao\b|\bdecido\b|\bdefiro\b|"
                r"\bindefiro\b|\bdetermino\b"),
    ("audiencia", r"\btermo\s+de\s+audiencia\b|\baudiencia\s+de\s+(?:concilia|"
                  r"instru|mediac)"),
    ("ato_ordinatorio", r"\bato\s+ordinatorio\b"),
    ("despacho", r"\bdespacho\b|\bcumpra-se\b|\bintime-se\b"),
    ("distribuicao", r"\bdistribuid[oa]\s+(?:para|por)\b|\blista\s+de\s+distribuicao\b"),
    ("sigiloso", r"\bprocesso\s+sigiloso\b|\bsegredo\s+de\s+justica\b"),
]

ROTULO_ATO = {
    "acordao": "Acórdão",
    "sentenca": "Sentença",
    "decisao": "Decisão",
    "audiencia": "Audiência",
    "ato_ordinatorio": "Ato ordinatório",
    "despacho": "Despacho",
    "distribuicao": "Distribuição",
    "sigiloso": "Sigiloso (só nos autos)",
    "indefinido": "Não identificado",
}


def tipo_de_ato(texto: str) -> str:
    t = normalizar(texto)
    for nome, pat in TIPOS_ATO:
        if re.search(pat, t):
            return nome
    return "indefinido"


# --------------------------------------------------------------------------
# 1.5. Onde mora a ORDEM (e onde mora so a narrativa)
# --------------------------------------------------------------------------

# "Intime-se o agravante para...", "fica a parte requerida INTIMADA para...",
# "Cite-se o reu para...", "Fica V. Sa. intimado para..."
RE_COMANDO = re.compile(
    r"(?:intime[m]?-se|notifique[m]?-se|cite[m]?-se|"
    r"fica[m]?\s+(?:a|o|as|os)\s+[\w\s]{0,40}?intimad\w+|"
    r"fica\s+v\.?\s*s\.?\s*a\.?|"
    r"fica[m]?\s+(?:a|o|as|os)\s+[\w\s]{0,40}?(?:citad|notificad)\w+)"
    r".{0,450}?(?=\.\s|$)",
    re.IGNORECASE | re.DOTALL,
)

# "sob pena de X" vale mesmo fora de um "intime-se": e sempre uma ameaca real
RE_SOB_PENA = re.compile(r".{0,150}sob\s+pena\s+de.{0,150}", re.IGNORECASE | re.DOTALL)


def trechos_de_ordem(texto: str) -> str:
    """
    Devolve so os pedacos que MANDAM fazer algo. String vazia se nao houver.

    Por que isto existe: um acordao de 10 mil caracteres cita "contrarrazoes",
    "embargos", "apelacao", "custas" e "impugnacao" so ao narrar o historico do
    processo. Nada disso e ordem para voce. Classificar o texto inteiro fazia o
    relatorio dizer que uma unica decisao pedia seis providencias diferentes -
    ruido que faz o advogado parar de ler. A ordem de verdade mora em
    "Intime-se X para Y, sob pena de Z".
    """
    achados = [m.group(0) for m in RE_COMANDO.finditer(texto or "")]
    achados += [m.group(0) for m in RE_SOB_PENA.finditer(texto or "")]
    return " ".join(achados)


# --------------------------------------------------------------------------
# 2. O que ele manda fazer?
# --------------------------------------------------------------------------

PROVIDENCIAS = [
    ("preparo", r"\bpreparo\s+recursal\b|\brecolhimento\s+do\s+preparo\b|"
                r"\bporte\s+de\s+remessa\b"),
    ("custas", r"\bcustas\s+processuais\b|\brecolh\w+\s+(?:as\s+)?custas\b|"
               r"\bpagamento.{0,30}\bcustas\b"),
    ("contrarrazoes", r"\bcontrarrazo\w+\b"),
    ("contestacao", r"\bcontesta\w+\b|\bdefesa\s+escrita\b"),
    ("impugnacao", r"\bimpugna\w+\b"),
    ("embargos", r"\bembargos\s+(?:de\s+declaracao|a\s+execucao|do\s+devedor)\b"),
    ("recurso", r"\bapelacao\b|\bagravo\b|\brecurso\s+(?:ordinario|especial|"
                r"extraordinario|inominado)\b"),
    ("emenda", r"\bemend\w+\s+(?:a\s+)?inicial\b|\bemende-se\b"),
    ("provas", r"\bespecific\w+\s+(?:as\s+)?provas\b|\bprovas\s+(?:que\s+)?"
               r"pretend\w+\s+produzir\b"),
    ("pagamento", r"\bcumprimento\s+voluntario\b|\bpague\b|\bpagamento\s+"
                  r"(?:do\s+)?debito\b"),
    ("documentos", r"\bjunt\w+\s+(?:os\s+)?documentos\b|\bapresent\w+\s+"
                   r"(?:os\s+)?documentos\b"),
    ("ciencia", r"\bde-se\s+ciencia\b|\bfica\w*\s+ciente\b|\btome\s+ciencia\b"),
    ("manifestacao", r"\bmanifest\w+\b"),
]

ROTULO_PROVIDENCIA = {
    "preparo": "recolher preparo recursal",
    "custas": "recolher custas",
    "contrarrazoes": "apresentar contrarrazões",
    "contestacao": "contestar",
    "impugnacao": "impugnar",
    "embargos": "embargos",
    "recurso": "recurso",
    "emenda": "emendar a inicial",
    "provas": "especificar provas",
    "pagamento": "pagamento/cumprimento",
    "documentos": "juntar documentos",
    "ciencia": "ciência",
    "manifestacao": "manifestar-se",
}


def providencias(texto: str) -> list[str]:
    """
    So o que a ordem manda fazer. Le apenas os trechos de comando: se a peca
    nao manda nada (uma sentenca que so julga, por exemplo), devolve vazio -
    melhor calar do que listar seis providencias que ninguem pediu.
    """
    ordem = trechos_de_ordem(texto)
    if not ordem:
        return []
    t = normalizar(ordem)
    achadas = [nome for nome, pat in PROVIDENCIAS if re.search(pat, t)]
    # "ciencia" e "manifestacao" sao genericas: so valem se nada mais apareceu
    especificas = [a for a in achadas if a not in ("ciencia", "manifestacao")]
    return especificas or achadas


# --------------------------------------------------------------------------
# 3. Quao grave?
# --------------------------------------------------------------------------

# peso: 3 = perde o direito | 2 = consequencia dura | 1 = incomodo
# Estes padroes sao casados APENAS contra o que vem depois de "sob pena de".
SANCOES = [
    (3, "deserção", r"desercao|deserto"),
    (3, "não conhecimento", r"nao\s+conhecimento|nao\s+ser\s+conhecid"),
    (3, "extinção", r"extincao|extinto"),
    (3, "arquivamento", r"arquivamento|arquivad"),
    (3, "revelia", r"revelia|confissao"),
    (3, "preclusão", r"preclusao|preclus"),
    (3, "indeferimento", r"indeferimento|indeferid"),
    (3, "cancelamento da distribuição", r"cancelamento\s+da\s+distribuicao"),
    (2, "penhora/bloqueio", r"penhora|bloqueio|constricao"),
    (2, "multa", r"multa|astreinte"),
    (2, "busca e apreensão", r"busca\s+e\s+apreensao"),
    (1, "desentranhamento", r"desentranhamento"),
]

# ameacas que a lei escreve sem a formula "sob pena de"
INEQUIVOCOS = [
    (3, "deserção", r"julgad[oa]\s+deserto|recurso\s+deserto"),
    (3, "revelia", r"presumir-se-ao\s+verdadeiras|reputar-se-ao\s+verdadeiros"),
]


def sancoes(texto: str) -> list[tuple[int, str]]:
    """
    Consequencias de nao cumprir, da mais grave para a menos.

    So conta o que vem DEPOIS de "sob pena de". Uma sentenca que diz "julgo
    extinto o processo sem resolucao do merito" nao esta ameacando ninguem -
    esta decidindo. Casar "extincao" no texto inteiro fazia toda sentenca virar
    alarme de gravidade maxima.
    """
    t = normalizar(texto)
    achadas: list[tuple[int, str]] = []

    for m in re.finditer(r"sob\s+pena\s+de\s+([^.;]{0,140})", t):
        alvo = m.group(1)
        for peso, nome, pat in SANCOES:
            if re.search(pat, alvo) and (peso, nome) not in achadas:
                achadas.append((peso, nome))

    for peso, nome, pat in INEQUIVOCOS:
        if re.search(pat, t) and (peso, nome) not in achadas:
            achadas.append((peso, nome))

    return sorted(achadas, key=lambda x: -x[0])


def gravidade(texto: str) -> int:
    s = sancoes(texto)
    return s[0][0] if s else 0


# --------------------------------------------------------------------------
# 4. O prazo e MEU?
# --------------------------------------------------------------------------

MEU = "MEU"
DA_OUTRA_PARTE = "DA_OUTRA_PARTE"
INCERTO = "INCERTO"

# quem o ato manda agir -> polo que deve cumprir
ALVOS_ATIVO = r"(?:parte\s+)?(?:autor(?:a|es)?|requerente|exequente|agravante|" \
              r"apelante|impetrante|reclamante|embargante|recorrente)"
ALVOS_PASSIVO = r"(?:parte\s+)?(?:re(?:u|us|querid[oa]s?)|executad[oa]s?|agravad[oa]s?|" \
                r"apelad[oa]s?|impetrad[oa]s?|reclamad[oa]s?|embargad[oa]s?|recorrid[oa]s?)"

# "fica a parte requerida INTIMADA para...", "Intime-se o agravante para..."
PADROES_INTIMACAO = [
    r"fica[m]?\s+(?:a|o|as|os)\s+{alvo}\s+intimad",
    r"intime[m]?-se\s+(?:a|o|as|os)\s+{alvo}",
    r"intimacao\s+d[ao]s?\s+{alvo}",
    r"{alvo}\s+(?:fica|ficam)\s+intimad",
    r"intimar\s+(?:a|o|as|os)\s+{alvo}",
]


def _quem_deve_agir(texto: str) -> set[str]:
    """Devolve {'A'}, {'P'}, os dois, ou vazio se o texto nao diz."""
    t = normalizar(texto)
    achados = set()
    for base in PADROES_INTIMACAO:
        if re.search(base.format(alvo=ALVOS_ATIVO), t):
            achados.add("A")
        if re.search(base.format(alvo=ALVOS_PASSIVO), t):
            achados.add("P")
    return achados


def polos_do_cliente(destinatarios: list[dict]) -> set[str]:
    """
    Polos das partes destinatarias da comunicacao.

    Se vier so uma parte, sabemos de quem o advogado atua. Se vierem as duas
    (autor e reu na mesma comunicacao), o DJEN nao diz qual delas e do nosso
    advogado - e ai nao da para afirmar nada.
    """
    return {d.get("polo") for d in (destinatarios or []) if d.get("polo") in ("A", "P")}


def de_quem_e_o_prazo(texto: str, destinatarios: list[dict]) -> tuple[str, str]:
    """
    Devolve (veredito, motivo).

    So diz DA_OUTRA_PARTE quando: o texto nomeia explicitamente UM polo, o
    cliente e de UM polo conhecido, e os dois sao opostos. Todo o resto e
    INCERTO ou MEU - porque errar para "nao e seu" faz perder prazo.
    """
    polos_cli = polos_do_cliente(destinatarios)
    deve_agir = _quem_deve_agir(texto)

    if not deve_agir:
        return INCERTO, "o texto não diz explicitamente quem deve agir"
    if len(polos_cli) != 1:
        if not polos_cli:
            return INCERTO, "a comunicação não informa o polo do seu cliente"
        return INCERTO, ("a comunicação lista as duas partes; não dá para saber "
                         "qual delas é seu cliente")

    cli = next(iter(polos_cli))
    nome = {"A": "polo ativo", "P": "polo passivo"}[cli]

    if len(deve_agir) > 1:
        return MEU, f"o ato intima os dois polos e seu cliente é do {nome}"
    alvo = next(iter(deve_agir))
    alvo_nome = {"A": "o polo ativo", "P": "o polo passivo"}[alvo]
    if alvo == cli:
        return MEU, f"o ato intima {alvo_nome} e seu cliente é do {nome}"
    return DA_OUTRA_PARTE, (f"o ato intima {alvo_nome}, mas seu cliente é do {nome}")


# --------------------------------------------------------------------------

def analisar(texto: str, destinatarios: list[dict]) -> dict:
    veredito, motivo = de_quem_e_o_prazo(texto, destinatarios)
    sanc = sancoes(texto)
    provs = providencias(texto)
    return {
        "ato": tipo_de_ato(texto),
        "ato_rotulo": ROTULO_ATO[tipo_de_ato(texto)],
        "providencias": provs,
        "providencias_rotulo": [ROTULO_PROVIDENCIA[p] for p in provs],
        "sancoes": sanc,
        "gravidade": sanc[0][0] if sanc else 0,
        "sancao_principal": sanc[0][1] if sanc else "",
        "de_quem": veredito,
        "de_quem_motivo": motivo,
    }
