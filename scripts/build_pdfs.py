#!/usr/bin/env python3
"""Gera os PDFs de docs/ a partir dos .md correspondentes.

Pipeline: markdown → HTML estilizado → PDF via Chrome headless.
Requer: markdown (pip) + Google Chrome instalado no macOS.

Uso:
    .venv/bin/python scripts/build_pdfs.py

Saída:
    docs/MANUAL-DO-CONSULTOR.pdf
    docs/ANEXO-CONSULTOR.pdf
    docs/TERMO-DE-RESPONSABILIDADE.pdf
"""
from __future__ import annotations
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.exit("Faltam dependências. Rode: .venv/bin/pip install markdown")

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page { size: A4; margin: 2cm 2cm 2.2cm 2cm; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif;
       color: #1a1a1a; line-height: 1.55; font-size: 11pt; }
h1 { color: #a91b1b; font-size: 22pt; border-bottom: 3px solid #a91b1b;
     padding-bottom: 6px; margin-top: 24pt; }
h2 { color: #a91b1b; font-size: 15pt; margin-top: 22pt;
     border-bottom: 1px solid #e0e0e0; padding-bottom: 3px; }
h3 { color: #333; font-size: 12.5pt; margin-top: 16pt; }
h4 { color: #555; font-size: 11.5pt; margin-top: 12pt; }
p  { margin: 6pt 0; text-align: justify; }
code { font-family: "SF Mono", Consolas, monospace; font-size: 9.5pt;
       background: #f4f4f4; padding: 1px 4px; border-radius: 3px; }
pre  { background: #f7f7f7; border: 1px solid #e0e0e0; padding: 10px 14px;
       border-radius: 4px; font-size: 9pt; overflow-x: auto; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; margin: 12pt 0; width: 100%;
        font-size: 9.5pt; page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: 5px 8px; vertical-align: top;
         text-align: left; }
th { background: #a91b1b; color: #fff; font-weight: 600; }
tr:nth-child(even) td { background: #fafafa; }
blockquote { border-left: 4px solid #a91b1b; margin: 10pt 0;
             padding: 4pt 12pt; color: #444; background: #fdf7f7; }
ul, ol { margin: 6pt 0 6pt 22pt; }
li { margin: 3pt 0; }
strong { color: #111; }
hr { border: none; border-top: 1px solid #ddd; margin: 20pt 0; }
.footer { color: #888; font-size: 8pt; text-align: right; margin-top: 18pt;
          border-top: 1px solid #eee; padding-top: 4pt; }
"""

HTML_TPL = """<!DOCTYPE html>
<html lang="pt-br"><head><meta charset="utf-8"><title>{title}</title>
<style>{css}</style></head><body>{body}
<div class="footer">Mapa IA-PPPM · v1.2 · Prof. Dr. José Bezerra (BSBr)
&middot; Consultor: Geovane Virmecati (Eixo Estratégico)</div>
</body></html>
"""

def md_to_pdf(md_file: Path, pdf_file: Path) -> None:
    text = md_file.read_text(encoding="utf-8")
    body = markdown.markdown(
        text,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    html = HTML_TPL.format(title=md_file.stem, css=CSS, body=body)
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(html)
        tmp_path = Path(tmp.name)
    try:
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_file}",
                tmp_path.as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    finally:
        tmp_path.unlink(missing_ok=True)
    print(f"PDF gerado: {pdf_file} ({pdf_file.stat().st_size // 1024} KB)")

def main() -> None:
    for name in ("MANUAL-DO-CONSULTOR", "ANEXO-CONSULTOR", "TERMO-DE-RESPONSABILIDADE"):
        md = DOCS / f"{name}.md"
        pdf = DOCS / f"{name}.pdf"
        if not md.exists():
            print(f"AVISO: {md} não existe, pulando.")
            continue
        md_to_pdf(md, pdf)

    # o termo tambem sai em .docx: e documento para o consultor editar
    # (preencher identificacao, ajustar clausulas com advogado), nao so imprimir
    termo_md = DOCS / "TERMO-DE-RESPONSABILIDADE.md"
    if termo_md.exists():
        conv = Path.home() / ".claude" / "scripts" / "md_to_docx.py"
        if conv.exists():
            docx = DOCS / "TERMO-DE-RESPONSABILIDADE.docx"
            r = subprocess.run([sys.executable, str(conv), str(termo_md), str(docx)],
                               capture_output=True, text=True)
            if r.returncode == 0:
                print(f"DOCX gerado: {docx} ({docx.stat().st_size // 1024} KB)")
            else:
                print(f"aviso: docx do termo falhou — {r.stderr.strip().splitlines()[-1:]}")


if __name__ == "__main__":
    main()
