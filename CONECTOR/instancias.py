#!/usr/bin/env python3
"""
instancias.py — as INSTANCIAS PJe que o conector sabe visitar.

O fluxo de leitura (login por certificado -> Acervo -> "Download autos do
processo" -> PDF assinado) e PADRAO do PJe. O que muda de um tribunal para outro
e o ENDERECO: o host, a raiz do app e a URL de login. Este arquivo isola isso,
para o mesmo conector servir TJPA, TJMA, TRT-8, etc. — sem duplicar codigo e sem
afrouxar o R7 (a blocklist de URLs em regras.py e agnostica de tribunal).

  verificado=True  -> o fluxo ja rodou de verdade nesta instancia.
  verificado=False -> endereco pelo padrao conhecido do PJe; PRECISA de uma
                      sessao real para confirmar (acervo, botao, host do pacote).

Trocar de instancia: `--instancia <chave>` no baixar_autos.py / sessao.py.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Instancia:
    chave: str
    nome: str
    host: str          # ex.: "pje.tjpa.jus.br" (reconhece o painel e monta URLs)
    raiz: str          # raiz do app PJe, ex.: "https://pje.tjpa.jus.br/pje"
    login: str         # URL da tela de login
    verificado: bool   # o fluxo ja rodou de verdade aqui?
    nota: str = ""     # ressalva quando verificado=False
    mni_soap: bool = True  # fala o MNI SOAP classico (intercomunicacao 2.2.2)?
    #  A familia TJ (TJPA, TJMA) publica o MNI em raiz + '/intercomunicacao'.
    #  A Justica do Trabalho (PJe-JT/TRT) NAO: sondagem publica de 20/07/2026
    #  deu 404 nesse caminho e 403 (existe, exige auth) em /pje-comum-api/api/mni.
    #  Quando False, o mni.py se RECUSA a montar endpoint — nao POSTa em 404.
    api_pdpj: bool = False  # PJe NOVO (PDPJ/"Meu Painel"): tem a API REST em
    #  https://<host>/pje-comum-api/api/ ? Confirmado no TRT-8 (sessao logada
    #  20/07/2026). O trt8_api.py so opera instancias com isto True.


REGISTRO: dict[str, Instancia] = {
    # -- confirmado em execucao real (16/07/2026): 16 processos, 280 MB ---------
    "tjpa": Instancia(
        "tjpa", "TJPA — 1o grau", "pje.tjpa.jus.br",
        "https://pje.tjpa.jus.br/pje",
        "https://pje.tjpa.jus.br/pje/login.seam", True),

    # -- padrao conhecido do PJe; confirmar com uma sessao real -----------------
    "tjpa2g": Instancia(
        "tjpa2g", "TJPA — 2o grau", "pje.tjpa.jus.br",
        "https://pje.tjpa.jus.br/pje-2g",
        "https://pje.tjpa.jus.br/pje-2g/login.seam", True,
        "VERIFICADO 20/07 (contexto /pje-2g, client_id pje-tjpa-2g). Acervo por "
        "ORGAO (Camaras + Turma Recursal), nao comarca; download igual ao 1o grau "
        "(window.open/S3). Processos proprios do 2o grau tem CNJ ...8.14.0000"),
    "tjma": Instancia(
        "tjma", "TJMA — 1o grau", "pje.tjma.jus.br",
        "https://pje.tjma.jus.br/pje",
        "https://pje.tjma.jus.br/pje/login.seam", True,
        "VERIFICADO 20/07: login, acervo (listAutosDigitais) e download OK. O "
        "download e por form POST (submit navbar:downloadProcesso), nao o "
        "window.open/S3 do TJPA — o conector detecta e escolhe o fluxo sozinho"),
    "trt8": Instancia(
        "trt8", "TRT-8 — 1o grau", "pje.trt8.jus.br",
        "https://pje.trt8.jus.br/primeirograu",
        "https://pje.trt8.jus.br/primeirograu/login.seam", False,
        "PJe NOVO (PDPJ/'Meu Painel', SPA Angular v2.19.2) — NAO e o Seam do "
        "TJPA. Sessao LOGADA 20/07/2026: acervo pela API REST GET "
        "/pje-comum-api/api/paineladvogado/{idAdv}/processos (idPainelAdvogadoEnum "
        "1=acervo, 5=arquivados; idAdv do titular=837986), auth Bearer do PDPJ. "
        "MNI SOAP classico ausente (/intercomunicacao=404). Autos via PJe-Kz "
        "(window.open) — download a mapear. Detalhes em MAPA_PJE.md §13.9.",
        mni_soap=False, api_pdpj=True),
    "trt8-2g": Instancia(
        "trt8-2g", "TRT-8 — 2o grau", "pje.trt8.jus.br",
        "https://pje.trt8.jus.br/segundograu",
        "https://pje.trt8.jus.br/segundograu/login.seam", False,
        "PJe-TRT contexto /segundograu; mesmo caso do 1o grau — sem MNI SOAP "
        "classico, leitura pela API REST /pje-comum-api ou pelo navegador.",
        mni_soap=False, api_pdpj=True),
}

_atual: Instancia = REGISTRO["tjpa"]


def atual() -> Instancia:
    return _atual


def definir(chave: str) -> Instancia:
    global _atual
    if chave not in REGISTRO:
        raise KeyError(f"instancia {chave!r} desconhecida. Conheco: "
                       f"{', '.join(sorted(REGISTRO))}")
    _atual = REGISTRO[chave]
    return _atual


def listar() -> list[Instancia]:
    return [REGISTRO[k] for k in sorted(REGISTRO)]
