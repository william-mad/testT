# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 14:07:18 2026

@author: USUARIO
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


arquivo = input("nome do arquivo pls:")

dados = pd.read_csv(
    arquivo,
    sep="\t",
    index_col=0,
    decimal=",",
    encoding="latin-1",
)

dados_limpos = dados.dropna()

padronizador = StandardScaler()
dados_padronizados = padronizador.fit_transform(dados_limpos)

pca = PCA()
componentes = pca.fit_transform(dados_padronizados)

variancia = pca.explained_variance_ratio_ * 100

print("porcentagem de explicação de cada componente principal (pc)")

for i in range(len(variancia)):
    print(f"PC, {i + 1}: {variancia[i]:.2f} %")


cargas = pd.DataFrame(
    pca.components_.T,
    columns=[f"PC{i + 1}" for i in range(len(variancia))],
    index=dados_limpos.columns,
)

cargas.to_csv("Resultado_Cargas_PCA.txt", sep="\t", decimal=",")

# Percentage contribution of each variable to each principal component.
contribuicoes = pd.DataFrame(
    (pca.components_ ** 2)
    / np.sum(pca.components_ ** 2, axis=1, keepdims=True)
    * 100,
    columns=[f"PC{i + 1}" for i in range(pca.n_components_)],
    index=dados_limpos.columns,
)

contribuicoes.to_csv(
    "Resultado_Contribuicoes_PCA.txt",
    sep="\t",
    decimal=",",
)

autovalores = pca.explained_variance_

tabela_eigen = pd.DataFrame(
    {
        "Componente": [f"PC{i + 1}" for i in range(len(variancia))],
        "Eigenvalue": autovalores,
        "%Variance": variancia,
    }
)

tabela_eigen.to_csv(
    "Resultado_Eigenvalues_PCA.txt",
    sep="\t",
    decimal=",",
    index=False,
)


print("\nProcesso concluído! Foram gerados três arquivos de texto:")
print("1. 'Resultado_Cargas_PCA.txt' (pesos das variaveis)")
print("2. 'Resultado_Contribuicoes_PCA.txt' (% de contribuição por componente)")
print("3. 'Resultado_Eigenvalues_PCA.txt' (autovalores e % de variancia)")


quantidade_componentes_plot = min(2, pca.n_components_)
fig_contribuicoes, eixos_contribuicoes = plt.subplots(
    1,
    quantidade_componentes_plot,
    figsize=(16, 10),
    squeeze=False,
)

for indice in range(quantidade_componentes_plot):
    nome_componente = f"PC{indice + 1}"
    contribuicoes_componente = contribuicoes[nome_componente].sort_values()
    eixo = eixos_contribuicoes[0, indice]

    barras = eixo.barh(
        contribuicoes_componente.index,
        contribuicoes_componente.values,
        color="steelblue" if indice == 0 else "darkorange",
    )
    eixo.set_title(
        f"Contribuição das variáveis para {nome_componente}\n"
        f"({variancia[indice]:.2f}% da variância total)",
        fontsize=12,
    )
    eixo.set_xlabel("Contribuição (%)")
    eixo.grid(axis="x", linestyle="--", alpha=0.4)

    for barra, valor in zip(barras, contribuicoes_componente.values):
        eixo.text(
            valor + 0.5,
            barra.get_y() + barra.get_height() / 2,
            f"{valor:.1f}%",
            va="center",
            fontsize=8,
        )

fig_contribuicoes.tight_layout()
fig_contribuicoes.savefig(
    "Grafico_Contribuicoes_PCA_PC1_PC2.png",
    dpi=300,
    bbox_inches="tight",
)

print("4. 'Grafico_Contribuicoes_PCA_PC1_PC2.png' (gráfico das contribuições)")


print("\nGerando o grafico Biplot do PCA... (feche a janela do grafico para continuar)\n")

plt.figure(figsize=(12, 8))

if componentes.shape[1] < 2:
    raise ValueError("O biplot requer pelo menos dois componentes principais.")

plt.scatter(componentes[:, 0], componentes[:, 1], color="black", s=25)

for i, nome_amostra in enumerate(dados_limpos.index):
    plt.text(
        componentes[i, 0] + 0.1,
        componentes[i, 1] + 0.1,
        nome_amostra,
        color="blue",
        fontsize=10,
    )

escala = np.max(np.abs(componentes)) / np.max(np.abs(pca.components_)) * 0.7

for i, nome_variavel in enumerate(dados_limpos.columns):
    vetor_x = pca.components_[0, i] * escala
    vetor_y = pca.components_[1, i] * escala

    plt.plot([0, vetor_x], [0, vetor_y], color="forestgreen", linewidth=1.2)

    plt.text(vetor_x * 1.05, vetor_y * 1.05, nome_variavel, color="green", fontsize=9)


plt.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
plt.axvline(x=0, color="black", linestyle="-", linewidth=0.8)

plt.xlabel("component 1", fontsize=11)
plt.ylabel("component 2", fontsize=11)

plt.savefig("Grafico_Biplot_PCA_900dpi.png", dpi=900, bbox_inches="tight")
plt.show()

print("copia do grafico salva como 'Grafico_Biplot_PCA_900dpi.png'")

