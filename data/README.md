# Bases de dados

As bases são tabelas sintéticas de treinamento com 60 observações e 14 colunas numéricas. Elas usam TAB como separador e duas linhas de cabeçalho: grupo/momento na primeira e variável na segunda.

## Base independente

`base_workflow_independente.txt`

- `Controle` e `Tratamento` são grupos independentes;
- adequada para Mann–Whitney, Levene e t independente/Welch;
- contém variáveis normais, uma porcentagem e variáveis positivas assimétricas.

## Base pareada

`base_workflow_pareado.txt`

- `Antes` e `Depois` são medidas das mesmas unidades;
- adequada para t pareado e Wilcoxon;
- contém a mesma variedade de tipos de variável.

Os arquivos `*_log10.txt` e `*_log10_transformada.txt` são versões didáticas já processadas. Para uma nova análise, comece pelas bases sem sufixo e rode `run_workflow.py`; ele cria uma cópia transformada dentro de uma pasta única em `results/generated/`.
