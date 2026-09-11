import asyncio, json, os, sys, re
from playwright.async_api import async_playwright
ESPERADO = ["Identificação","Diagnóstico","Mapa Inicial","Cadastro de casos","Avaliação dos casos",
            "Matriz","Governança","Seleção","Business Case preliminar","Business Case comparativo",
            "Sessão de riscos","Recomendação executiva"]
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page(viewport={"width":1100,"height":900})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("dialog", lambda d: asyncio.create_task(d.accept()))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(350)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
        print("ordem das etapas:")
        for n in range(1,13):
            await pg.evaluate(f"goToStep({n})"); await pg.wait_for_timeout(260)
            tit = await pg.evaluate(f"""(function(){{
               const s=document.querySelector('[data-step="{n}"]');
               const h=s?s.querySelector('h2'):null;
               return {{titulo:h?h.innerText.trim():'(sem h2)', ativo:s?s.classList.contains('active'):false}};
            }})()""")
            ok = ESPERADO[n-1].lower() in tit["titulo"].lower()
            print(f"   {n:>2}. {tit['titulo'][:44]:<46} ativo={tit['ativo']} {'ok' if ok else 'ERRO'}")
            if not ok: falhas.append(f"etapa {n}: esperado '{ESPERADO[n-1]}', veio '{tit['titulo'][:30]}'")
            if not tit["ativo"]: falhas.append(f"etapa {n} nao ficou ativa")
        # comparativo herdou e riscos renderizaram nas posicoes novas
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(400)
        proj = await pg.evaluate("state.projetos.length")
        await pg.evaluate("goToStep(11)"); await pg.wait_for_timeout(300)
        ris = await pg.evaluate("document.getElementById('riscoMatriz').innerText.length")
        await pg.evaluate("goToStep(12)"); await pg.wait_for_timeout(400)
        sug = await pg.evaluate("(document.getElementById('suggestionText')||{}).innerHTML || ''")
        await pg.evaluate("goToStep(13)"); await pg.wait_for_timeout(500)
        rel = re.sub(r"<[^>]+>","", await pg.evaluate("document.getElementById('finalReport').innerHTML"))
        print(f"\n   etapa 10 herdou projetos: {proj}")
        print(f"   etapa 11 renderizou riscos: {ris>50}")
        print(f"   etapa 12 gerou sugestao: {len(sug)>50}")
        print(f"   relatorio tem comparativo+riscos+justificativa: "
              f"{('Business case comparativo' in rel) and ('Riscos priorizados' in rel) and ('Justificativa' in rel)}")
        if proj!=3: falhas.append(f"etapa 10 herdou {proj} projetos")
        if ris<=50: falhas.append("etapa 11 nao renderizou riscos")
        if len(sug)<=50: falhas.append("etapa 12 nao gerou sugestao de recomendacao")
        if errs: falhas.append("erro JS: "+errs[0][:70])
        await b.close()
    print("\n"+("FALHAS:\n  "+"\n  ".join(falhas) if falhas else ">>> NOVA ORDEM OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
