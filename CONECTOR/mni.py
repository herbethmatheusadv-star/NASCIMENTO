#!/usr/bin/env python3
"""
mni.py — cliente do MNI/TJPA. LEITURA, e so leitura.

Emenda 05 (titular, 15/07/2026): autorizado o acesso pelo MNI com CPF+senha
DIGITADA A CADA EXECUCAO. A senha nao vai para disco, env, codigo nem log —
vive na memoria deste processo e morre com ele. Mesma logica do certificado com
humano no portao (Emenda 02): quem autentica e ele; o robo so processa.

  POR QUE O ENVELOPE E ESCRITO A MAO, E NAO COM `zeep`

Esta e a decisao central deste arquivo, e ela e sobre a R7. Uma biblioteca SOAP
gera o cliente A PARTIR do WSDL: ela cria um metodo para CADA operacao que o
servidor anuncia — inclusive as duas que este escritorio proibiu. Bastaria uma
linha para tomar ciencia, e ela existiria, pronta, esperando um dia apressado.

R7 e ausencia, nao bloqueio. Montando o XML a mao, so existe o que esta escrito
aqui — e aqui so estao consultas. As operacoes de escrita nao sao "bloqueadas":
elas nao tem funcao, nao tem envelope, nao tem nome no codigo. Chamar uma delas
nao e uma decisao de runtime que alguem possa inverter: e um AttributeError.

  O CONTRATO (lido do WSDL real em 15/07/2026, nao inventado)

  endpoint 1o grau : https://pje.tjpa.jus.br/pje/intercomunicacao
  endpoint 2o grau : https://pje.tjpa.jus.br/pje-2g/intercomunicacao
  style            : document/literal, SOAP 1.1
  wrapper          : {http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/}
  filhos           : {http://www.cnj.jus.br/tipos-servico-intercomunicacao-2.2.2}
                     (form="qualified" em CADA elemento — sobrepoe o
                     elementFormDefault do schema; escrever sem prefixo aqui
                     seria o erro obvio de quem chuta em vez de ler o WSDL)
  soapAction       : {namespace do servico}/{nome da operacao}

  tipoConsultarProcesso:
      idConsultante      xs:string             obrigatorio
      senhaConsultante   xs:string             obrigatorio
      numeroProcesso     tipoNumeroUnico       obrigatorio
      dataReferencia     tipoDataHora          opcional
      movimentos         xs:boolean            opcional
      incluirCabecalho   xs:boolean            opcional
      incluirDocumentos  xs:boolean            opcional   <- os AUTOS
      documento          xs:string             opcional

Uso (o titular digita a senha; ela nunca aparece na linha de comando):
    python CONECTOR/mni.py --teste
    python CONECTOR/mni.py --processo 0805058-87.2025.8.14.0040
    python CONECTOR/mni.py --processo <numero> --com-documentos
"""
from __future__ import annotations

import argparse
import getpass
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import regras

NS_SERVICO = "http://www.cnj.jus.br/servico-intercomunicacao-2.2.2/"
NS_TIPOS = "http://www.cnj.jus.br/tipos-servico-intercomunicacao-2.2.2"
NS_INTER = "http://www.cnj.jus.br/intercomunicacao-2.2.2"
NS_SOAP = "http://schemas.xmlsoap.org/soap/envelope/"

ENDPOINTS = {
    1: "https://pje.tjpa.jus.br/pje/intercomunicacao",
    2: "https://pje.tjpa.jus.br/pje-2g/intercomunicacao",
}

TIMEOUT = 90


# ---------------------------------------------------------------------------
# Credencial: entra pelas maos dele, sai da memoria com o processo
# ---------------------------------------------------------------------------

@dataclass
class Credencial:
    """CPF e senha do PJe. Existe so enquanto o processo roda.

    Nao ha `salvar()`, nao ha `carregar()`, nao ha caminho de arquivo. Se um dia
    alguem quiser persistir isto, vai ter de escrever o codigo do zero — e o
    teste_regras.py vai barrar.
    """
    cpf: str
    _segredo: str

    def __repr__(self) -> str:
        return f"Credencial(cpf={self.cpf[:3]}***, segredo=<oculto>)"

    __str__ = __repr__


def pedir_credencial() -> Credencial:
    """Pergunta ao titular. getpass nao ecoa, nao vai para o historico do shell."""
    print("\n  Credencial do PJe/TJPA — digitada agora, nunca gravada.")
    print("  (Ela morre quando este processo terminar.)\n")
    cpf = input("  CPF (so digitos): ").strip()
    cpf = re.sub(r"\D", "", cpf)
    if len(cpf) != 11:
        sys.exit("  CPF deve ter 11 digitos.")
    seg = getpass.getpass("  Senha do PJe (nao aparece na tela): ")
    if not seg:
        sys.exit("  Sem senha, sem consulta.")
    return Credencial(cpf, seg)


# ---------------------------------------------------------------------------
# Envelope
# ---------------------------------------------------------------------------

def _txt(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def _escapar(s: str) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _envelope(operacao: str, campos: list[tuple[str, object]]) -> bytes:
    """
    Monta o SOAP de UMA operacao permitida.

    A allowlist e conferida aqui tambem — mas ela e a segunda camada, nao a
    primeira. A primeira e que nao existe funcao neste arquivo para as
    operacoes de escrita: nao ha o que passar por aqui.
    """
    if operacao not in regras.OPERACOES_MNI_PERMITIDAS:
        raise regras.ViolacaoR7(
            f"'{operacao}' nao esta na allowlist do MNI "
            f"({sorted(regras.OPERACOES_MNI_PERMITIDAS)}). "
            "Se e uma operacao de escrita, ela nao deve existir neste pacote."
        )
    corpo = "".join(
        f"<tip:{k}>{_escapar(_txt(v))}</tip:{k}>"
        for k, v in campos if v is not None
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<soapenv:Envelope xmlns:soapenv="{NS_SOAP}" '
        f'xmlns:ser="{NS_SERVICO}" xmlns:tip="{NS_TIPOS}">'
        "<soapenv:Header/><soapenv:Body>"
        f"<ser:{operacao}>{corpo}</ser:{operacao}>"
        "</soapenv:Body></soapenv:Envelope>"
    )
    return xml.encode("utf-8")


def _chamar(operacao: str, campos: list[tuple[str, object]], grau: int = 1):
    """POST no endpoint. Devolve (ok, raiz_xml, erro)."""
    url = ENDPOINTS[grau]
    regras.guarda_de_url(url)
    dados = _envelope(operacao, campos)
    req = urllib.request.Request(url, data=dados, method="POST")
    req.add_header("Content-Type", "text/xml; charset=utf-8")
    req.add_header("SOAPAction", f"{NS_SERVICO}{operacao}")
    req.add_header("User-Agent", "SOJ-Conector/1.0 (leitura; OAB 39261/PA)")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return True, ET.fromstring(r.read()), ""
    except urllib.error.HTTPError as e:
        bruto = e.read()
        # a falha SOAP vem em 500 com o motivo dentro
        try:
            raiz = ET.fromstring(bruto)
            fs = raiz.iter("{http://schemas.xmlsoap.org/soap/envelope/}faultstring")
            motivo = next((f.text for f in fs if f.text), "")
            if motivo:
                return False, None, f"HTTP {e.code} — falha SOAP: {motivo}"
        except ET.ParseError:
            pass
        return False, None, f"HTTP {e.code} — {bruto[:200].decode('utf-8', 'ignore')}"
    except Exception as e:
        return False, None, f"{type(e).__name__}: {e}"


def _achar(no, nome: str):
    """Busca por nome local, ignorando o namespace (o PJe varia o prefixo)."""
    for el in no.iter():
        if el.tag.rsplit("}", 1)[-1] == nome:
            return el
    return None


def _todos(no, nome: str):
    return [el for el in no.iter() if el.tag.rsplit("}", 1)[-1] == nome]


# ---------------------------------------------------------------------------
# As UNICAS operacoes que existem neste arquivo
# ---------------------------------------------------------------------------

def consultar_avisos_pendentes(cred: Credencial, grau: int = 1):
    """
    Lista os expedientes SEM abrir nenhum — e o dado que a quarentena precisa.

    E o teste que o spike chamou de decisivo: se isto responder, o MNI atende e
    o conector dispensa navegador no TJPA.
    """
    return _chamar("consultarAvisosPendentes", [
        ("idConsultante", cred.cpf),
        ("senhaConsultante", cred._segredo),
    ], grau)


def consultar_processo(cred: Credencial, numero: str, *, movimentos: bool = True,
                       cabecalho: bool = True, documentos: bool = False,
                       grau: int = 1):
    """
    O processo. Com `documentos=True`, vem tambem o inteiro teor das pecas.

    Cuidado deliberado: `documentos` e False por padrao. Autos integrais sao
    pesados e sao dado de cliente — puxa-los e decisao consciente, nao efeito
    colateral de uma consulta de rotina.
    """
    limpo = re.sub(r"\D", "", numero)
    if len(limpo) != 20:
        raise ValueError(f"numero CNJ deve ter 20 digitos, veio {len(limpo)}: {numero}")
    return _chamar("consultarProcesso", [
        ("idConsultante", cred.cpf),
        ("senhaConsultante", cred._segredo),
        ("numeroProcesso", limpo),
        ("movimentos", movimentos),
        ("incluirCabecalho", cabecalho),
        ("incluirDocumentos", documentos),
    ], grau)


def consultar_alteracao(cred: Credencial, numero: str, grau: int = 1):
    """O que mudou — o alvo natural do radar diario, quando isto amadurecer."""
    return _chamar("consultarAlteracao", [
        ("idConsultante", cred.cpf),
        ("senhaConsultante", cred._segredo),
        ("numeroProcesso", re.sub(r"\D", "", numero)),
    ], grau)


# NAO existe funcao para tomar ciencia nem para peticionar neste arquivo, e
# isso nao e esquecimento: e a R7. Ver regras.py e o relatorio do spike —
# no MNI a porta de leitura e a mesma da escrita, e a unica defesa que nao
# depende de disciplina humana e a operacao simplesmente nao estar escrita.


# ---------------------------------------------------------------------------

def _resumo(raiz) -> None:
    suc = _achar(raiz, "sucesso")
    msg = _achar(raiz, "mensagem")
    print(f"    sucesso : {suc.text if suc is not None else '?'}")
    if msg is not None and msg.text:
        print(f"    mensagem: {msg.text}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Cliente MNI/TJPA — leitura apenas.")
    ap.add_argument("--teste", action="store_true",
                    help="o teste decisivo: lista expedientes (sem abrir nenhum)")
    ap.add_argument("--processo", help="numero CNJ a consultar")
    ap.add_argument("--com-documentos", action="store_true",
                    help="tambem trazer o inteiro teor das pecas (pesado)")
    ap.add_argument("--grau", type=int, default=1, choices=[1, 2])
    args = ap.parse_args()

    if not args.teste and not args.processo:
        ap.print_help()
        return

    print("=" * 74)
    print("  MNI / TJPA — CONECTOR SOJ (somente leitura)")
    print(f"  allowlist: {', '.join(sorted(regras.OPERACOES_MNI_PERMITIDAS))}")
    print(f"  endpoint : {ENDPOINTS[args.grau]}")
    print("=" * 74)

    cred = pedir_credencial()

    if args.teste:
        print("\n  [consultarAvisosPendentes] — lista, nao abre.")
        ok, raiz, err = consultar_avisos_pendentes(cred, args.grau)
        if not ok:
            print(f"    FALHOU: {err}")
            sys.exit(2)
        _resumo(raiz)
        avisos = _todos(raiz, "aviso")
        print(f"    avisos pendentes: {len(avisos)}")
        for a in avisos[:10]:
            npr = _achar(a, "numeroProcesso")
            print(f"      - {npr.text if npr is not None else '?'}")

    if args.processo:
        print(f"\n  [consultarProcesso] {args.processo}"
              f"{' + documentos' if args.com_documentos else ''}")
        ok, raiz, err = consultar_processo(cred, args.processo,
                                           documentos=args.com_documentos,
                                           grau=args.grau)
        if not ok:
            print(f"    FALHOU: {err}")
            sys.exit(2)
        _resumo(raiz)
        for nome in ("classeProcessual", "orgaoJulgador", "valorCausa"):
            el = _achar(raiz, nome)
            if el is not None:
                print(f"    {nome}: {el.text or el.attrib}")
        movs = _todos(raiz, "movimento")
        docs = _todos(raiz, "documento")
        print(f"    movimentos: {len(movs)}   documentos: {len(docs)}")
        for d in docs[:15]:
            print(f"      - {d.attrib.get('descricao') or d.attrib.get('tipoDocumento','?')}"
                  f"  (id {d.attrib.get('idDocumento','?')})")


if __name__ == "__main__":
    main()
