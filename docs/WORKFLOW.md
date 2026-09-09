# Como executar o workflow

## 1. Organização das células

Todas as bases usam duas linhas de cabeçalho:

- linha 1: grupo ou momento (`Controle`, `Tratamento`, `Antes`, `Depois`);
- linha 2: nome da variável;
- linhas seguintes: uma observação por linha.

As colunas de cada variável ficam lado a lado. Não há uma coluna textual de identificação, porque os scripts tentam analisar todas as colunas e esperam encontrar números.

Cada base tem 60 observações, 14 colunas numéricas e 7 pares de variáveis.

## 2. Diferença entre os desenhos

### Dados independentes

Use `data/independent/base_workflow_independente.txt` quando Controle e Tratamento forem grupos diferentes de indivíduos.

Use:

- `Mann_W_Comentado.py`;
- `TesteLenvene_Test_T_Test_Welch_Comentado.py`.

### Dados pareados

Use `data/paired/base_workflow_pareado.txt` quando Antes e Depois forem medidas da mesma unidade experimental.

Use:

- `Test_T_Pareado_Comentado.py`;
- `Test_Wilcoxon_Comentado.py`.

Não use o teste pareado em grupos independentes nem o teste independente em medidas Antes/Depois, mesmo que o programa consiga executar.

## 3. Shapiro-Wilk

Execute:

```bash
python Shapiro_Comentado.py
```

Informe a base original quando o programa pedir o arquivo.

- `p > 0,05`: não rejeita a hipótese de normalidade;
- `p <= 0,05`: registra a coluna em `lista.txt` como não normal.

Isso não prova normalidade perfeita; significa apenas que o teste não encontrou evidência suficiente contra a normalidade.

## 4. Transformação log10

O script `log10_Comentado.py` lê `lista.txt`. Execute-o logo depois do Shapiro:

```bash
python log10_Comentado.py
```

Informe novamente o mesmo arquivo original. Os dados assimétricos positivos serão transformados e o arquivo `*_log10.txt` será criado na mesma pasta da base.

Nesta demonstração, foram selecionadas:

- `Biomassa_seca_mg`;
- `Compostos_fenolicos_ug_g`.

## 5. Transformação das porcentagens

Depois do log10, execute:

```bash
python Transformar_Percentual_Comentado.py
```

Informe o arquivo `*_log10.txt`. O script procura o símbolo `%` no nome da variável e aplica:

```text
arcsin(sqrt(valor / 100))
```

O resultado será salvo como `*_log10_transformada.txt`.

## 6. Verificação final

Rode novamente:

```bash
python Shapiro_Comentado.py
```

Informe o arquivo `*_log10_transformada.txt`. Nas bases de demonstração, as 14 colunas ficaram com `p > 0,05` após as transformações.

## 7. Testes finais

Para a base independente:

```bash
python Mann_W_Comentado.py
python TesteLenvene_Test_T_Test_Welch_Comentado.py
```

Para a base pareada:

```bash
python Test_T_Pareado_Comentado.py
python Test_Wilcoxon_Comentado.py
```

Informe o arquivo final `*_log10_transformada.txt`.

## 8. Arquivos fixos

Os scripts usam nomes fixos como `lista.txt` e `Resultado_*.txt`. Execute um desenho experimental por vez ou copie/renomeie os resultados entre as execuções.

Os relatórios em `results/` são exemplos já executados.
