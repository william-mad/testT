# Análise de componentes principais (PCA)

O script `pca_for_julia_fixed.py` executa uma PCA sobre uma tabela numérica separada por TAB.

## Teste rápido

Na raiz do repositório, execute:

```bash
python pca/pca_for_julia_fixed.py
```

Quando o programa solicitar o arquivo, informe:

```text
data/pca/dados_pca_teste.txt
```

A tabela usa:

- TAB como separador;
- vírgula como separador decimal;
- a primeira coluna como identificador das amostras;
- apenas variáveis numéricas nas demais colunas.

O programa gera os arquivos de cargas, autovalores e o gráfico biplot no diretório de trabalho atual. O arquivo de dados é sintético e serve apenas para teste.
