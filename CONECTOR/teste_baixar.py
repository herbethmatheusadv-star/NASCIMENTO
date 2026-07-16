#!/usr/bin/env python3
"""
teste_baixar.py — o parser e a allowlist do baixar_autos, sem rede.

HTML sintetico (ids/nomes falsos), nenhum dado de cliente. Testa o que pode dar
errado sem um servidor: extrair o CNJ, extrair TODAS as pecas (mesmo as sem nome
na arvore lazy), montar a URL de leitura e recusar rota fora da allowlist.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baixar_autos as ba
import regras

falhas = []
def check(nome, obtido, esperado):
    ok = obtido == esperado
    print(f"  [{'ok ' if ok else 'FALHA'}] {nome}")
    if not ok:
        print(f"          esperado: {esperado!r}")
        print(f"          obtido  : {obtido!r}")
        falhas.append(nome)

def check_levanta(nome, fn, *a):
    try:
        fn(*a)
    except regras.ViolacaoR7:
        print(f"  [ok ] {nome}")
        return
    print(f"  [FALHA] {nome} — NAO levantou ViolacaoR7")
    falhas.append(nome)

# HTML sintetico: uma peca com nome (arvore aberta) + tres so com id (lazy) +
# o mesmo id repetido (dedup) + botao de lembrete (mesma familia de id).
HTML = """
<html><head><title>Autos</title></head><body>
  <span>Processo n. 0809135-08.2026.8.14.0040</span>
  <a title="900000001 - Peticao Inicial" href="#">abrir</a>
  <a href="javascript:void(0)" onclick="window.open('/pje/Processo/lembretes.seam?idProcessoDocumento=900000002')">lembrete</a>
  <a href="/pje/seam/resource/rest/pje-legacy/documento/download/900000003">baixar</a>
  <a onclick="abrir('idProcessoDocumento=900000004')">x</a>
  <a onclick="repetido idProcessoDocumento=900000002 de novo">y</a>
</body></html>
"""

print("=" * 66)
print("  baixar_autos — parser + allowlist (sem rede)")
print("=" * 66)

print("\n=== 1. Extrai o numero CNJ do cabecalho ===")
check("acha o CNJ", ba.extrair_cnj(HTML), "0809135-08.2026.8.14.0040")
check("sem CNJ devolve vazio", ba.extrair_cnj("<html>nada</html>"), "")

print("\n=== 2. Extrai TODAS as pecas (nome onde ha, id onde nao) ===")
docs = ba.extrair_documentos(HTML)
ids = [d[0] for d in docs]
check("pega as 4 pecas distintas (dedup do repetido)",
      ids, ["900000001", "900000002", "900000003", "900000004"])
check("a peca com nome traz o nome", dict(docs)["900000001"], "Peticao Inicial")
check("peca sem nome fica com nome vazio (nao some)",
      dict(docs)["900000002"], "")

print("\n=== 2b. Acervo: liga CNJ -> URL dos autos (id+ca) ===")
# como aparece no painel real: link dos autos com id&amp;ca, e o CNJ logo apos.
ACERVO = """
<a href="/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado.seam?id=8465436&amp;ca=da6365dd27bb74" title="Autos Digitais"><span class="text-bold">PJEC 0809135-08.2026.8.14.0040</span></a>
<a href="/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado.seam?id=7628422&amp;ca=acee94e15194" title="Autos Digitais"><span class="text-bold">PJEC 0808548-83.2026.8.14.0040</span></a>
"""
acervo = ba.extrair_acervo(ACERVO)
check("acha os 2 processos", sorted(acervo), sorted([
    "0809135-08.2026.8.14.0040", "0808548-83.2026.8.14.0040"]))
check("monta a URL absoluta com id e ca (amp; desescapado)",
      acervo["0809135-08.2026.8.14.0040"],
      "https://pje.tjpa.jus.br/pje/Processo/ConsultaProcesso/Detalhe/"
      "listProcessoCompletoAdvogado.seam?id=8465436&ca=da6365dd27bb74")
check("normaliza CNJ (so digitos)", ba._norm_cnj("0809135-08.2026.8.14.0040"),
      "08091350820268140040")

print("\n=== 3. URL de download: allowlist de leitura ===")
url = ba._url_download("900000001")
check("monta a rota REST de leitura correta", url,
      "https://pje.tjpa.jus.br/pje/seam/resource/rest/pje-legacy/documento/download/900000001")

print("\n=== 4. guarda_de_url libera leitura, barra escrita ===")
regras.guarda_de_url(url)   # nao pode levantar
print("  [ok ] guarda libera documento/download (leitura)")
for ruim in ["https://pje.tjpa.jus.br/pje/Processo/CadastroPeticaoAvulsa/peticaoavulsa.seam",
             "https://pje.tjpa.jus.br/pje/Painel/advogado/consultaDocnaoAssinado.seam"]:
    check_levanta(f"barra {ruim[-30:]!r}", regras.guarda_de_url, ruim)

print("\n=== 5. Deteccao de tipo do arquivo ===")
check("bytes de PDF viram pdf", ba._extensao("application/octet-stream", b"%PDF-1.7 ..."), "pdf")
check("content-type pdf vira pdf", ba._extensao("application/pdf;x", b"xx"), "pdf")
check("html vira html", ba._extensao("text/html;charset=UTF-8", b"<htm"), "html")

print("\n=== 6. Slug de nome de arquivo ===")
check("acento e espaco viram slug limpo",
      ba._slug("Petição Inicial (Ação)"), "peticao-inicial-acao")
check("vazio vira 'peca'", ba._slug(""), "peca")

# A garantia de "so leitura" no fonte do baixar_autos e do teste_regras.py
# (que varre este pacote inteiro por vocabulario de acao). Nao se repete aqui
# com os verbos crus como string — isso e que faz a R7 disparar sobre o proprio
# teste. Ver o percalco de 16/07/2026 (mesmo caso do teste_mni).

print("\n" + "=" * 66)
if falhas:
    print(f"  {len(falhas)} FALHA(S): " + ", ".join(falhas))
    sys.exit(1)
print("  Tudo verde. Parser e allowlist OK — falta so a sessao real.")
print("=" * 66)
