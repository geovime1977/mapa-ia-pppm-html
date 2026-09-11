import asyncio, json, os, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True)
        pg=await b.new_page(viewport={"width":1100,"height":900})
        pg.on("dialog", lambda d: asyncio.create_task(d.accept()))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(350)
        dados=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        # zera os projetos para provar que a heranca reconstroi a partir da etapa 9
        dados["projetos"]=[]
        await pg.evaluate("d => { localStorage.clear(); hidratarState(d); }", dados)
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(300)
        print("projetos antes:", await pg.evaluate("state.projetos.length"))
        await pg.evaluate("trazerDaEtapa9()"); await pg.wait_for_timeout(400)
        n = await pg.evaluate("state.projetos.length")
        print("projetos apos trazer da etapa 9:", n)
        detalhe = await pg.evaluate("""state.projetos.map(p => ({
            rotulo: p.rotulo, origem: p.origem_caso || null,
            economia: p.economia_anual,
            inv: p.custo_tecnologia+p.custo_dados+p.custo_pessoas+p.custo_mudanca+p.custo_governanca,
            cenario: p.cenario
        }))""")
        for d in detalhe: print("   ", d)
        # confere paridade com a etapa 9
        par = await pg.evaluate("""state.projetos.filter(p=>p.origem_caso).every(function(p){
            const bc = state.business_cases[p.origem_caso];
            const inv = Object.values(bc.custos).reduce((s,c)=>s+(Number(c.valor)||0),0);
            const eco = Number(bc.beneficios.financeiro.economia_anual)||0;
            const meu = p.custo_tecnologia+p.custo_dados+p.custo_pessoas+p.custo_mudanca+p.custo_governanca;
            return inv===meu && eco===p.economia_anual && bc.cenario===p.cenario;
        })""")
        print("paridade exata com a etapa 9:", par)
        if n != 3: falhas.append(f"esperado 3 projetos, veio {n}")
        if not par: falhas.append("numeros divergem da etapa 9")
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> HERANCA OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
