import asyncio, os, sys
from playwright.async_api import async_playwright
ESPERADO = {
 "evitar":"eliminar a causa", "mitigar":"reduz a probabilidade",
 "transferir":"clausula contratual", "aceitar":"rotina de monitoramento",
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
            await pg.wait_for_timeout(180)
            ph = await pg.evaluate("""(function(){
               const ins = document.querySelectorAll('#riscoContainer input[type=text]');
               for(const i of ins){ if((i.placeholder||'').startsWith('Padrão:')) return i.placeholder; }
               return '';
            })()""")
            ok = trecho in ph
            print(f"  {resp:<11} placeholder: {ph[:62]!r} {'ok' if ok else 'ERRO'}")
            if not ok: falhas.append(f"placeholder de '{resp}'")
        # o valor digitado nao pode ser apagado pelo placeholder
        await pg.evaluate("state.riscos[0].acao='Padronizar template em 3 obras'; renderRiscos();")
        await pg.wait_for_timeout(180)
        val = await pg.evaluate("""(function(){
           const ins=document.querySelectorAll('#riscoContainer input[type=text]');
           for(const i of ins){ if(i.value.includes('Padronizar')) return i.value; } return '';
        })()""")
        print(f"  valor digitado preservado: {val!r}")
        if "Padronizar" not in val: falhas.append("valor digitado sumiu")
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> PLACEHOLDERS OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
