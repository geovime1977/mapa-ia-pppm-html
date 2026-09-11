import asyncio, json, os, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        pg.on("dialog", lambda d: asyncio.create_task(d.accept()))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
        await pg.evaluate("goToStep(9)"); await pg.wait_for_timeout(450)
        r = await pg.evaluate("""({
            cards: document.querySelectorAll('#bcContainer .bc-card').length,
            vazio: document.getElementById('bcContainer').innerText.includes('Cadastre casos'),
            chars: document.getElementById('bcContainer').innerText.length
        })""")
        print(f"etapa 9 -> cards: {r['cards']} | mensagem de vazio: {r['vazio']} | texto: {r['chars']} chars")
        if r["cards"] < 3: falhas.append(f"esperado 3 cards, veio {r['cards']}")
        if r["vazio"]: falhas.append("mostrou mensagem de vazio")
        await b.close()
    print(">>> ETAPA 9 OK" if not falhas else "FALHAS: "+"; ".join(falhas))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
