# Diretiva de Contexto Global

Sempre consulte as configurações, comandos e subagentes definidos em `~/.claude/` antes de executar tarefas complexas.

---

# CLAUDE.md — mapa-ia-pppm-html

## Sobre este projeto

- **O que faz:** versão HTML standalone (arquivo único) do app `mapa-ia-pppm`. Cobre Aula 1 (diagnóstico 5D + Mapa 5 Blocos) e Aula 2 (priorização 5 critérios + matriz + governança + recomendação) do Prof. Bezerra. Cada aluno/consultor baixa o `.html` e abre no browser — funciona offline, sem servidor, em qualquer OS. Alternativa portátil à versão Streamlit.
- **Stack:** HTML5 + CSS3 + JS puro (nenhuma dependência externa, nenhum CDN)
- **Como rodar:** `open ~/projetos/mapa-ia-pppm-html/index.html`
- **Status:** ativo

## Localização

- **Local:** `~/projetos/mapa-ia-pppm-html/`
- **Backup:** `onedrive-eixoestrategico10:repos/mapa-ia-pppm-html`
- **GitHub:** `geovime1977/mapa-ia-pppm-html` (a criar; sugerido privado)
- **Nota no vault:** `01 - Profissional/Projetos/mapa-ia-pppm-html.md` (a criar via vault-writer)

## Estrutura

```
mapa-ia-pppm-html/
├── index.html              # arquivo único — CSS e JS inline
├── README.md               # instruções de uso e distribuição
├── CLAUDE.md               # este arquivo
└── _referencia/            # NÃO EDITAR (regra de bancos de terceiros)
    ├── aula-2-original.html
    └── README-aula-2-original.txt
```

## Comandos principais

```bash
# Abrir localmente
open ~/projetos/mapa-ia-pppm-html/index.html

# Servir via HTTP (opcional — só se algum browser bloquear file://)
cd ~/projetos/mapa-ia-pppm-html && python3 -m http.server 8000

# Backup
rclone copy . onedrive-eixoestrategico10:repos/mapa-ia-pppm-html \
  --exclude ".git/**"

# Tamanho do arquivo (deve ficar < 300KB)
wc -c index.html
```

## Contexto relevante

- **Projeto-irmão:** `~/projetos/mapa-ia-pppm/` (Streamlit v1.3, porta 8513). Este HTML é o port standalone da mesma lógica.
- **Fonte da lógica portada:** `src/recomendacao.py`, `src/priorizacao.py`, `src/diagnostico.py`, `src/glossario.py` (todos do projeto Streamlit).
- **Fonte dos dados embutidos:** `data/dimensoes.json`, `data/niveis.json`, `data/criterios_priorizacao.json`, `data/governanca.json`, `data/glossario.json` (todos copiados exatos para dentro do JS do `index.html`).
- **Schema de import compatível:** aceita JSON exportado tanto por este HTML quanto pela v1.3 Streamlit (função `hidratarState` normaliza os dois formatos).
- **Regra de terceiros:** `_referencia/aula-2-original.html` é o app do Prof. Bezerra — jamais editar. Serve apenas como referência de paleta e estrutura; o `index.html` foi escrito autoralmente.
- **Telemetria:** stub via `TELEMETRIA_URL` no topo do script. Deixar vazio esconde o botão. Preencher com endpoint Apps Script para ativar coleta anônima (payload documentado em `enviarTelemetria()`).
- **Distribuição:** copiar `index.html` para OneDrive público, GitHub Pages ou anexar no e-mail para a turma. Zero setup do aluno.

## Trilogia PPPM

- `diag-ia-pppm` (Streamlit, porta 8511) — diagnóstico 5D + Mapa 5 Blocos + 3 pilotos
- `mapa-ia-pppm` (Streamlit, porta 8513) — versão completa Aulas 1 e 2
- **`mapa-ia-pppm-html`** (HTML standalone) — este projeto, distribuível offline
- `consultor-ia-pppm` (Streamlit, porta 8509) — consultor
