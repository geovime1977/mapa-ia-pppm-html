import asyncio, os, sys
from playwright.async_api import async_playwright
ESPERADO = {1:"Baixo",4:"Baixo",5:"Medio",12:"Medio",13:"Medio",14:"Medio",15:"Alto",20:"Alto",25:"Alto"}
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        print("sev -> faixa")
        for sev, esp in ESPERADO.items():
            r = await pg.evaluate("s => faixaRisco(s).rotulo", sev)
            ok = "ok" if r==esp else f"ERRO (esperado {esp})"
            print(f"  {sev:>2} -> {r:<6} {ok}")
            if r!=esp: falhas.append(f"sev {sev}: {r} != {esp}")
        # nenhuma severidade possivel pode ficar sem faixa
        vazios = await pg.evaluate("""(() => { const out=[];
          for(let pr=1;pr<=5;pr++) for(let im=1;im<=5;im++){
            const s=pr*im; const f=RISCO_CFG.faixas.find(x=> s>=x.min && s<=x.max);
            if(!f) out.push(s);
          } return [...new Set(out)]; })()""")
        print("severidades sem faixa:", vazios or "nenhuma")
        if vazios: falhas.append(f"sem faixa: {vazios}")
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> FAIXAS OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
