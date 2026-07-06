# -*- coding: utf-8 -*-
"""
preparar_audiencia.py — comando "preparar audiencia do caso X" (Onda 2/F6).
Cria CASOS/X/AUDIENCIAS/<data>_<tipo>/ com o ROTEIRO.md (esqueleto que a
SESSAO completa a partir do CASO.yaml/ESTRATEGIA e o ADVOGADO revisa),
registra a audiencia em audiencias[], cria o PZ## no vigia e registra no
DIARIO. Depois: espelhar no Calendar (sessao) e, realizada a audiencia,
"chegou a ata" pela porta unica (--tipo ata_audiencia --audiencia-data ...).

Uso:
  python preparar_audiencia.py CLIENTE --data YYYY-MM-DD --tipo instrucao|conciliacao
         [--hora "09:00"] [--local "..."]
"""
import argparse
import re

import soj_lib as soj

ROTEIRO = """# ROTEIRO DE AUDIÊNCIA — {tipo_maiuscula} · {data} {hora}
**Caso:** {cliente} ({caso_id}) · **Local:** {local}

> Esqueleto gerado por preparar_audiencia.py — a SESSÃO completa as seções a
> partir do CASO.yaml/ESTRATEGIA e o ADVOGADO revisa ANTES da audiência.
> Efêmero por natureza (regenerável), mas fica na pasta da audiência como
> registro do que foi levado.

## 1. Perguntas às NOSSAS testemunhas (por testemunha)

*(a completar na sessão: objetivo de cada testemunha → o fato F## que ela
sustenta → perguntas em escada, das abertas às específicas)*

## 2. Testemunhas DELES — perguntas e pontos de ataque ao depoimento

*(a completar: contradições esperadas com os fatos alegado_pelo_adversario,
limites de conhecimento, vínculos/suspeição a explorar)*

## 3. Provas a exibir (referência rápida)

{provas}

## 4. Riscos da simulação adversária nesta audiência

*(a completar da ESTRATEGIA: o que a outra parte tentará produzir aqui e a
contramedida em tempo real)*

## 5. Checklist logístico

- [ ] Cliente orientada(o): o que vai ser perguntado, como responder (a
      verdade, curto, sem adivinhar), trajes, chegada 30 min antes
- [ ] Testemunhas confirmadas e cientes de data/hora/local
- [ ] Documentos ORIGINAIS na pasta (conferir contra o rol)
- [ ] Cópia da petição, da contestação e das decisões principais impressas
- [ ] Procuração e documentos do advogado
- [ ] Celular no silencioso; chegada com antecedência
- [ ] Pós-audiência: pedir cópia da ata → "chegou a ata" pela porta única
"""


def main():
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Prepara audiencia (SOJ).")
    ap.add_argument("cliente")
    ap.add_argument("--data", required=True, help="YYYY-MM-DD")
    ap.add_argument("--tipo", required=True, choices=["instrucao", "conciliacao"])
    ap.add_argument("--hora", default="09:00")
    ap.add_argument("--local", default="(a confirmar no ato de intimacao)")
    args = ap.parse_args()

    pasta = soj.caso_dir(args.cliente)
    dados = soj.load_caso(pasta)

    pasta_aud = pasta / "AUDIENCIAS" / f"{args.data}_{args.tipo}"
    pasta_aud.mkdir(parents=True, exist_ok=True)

    provas = "\n".join(
        f"- {p.get('id')} · {str(p.get('doc', '')).replace('01_documentos/', '')}"
        f" — {p.get('o_que_prova')}"
        for p in (dados.get("provas") or [])) or "- (nenhuma prova registrada)"

    (pasta_aud / "ROTEIRO.md").write_text(
        ROTEIRO.format(tipo_maiuscula=args.tipo.upper(), data=args.data,
                       hora=args.hora, cliente=args.cliente,
                       caso_id=dados["caso"].get("id"),
                       local=args.local, provas=provas),
        encoding="utf-8", newline="\n")

    # audiencia na fonte da verdade
    soj.lista_de(dados, "audiencias").append({
        "data": args.data, "hora": args.hora, "tipo": args.tipo,
        "local": args.local, "status": "designada",
        "pasta": f"AUDIENCIAS/{args.data}_{args.tipo}/"})

    # prazo no vigia
    maior = 0
    for pz in (dados.get("prazos") or []):
        m = re.match(r"PZ(\d+)", str(pz.get("id", "")))
        if m:
            maior = max(maior, int(m.group(1)))
    prazo_id = f"PZ{maior + 1:02d}"
    soj.lista_de(dados, "prazos").append({
        "id": prazo_id,
        "descricao": f"AUDIENCIA de {args.tipo} ({args.hora}, {args.local})",
        "data": args.data, "criticidade": "alta"})
    soj.save_caso(pasta, dados)

    num = soj.append_diario(
        pasta, "EVENTO_PROCESSUAL",
        f"Audiencia de {args.tipo.upper()} designada para {args.data} "
        f"{args.hora} ({args.local}). Roteiro para revisao do advogado em "
        f"AUDIENCIAS/{args.data}_{args.tipo}/ROTEIRO.md. Prazo {prazo_id} no "
        "vigia. Proximos passos: sessao completa o roteiro (perguntas, "
        "ataques, riscos), advogado revisa, espelhar no Calendar "
        "(anonimizado). Apos a audiencia: 'chegou a ata' pela porta unica.")

    import gerar_views
    gerar_views.gerar_views(args.cliente)

    print(f"[OK] Audiencia {args.data} ({args.tipo}) preparada: "
          f"AUDIENCIAS/{args.data}_{args.tipo}/ROTEIRO.md · {prazo_id} no "
          f"vigia · DIARIO #{num:03d}.")
    print("     Sessao: completar o roteiro AGORA e submeter a revisao do "
          "advogado; espelhar o prazo no Calendar; rodar o vigia.")


if __name__ == "__main__":
    main()
