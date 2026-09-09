# Guia do workflow

## 1. Escolha o desenho antes do teste

| Situação | Entrada de exemplo | Desenho | Testes reportados |
|---|---|---|---|
| Controle e Tratamento são indivíduos diferentes | `data/independent/base_workflow_independente.txt` | `independent` | Welch, Mann–Whitney e Levene diagnóstico |
| Antes e Depois pertencem à mesma unidade, na mesma linha | `data/paired/base_workflow_pareado.txt` | `paired` | t pareado e Wilcoxon |

Não transforme um dado independente em pareado por colocá-lo lado a lado. O pareamento é uma propriedade do experimento: cada linha precisa representar a mesma unidade nos dois momentos.

## 2. Use a tabela sem bagunçar os pares

O programa trabalha com uma tabela larga de duas linhas de cabeçalho:

```text
Controle    Tratamento    Controle    Tratamento
Altura_cm   Altura_cm     Biomassa_mg Biomassa_mg
21,5        19,8          44,1        37,2
```

As colunas só são pares válidos quando têm a mesma variável na segunda linha. Assim, trocar uma única coluna não produz uma análise silenciosamente errada: o programa interrompe a execução e informa o par que precisa ser corrigido.

Evite colunas de texto, identificador, média ou desvio-padrão na mesma tabela. Deixe apenas observações numéricas. Valores ausentes são aceitos:

- em grupos independentes, cada grupo é limpo separadamente;
- em dados pareados, uma linha é usada somente se os dois valores do par estiverem presentes.

## 3. Execução completa

```bash
python run_workflow.py --input CAMINHO_DA_BASE.txt --design independent
```

ou:

```bash
python run_workflow.py --input CAMINHO_DA_BASE.txt --design paired
```

Opções úteis:

```bash
# Não aplicar transformações automáticas
python run_workflow.py --input minha_base.txt --design independent --log10 off --percentage off

# Aplicar arcsen(√p) a todas as variáveis cujo nome contém %
python run_workflow.py --input minha_base.txt --design independent --percentage all

# Escolher outra pasta para as execuções
python run_workflow.py --input minha_base.txt --design paired --output meus_resultados
```

`--log10 auto` é o padrão: seleciona uma variável positiva não percentual quando pelo menos uma coluna dela rejeita normalidade pelo Shapiro. `--percentage auto` faz o mesmo apenas para variáveis com `%` no nome. Essas regras são transparentes em `transformations.csv`; elas não substituem o julgamento sobre a escala e o significado biológico da variável.

## 4. O que é passado de uma etapa à outra

No programa novo, a tabela transformada e os resultados são objetos do mesmo fluxo; não há arquivo temporário compartilhado entre análises. Depois, tudo é salvo apenas para auditoria:

```text
base original
  → validação da estrutura e mapa explícito dos pares
  → Shapiro bruto
  → plano de transformação
  → tabela transformada
  → Shapiro final
  → testes e relatório
```

Isso elimina o problema do `lista.txt` antigo: ele podia ser sobrescrito por outra base e fazer o log10 atuar nas variáveis erradas. Também elimina `Resultado_*.txt` globais, que sobrescreviam análises anteriores.

## 5. Como interpretar os arquivos

### Normalidade

Em `normality_raw.csv` e `normality_final.csv`:

- `statistic_w` é a estatística W de Shapiro–Wilk;
- `pvalue > alpha` significa “não rejeita normalidade”; não significa que a distribuição foi provada normal;
- `insufficient_data` significa menos de três valores válidos.

Em dados pareados, consulte também `normality_differences_final.csv`: o t pareado pressupõe normalidade aproximada das diferenças, não necessariamente de cada coluna separada.

### Testes

`tests.csv` guarda todos os testes calculados, para que a decisão seja conferível.

- `recommended=True` sinaliza a escolha didática baseada na normalidade final;
- t de Welch é usado como alternativa paramétrica independente sem exigir uma etapa de pré-teste de variâncias;
- `pvalue_holm` controla o aumento de falsos positivos ao testar várias variáveis dentro da mesma família de teste;
- `effect_size` acrescenta a magnitude estimada, não só a significância.

Uma conclusão com `p > 0,05` deve ser lida como “não há evidência suficiente de diferença neste conjunto de dados”. Ela não demonstra que as médias são iguais.

## 6. Transformações: limites importantes

### Log10

Log10 só é aplicado a valores estritamente positivos. Zero ou valores negativos geram um erro claro, pois deixá-los sem transformar mistura escalas e invalida a interpretação. Se o experimento realmente possui zeros, defina antecipadamente uma estratégia metodológica adequada; não adicione uma constante automaticamente sem justificar.

### Porcentagens

O programa usa `arcsin(sqrt(p / 100))` e só aceita valores de 0 a 100. A transformação não é obrigatória para toda porcentagem; em muitas situações, especialmente com modelos adequados ou porcentagens longe dos limites, pode não ser a melhor escolha. Use-a conscientemente e registre a decisão.

## 7. Scripts antigos

Os arquivos `*_Comentado.py` continuam como atalhos interativos, mas agora chamam o código seguro de `stats_workflow/`. Eles não usam `eval()` e não dependem de `lista.txt` global. Para manter todas as etapas conectadas em uma única execução, use `run_workflow.py`.
