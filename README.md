# Mapa IA-PPPM — versão HTML standalone

Aplicativo de mesa (single-file HTML) que operacionaliza as **Aulas 1 e 2** da Formação de Consultores em IA aplicada ao PPPM do **Prof. Dr. José Bezerra (BSBr)**.

Roda 100% no navegador. Sem servidor, sem instalação, sem coleta de dados. O aluno baixa `index.html`, dá duplo clique e usa.

## Como usar

1. Baixe o arquivo `index.html` (ou clone este repositório).
2. Dê duplo clique — ele abre no seu navegador padrão (Chrome, Safari, Firefox ou Edge).
3. Preencha as 10 etapas em ordem:
   1. Identificação
   2. Diagnóstico de maturidade (5 dimensões)
   3. Mapa Inicial (5 blocos)
   4. Cadastro dos casos de uso
   5. Avaliação dos casos (5 critérios ponderados)
   6. Matriz Impacto × Viabilidade
   7. Governança & HITL
   8. Seleção dos 3 prioritários
   9. Recomendação executiva (sugestão automática editável)
   10. Relatório final
4. No relatório final, use os botões:
   - **Exportar PDF** — abre o diálogo de impressão do navegador; escolha "Salvar como PDF".
   - **Exportar CSV** — baixa uma planilha dos casos avaliados.
   - **Salvar JSON** — baixa o estado completo (retomar depois com "Carregar progresso" na Etapa 1).

## O que ele faz

- Calcula o **nível de maturidade** (0-3) a partir das 5 dimensões da Aula 1.
- Identifica o **gargalo** (dimensão com menor nota).
- Aplica os **5 critérios ponderados da Aula 2** (impacto 0,30 · viabilidade 0,20 · dados 0,20 · risco 0,15 · valor 0,15).
- Classifica cada caso em **Fazer agora / Preparar / Não priorizar**.
- Aplica o **corte obrigatório**: sem dono humano declarado + governança completa, o caso não vira "Fazer agora".
- Sugere o **nível de HITL** (leve / estruturada / executiva) com base no impacto.
- Gera uma **recomendação executiva** com template determinístico usando os dados preenchidos.
- Exporta em PDF, CSV e JSON.

## O que ele NÃO faz

- Não envia nenhum dado para servidor externo por padrão (o campo de telemetria opt-in fica oculto se não configurado).
- Não salva automaticamente entre sessões — use "Salvar JSON" para preservar o progresso.
- Não substitui o julgamento humano — é ferramenta de apoio à decisão executiva, não decisor.

## Distribuição

O arquivo pesa menos de 100 KB e roda offline. Pode ser distribuído por:

- E-mail (anexo direto)
- OneDrive / Google Drive (link de download)
- GitHub Pages (link público)
- Compartilhamento local pelo AirDrop / pendrive

## Licença

Uso educacional para os alunos da Formação BSBr. Adaptado autoralmente pela **Eixo Estratégico** a partir do material do Prof. Bezerra.

O arquivo `_referencia/aula-2-original.html` pertence ao Prof. Bezerra e é preservado apenas como referência técnica.

---

**Eixo Estratégico** · v1.0 HTML · baseado na v1.3 Streamlit (`mapa-ia-pppm`).
