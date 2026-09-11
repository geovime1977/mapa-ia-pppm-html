"""Percorre o app CLICANDO nos botoes, do inicio ao relatorio.

Existe porque o teste que usava goToStep() direto nao pegou uma renumeracao
errada dos botoes: a etapa de riscos pulava a recomendacao e ia direto ao
relatorio, deixando a recomendacao vazia no PDF.
"""
import asyncio, json, os, re, sys
from playwright.async_api import async_playwright

async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True)
        pg=await b.new_page(viewport={"width":1100,"height":900})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("dialog", lambda d: asyncio.create_task(d.accept()))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(350)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
        await pg.evaluate("goToStep(1)"); await pg.wait_for_timeout(250)

        visitadas=[]
        for _ in range(20):
            atual = await pg.evaluate("""(function(){
                const s=document.querySelector('.step.active');
                return s ? Number(s.dataset.step) : null;
            })()""")
            if atual is None: falhas.append("nenhuma etapa ativa"); break
            visitadas.append(atual)
            if atual == 13: break
            clicou = await pg.evaluate("""(function(){
                const s=document.querySelector('.step.active');
                const bs=[...s.querySelectorAll('button')];
                const av=bs.find(x=>/Avançar|Continuar|Gerar relatório/i.test(x.textContent));
                if(!av) return false; av.click(); return true;
            })()""")
            if not clicou: falhas.append(f"etapa {atual}: sem botao de avanco"); break
            await pg.wait_for_timeout(420)

        print("caminho percorrido pelos botoes:", " → ".join(map(str, visitadas)))
        esperado = list(range(1,14))
        if visitadas != esperado:
            falhas.append(f"caminho {visitadas} != {esperado}")
        # a recomendacao precisa estar preenchida ao chegar no relatorio
        rel = re.sub(r"<[^>]+>","", await pg.evaluate("document.getElementById('finalReport').innerHTML"))
        trecho = d["recomendacao_texto"][:40]
        print("recomendacao no relatorio:", trecho in rel)
        if trecho not in rel: falhas.append("recomendacao vazia no relatorio")
        if errs: falhas.append("erro JS: "+errs[0][:70])
        await b.close()
    print("\n"+("FALHAS:\n  "+"\n  ".join(falhas) if falhas else ">>> NAVEGACAO POR BOTOES OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
