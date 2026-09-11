import asyncio, os, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page(viewport={"width":1100,"height":900})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        await pg.evaluate("goToStep(12); addRisco(); state.riscos[0].probabilidade=4; state.riscos[0].impacto=5; renderRiscos();")
        await pg.wait_for_timeout(300)
        txt = await pg.evaluate("document.getElementById('riscoContainer').innerText")
        print("select mostra rotulo da nota:", "4 — Alta" in txt or "Alta" in txt)
        print("ancora de probabilidade visivel:", "iniciativa recente" in txt)
        print("ancora de impacto por dimensao:", ("Prazo:" in txt and "Custo:" in txt and "Escopo:" in txt))
        for cond,msg in [("Alta" in txt,"rotulo da nota ausente"),
                         ("iniciativa recente" in txt,"ancora de probabilidade ausente"),
                         ("Prazo:" in txt,"ancora de impacto ausente")]:
            if not cond: falhas.append(msg)
        sev = await pg.evaluate("severidade(state.riscos[0])")
        faixa = await pg.evaluate("faixaRisco(severidade(state.riscos[0])).rotulo")
        print(f"severidade 4x5 = {sev} -> {faixa}")
        if sev!=20 or faixa!="Alto": falhas.append("classificacao errada")
        over = await pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
        print("estoura largura:", over)
        if over: falhas.append("layout estourou")
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> ANCORAS OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
