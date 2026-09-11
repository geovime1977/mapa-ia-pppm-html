import asyncio, json, os, sys
from playwright.async_api import async_playwright
async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True)
        pg=await b.new_page(viewport={"width":1100,"height":900})
        dialogs=[]
        pg.on("dialog", lambda d: (dialogs.append(d.message), asyncio.create_task(d.accept())))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(350)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8")); d["projetos"]=[]
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)

        # 1) primeira visita: deve herdar sozinho, sem alert
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(450)
        n1 = await pg.evaluate("state.projetos.length")
        print("1) entrada automatica -> projetos:", n1, "| alertas:", len(dialogs))
        if n1 != 3: falhas.append(f"auto-heranca trouxe {n1}, esperado 3")
        if dialogs: falhas.append("entrada automatica nao deveria alertar")

        # 2) usuario edita e sai/volta: nao pode sobrescrever
        await pg.evaluate("state.projetos[0].rotulo='EDITADO PELO USUARIO'; state.projetos.pop(); salvarLocal();")
        await pg.evaluate("goToStep(9)"); await pg.wait_for_timeout(200)
        await pg.evaluate("goToStep(10)"); await pg.wait_for_timeout(400)
        n2 = await pg.evaluate("state.projetos.length")
        rot = await pg.evaluate("state.projetos[0].rotulo")
        print("2) voltando depois de editar -> projetos:", n2, "| primeiro rotulo:", rot)
        if n2 != 2 or rot != "EDITADO PELO USUARIO": falhas.append("entrada automatica sobrescreveu edicao do usuario")

        # 3) re-sincronizar manual: restaura os 3 e avisa
        dialogs.clear()
        await pg.evaluate("trazerDaEtapa9(false)"); await pg.wait_for_timeout(400)
        n3 = await pg.evaluate("state.projetos.length")
        print("3) re-sincronizar -> projetos:", n3, "| avisou:", len(dialogs)>0)
        if n3 != 3: falhas.append(f"re-sincronizar trouxe {n3}, esperado 3")
        if not dialogs: falhas.append("re-sincronizar deveria avisar")

        # 4) projeto manual sobrevive a re-sincronizacao
        await pg.evaluate("addProjeto(); state.projetos[state.projetos.length-1].rotulo='Fornecedor externo';")
        await pg.evaluate("trazerDaEtapa9(false)"); await pg.wait_for_timeout(350)
        manuais = await pg.evaluate("state.projetos.filter(p=>!p.origem_caso).map(p=>p.rotulo)")
        print("4) manuais preservados na re-sincronizacao:", manuais)
        if "Fornecedor externo" not in manuais: falhas.append("re-sincronizar apagou projeto manual")
        await b.close()
    print("\n"+("FALHAS: "+"; ".join(falhas) if falhas else ">>> AUTO-HERANCA OK"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
