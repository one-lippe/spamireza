#!/usr/bin/env python3
"""
Coletor CWL — Spamireza
Puxa os 5 clãs da família via API oficial do CoC (proxy RoyaleAPI) e gera:
  - cwl_data.json  : snapshot completo (elenco, rodadas, ataques, defesa)
  - injeta no index.html o bloco CLANS com: escalação (esc/res), timer (state/inicio/fim)
    e RANKING agregado das 7 rodadas (Índice, MVP, zonas de promoção/rebaixamento).

Modelo do Índice: 55% ataque + 20% defesa + 25% confiabilidade, x multiplicador de liga.
Token CoC: env COC_TOKEN  ou  ../COC - Coach/api/.token
Uso: python3 coletor_cwl.py
"""
import os, sys, json, re, urllib.request, urllib.parse, pathlib

PROXY = "https://cocproxy.royaleapi.dev/v1"
CLANS = [
    (1, "SpamiReza",     "#2J90U9GYP"),
    (2, "RezaSpamandu",  "#2R9CC2P02"),
    (3, "ScamiReza",     "#2CY9P2L9J"),
    (4, "RezaScamandu",  "#2JUQCYL9J"),
    (5, "e-SpamiReza",   "#2CPQQQ008"),
]
ROOT = pathlib.Path(__file__).resolve().parent
PESO_ATK, PESO_DEF, PESO_CONF, PISO, NMOV = 0.55, 0.20, 0.25, 3, 2

def token():
    if os.environ.get("COC_TOKEN"): return os.environ["COC_TOKEN"].strip()
    cands = [ROOT / ".token", ROOT / "COC_TOKEN.txt"]
    p = ROOT
    for _ in range(6):  # sobe as pastas procurando "COC - Coach/api/.token"
        cands.append(p / "COC - Coach" / "api" / ".token")
        p = p.parent
    for c in cands:
        if c.exists(): return c.read_text().strip()
    sys.exit("Token CoC não encontrado (defina COC_TOKEN ou tenha 'COC - Coach/api/.token' perto do projeto)")

TOK = token()
def get(path):
    req = urllib.request.Request(f"{PROXY}{path}", headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json", "User-Agent": "spamireza-cwl/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r: return r.status, json.load(r)
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)

def mult_liga(nome):
    if not nome: return 0.85
    # ordem checada do topo pro fundo (Titan/Legend adicionados em 2026, acima de Champion)
    base = {"legend": 1.15, "titan": 1.07, "champion": 1.00, "master": 0.93,
            "crystal": 0.83, "gold": 0.72, "silver": 0.62, "bronze": 0.55}
    passo = {0: 0.0, 1: -0.03, 2: -0.06}  # I, II, III
    n = nome.lower()
    tier = next((v for k, v in base.items() if k in n), 0.85)
    m = re.search(r"\b(iii|ii|i)\b", n)
    roman = {"i": 0, "ii": 1, "iii": 2}.get(m.group(1), 0) if m else 0
    return round(tier + passo[roman], 3)

def icones_ligas():
    """Ícones OFICIAIS das ligas, direto do CDN da Supercell (api-assets.clashofclans.com).
    O endpoint /leagues devolve nome + iconUrls; os nomes batem com o warLeague do clã
    ('Titan League III', 'Champion League I'...). Se falhar, o site cai no badge desenhado."""
    st, dados = get("/leagues?limit=200")
    if st != 200 or not isinstance(dados, dict):
        print("  ! ícones de liga indisponíveis (status", st, ")")
        return {}
    mapa = {}
    for l in dados.get("items", []):
        ic = l.get("iconUrls") or {}
        url = ic.get("medium") or ic.get("small") or ic.get("tiny")
        if l.get("name") and url:
            mapa[l["name"]] = url
    print(f"  ícones de liga: {len(mapa)}")
    return mapa


def coletar_cla(num, nome, tag):
    q = urllib.parse.quote(tag)
    out = {"num": num, "nome": nome, "tag": tag, "elenco": [], "rodadas": [],
           "atual": None, "liga": None, "mult": 0.85}
    st, lg = get(f"/clans/{q}/currentwar/leaguegroup")
    if st != 200 or not isinstance(lg, dict):
        out["erro"] = f"leaguegroup status {st}"; return out
    sc, ci = get(f"/clans/{q}")
    if isinstance(ci, dict):
        out["liga"] = (ci.get("warLeague") or {}).get("name")
        out["mult"] = mult_liga(out["liga"])
    me = next((c for c in lg.get("clans", []) if c.get("tag") == tag), None)
    if me:
        out["elenco"] = [{"nome": m.get("name"), "tag": m.get("tag"),
                          "th": m.get("townHallLevel")} for m in me.get("members", [])]
    war_tags = [wt for rd in lg.get("rounds", []) for wt in rd.get("warTags", []) if wt and wt != "#0"]
    for wt in war_tags:
        s, w = get(f"/clanwarleagues/wars/{urllib.parse.quote(wt)}")
        if not isinstance(w, dict): continue
        c, o = w.get("clan") or {}, w.get("opponent") or {}
        if tag not in (c.get("tag"), o.get("tag")): continue
        eu, adv = (c, o) if c.get("tag") == tag else (o, c)
        # TODAS as defesas: o bestOpponentAttack só mostra o pior tombo. Os ataques do
        # adversário trazem o defenderTag, então dá para contar cada defesa de verdade —
        # quem apanhou 3 vezes e segurou 2 não pode valer o mesmo que quem apanhou uma.
        sofridos = {}
        for am in adv.get("members", []):
            for a in am.get("attacks") or []:
                sofridos.setdefault(a.get("defenderTag"), []).append(
                    {"estrelas": a.get("stars"), "destr": a.get("destructionPercentage")})
        membros = []
        for m in eu.get("members", []):
            atks = m.get("attacks") or []
            bo = m.get("bestOpponentAttack") or {}
            membros.append({
                "nome": m.get("name"), "tag": m.get("tag"), "th": m.get("townhallLevel"),
                "pos": m.get("mapPosition"),
                "ataques": [{"estrelas": a.get("stars"), "destr": a.get("destructionPercentage")} for a in atks],
                "def_estrelas": bo.get("stars"), "def_destr": bo.get("destructionPercentage"),
                "defesas": sorted(sofridos.get(m.get("tag"), []),
                                  key=lambda x: -(x["estrelas"] or 0))})
        membros.sort(key=lambda x: x.get("pos") or 99)
        placar = lambda lado: {"est": lado.get("stars"), "destr": lado.get("destructionPercentage"),
                               "atk": lado.get("attacks")}
        out["rodadas"].append({"warTag": wt, "state": w.get("state"), "teamSize": w.get("teamSize"),
                               "adversario": adv.get("name"), "prep": w.get("preparationStartTime"),
                               "inicio": w.get("startTime"), "fim": w.get("endTime"),
                               "nos": placar(eu), "eles": placar(adv), "membros": membros})
    if out["rodadas"]:
        # prioriza guerra ATIVA (inWar) > preparação > encerrada; desempate pelo horário
        ordem = {"inWar": 3, "preparation": 2, "warEnded": 1, "notInWar": 0}
        out["atual"] = max(out["rodadas"],
                           key=lambda r: (ordem.get(r.get("state"), 0), r.get("inicio") or r.get("prep") or ""))
    return out

def agregar(out):
    """Ranking agregado das rodadas: Índice, MVP, confiabilidade, zona."""
    mult = out.get("mult") or 1.0
    agg = {}
    for rd in out["rodadas"]:
        if rd.get("state") not in ("inWar", "warEnded"):
            continue  # rodada em preparação ainda não é oportunidade (ninguém pôde atacar)
        for m in rd["membros"]:
            a = agg.setdefault(m["tag"], {"nome": m["nome"], "tag": m["tag"], "th": m["th"],
                                          "rounds": 0, "atk": 0, "est": 0, "destr": 0.0,
                                          "defsof": 0, "defcnt": 0, "defneg": 0, "defseg": 0})
            a["nome"], a["th"] = m["nome"], m["th"]; a["rounds"] += 1
            for at in m["ataques"]:
                a["atk"] += 1; a["est"] += at["estrelas"] or 0; a["destr"] += at["destr"] or 0
            defesas = m.get("defesas")
            if defesas:   # cada ataque sofrido conta como uma defesa
                for d in defesas:
                    e = d["estrelas"] or 0
                    a["defsof"] += e; a["defcnt"] += 1; a["defneg"] += (3 - e)
                    if e < 3: a["defseg"] += 1
            elif m.get("def_estrelas") is not None:   # dado antigo, sem a lista de defesas
                ds = m["def_estrelas"]
                a["defsof"] += ds; a["defcnt"] += 1; a["defneg"] += (3 - ds)
                if ds < 3: a["defseg"] += 1
    rank = []
    for a in agg.values():
        atk = a["atk"]; spa = a["est"] / atk if atk else 0
        notaAtk = spa / 3 * 100
        conf = min(1, atk / a["rounds"]) if a["rounds"] else 0
        # defesa só entra no índice se a vila foi atacada; senão os pesos se redistribuem
        comps = [(PESO_ATK, notaAtk), (PESO_CONF, conf * 100)]
        notaDef = None
        if a["defcnt"] > 0:
            notaDef = (1 - (a["defsof"] / a["defcnt"]) / 3) * 100
            comps.append((PESO_DEF, notaDef))
        wsum = sum(p for p, _ in comps) or 1
        idx = (sum(p * v for p, v in comps) / wsum) * mult
        sof = round(a["defsof"] / a["defcnt"], 1) if a["defcnt"] else None  # estrelas sofridas/defesa
        rank.append({"n": a["nome"], "tag": a["tag"], "th": a["th"], "atk": atk, "est": a["est"],
                     "spa": round(spa, 2), "conf": round(conf * 100),
                     "def": (round(notaDef) if notaDef is not None else None),
                     "sof": sof, "ndef": a["defcnt"], "seg": a["defseg"], "idx": round(idx, 1),
                     "idxb": round(idx, 1), "amostra": 100,
                     "mvp": a["est"] + a["defneg"]})

    # --- Peso por amostra (shrinkage) ---------------------------------------
    # Quem atacou em poucas guerras tem amostra pequena: 2 ataques perfeitos não
    # provam o mesmo que 7. O índice desses jogadores é puxado na direção da
    # média do clã, proporcional à fração de guerras que ele jogou.
    #   w = ataques / guerras de batalha da temporada
    #   idx = idx_bruto * w + media * (1 - w)
    # Só puxa PARA BAIXO: quem está abaixo da média não ganha nota por ter
    # jogado pouco (senão bastaria atacar pouco para herdar a média do clã).
    guerras = sum(1 for rd in out["rodadas"] if rd.get("state") in ("inWar", "warEnded"))
    if guerras:
        base = [x["idx"] for x in rank if x["atk"] >= PISO] or [x["idx"] for x in rank if x["atk"] > 0]
        if base:
            media = sum(base) / len(base)
            for x in rank:
                w = min(1.0, x["atk"] / guerras)
                x["amostra"] = round(w * 100)
                if w < 1 and x["idxb"] > media:
                    x["idx"] = round(x["idxb"] * w + media * (1 - w), 1)

    rank.sort(key=lambda x: -x["idx"])
    total_atk = sum(x["atk"] for x in rank); n = len(rank); c = out["num"]
    for i, x in enumerate(rank):
        x["pos"] = i + 1
        if x["atk"] < PISO: x["zona"] = "—"
        elif c > 1 and x["pos"] <= NMOV: x["zona"] = "promo"
        elif c < 5 and x["pos"] > n - NMOV: x["zona"] = "rebx"
        else: x["zona"] = "—"
    return rank, ("rank" if total_atk > 0 else "esc")

def detalhe_jogadores(out):
    """Histórico guerra a guerra por jogador (tag -> lista de guerras), para o popup
    de auditoria do site: em cada guerra, o que atacou e quanto sofreu na defesa."""
    rods = [rd for rd in out["rodadas"] if rd.get("state") in ("inWar", "warEnded")]
    tags = {m["tag"] for rd in rods for m in rd["membros"]}
    det = {t: [] for t in tags}
    for i, rd in enumerate(rods, 1):
        porTag = {m["tag"]: m for m in rd["membros"]}
        for t in tags:
            m = porTag.get(t)
            if m is None:  # não escalado nessa guerra: neutro, não é oportunidade
                det[t].append({"g": i, "vs": rd.get("adversario"), "st": rd.get("state"), "fora": True})
            else:
                defs = m.get("defesas")
                if not defs and m.get("def_estrelas") is not None:
                    defs = [{"estrelas": m["def_estrelas"], "destr": m.get("def_destr")}]
                det[t].append({"g": i, "vs": rd.get("adversario"), "st": rd.get("state"),
                               "pos": m.get("pos"),
                               "a": [{"e": a["estrelas"], "d": a["destr"]} for a in m["ataques"]],
                               "df": [{"e": x["estrelas"], "d": x["destr"]} for x in (defs or [])],
                               "d": m.get("def_estrelas"), "dd": m.get("def_destr")})
    return det


def build_clans_js(dados):
    j = lambda v: json.dumps(v, ensure_ascii=False)
    linhas = []
    for d in dados:
        atual = d.get("atual")
        rank, mode = agregar(d)
        placar = {"nos": None, "eles": None}
        falta = []
        if atual:
            esc = [m["nome"] for m in atual["membros"]]
            esc_tags = {m["tag"] for m in atual["membros"]}
            res = [e["nome"] for e in d["elenco"] if e["tag"] not in esc_tags]
            vs = atual["adversario"]; tam = f'{atual["teamSize"]} x {atual["teamSize"]}'
            state, inicio, fim = atual["state"], atual["inicio"], atual["fim"]
            placar = {"nos": atual.get("nos"), "eles": atual.get("eles")}
            if state == "inWar":   # quem ainda não usou o ataque na guerra que está rolando
                falta = [{"n": m["nome"], "th": m.get("th"), "pos": m.get("pos")}
                         for m in atual["membros"] if not m["ataques"]]
                falta.sort(key=lambda x: x.get("pos") or 99)
        else:
            esc, res, vs, tam, state, inicio, fim = [], [e["nome"] for e in d["elenco"]], None, None, None, None, None
        rodadas = d.get("rodadas") or []
        liga_fim = len(rodadas) >= 7 and all(r.get("state") == "warEnded" for r in rodadas)
        linhas.append(
            f' {d["num"]}:{{nome:{j(d["nome"])},vs:{j(vs)},tam:{j(tam)},liga:{j(d["liga"])},'
            f'state:{j(state)},inicio:{j(inicio)},fim:{j(fim)},mode:{j(mode)},ligaFim:{j(liga_fim)},'
            f'placar:{j(placar)},falta:{j(falta)},'
            f'esc:{j(esc)},res:{j(res)},rank:{j(rank)},det:{j(detalhe_jogadores(d))}}}')
    return "const CLANS={\n" + ",\n".join(linhas) + "\n};\n"


def build_hist_js(dados):
    """Bloco HIST: resultado de cada temporada arquivada + a corrente, por jogador,
    para o popup mostrar a evolução liga a liga e para o Hall da Fama.
    Temporadas antigas não têm tag (o coletor só passou a gravar depois), então a
    chave cai para o nome quando a tag não existe."""
    hd = ROOT / "historico"
    temporadas = {}
    if hd.exists():
        for fp in sorted(hd.glob("*.json")):
            if fp.stem.endswith("_detalhe") or fp.stem == "temporada_fechada":
                continue
            try:
                arq = json.loads(fp.read_text(encoding="utf-8"))
            except Exception:
                continue
            clas = arq.get("clas") or arq          # 2026-07.json antigo não tem "clas"
            season, jog = fp.stem, []
            for cnum, c in clas.items():
                for p in c.get("rank", []):
                    if not p.get("atk"):
                        continue
                    jog.append({"k": p.get("tag") or p.get("n"), "n": p.get("n"),
                                "c": int(cnum), "cn": c.get("nome"), "liga": c.get("liga"),
                                "idx": p.get("idx"), "pos": p.get("pos"), "atk": p.get("atk"),
                                "spa": p.get("spa"), "mvp": p.get("mvp")})
            if jog:
                temporadas[season] = jog
    # a temporada corrente vem do que acabou de ser coletado (o arquivo pode estar atrás)
    import datetime
    atualss = datetime.datetime.utcnow().strftime("%Y-%m")
    corrente = []
    for d in dados:
        rank, _ = agregar(d)
        for p in rank:
            if p["atk"]:
                corrente.append({"k": p.get("tag") or p["n"], "n": p["n"], "c": d["num"],
                                 "cn": d["nome"], "liga": d.get("liga"), "idx": p["idx"],
                                 "pos": p["pos"], "atk": p["atk"], "spa": p["spa"], "mvp": p["mvp"]})
    if corrente:
        temporadas[atualss] = corrente
    return "const HIST=" + json.dumps(temporadas, ensure_ascii=False) + ";\n"

def salvar_historico(dados):
    """Arquiva o resultado da temporada atual (YYYY-MM) para preservar histórico
    entre ligas — a API só expõe a temporada corrente.
    BLINDAGEM: mescla por clã e NUNCA sobrescreve os dados de um clã por dados
    com MENOS ataques. Assim, quando a API zera um clã ao fim da liga, o resultado
    final já arquivado é preservado (evita a perda de dados de julho/26)."""
    import datetime
    season = datetime.datetime.utcnow().strftime("%Y-%m")
    hd = ROOT / "historico"; hd.mkdir(exist_ok=True)
    fp = hd / f"{season}.json"
    try:
        atual = json.loads(fp.read_text(encoding="utf-8"))
        clas = atual.get("clas", {})
    except Exception:
        clas = {}
    mudou = False
    for d in dados:
        rank, mode = agregar(d)
        k = str(d["num"])
        novo_atk = sum(p.get("atk", 0) for p in rank)
        ant = clas.get(k)
        ant_atk = sum(p.get("atk", 0) for p in (ant or {}).get("rank", []))
        if ant is None or novo_atk >= ant_atk:  # só grava se não regride
            clas[k] = {"nome": d["nome"], "liga": d["liga"], "mode": mode, "rank": rank}
            mudou = True
    if not mudou:
        return
    fp.write_text(json.dumps(
        {"season": season, "atualizado": datetime.datetime.utcnow().isoformat() + "Z", "clas": clas},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("historico:", season, "salvo")

def salvar_detalhe(dados):
    """Arquiva o DETALHE guerra-a-guerra (quem atacou em cada guerra, com quantas
    estrelas) por temporada, em historico/<season>_detalhe.json. Permite dizer depois
    'fulano furou a guerra X'. Blindado igual ao historico: só atualiza um clã se o novo
    tiver >= ataques (nunca perde dado quando a API zera a temporada encerrada).
    Fica no repositório (git), mas NÃO é publicado no site (só index.html vai pro Pages)."""
    import datetime
    season = datetime.datetime.utcnow().strftime("%Y-%m")
    hd = ROOT / "historico"; hd.mkdir(exist_ok=True)
    fp = hd / f"{season}_detalhe.json"
    try:
        clas = json.loads(fp.read_text(encoding="utf-8")).get("clas", {})
    except Exception:
        clas = {}
    mudou = False
    for d in dados:
        rods = [r for r in d.get("rodadas", []) if r.get("state") in ("inWar", "warEnded")]
        guerras, total_atk = [], 0
        for i, r in enumerate(rods, 1):
            jog = []
            for m in r["membros"]:
                ats = [a.get("estrelas") for a in m.get("ataques", [])]
                total_atk += len(ats)
                jog.append({"nome": m["nome"], "tag": m["tag"], "th": m.get("th"),
                            "atk": ats, "def_est": m.get("def_estrelas")})
            guerras.append({"g": i, "vs": r.get("adversario"), "state": r.get("state"),
                            "size": r.get("teamSize"), "jogadores": jog})
        k = str(d["num"])
        ant = clas.get(k)
        ant_atk = sum(len(j.get("atk", [])) for g in (ant or {}).get("guerras", [])
                      for j in g.get("jogadores", [])) if ant else -1
        if ant is None or total_atk >= ant_atk:  # só grava se não regride
            clas[k] = {"nome": d["nome"], "liga": d["liga"], "guerras": guerras}
            mudou = True
    if not mudou:
        return
    fp.write_text(json.dumps(
        {"season": season, "atualizado": datetime.datetime.utcnow().isoformat() + "Z", "clas": clas},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print("detalhe:", season, "salvo (guerra a guerra)")

def injetar_no_html(clans_js, hist_js=None, ligas_js=None):
    idx = ROOT / "index.html"
    html = idx.read_text(encoding="utf-8")
    html = re.sub(r"const CLANS=\{.*?\n\};\s*", clans_js, html, count=1, flags=re.DOTALL)
    if hist_js:
        # HIST é sempre UMA linha (json sem quebras) — casar só até o fim da linha
        html = re.sub(r"const HIST=.*\n", hist_js, html, count=1)
    if ligas_js:
        html = re.sub(r"const LIGAS=.*\n", ligas_js, html, count=1)
    html = html.replace("const locked=c===5;", "const locked=CLANS[c].vs===null;")
    idx.write_text(html, encoding="utf-8")
    (ROOT / "Dashboard_Spamireza.html").write_text(html, encoding="utf-8")
    # o Hall da Fama é página própria e só precisa do HIST
    hall = ROOT / "hall.html"
    if hall.exists():
        h = hall.read_text(encoding="utf-8")
        if hist_js:  h = re.sub(r"const HIST=.*\n", hist_js, h, count=1)
        if ligas_js: h = re.sub(r"const LIGAS=.*\n", ligas_js, h, count=1)
        hall.write_text(h, encoding="utf-8")

MARCADOR = ROOT / "historico" / "temporada_fechada.json"


def season_atual():
    import datetime
    return datetime.datetime.utcnow().strftime("%Y-%m")


def congelado():
    """True se a temporada corrente já terminou e foi congelada.
    Se o marcador for de uma temporada anterior (virou o mês), ele é apagado aqui
    mesmo — a liga nova volta a coletar sozinha, sem religar nada na mão."""
    try:
        marca = json.loads(MARCADOR.read_text(encoding="utf-8"))
    except Exception:
        return False
    if marca.get("season") == season_atual():
        return True
    MARCADOR.unlink(missing_ok=True)
    print("temporada nova detectada — descongelando o coletor")
    return False


def temporada_encerrada(dados):
    """Todo clã que jogou tem as 7 rodadas e todas já acabaram."""
    comdados = [d for d in dados if d.get("rodadas")]
    return bool(comdados) and all(
        len(d["rodadas"]) >= 7 and all(r.get("state") == "warEnded" for r in d["rodadas"])
        for d in comdados)


def congelar(dados):
    import datetime
    MARCADOR.parent.mkdir(exist_ok=True)
    MARCADOR.write_text(json.dumps({
        "season": season_atual(),
        "congelado_em": datetime.datetime.utcnow().isoformat() + "Z",
        "clas": {str(d["num"]): d.get("liga") for d in dados if d.get("rodadas")},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("TEMPORADA ENCERRADA -> resultado congelado; o coletor para até a próxima liga")


def main():
    if congelado():
        print("temporada congelada — nada a fazer (o site mantém o resultado final)")
        return
    dados = []
    print("Coletando CWL dos 5 clãs...")
    for num, nome, tag in CLANS:
        d = coletar_cla(num, nome, tag); dados.append(d)
        at = d.get("atual")
        _, mode = agregar(d)
        if at:
            esc = len(at["membros"]); res = len(d["elenco"]) - esc
            print(f"  Clã {num} {nome:14} vs {at['adversario']:16} {at['teamSize']}x{at['teamSize']} "
                  f"| {esc} esc + {res} res | {d['liga']} (x{d['mult']}) | modo={mode} | {at['state']}")
        else:
            print(f"  Clã {num} {nome:14} — sem guerra ativa  {d.get('erro','')}")
    (ROOT / "cwl_data.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    salvar_historico(dados)
    salvar_detalhe(dados)
    ligas_js = "const LIGAS=" + json.dumps(icones_ligas(), ensure_ascii=False) + ";\n"
    injetar_no_html(build_clans_js(dados), build_hist_js(dados), ligas_js)
    if temporada_encerrada(dados):
        congelar(dados)
    print("OK -> index.html + historico + detalhe atualizados")

if __name__ == "__main__":
    main()
