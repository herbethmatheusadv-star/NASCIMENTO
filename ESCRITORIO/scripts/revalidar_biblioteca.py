# -*- coding: utf-8 -*-
"""
revalidar_biblioteca.py — comando "revalidar biblioteca" (Onda 1/F6).
Ritual mensal da BASE_LEGAL (lembrete automatico na 1a sessao do mes, via vigia):

  1. Lista os verbetes VENCIDOS (e os a vencer em ate --janela dias) de todos
     os arquivos de ESCRITORIO/BASE_LEGAL/*.md;
  2. Para cada um, LISTA OS CASOS ATIVOS AFETADOS — pelo campo "Casos que
     citam" do verbete E pelo cruzamento com fundamentos_citados dos casos
     nao encerrados (fase != encerrado);
  3. A REVERIFICACAO em si e trabalho da sessao (baixar a fonte oficial,
     conferir o texto literal, atualizar notas) — nunca de memoria;
  4. Confirmada a revalidacao, o script atualiza a data mecanicamente:
     --marcar "REF=YYYY-MM-DD" (repetivel). Se o TEXTO mudou, alem da data,
     a sessao atualiza o verbete e ABRE ALERTA nos casos afetados.

Uso:
  python revalidar_biblioteca.py [--janela 15] [--marcar "REF=DATA"]...
"""
import argparse
import datetime
import re
import sys

import soj_lib as soj

BASE = soj.ESCRITORIO / "BASE_LEGAL"


def verbetes():
    """(arquivo, ref, verificado(date|None), validade_dias|None, casos_que_citam, bloco)"""
    out = []
    for arq in sorted(BASE.glob("*.md")):
        texto = arq.read_text(encoding="utf-8")
        for bloco in re.split(r"(?m)^## ", texto)[1:]:
            titulo = bloco.splitlines()[0].strip()
            ref = titulo.split(" —")[0].strip()
            m_ver = re.search(r"\*\*Verificado em:\*\*\s*(\d{4}-\d{2}-\d{2})", bloco)
            m_val = re.search(r"\*\*Validade:\*\*\s*(\d+)\s*dias", bloco)
            m_cit = re.search(r"\*\*Casos que citam:\*\*\s*(.+)", bloco)
            out.append((arq, ref,
                        datetime.date.fromisoformat(m_ver.group(1)) if m_ver else None,
                        int(m_val.group(1)) if m_val else None,
                        (m_cit.group(1).strip() if m_cit else ""), bloco))
    return out


def casos_ativos_que_usam(ref):
    """Casos com fase != encerrado cujo fundamentos_citados contem a ref."""
    alvo = soj.normaliza_ref(ref)
    achados = []
    if soj.CASOS.exists():
        for pasta in sorted(soj.CASOS.iterdir()):
            if not (pasta / "CASO.yaml").exists():
                continue
            dados = soj.load_caso(pasta)
            if soj.normaliza(dados["caso"].get("fase", "")) == "encerrado":
                continue
            refs = {soj.normaliza_ref(c.get("ref")) for c in
                    (dados.get("fundamentos_citados") or [])}
            if alvo in refs:
                achados.append(f"{pasta.name} ({dados['caso'].get('id')})")
    return achados


def marcar(par):
    """--marcar REF=DATA: atualiza 'Verificado em' SO dentro do bloco da REF."""
    if "=" not in par:
        sys.exit(f"[ERRO] --marcar invalido (use REF=YYYY-MM-DD): {par}")
    ref, data = par.split("=", 1)
    datetime.date.fromisoformat(data)          # valida o formato
    for arq in sorted(BASE.glob("*.md")):
        texto = arq.read_text(encoding="utf-8")
        padrao = re.compile(
            r"(?ms)(^## " + re.escape(ref) + r"\b.*?\*\*Verificado em:\*\*\s*)"
            r"\d{4}-\d{2}-\d{2}")
        novo, n = padrao.subn(r"\g<1>" + data, texto)
        if n:
            arq.write_text(novo, encoding="utf-8", newline="\n")
            return f"{ref}: Verificado em -> {data} ({arq.name})"
    return f"{ref}: NAO ENCONTRADO em nenhum arquivo da BASE_LEGAL"


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Revalida a BASE_LEGAL em lote (SOJ).")
    ap.add_argument("--janela", type=int, default=15,
                    help="Alem dos vencidos, listar os que vencem em ate N dias")
    ap.add_argument("--marcar", action="append", default=[],
                    metavar="REF=DATA", help="Registrar revalidacao confirmada")
    args = ap.parse_args()

    for par in args.marcar:
        print("[MARCADO] " + marcar(par))
    if args.marcar:
        print()

    hoje = soj.hoje()
    trabalho = []
    for arq, ref, ver, val, citam, _ in verbetes():
        if ver is None or val is None:
            continue                      # permanente / sem validade em dias
        dias = (ver + datetime.timedelta(days=val) - hoje).days
        if dias <= args.janela:
            trabalho.append((dias, ref, arq.name, ver, val, citam))
    trabalho.sort()

    if not trabalho:
        print(f"[BIBLIOTECA] Nenhum verbete vencido ou a vencer em "
              f"{args.janela} dias. Base legal em dia.")
        return
    print(f"[BIBLIOTECA] {len(trabalho)} verbete(s) para revalidar "
          "(reverificar NA FONTE — nunca de memoria):")
    for dias, ref, arq, ver, val, citam in trabalho:
        situacao = f"VENCIDO ha {-dias}d" if dias < 0 else f"vence em {dias}d"
        print(f"  [!] {ref} ({arq}) · verificado {ver} · validade {val}d · {situacao}")
        ativos = casos_ativos_que_usam(ref)
        etiqueta = ", ".join(ativos) if ativos else "nenhum caso ativo"
        print(f"      Casos ativos afetados: {etiqueta}"
              + (f" · ficha do verbete cita: {citam}" if citam else ""))
    print("\n  Fluxo: reverificar cada um na fonte oficial -> se o texto "
          "mudou, atualizar o verbete e abrir ALERTA nos casos afetados -> "
          "registrar: revalidar_biblioteca.py --marcar \"REF=%s\"" % hoje)


if __name__ == "__main__":
    main()
