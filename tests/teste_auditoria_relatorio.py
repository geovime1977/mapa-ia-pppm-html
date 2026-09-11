import asyncio, json, os, re
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True); pg=await b.new_page()
        pg.on("dialog", lambda d: asyncio.create_task(d.accept()))
        await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(300)
        d=json.load(open("exemplos/exemplo-1-construtora.json",encoding="utf-8"))
        await pg.evaluate("x => { localStorage.clear(); hidratarState(x); }", d)
        for n in (9,10,11,12,13):
            await pg.evaluate(f"goToStep({n})"); await pg.wait_for_timeout(350)
        rel = re.sub(r"<[^>]+>"," ", await pg.evaluate("document.getElementById('finalReport').innerHTML"))
        rel = re.sub(r"\s+"," ", rel)
        print("=== secoes no relatorio ===")
        for h in re.findall(r'<h3>([^<]{0,50})', await pg.evaluate("document.getElementById('finalReport').innerHTML")):
            print("   ", h)
        print("\n=== auditoria de campos ===")
        i=d["identificacao"]; c0=d["casos"][0]; g0=list(d["governanca"].values())[0]
        bc0=list(d["business_cases"].values())[0]
        checks = [
         ("identificacao: nome",       i["nome"][:18]),
         ("identificacao: empresa",    i["empresa"][:14]),
         ("identificacao: cargo",      i["cargo"][:12]),
         ("identificacao: turma",      i["turma"][:14]),
         ("identificacao: porte",      i["porte"][:10]),
         ("mapa: contexto",            d["mapa"]["contexto"][:26]),
         ("mapa: dor",                 d["mapa"]["dor"][:26]),
         ("mapa: dados",               d["mapa"]["dados"][:26]),
         ("mapa: riscos",              d["mapa"]["riscos"][:26]),
         ("mapa: valor",               d["mapa"]["valor"][:26]),
         ("caso: rotulo",              c0["rotulo"][:22]),
         ("caso: descricao",           c0["descricao"][:26]),
         ("caso: dor",                 c0["dor"][:20]),
         ("caso: dono",                c0["dono"][:14]),
         ("governanca: responsavel",   g0["responsavel"][:16]),
         ("governanca: validador",     g0["validador"][:14]),
         ("governanca: metrica",       g0["metrica"][:20]),
         ("bc: linha de base",         bc0["linha_de_base"][:26]),
         ("bc: caso de uso",           bc0["caso_uso"][:22]),
         ("bc: dados/validacao",       bc0["dados"][:22]),
         ("bc: premissa financeira",   bc0["beneficios"]["financeiro"]["premissa"][:24]),
         ("bc: premissa operacional",  bc0["beneficios"]["operacional"]["premissa"][:24]),
         ("bc: estrategico velocidade",bc0["beneficios"]["estrategico"]["velocidade_decisao"][:24]),
         ("bc: justificativa decisao", bc0["decisao_justificativa"][:24]),
         ("risco: descricao",          d["riscos"][0]["descricao"][:24]),
         ("risco: gatilho",            d["riscos"][0]["gatilho"][:22]),
         ("risco: acao acordada",      d["riscos"][0]["acao"][:22]),
         ("recomendacao",              d["recomendacao_texto"][:26]),
        ]
        faltando=[]
        for nome, trecho in checks:
            ok = trecho and trecho in rel
            print(f"   {'OK ' if ok else 'FALTA'}  {nome}")
            if not ok: faltando.append(nome)
        print(f"\nFALTANDO NO RELATORIO ({len(faltando)}):")
        for f in faltando: print("   -", f)
        await b.close()
asyncio.run(main())
