#!/usr/bin/env python3
"""TEMPORÁRIO: despeja o JSON cru da API para descobrir onde está a liga da temporada atual."""
import os, json, urllib.request, urllib.parse, pathlib
PROXY="https://cocproxy.royaleapi.dev/v1"
TOK=os.environ["COC_TOKEN"].strip()
def get(p):
    r=urllib.request.Request(f"{PROXY}{p}",headers={"Authorization":f"Bearer {TOK}","Accept":"application/json","User-Agent":"dbg/1.0"})
    try:
        with urllib.request.urlopen(r,timeout=25) as x: return x.status, json.load(x)
    except Exception as e: return getattr(e,"code","ERR"), str(e)

out={}
st,p=get("/players/"+urllib.parse.quote("#99220V0Q8"))
out["player_Nesk"]={"status":st,"chaves":sorted(p.keys()) if isinstance(p,dict) else p,
                    "amostra":{k:v for k,v in p.items() if isinstance(v,(str,int,float,dict)) and not isinstance(v,list)} if isinstance(p,dict) else None}
st,m=get("/clans/"+urllib.parse.quote("#2J90U9GYP")+"/members?limit=3")
out["clan_members"]={"status":st,"items":(m.get("items") if isinstance(m,dict) else m)}
st,l=get("/leagues?limit=200")
out["leagues"]={"status":st,"nomes":[x.get("name") for x in l.get("items",[])] if isinstance(l,dict) else l}
for extra in ["/warleagues?limit=200","/capitalleagues?limit=50","/builderbaseleagues?limit=50"]:
    st,d=get(extra)
    out[extra]={"status":st,"nomes":[x.get("name") for x in d.get("items",[])] if isinstance(d,dict) else str(d)[:200]}
pathlib.Path("debug_api.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
print("ok")
