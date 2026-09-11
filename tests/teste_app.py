"""Teste end-to-end do Mapa IA-PPPM (etapas 11, 12 e relatorio final).

Requer playwright. Executar a partir da raiz do repositorio:
    python tests/teste_app.py

Verifica o que quebraria na mao do aluno: calculo de ROI e payback,
severidade de risco, presenca das secoes no relatorio, persistencia local
e ausencia de rolagem horizontal em tela de celular (390px).
"""
import asyncio, os, sys
from playwright.async_api import async_playwright
ARQ = "file://" + os.path.abspath("index.html")

async def main():
    falhas = []
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        pg = await b.new_page(viewport={"width":390,"height":844})  # tamanho de celular
        erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.on("console", lambda m: erros.append("console:"+m.text) if m.type=="error" else None)
        await pg.goto(ARQ)
        await pg.wait_for_timeout(600)

        total = await pg.evaluate("TOTAL_STEPS")
        print("TOTAL_STEPS:", total)
        if total != 13: falhas.append(f"TOTAL_STEPS={total}, esperado 13")

        # etapa 11 — projeto com numeros conhecidos
        await pg.evaluate("goToStep(11)")
        await pg.wait_for_timeout(300)
        vis = await pg.evaluate("document.querySelector('[data-step=\"11\"]').classList.contains('active')")
        print("etapa 11 visivel:", vis)
        if not vis: falhas.append("etapa 11 nao ficou ativa")

        await pg.evaluate("""
          addProjeto();
          const p = state.projetos[0];
          p.economia_anual = 120000; p.custo_tecnologia = 50000; p.janela_meses = 12; p.cenario = 'provavel';
          renderProjetos();
        """)
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("calcProjeto(state.projetos[0])")
        print("calculo:", {k:(round(v,2) if isinstance(v,(int,float)) else v) for k,v in r.items() if k in ('beneficioAjustado','investimento','beneficioLiquido','roi','payback')})
        # esperado: benef 120000, inv 50000, BL 70000, ROI 140%, payback 5 meses
        if round(r["roi"],1) != 140.0: falhas.append(f"ROI={r['roi']}, esperado 140")
        if round(r["payback"],1) != 5.0: falhas.append(f"payback={r['payback']}, esperado 5")

        tabela = await pg.evaluate("document.getElementById('projComparativo').innerText.length")
        print("comparativo renderizado:", tabela > 50)
        if tabela <= 50: falhas.append("comparativo nao renderizou")

        # etapa 12 — risco
        await pg.evaluate("goToStep(12); addRisco(); state.riscos[0].probabilidade=5; state.riscos[0].impacto=4; state.riscos[0].descricao='Base de dados incompleta'; renderRiscos();")
        await pg.wait_for_timeout(300)
        sev = await pg.evaluate("severidade(state.riscos[0])")
        print("severidade (5x4):", sev)
        if sev != 20: falhas.append(f"severidade={sev}, esperado 20")
        crit = await pg.evaluate("document.getElementById('riscoMatriz').innerText.includes('severidade alta')")
        print("alerta de severidade alta:", crit)
        if not crit: falhas.append("nao alertou risco de severidade alta")

        # relatorio final
        await pg.evaluate("goToStep(13)")
        await pg.wait_for_timeout(400)
        rel = await pg.evaluate("document.getElementById('finalReport').innerHTML")
        import re as _re
        limpo = _re.sub(r"<[^>]+>", "", rel)
        print("relatorio tem comparativo:", "Business case comparativo" in limpo)
        print("relatorio tem riscos:", "Riscos priorizados" in limpo)
        if "Business case comparativo" not in limpo: falhas.append("relatorio sem comparativo")
        if "Riscos priorizados" not in limpo: falhas.append("relatorio sem riscos")

        # persistencia
        salvo = await pg.evaluate("localStorage.getItem('mapa-ia-pppm-v2') !== null")
        print("persistencia gravou:", salvo)
        if not salvo: falhas.append("localStorage nao gravou")

        # rolagem horizontal no celular
        over = await pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 2")
        print("rola horizontal no celular (ruim se True):", over)
        if over: falhas.append("layout estoura a largura no celular")

        if erros: falhas.append("erros JS: " + "; ".join(erros[:3]))
        await b.close()
    print("\n" + ("FALHAS:\n  " + "\n  ".join(falhas) if falhas else ">>> TODOS OS TESTES PASSARAM"))
    return 1 if falhas else 0

sys.exit(asyncio.run(main()))
