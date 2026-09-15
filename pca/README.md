# Análise de componentes principais (PCA)

O script `pca_for_julia_fixed.py` executa uma PCA sobre uma tabela numérica separada por TAB. As variáveis são padronizadas antes da análise para evitar que unidades diferentes dominem o resultado.

## Testes disponíveis

Na raiz do repositório, execute:

```bash
python pca/pca_for_julia_fixed.py
```

Quando o programa solicitar o arquivo, informe uma destas bases:

```text
data/pca/dados_pca_40_amostras_20_variaveis.txt
data/pca/dados_pca_folhas_40_amostras_30_variaveis.txt
```

As tabelas usam TAB como separador, vírgula como separador decimal e a primeira coluna como identificador das amostras. Os arquivos são sintéticos e servem apenas para teste.

## Arquivos gerados

Os resultados de exemplo ficam em `results/pca/`:

- `Resultado_Cargas_PCA.txt` — pesos das variáveis nos componentes;
- `Resultado_Contribuicoes_PCA.txt` — contribuição percentual de cada variável;
- `Resultado_Eigenvalues_PCA.txt` — autovalores e variância explicada;
- `Grafico_Contribuicoes_PCA_PC1_PC2_Pizza.png` — comparação em gráficos de pizza;
- `Grafico_Contribuicoes_PCA_PC1_PC2_Barras.png` — comparação em gráficos de barras;
- `Grafico_Biplot_PCA_900dpi.png` — biplot de amostras e variáveis.

A PCA não demonstra causalidade. As contribuições indicam quais variáveis ajudam a definir cada componente.
