#!/usr/bin/env python3
"""
Elenco atual — Spamireza
Puxa a lista de membros ATUAIS de cada um dos 5 clãs (endpoint /clans/{tag}/members)
e grava elenco_atual.json: tag -> {nome, cla, cla_nome, th, cargo}.

Isso responde "de qual clã o jogador É hoje", independente de onde ele JOGOU a CWL
(jogador emprestado para outro clã na liga continua sendo do clã de origem).

Token CoC: env COC_TOKEN
Uso: python3 elenco_atual.py
"""
import os, sys, json, urllib.request, urllib.parse, pathlib, datetime

PROXY = "https://cocproxy.royaleapi.dev/v1"
CLANS = [
    (1, "SpamiReza",     "#2J90U9GYP"),
    (2, "RezaSpamandu",  "#2R9CC2P02"),
    (3, "ScamiReza",     "#2CY9P2L9J"),
    (4, "RezaScamandu",  "#2JUQCYL9J"),
    (5, "e-SpamiReza",   "#2CPQQQ008"),
]
ROOT = pathlib.Path(__file__).resolve().parent

def token():
    if os.environ.get("COC_TOKEN"):
        return os.environ["COC_TOKEN"].strip()
    for c in [ROOT / ".token", ROOT / "COC_TOKEN.txt"]:
        if c.exists():
            return c.read_text().strip()
    sys.exit("Token CoC não encontrado (defina COC_TOKEN)")

TOK = token()

def get(path):
    req = urllib.request.Request(f"{PROXY}{path}", headers={
        "Authorization": f"Bearer {TOK}", "Accept": "application/json",
        "User-Agent": "spamireza-elenco/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, json.load(r)
    except Exception as e:
        return getattr(e, "code", "ERR"), str(e)

def main():
    membros = {}
    resumo = []
    for num, nome, tag in CLANS:
        st, data = get(f"/clans/{urllib.parse.quote(tag)}/members")
        if st != 200 or not isinstance(data, dict):
            resumo.append(f"  Clã {num} {nome:14} — ERRO {st}")
            continue
        itens = data.get("items", []) or []
        for m in itens:
            membros[m.get("tag")] = {
                "nome": m.get("name"),
                "cla": num,
                "cla_nome": nome,
                "th": m.get("townHallLevel"),
                "cargo": m.get("role"),
            }
        resumo.append(f"  Clã {num} {nome:14} — {len(itens)} membros")

    out = {
        "atualizado": datetime.datetime.utcnow().isoformat() + "Z",
        "membros": membros,
    }
    (ROOT / "elenco_atual.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Elenco atual dos 5 clãs:")
    for l in resumo:
        print(l)
    print(f"OK -> elenco_atual.json ({len(membros)} jogadores no total)")

if __name__ == "__main__":
    main()
