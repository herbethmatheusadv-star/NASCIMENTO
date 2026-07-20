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


REGISTRO: dict[str, Instancia] = {
    # -- confirmado em execucao real (16/07/2026): 16 processos, 280 MB ---------
    "tjpa": Instancia(
        "tjpa", "TJPA — 1o grau", "pje.tjpa.jus.br",
        "https://pje.tjpa.jus.br/pje",
        "https://pje.tjpa.jus.br/pje/login.seam", True),

    # -- padrao conhecido do PJe; confirmar com uma sessao real -----------------
    "tjpa2g": Instancia(
        "tjpa2g", "TJPA — 2o grau (Turma/Camara)", "pje.tjpa.jus.br",
        "https://pje.tjpa.jus.br/pje",
        "https://pje.tjpa.jus.br/pje/login.seam", False,
        "confirmar a entrada do 2o grau ao abrir o painel — pode compartilhar o "
        "acervo do 1o grau ou exigir URL propria"),
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
        "PJe-TRT usa contexto /primeirograu; confirmar acervo e o botao de "
        "download integral"),
    "trt8-2g": Instancia(
        "trt8-2g", "TRT-8 — 2o grau", "pje.trt8.jus.br",
        "https://pje.trt8.jus.br/segundograu",
        "https://pje.trt8.jus.br/segundograu/login.seam", False,
        "PJe-TRT contexto /segundograu"),
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
