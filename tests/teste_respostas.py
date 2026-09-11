import asyncio, os, sys
from playwright.async_api import async_playwright
ESPERADO = {
 "evitar":"inaceitavel", "mitigar":"controla a causa",
 "transferir":"muda quem paga", "aceitar":"supera o dano esperado",
}
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        await pg.evaluate("goToStep(11); addRisco();"); await pg.wait_for_timeout(250)
        for resp, trecho in ESPERADO.items():
            await pg.evaluate("r => { state.riscos[0].resposta = r; renderRiscos(); }", resp)
            await pg.wait_for_timeout(200)
            txt = await pg.evaluate("document.getElementById('riscoContainer').innerText")
            ok = trecho in txt
            print(f"  {resp:<11} ancora visivel: {'SIM' if ok else 'NAO'}")
            if not ok: falhas.append(f"ancora de '{resp}' ausente")
        # as tres perguntas orientadoras aparecem na etapa
        passo = await pg.evaluate("document.querySelector('[data-step=\"11\"]').innerText")
        tem = ("pode acontecer" in passo.lower()) and ("controlo a causa" in passo.lower())
        print(f"  perguntas orientadoras na etapa: {'SIM' if tem else 'NAO'}")
        if not tem: falhas.append("perguntas orientadoras ausentes")
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> ANCORAS DE RESPOSTA OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
