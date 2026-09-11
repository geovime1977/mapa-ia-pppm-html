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
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(400)   # herda projetos
        await pg.evaluate("goToStep(12)"); await pg.wait_for_timeout(400)   # popula recomendacao
        await pg.evaluate("goToStep(13)"); await pg.wait_for_timeout(550)
        html = await pg.evaluate("document.getElementById('finalReport').innerHTML")
        limpo = re.sub(r"<[^>]+>", "", html)
        marcos = ["Business case comparativo","Riscos priorizados","Recomendação executiva"]
        pos = {m: limpo.find(m) for m in marcos}
        print("posicao no relatorio:")
        for m,v in sorted(pos.items(), key=lambda x:x[1]): print(f"   {v:>6}  {m}")
        if any(v<0 for v in pos.values()): falhas.append(f"secao ausente: {[m for m,v in pos.items() if v<0]}")
        else:
            if not (pos["Business case comparativo"] < pos["Riscos priorizados"] < pos["Recomendação executiva"]):
                falhas.append("recomendacao nao esta depois de comparativo e riscos")
        # a recomendacao precisa ter conteudo, nao so o titulo
        trecho = d["recomendacao_texto"][:40]
        print("recomendacao preenchida no relatorio:", trecho in limpo)
        if trecho not in limpo: falhas.append("texto da recomendacao ausente no relatorio")
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> ORDEM DO RELATORIO OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
