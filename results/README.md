# Resultados de exemplo

Estes arquivos são relatórios didáticos históricos, gerados sobre as bases em `data/` antes da versão integrada do programa.

- `lista_antes_log10.txt`: variáveis selecionadas pelo primeiro Shapiro-Wilk;
- `log10.txt`: confirmação das colunas transformadas;
- `transformacao_percentual.txt`: confirmação das colunas percentuais transformadas;
- `Shapiro_final.txt`: verificação da normalidade depois das transformações;
- os demais relatórios contêm os testes apropriados para cada desenho experimental.

Para novas execuções, use `run_workflow.py`. Cada execução cria `results/generated/run_AAAAMMDD_HHMMSS/` com tabela transformada, verificações de normalidade, testes, resumo e `manifest.json`; essa pasta é ignorada pelo Git para não misturar resultados pessoais com os exemplos do repositório.

Os resultados são didáticos e sintéticos.
