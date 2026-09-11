"""Verifica que os exemplos em exemplos/*.json carregam completos no app.

Executar da raiz do repositorio:
    python tests/teste_exemplos.py
"""
import asyncio, json, os, sys, glob
from playwright.async_api import async_playwright

async def main():
    falhas=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True)
        for arq in sorted(glob.glob("exemplos/*.json")):
            dados=json.load(open(arq,encoding="utf-8"))
            pg=await b.new_page(viewport={"width":1100,"height":900})
            errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto("file://"+os.path.abspath("index.html")); await pg.wait_for_timeout(350)
            await pg.evaluate("d => { localStorage.clear(); hidratarState(d); }", dados)
            await pg.wait_for_timeout(250)
            r = await pg.evaluate("""({
              nome: state.identificacao.nome,
              diag: Object.values(state.diagnostico).filter(v=>v>0).length,
              mapa: Object.values(state.mapa).filter(v=>v && v.length>10).length,
              casos: state.casos.length,
              gov: Object.keys(state.governanca).length,
              bcs: Object.keys(state.business_cases).length,
              sel: state.selecionados.length,
              projetos: state.projetos.length,
              riscos: state.riscos.length,
              rec: (state.recomendacao_texto||"").length,
              op_preenchido: Object.values(state.business_cases).filter(function(bc){
                 const o=(bc.beneficios||{}).operacional||{};
                 return (Number(o.horas_economizadas_mes)||0)>0 && (Number(o.pessoas_impactadas)||0)>0 && (Number(o.custo_hora)||0)>0;
              }).length,
              est_preenchido: Object.values(state.business_cases).filter(function(bc){
                 const e=(bc.beneficios||{}).estrategico||{};
                 return String(e.velocidade_decisao||"").length>10;
              }).length
            })""")
            # etapa 11 herda da 10; so depois disso o relatorio tem o comparativo
            await pg.evaluate("goToStep(11)"); await pg.wait_for_timeout(400)
            r["projetos"] = await pg.evaluate("state.projetos.length")
            await pg.evaluate("goToStep(13)"); await pg.wait_for_timeout(450)
            rel = await pg.evaluate("document.getElementById('finalReport').innerHTML")
            import re as _re
            limpo=_re.sub(r"<[^>]+>","",rel)
            ok_rel = ("Business case comparativo" in limpo) and ("Riscos priorizados" in limpo)
            base=os.path.basename(arq)
            print(f"{base}")
            print(f"   nome={r['nome'][:34]!r} diag={r['diag']}/5 mapa={r['mapa']}/5 casos={r['casos']} gov={r['gov']} bc={r['bcs']} sel={r['sel']} proj={r['projetos']} riscos={r['riscos']} rec={r['rec']}ch")
            print(f"   camadas: operacional={r['op_preenchido']}/3  estrategico={r['est_preenchido']}/3")
            print(f"   relatorio com comparativo+riscos: {ok_rel}")
            for cond,msg in [(r['diag']==5,"diagnostico incompleto"),(r['mapa']==5,"mapa incompleto"),
                             (r['casos']>=3,"poucos casos"),(r['gov']>=3,"governanca incompleta"),
                             (r['bcs']>=2,"business cases faltando"),(r['sel']>=3,"selecionados faltando"),
                             (r['projetos']>=3,"heranca da etapa 11 nao trouxe os casos"),(r['riscos']>=4,"riscos faltando"),
                             (r['rec']>100,"recomendacao curta"),(ok_rel,"relatorio sem secoes novas"),
                             (r['op_preenchido']==3,"camada operacional incompleta"),
                             (r['est_preenchido']==3,"camada estrategica incompleta")]:
                if not cond: falhas.append(f"{base}: {msg}")
            if errs: falhas.append(f"{base}: erro JS {errs[0][:70]}")
            await pg.close()
        await b.close()
    print("\n" + ("FALHAS:\n  "+"\n  ".join(falhas) if falhas else ">>> OS 3 EXEMPLOS CARREGAM COMPLETOS"))
    return 1 if falhas else 0
sys.exit(asyncio.run(main()))
