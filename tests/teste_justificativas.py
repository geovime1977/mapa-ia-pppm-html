import asyncio, json, os, glob, re, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True)
        for arq in sorted(glob.glob("exemplos/*.json")):
            d=json.load(open(arq,encoding="utf-8"))
            pg=await b.new_page()
            await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
            await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
            n = await pg.evaluate("""Object.values(state.business_cases)
                 .filter(function(bc){ return String(bc.decisao_justificativa||"").length > 20; }).length""")
            await pg.evaluate("goToStep(11)"); await pg.wait_for_timeout(300)
            await pg.evaluate("goToStep(13)"); await pg.wait_for_timeout(500)
            rel = await pg.evaluate("document.getElementById('finalReport').innerHTML")
            limpo = re.sub(r"<[^>]+>","",rel)
            amostra = list(d["business_cases"].values())[0]["decisao_justificativa"][:38]
            no_pdf = amostra in limpo
            print(f"{os.path.basename(arq)}: justificativas no state={n}/3 | aparece no relatorio: {no_pdf}")
            if n!=3: falhas.append(f"{arq}: {n}/3 justificativas")
            if not no_pdf: falhas.append(f"{arq}: justificativa nao chega ao relatorio/PDF")
            await pg.close()
        await b.close()
    print("\n"+("FALHAS:\n  "+"\n  ".join(falhas) if falhas else ">>> JUSTIFICATIVAS OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
