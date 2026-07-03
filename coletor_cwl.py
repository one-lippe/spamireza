#!/usr/bin/env python3
"""
Coletor CWL — Spamireza
Puxa os 5 clãs da família via API oficial do CoC (proxy RoyaleAPI) e gera:
  - cwl_data.json  : snapshot completo (elenco, rodadas, escalação, ataques, defesa)
  - injeta os dados no index.html (bloco CLANS) e sincroniza Dashboard_Spamireza.html

Token CoC: env COC_TOKEN  ou  ../COC - Coach/api/.token
Uso: python3 coletor_cwl.py
"""
import os, sys, json, re, urllib.request, urllib.parse, pathlib

PROXY = "https://cocproxy.royaleapi.dev/v1"
CLANS = [  # (nº, nome, tag)
    (1, "SpamiReza",     "#2J90U9GYP"),
    (2, "RezaSpamandu",  "#2R9CC2P02"),
    (3, "ScamiReza",     "#2CY9P2L9J"),
    (4, "RezaScamandu",  "#2JUQCYL9J"),
    (5, "e-SpamiReza",   "#2CPQQQ008"),
]
ROOT = pathlib.Path(__file__).resolve().parent

def token():
    if os.environ.get("COC_TOKEN"): return os.environ["COC_TOKEN"].strip()
    for p in [ROOT/".token", ROOT/"COC_TOKEN.txt", ROOT/".."/"COC - Coach"/"api"/".token"]:
        if p.exists(): return p.read_text().strip()
    sys.exit("Token CoC não encontrado (env COC_TOKEN ou ../COC - Coach/api/.token)")

TOK = token()
def get(path):
    req = urllib.request.Request(f"{PROXY}{path}", headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json", "User-Agent": "spamireza-cwl/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r: return r.status, json.load(r)
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)

def coletar_cla(num, nome, tag):
    q = urllib.parse.quote(tag)
    st, lg = get(f"/clans/{q}/currentwar/leaguegroup")
    out = {"num": num, "nome": nome, "tag": tag, "estado_grupo": None,
           "elenco": [], "rodadas": [], "atual": None}
    if st != 200 or not isinstance(lg, dict):
        out["erro"] = f"leaguegroup status {st}"
        return out
    out["estado_grupo"] = lg.get("state")
    me = next((c for c in lg.get("clans", []) if c.get("tag") == tag), None)
    if me:
        out["elenco"] = [{"nome": m.get("name"), "tag": m.get("tag"),
                          "th": m.get("townHallLevel")} for m in me.get("members", [])]
    # todas as guerras da família nesse clã
    war_tags = [wt for rd in lg.get("rounds", []) for wt in rd.get("warTags", []) if wt and wt != "#0"]
    for wt in war_tags:
        s, w = get(f"/clanwarleagues/wars/{urllib.parse.quote(wt)}")
        if not isinstance(w, dict): continue
        c, o = w.get("clan") or {}, w.get("opponent") or {}
        if tag not in (c.get("tag"), o.get("tag")): continue
        eu, adv = (c, o) if c.get("tag") == tag else (o, c)
        membros = []
        for m in eu.get("members", []):
            atks = m.get("attacks") or []
            bo = m.get("bestOpponentAttack") or {}
            membros.append({
                "nome": m.get("name"), "tag": m.get("tag"), "th": m.get("townhallLevel"),
                "pos": m.get("mapPosition"),
                "ataques": [{"estrelas": a.get("stars"), "destr": a.get("destructionPercentage")} for a in atks],
                "def_estrelas": bo.get("stars"), "def_destr": bo.get("destructionPercentage"),
            })
        membros.sort(key=lambda x: x.get("pos") or 99)
        rodada = {"warTag": wt, "state": w.get("state"), "teamSize": w.get("teamSize"),
                  "adversario": adv.get("name"), "prep": w.get("preparationStartTime"),
                  "inicio": w.get("startTime"), "fim": w.get("endTime"), "membros": membros}
        out["rodadas"].append(rodada)
    # rodada "atual" = a mais recente disponível (maior prep)
    if out["rodadas"]:
        out["atual"] = max(out["rodadas"], key=lambda r: r.get("prep") or "")
    return out

def build_clans_js(dados):
    linhas = []
    for d in dados:
        atual = d.get("atual")
        if atual:
            esc = [m["nome"] for m in atual["membros"]]
            esc_tags = {m["tag"] for m in atual["membros"]}
            res = [e["nome"] for e in d["elenco"] if e["tag"] not in esc_tags]
            vs = atual["adversario"]; tam = f'{atual["teamSize"]} x {atual["teamSize"]}'
        else:
            esc, res, vs, tam = [], [e["nome"] for e in d["elenco"]], None, None
        j = lambda v: json.dumps(v, ensure_ascii=False)
        linhas.append(f' {d["num"]}:{{nome:{j(d["nome"])},vs:{j(vs)},tam:{j(tam)},'
                      f'esc:{j(esc)},res:{j(res)}}}')
    return "const CLANS={\n" + ",\n".join(linhas) + "\n};\n"

def injetar_no_html(clans_js):
    idx = ROOT / "index.html"
    html = idx.read_text(encoding="utf-8")
    html = re.sub(r"const CLANS=\{.*?\};\s*", clans_js, html, count=1, flags=re.DOTALL)
    # destrava qualquer clã que tenha guerra (vs != null)
    html = html.replace("const locked=c===5;", "const locked=CLANS[c].vs===null;")
    idx.write_text(html, encoding="utf-8")
    (ROOT / "Dashboard_Spamireza.html").write_text(html, encoding="utf-8")

def main():
    dados = []
    print("Coletando CWL dos 5 clãs...")
    for num, nome, tag in CLANS:
        d = coletar_cla(num, nome, tag)
        dados.append(d)
        at = d.get("atual")
        if at:
            esc = len(at["membros"]); res = len(d["elenco"]) - esc
            print(f"  Clã {num} {nome:14} vs {at['adversario']:18} {at['teamSize']}x{at['teamSize']} "
                  f"| {esc} esc + {res} res | state={at['state']}")
        else:
            print(f"  Clã {num} {nome:14} — sem guerra ativa (elenco: {len(d['elenco'])})  {d.get('erro','')}")
    (ROOT / "cwl_data.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    injetar_no_html(build_clans_js(dados))
    print("OK -> cwl_data.json + index.html atualizados")

if __name__ == "__main__":
    main()
