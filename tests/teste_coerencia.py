import asyncio, os, sys
from playwright.async_api import async_playwright

CASOS = [
  # (prob, imp, resposta, dono, gatilho, acao, trecho esperado no alerta, rotulo)
  (5,4,"aceitar","Ana","uso cai 40%","",        'severidade alta com resposta "Aceitar"', "alto + aceitar"),
  (3,3,"aceitar","Ana","",           "",        "aceito(s) sem ação escrita",             "medio + aceitar sem acao"),
  (5,4,"mitigar","Ana","",           "plano X", "sem gatilho",                            "alto sem gatilho"),
  (2,2,"aceitar","Ana","",           "",        None,                                     "baixo + aceitar (nao alerta)"),
]

async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        for prob, imp, resp, dono, gat, acao, esperado, rotulo in CASOS:
            await pg.evaluate("""o => {
                state.riscos = [];
                addRisco();
                const r = state.riscos[0];
                r.descricao="Teste"; r.probabilidade=o.p; r.impacto=o.i;
                r.resposta=o.r; r.dono=o.d; r.gatilho=o.g; r.acao=o.a;
                renderRiscos();
            }""", {"p":prob,"i":imp,"r":resp,"d":dono,"g":gat,"a":acao})
            await pg.wait_for_timeout(220)
            txt = await pg.evaluate("document.getElementById('riscoMatriz').innerText")
            sev = prob*imp
            if esperado:
                ok = esperado in txt
                print(f"  sev {sev:>2} {rotulo:<28} alerta: {'SIM' if ok else 'NAO'}")
                if not ok: falhas.append(f"{rotulo}: alerta ausente")
            else:
                limpo = "Nenhum risco de severidade alta sem tratamento" in txt
                print(f"  sev {sev:>2} {rotulo:<28} sem alerta: {'SIM' if limpo else 'NAO'}")
                if not limpo: falhas.append(f"{rotulo}: alertou sem motivo")
        if errs: falhas.append("erro JS: "+errs[0][:60])
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> COERENCIA OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
