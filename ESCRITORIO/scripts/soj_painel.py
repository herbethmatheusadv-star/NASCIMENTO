# -*- coding: utf-8 -*-
"""
soj_painel.py — O PAINEL DO DIA (cockpit do SOJ).

Gera UM HTML autocontido (sem servidor, sem dependencia externa, offline) a
partir da VERDADE do sistema — fichas de PROCESSOS/, manifestos e linhas do tempo
em AUTOS/, resumos e minutas. E uma VISTA gerada, nao uma segunda verdade: fica em
index/ (gitignored), reconstruivel a qualquer momento, como o indice FTS5.

O painel reune, num lugar so, o que o advogado precisa ver todo dia:
  - Precisa de voce hoje: audiencias proximas + prazos em curso + acoes urgentes.
  - Preparado pelo robo (voce assina): resumos e minutas em rascunho (R7).
  - Acervo: todos os processos, filtravel, com o estado dos autos.
  - Cobertura por instancia e pontos cegos.

Uso:
  python soj_painel.py                 # gera e abre no navegador
  python soj_painel.py --sem-abrir     # so gera o arquivo
"""
import argparse
import html as H
import json
import re
import sys
import webbrowser
from datetime import date, datetime
from pathlib import Path

import soj_lib as soj
import soj_prazos as prazos
import soj_pendencias as pendencias

try:
    import yaml
except ImportError:
    sys.exit("[painel] falta pyyaml: pip install pyyaml")

PROCESSOS = soj.ROOT / "PROCESSOS"
AUTOS = soj.ROOT / "AUTOS"
CLIENTES = soj.ROOT / "CLIENTES"
SAIDA = soj.ROOT / "index" / "painel.html"
HOJE = date.today()
JANELA = 21   # dias a frente que contam como "proximo"


def _fm(caminho: Path) -> tuple[dict, str]:
    txt = caminho.read_text(encoding="utf-8", errors="ignore")
    if not txt.startswith("---"):
        return {}, txt
    fim = txt.find("\n---", 3)
    if fim < 0:
        return {}, txt
    try:
        return (yaml.safe_load(txt[3:fim]) or {}), txt[fim + 4:]
    except Exception:  # noqa: BLE001
        return {}, txt


def _data(v) -> date | None:
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


def clientes_map() -> dict:
    """{CLI-XXXX: nome} lido de CLIENTES/, para o painel mostrar o nome real."""
    out = {}
    if not CLIENTES.exists():
        return out
    for f in CLIENTES.glob("CLI-*.md"):
        fm, _ = _fm(f)
        nome = str(fm.get("nome") or "").strip()
        if nome:
            out[str(fm.get("id") or f.stem)] = nome
    return out


def _cliente(v, mapa=None) -> str:
    s = str(v or "").strip().strip('"')
    m = re.search(r"CLI-\d+", s)
    if m:
        return (mapa or {}).get(m.group(0), m.group(0))
    if "a cadastrar" in s.lower() or "pendente" in s.lower():
        return "cliente a cadastrar"
    return s or "—"


def _autos_de(numero: str) -> dict:
    base = AUTOS / str(numero)
    manif = base / "texto" / "manifesto.json"
    if not manif.exists():
        return {"indexado": False}
    d = {"indexado": True, "paginas": 0, "pecas": 0, "alta": 0,
         "periodo": "", "ultima": None, "novidades": None,
         "resumo": None, "minuta": False}
    try:
        m = json.loads(manif.read_text(encoding="utf-8"))
        d["paginas"] = m.get("paginas", 0)
        d["pecas"] = m.get("documentos", 0)
        d["novidades"] = m.get("novidades")
    except Exception:  # noqa: BLE001
        pass
    tl = base / "inteligencia" / "linha_do_tempo.json"
    if tl.exists():
        try:
            j = json.loads(tl.read_text(encoding="utf-8"))
            d["alta"] = j.get("alta", 0)
            d["periodo"] = j.get("periodo", "")
            altas = [it for it in j.get("itens", []) if it.get("relevancia") == "alta"]
            d["ultima"] = altas[-1] if altas else None
        except Exception:  # noqa: BLE001
            pass
    res = base / "inteligencia" / "resumo_executivo.md"
    if res.exists():
        fm, _ = _fm(res)
        d["resumo"] = str(fm.get("status") or "rascunho")
    minutas = base / "inteligencia" / "minutas"
    d["minuta"] = minutas.exists() and any(minutas.glob("*_RASCUNHO.md"))
    return d


def carregar() -> dict:
    processos, audiencias = [], []
    cmap = clientes_map()
    for f in sorted(PROCESSOS.glob("PROC-*.md")):
        fm, corpo = _fm(f)
        numero = str(fm.get("numero") or "").strip().strip('"')
        # sub-ficha de audiencia: data no nome
        m = re.search(r"_audiencia_(\d{4}-\d{2}-\d{2})", f.stem)
        if m:
            d = _data(m.group(1))
            hora = re.search(r"\b(\d{1,2}:\d{2})\b", str(fm.get("proxima_acao") or ""))
            if d:
                audiencias.append({
                    "proc": f.stem.split("_audiencia")[0], "numero": numero,
                    "data": d, "hora": hora.group(1) if hora else "",
                    "dias": (d - HOJE).days,
                    "cliente": _cliente(fm.get("cliente"), cmap),
                    "adverso": str(fm.get("parte_adversa") or "?"),
                    "obs": str(fm.get("proxima_acao") or "")[:220]})
            continue
        if str(fm.get("tipo") or "") != "processo":
            continue
        processos.append({
            "id": fm.get("id") or f.stem, "numero": numero,
            "cliente": _cliente(fm.get("cliente"), cmap),
            "adverso": str(fm.get("parte_adversa") or "?"),
            "tribunal": str(fm.get("tribunal") or "?"),
            "grau": str(fm.get("grau") or "?"),
            "orgao": str(fm.get("orgao") or ""),
            "classe": str(fm.get("classe") or ""),
            "situacao": str(fm.get("situacao") or "?"),
            "fase": str(fm.get("fase") or "?"),
            "risco": str(fm.get("risco") or ""),
            "sigiloso": bool(fm.get("sigiloso")),
            "prazo": str(fm.get("prazo_em_curso")).lower() in ("true", "1"),
            "data_interna": _data(fm.get("data_interna")),
            "acao": str(fm.get("proxima_acao") or "—"),
            "autos": _autos_de(numero)})

    # "precisa de voce hoje": audiencias + prazos + acoes urgentes (🔴)
    hoje_itens = []
    for a in audiencias:
        if a["dias"] >= -1:
            hoje_itens.append({**a, "tipo": "audiência",
                               "quando": a["data"], "chave": a["dias"]})
    for p in processos:
        if p["prazo"] and p["data_interna"]:
            dias = (p["data_interna"] - HOJE).days
            hoje_itens.append({"tipo": "prazo", "proc": p["id"], "numero": p["numero"],
                               "cliente": p["cliente"], "adverso": p["adverso"],
                               "quando": p["data_interna"], "dias": dias,
                               "obs": p["acao"][:220], "chave": dias})
        elif "🔴" in p["acao"]:
            hoje_itens.append({"tipo": "ação", "proc": p["id"], "numero": p["numero"],
                               "cliente": p["cliente"], "adverso": p["adverso"],
                               "quando": None, "dias": 999, "obs": p["acao"][:220],
                               "chave": 50})
    # prazos ESTRUTURADOS (motor de prazos): vencimentos calculados das fichas
    try:
        for pz in prazos.prazos_do_acervo():
            d = pz["dias"]
            if d < -30 or d > 45:        # janela do "hoje": recentes + próximos
                continue
            tipo = "audiência" if "audi" in pz["tipo"].lower() else "prazo"
            venc = _data(pz["vencimento"])
            aviso = "⚠️ a conferir · " if not pz["conferido"] else ""
            hoje_itens.append({
                "tipo": tipo, "proc": pz["proc"], "numero": pz["numero"],
                "cliente": _cliente(pz["cliente"], cmap), "adverso": pz["adverso"],
                "quando": venc, "dias": d,
                "obs": f"{aviso}{pz['tipo']}: {pz['obs']}"[:220], "chave": d})
    except Exception:  # noqa: BLE001
        pass
    hoje_itens.sort(key=lambda x: x["chave"])

    # preparado pelo robo (R7): resumos e minutas em rascunho
    resumos = [p for p in processos if p["autos"].get("resumo")]
    minutas = [p for p in processos if p["autos"].get("minuta")]
    novidades = [p for p in processos if p["autos"].get("novidades")]

    # cobertura por tribunal
    cob = {}
    for p in processos:
        t = p["tribunal"]
        cob.setdefault(t, {"total": 0, "autos": 0})
        cob[t]["total"] += 1
        if p["autos"]["indexado"]:
            cob[t]["autos"] += 1

    total = len(processos)
    com_autos = sum(1 for p in processos if p["autos"]["indexado"])
    paginas = sum(p["autos"].get("paginas", 0) for p in processos)
    try:
        pend = pendencias.pendencias_do_acervo()
    except Exception:  # noqa: BLE001
        pend = []
    return {"processos": processos, "audiencias": audiencias, "hoje": hoje_itens,
            "resumos": resumos, "minutas": minutas, "novidades": novidades,
            "cobertura": cob, "pendencias": pend,
            "kpi": {"total": total, "com_autos": com_autos, "paginas": paginas,
                    "audiencias": sum(1 for a in audiencias if 0 <= a["dias"] <= 7)}}


# --------------------------------------------------------------------------- HTML
CSS = """
:root{--nav:#12314f;--gold:#b7893f;--bg:#f5f6f8;--card:#fff;--ln:#e5e7eb;
--tx:#1a2230;--tx2:#5b6472;--tx3:#8a92a0;--dan:#b23b3b;--danbg:#fbeceb;
--war:#9a6b12;--warbg:#fbf1dd;--suc:#2e7d46;--sucbg:#e7f3ec;--acc:#1f5fa5;--accbg:#e8f0f9;}
@media (prefers-color-scheme:dark){:root{--nav:#0d1f33;--gold:#c99b57;--bg:#12161c;
--card:#1b212b;--ln:#2b323d;--tx:#e6e9ee;--tx2:#a7afbc;--tx3:#7b8494;--dan:#e88;--danbg:#3a2422;
--war:#e3b24e;--warbg:#3a3016;--suc:#7ac899;--sucbg:#1e3326;--acc:#7bb0ec;--accbg:#1a2a3d;}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);
font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px 60px}
header{background:var(--nav);color:#fff;padding:18px 0;margin-bottom:22px}
header .wrap{padding-top:0;padding-bottom:0;display:flex;justify-content:space-between;align-items:baseline}
header h1{margin:0;font-size:20px;font-weight:600;letter-spacing:.3px}
header h1 b{color:var(--gold);font-weight:600}
header .dt{color:#c8d2df;font-size:13px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:26px}
.kpi{background:var(--card);border:1px solid var(--ln);border-radius:12px;padding:14px 16px}
.kpi .l{font-size:12px;color:var(--tx2)}.kpi .v{font-size:26px;font-weight:600;margin-top:2px}
h2{font-size:15px;font-weight:600;margin:26px 0 12px;display:flex;align-items:center;gap:8px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.card{background:var(--card);border:1px solid var(--ln);border-radius:12px;padding:13px 16px;margin-bottom:10px}
.row{display:flex;justify-content:space-between;align-items:center;gap:10px}
.tt{font-size:15px;font-weight:600}.mt{font-size:13px;color:var(--tx2);margin-top:4px}
.chip{font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;white-space:nowrap}
.c-dan{background:var(--danbg);color:var(--dan)}.c-war{background:var(--warbg);color:var(--war)}
.c-suc{background:var(--sucbg);color:var(--suc)}.c-acc{background:var(--accbg);color:var(--acc)}
.c-mut{background:var(--bg);color:var(--tx3);border:1px solid var(--ln)}
.btn{font-size:12px;font-weight:500;padding:6px 12px;border-radius:8px;border:1px solid var(--ln);
background:transparent;color:var(--tx);cursor:pointer}.btn:hover{background:var(--bg);border-color:var(--gold)}
.btns{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap}
.tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}
.tools input{flex:1;min-width:200px;padding:9px 12px;border:1px solid var(--ln);border-radius:8px;
background:var(--card);color:var(--tx);font-size:14px}
.fbtn{font-size:12px;padding:5px 11px;border-radius:20px;border:1px solid var(--ln);background:var(--card);
color:var(--tx2);cursor:pointer}.fbtn.on{background:var(--nav);color:#fff;border-color:var(--nav)}
details.proc{background:var(--card);border:1px solid var(--ln);border-radius:12px;margin-bottom:8px}
details.proc>summary{list-style:none;cursor:pointer;padding:12px 16px;display:flex;
justify-content:space-between;align-items:center;gap:10px}
details.proc>summary::-webkit-details-marker{display:none}
.pid{font-size:12px;color:var(--tx3);font-variant-numeric:tabular-nums}
.ppart{font-size:14px;font-weight:600}.pchips{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end}
.pbody{padding:0 16px 14px;border-top:1px solid var(--ln);margin-top:2px}
.pbody .lab{font-size:11px;color:var(--tx3);text-transform:uppercase;letter-spacing:.4px;margin:12px 0 3px}
.pbody p{margin:0;font-size:13px;color:var(--tx)}
a.link{color:var(--acc);text-decoration:none;font-size:12px;font-weight:500;border:1px solid var(--ln);
padding:6px 12px;border-radius:8px}a.link:hover{border-color:var(--gold)}
.foot{margin-top:26px;padding-top:14px;border-top:1px solid var(--ln);font-size:12px;color:var(--tx2);
display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.empty{font-size:13px;color:var(--tx3);padding:8px 2px}
#toast{position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:var(--nav);color:#fff;
padding:10px 18px;border-radius:10px;font-size:13px;opacity:0;transition:opacity .2s;pointer-events:none}
#toast.on{opacity:1}
.note{font-size:11px;color:var(--tx3);margin-top:8px}
.live{font-size:11px;color:#9fe6b8;margin-right:10px}
#drawer{display:none;position:fixed;right:0;top:0;bottom:0;width:min(580px,94vw);background:var(--card);
border-left:3px solid var(--suc);box-shadow:-8px 0 30px rgba(0,0,0,.18);padding:18px 20px;overflow:auto;z-index:50}
#drawer.err{border-left-color:var(--dan)}
#drawer h3{margin:0 22px 2px 0;font-size:15px}#drawer .x{float:right;cursor:pointer;color:var(--tx3);font-size:20px;line-height:1}
#drawer pre{white-space:pre-wrap;word-break:break-word;font-size:12px;background:var(--bg);border:1px solid var(--ln);
border-radius:8px;padding:12px;margin-top:10px;color:var(--tx);font-family:ui-monospace,Consolas,monospace}
"""

JS = """
function filtrar(){
  var q=(document.getElementById('busca').value||'').toLowerCase();
  var f=document.querySelector('.fbtn.on'); var fk=f?f.dataset.f:'todos';
  document.querySelectorAll('details.proc').forEach(function(d){
    var okq=!q||d.dataset.busca.indexOf(q)>=0;
    var okf=fk==='todos'||d.dataset[fk.split(':')[0]]===fk.split(':')[1];
    d.style.display=(okq&&okf)?'':'none';
  });
}
function setf(el){document.querySelectorAll('.fbtn').forEach(function(b){b.classList.remove('on')});
  el.classList.add('on');filtrar();}
function copiar(cmd){navigator.clipboard.writeText(cmd).then(function(){
  var t=document.getElementById('toast');t.textContent='Copiado: '+cmd;t.classList.add('on');
  setTimeout(function(){t.classList.remove('on')},2200);});}
"""

# So no MODO SERVIDOR (soj_servidor.py): os botoes RODAM os scripts de leitura
# via /acao, e os links abrem os arquivos renderizados via /ver. Sem servidor,
# nada disso existe — o HTML estatico so copia comandos.
JS_SERVIDOR = """
function drawer(t,c,ok){var d=document.getElementById('drawer');
 document.getElementById('dtit').textContent=t;document.getElementById('dbody').textContent=c;
 d.className=(ok===false?'err':'');d.style.display='block';}
function fechard(){document.getElementById('drawer').style.display='none';}
function rodar(a,cnj,termo){drawer('Rodando: '+a+' '+(cnj||''),'Um momento…',true);
 fetch('/acao',{method:'POST',headers:{'Content-Type':'application/json'},
 body:JSON.stringify({acao:a,cnj:cnj||'',termo:termo||''})}).then(function(r){return r.json();})
 .then(function(j){drawer(j.titulo||a,j.saida||'(sem saida)',j.ok);})
 .catch(function(e){drawer('Erro de conexao',String(e),false);});}
function buscar(cnj){var t=prompt('Buscar nos autos deste processo:');if(t)rodar('buscar',cnj,t);}
function ver(p){window.open('/ver?p='+encodeURIComponent(p),'_blank');}
"""


def _chip_risco(r):
    return {"alto": ("c-dan", "risco alto"), "medio": ("c-war", "risco médio"),
            "baixo": ("c-mut", "risco baixo")}.get(r, ("c-mut", r or "—"))


def _urg(dias):
    if dias < 0:
        return "c-dan", f"vencido há {-dias}d"
    if dias == 0:
        return "c-dan", "hoje"
    if dias == 1:
        return "c-dan", "amanhã"
    if dias <= 7:
        return "c-war", f"em {dias} dias"
    return "c-acc", f"em {dias} dias"


def _rel(numero: str, arquivo: str) -> str:
    return f"../AUTOS/{numero}/inteligencia/{arquivo}"


def _jsq(s: str) -> str:
    """Texto seguro para dentro de copiar('...') no onclick (sem aspas/barras)."""
    return str(s).replace("\\", "").replace("'", "").replace("\n", " ")


def _arq(num: str, arquivo: str, rotulo: str, servidor: bool) -> str:
    """Link para um arquivo da inteligencia. No servidor abre renderizado (/ver);
    no HTML estatico e um caminho de arquivo relativo."""
    if servidor:
        return (f"<a class='link' onclick=\"ver('AUTOS/{num}/inteligencia/{arquivo}')\">"
                f"{rotulo}</a>")
    return f"<a class='link' href='{_rel(num, arquivo)}'>{rotulo}</a>"


def bloco_hoje(itens, servidor=False):
    if not itens:
        return "<div class='empty'>Nada urgente hoje. Bom trabalho.</div>"
    out = []
    icone = {"audiência": ("c-acc", "audiência"), "prazo": ("c-war", "prazo"),
             "ação": ("c-dan", "ação")}
    for it in itens[:10]:
        cor, _ = icone.get(it["tipo"], ("c-mut", it["tipo"]))
        if it.get("quando"):
            uc, ul = _urg(it["dias"])
            quando = f"{it['quando']:%d/%m}" + (f" {it.get('hora','')}" if it.get("hora") else "")
            chip = f"<span class='chip {uc}'>{it['tipo']} · {ul}</span>"
        else:
            quando = ""
            chip = f"<span class='chip {cor}'>{it['tipo']}</span>"
        num = H.escape(it.get("numero") or "")
        obs = H.escape(re.sub(r"\s+", " ", it.get("obs") or "")[:200])
        partes = H.escape(f"{it['cliente']} × {it['adverso'][:40]}")
        if it["tipo"] == "audiência":
            prompt = _jsq(f"Preparar o roteiro da audiencia de {quando} do {it['proc']} "
                          f"({it['cliente']} x {it['adverso'][:40]})")
            botoes = (f"<button class='btn' onclick=\"copiar('{prompt}')\">Preparar roteiro</button>"
                      + _arq(num, "resumo_executivo.md", "Resumo", servidor))
        else:
            botoes = (_arq(num, "resumo_executivo.md", "Resumo", servidor)
                      + _arq(num, "linha_do_tempo.md", "Linha do tempo", servidor))
        out.append(
            f"<div class='card'><div class='row'><span class='tt'>{partes}</span>{chip}</div>"
            f"<div class='mt'>{H.escape(it['proc'])} · {H.escape(num)}"
            f"{(' · '+quando) if quando else ''} — {obs}</div>"
            f"<div class='btns'>{botoes}</div></div>")
    return "".join(out)


def bloco_robo(dados):
    res, minu, nov = dados["resumos"], dados["minutas"], dados["novidades"]
    linhas = []
    def linha(icone_txt, rotulo, chip, botao):
        return (f"<div class='row' style='padding:8px 0;border-bottom:1px solid var(--ln)'>"
                f"<span style='font-size:13px'>{rotulo}</span>"
                f"<span style='display:flex;gap:8px;align-items:center'>{chip}{botao}</span></div>")
    conf = sum(1 for p in res if p["autos"]["resumo"] == "conferido")
    rasc = len(res) - conf
    linhas.append(linha("", f"{len(res)} resumos executivos",
        f"<span class='chip c-suc'>citações verificadas</span>"
        + (f"<span class='chip c-war'>{rasc} rascunho</span>" if rasc else ""),
        "<button class='btn' onclick=\"document.getElementById('acervo').scrollIntoView()\">Ver no acervo</button>"))
    linhas.append(linha("", f"{len(minu)} minutas de peça (rascunho)",
        "<span class='chip c-suc'>citações verificadas</span>" if minu else "<span class='chip c-mut'>nenhuma</span>",
        ""))
    pend = dados.get("pendencias", [])
    npr = {"protocolo": 0, "procuração": 0, "documento": 0}
    for p in pend:
        if p["tipo"] in npr:
            npr[p["tipo"]] += 1
    linhas.append(linha("", "Petições prontas a protocolar (você assina)",
        f"<span class='chip {'c-war' if npr['protocolo'] else 'c-suc'}'>"
        f"{npr['protocolo']}</span>", ""))
    linhas.append(linha("", "Procurações a assinar / confirmar",
        f"<span class='chip {'c-war' if npr['procuração'] else 'c-suc'}'>"
        f"{npr['procuração']}</span>", ""))
    linhas.append(linha("", "Documentos a coletar",
        f"<span class='chip {'c-acc' if npr['documento'] else 'c-mut'}'>"
        f"{npr['documento']}</span>", ""))
    novtxt = (", ".join(f"{H.escape(p['id'])} (+{len(p['autos']['novidades'].get('novos_nums',[]))})"
                        for p in nov) if nov else "nenhuma hoje")
    prot = [p for p in pend if p["tipo"] == "protocolo"]
    prot_txt = ("; ".join(H.escape(f"{p['ref']} — {p['o_que'].replace('protocolar: ', '')}")
                          for p in prot[:4]) if prot else "nenhuma pronta")
    return (f"<div class='card'>{''.join(linhas)}"
            f"<div class='note'>📌 Prontas a protocolar: {prot_txt}.</div>"
            f"<div class='note'>Novidades nos autos: {novtxt}.</div>"
            f"<div class='note'>🔒 O robô lê e prepara. Assinar e protocolar são só seus "
            f"— o sistema nunca age no PJe (R7).</div></div>")


def bloco_proc(p, servidor=False):
    a = p["autos"]
    chips = [f"<span class='chip c-mut'>{H.escape(p['tribunal'])} · {H.escape(p['grau'])}º</span>"]
    sit = p["situacao"]
    chips.append(f"<span class='chip {'c-suc' if sit=='encerrado' else 'c-acc'}'>{H.escape(sit)}</span>")
    rc, rl = _chip_risco(p["risco"])
    if p["risco"]:
        chips.append(f"<span class='chip {rc}'>{rl}</span>")
    if a["indexado"]:
        chips.append(f"<span class='chip c-mut'>{a['paginas']} pgs</span>")
    if a.get("resumo"):
        chips.append(f"<span class='chip c-suc'>resumo</span>")
    busca = H.escape(soj.normaliza(f"{p['id']} {p['numero']} {p['cliente']} {p['adverso']} "
                                   f"{p['classe']} {p['orgao']} {p['acao']}"))
    partes = H.escape(f"{p['cliente']} × {p['adverso'][:44]}")
    autos_txt = "não baixados"
    if a["indexado"]:
        u = a.get("ultima")
        ult = (f" · última relevante: {H.escape(u['tipo'])} ({u.get('data') or '?'}, fls. {u['p_ini']})"
               if u else "")
        autos_txt = f"{a['paginas']} pgs · {a['pecas']} peças ({a.get('alta',0)} p/ leitura){ult}"
    num = H.escape(p["numero"])
    acao_limpa = re.sub(r"\s+", " ", p["acao"])
    cmd_res = f"python ESCRITORIO/scripts/soj_resumo.py --cnj {num}"
    cmd_busca = f"python ESCRITORIO/scripts/soj_search.py <termo> --processo {num}"
    if a.get("resumo"):
        links = _arq(num, "resumo_executivo.md", "Abrir resumo", servidor)
    elif servidor:
        links = f"<button class='btn' onclick=\"rodar('resumo','{num}')\">Gerar resumo</button>"
    else:
        links = f"<button class='btn' onclick=\"copiar('{cmd_res}')\">Gerar resumo</button>"
    if a["indexado"]:
        links += _arq(num, "linha_do_tempo.md", "Linha do tempo", servidor)
    if servidor:
        links += f"<button class='btn' onclick=\"buscar('{num}')\">Buscar nos autos</button>"
    else:
        links += f"<button class='btn' onclick=\"copiar('{cmd_busca}')\">Buscar nos autos</button>"
    return (f"<details class='proc' data-trib='{H.escape(p['tribunal'])}' "
            f"data-sit='{H.escape(sit)}' data-risco='{H.escape(p['risco'])}' data-busca='{busca}'>"
            f"<summary><span><span class='pid'>{H.escape(p['id'])}</span><br>"
            f"<span class='ppart'>{partes}</span></span>"
            f"<span class='pchips'>{''.join(chips)}</span></summary>"
            f"<div class='pbody'>"
            f"<div class='lab'>Próxima ação</div><p>{H.escape(acao_limpa)}</p>"
            f"<div class='lab'>Autos</div><p>{autos_txt}</p>"
            f"<div class='lab'>Classe · órgão</div><p>{H.escape(p['classe'])} · {H.escape(p['orgao'])}</p>"
            f"<div class='btns'>{links}</div></div></details>")


def render(dados, servidor=False) -> str:
    k = dados["kpi"]
    kpis = "".join(f"<div class='kpi'><div class='l'>{l}</div><div class='v'>{v}</div></div>"
                   for l, v in [("Processos", k["total"]),
                                ("Páginas indexadas", f"{k['paginas']:,}".replace(",", ".")),
                                ("Audiências (7 dias)", k["audiencias"]),
                                ("Com autos", f"{k['com_autos']}/{k['total']}")])
    filtros = ["<button class='fbtn on' data-f='todos' onclick='setf(this)'>todos</button>"]
    for t in sorted(dados["cobertura"]):
        filtros.append(f"<button class='fbtn' data-f='trib:{H.escape(t)}' onclick='setf(this)'>{H.escape(t)}</button>")
    filtros.append("<button class='fbtn' data-f='risco:alto' onclick='setf(this)'>risco alto</button>")
    filtros.append("<button class='fbtn' data-f='sit:ativo' onclick='setf(this)'>ativos</button>")
    acervo = "".join(bloco_proc(p, servidor) for p in sorted(
        dados["processos"], key=lambda x: ({"alto": 0, "medio": 1}.get(x["risco"], 2), x["id"])))
    selo = ("<span class='live'>● ao vivo</span>"
            "<button class='fbtn' onclick='location.reload()'>Atualizar</button> "
            if servidor else "")
    gaveta = ("<div id='drawer'><span class='x' onclick='fechard()'>✕</span>"
              "<h3 id='dtit'></h3><pre id='dbody'></pre></div>" if servidor else "")
    js = JS + (JS_SERVIDOR if servidor else "")
    cob = " ".join(
        f"<span class='chip {'c-suc' if v['autos']==v['total'] else 'c-war'}'>"
        f"{H.escape(t)} {v['autos']}/{v['total']}</span>"
        for t, v in sorted(dados["cobertura"].items()))
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SOJ · Painel do dia</title><style>{CSS}</style></head><body>
<header><div class="wrap"><h1>SOJ · <b>Painel do dia</b></h1>
<span class="dt">{selo}{HOJE:%d/%m/%Y} · gerado {datetime.now():%H:%M}</span></div></header>
<div class="wrap">
<div class="kpis">{kpis}</div>
<h2><span class="dot" style="background:var(--dan)"></span>Precisa de você hoje</h2>
{bloco_hoje(dados["hoje"], servidor)}
<h2><span class="dot" style="background:var(--acc)"></span>Preparado pelo robô — você assina</h2>
{bloco_robo(dados)}
<h2 id="acervo"><span class="dot" style="background:var(--gold)"></span>Acervo · {k['total']} processos</h2>
<div class="tools"><input id="busca" placeholder="buscar por cliente, número, classe…" oninput="filtrar()">
{''.join(filtros)}</div>
{acervo}
<div class="foot"><span style="color:var(--tx3)">Cobertura:</span> {cob}
<span class="chip c-mut">TRT-8 pendente</span></div>
</div>
{gaveta}<div id="toast"></div><script>{js}</script></body></html>"""


def main() -> None:
    soj.console_utf8()
    ap = argparse.ArgumentParser(description="Gera o painel do dia (HTML).")
    ap.add_argument("--sem-abrir", action="store_true", help="so gera, nao abre o navegador")
    args = ap.parse_args()
    if not PROCESSOS.exists():
        print("[painel] PROCESSOS/ nao existe."); sys.exit(1)
    # blindagem: uma ficha com YAML ilegivel some do painel — nao em silencio.
    quebradas = [f.name for f in sorted(PROCESSOS.glob("PROC-*.md"))
                 if "_audiencia" not in f.stem and not _fm(f)[0].get("tipo")]
    if quebradas:
        print(f"[painel] ⚠️  {len(quebradas)} ficha(s) com YAML ilegivel — "
              f"SOMEM do painel ate corrigir: {', '.join(quebradas)}")
    dados = carregar()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(render(dados), encoding="utf-8")
    k = dados["kpi"]
    print(f"[painel] {k['total']} processos, {k['com_autos']} com autos, "
          f"{len(dados['hoje'])} itens em 'precisa de voce hoje'.")
    print(f"[painel] {SAIDA}")
    if not args.sem_abrir:
        webbrowser.open(SAIDA.as_uri())


if __name__ == "__main__":
    main()
