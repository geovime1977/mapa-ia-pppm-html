import asyncio, json, os, re, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(350)
        await pg.evaluate("goToStep(12)"); await pg.wait_for_timeout(350)
        await pg.evaluate("goToStep(13)"); await pg.wait_for_timeout(550)
        limpo = re.sub(r"<[^>]+>","", await pg.evaluate("document.getElementById('finalReport').innerHTML"))
        checks = {
          "secao de origem": "Origem dos dados e responsabilidades" in limpo,
          "nome do responsavel": d["identificacao"]["nome"][:18] in limpo,
          "cargo": d["identificacao"]["cargo"][:10] in limpo,
          "aviso de nao auditoria": "Não audita" in limpo or "não audita" in limpo,
          "decisao tem dono": "cabe a quem tem alçada" in limpo,
          "recomendacao antes da declaracao": limpo.find("Recomendação executiva") < limpo.find("Origem dos dados"),
        }
        for k,v in checks.items():
            print(f"  {k:<34} {'ok' if v else 'ERRO'}")
            if not v: falhas.append(k)
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> DECLARACAO OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
