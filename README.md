# testT — workflow estatístico reprodutível em Python

Projeto didático para organizar tabelas, verificar normalidade, aplicar transformações e comparar dois grupos em Python. A versão atual substitui a sequência manual de arquivos soltos por um único programa seguro e reutilizável.

## O que mudou

- `run_workflow.py` executa todo o fluxo em uma única chamada;
- as funções reutilizáveis estão em `stats_workflow/`;
- cada execução cria uma pasta própria, sem sobrescrever análises anteriores;
- o programa valida os pares de colunas antes de calcular qualquer teste;
- `lista.txt` deixou de ser uma dependência global: a seleção para log10 é registrada no próprio resultado;
- log10 recusa valores zero ou negativos em vez de deixá-los misturados sem aviso;
- porcentagens são verificadas para permanecerem entre 0 e 100;
- os relatórios guardam valor-p, tamanho amostral, teste, transformação, ajuste de Holm e rastreabilidade da entrada;
- os nomes originais dos scripts continuam funcionando como atalhos compatíveis.

## Instalação

Na pasta do repositório:

```bash
pip install -r requirements.txt
```

## Rodar o programa principal

### Grupos independentes

Use quando Controle e Tratamento são indivíduos/unidades diferentes:

```bash
python run_workflow.py --input data/independent/base_workflow_independente.txt --design independent
```

### Dados pareados

Use quando Antes e Depois são medidas da mesma unidade experimental, na mesma linha:

```bash
python run_workflow.py --input data/paired/base_workflow_pareado.txt --design paired
```

Sem argumentos, `python run_workflow.py` abre perguntas simples — útil no Pydroid ou ao executar por duplo clique.

Os resultados aparecem em `results/generated/run_AAAAMMDD_HHMMSS/`. A base original nunca é alterada.

## Estrutura da tabela aceita

Use TAB como separador e duas linhas de cabeçalho:

```text
Controle    Tratamento    Controle    Tratamento
Altura_cm   Altura_cm     Área_cm2    Área_cm2
21,5        20,1          42,7        38,4
...
```

Cada variável deve ocupar exatamente duas colunas adjacentes e ter o mesmo nome na segunda linha. O programa para com uma mensagem clara se `Altura_cm` for emparelhada por engano com `Biomassa_mg`.

## Como o fluxo decide o que fazer

1. Lê, converte e valida apenas valores numéricos.
2. Executa Shapiro–Wilk por coluna.
3. Em modo `auto`, aplica log10 somente a variáveis não normais que não são porcentagens.
4. Em modo `auto`, aplica arcsen(√p) somente a porcentagens não normais.
5. Repete Shapiro–Wilk depois das transformações.
6. Executa os testes adequados ao desenho.

Para dados independentes, são calculados t de Welch e Mann–Whitney; o Levene é somente um diagnóstico, não uma “porta” que decide se Welch pode ser usado. Para dados pareados, o programa também verifica a normalidade das diferenças `Depois − Antes`, que é a suposição relevante para o t pareado, e calcula t pareado e Wilcoxon.

O campo `recommended` em `tests.csv` indica qual opção combina com a regra didática de normalidade. Os dois resultados ficam salvos para conferência; a escolha final deve respeitar o desenho e a pergunta biológica.

## Arquivos de cada execução

- `transformed_data.tsv` — cópia analisada, preservando os dois cabeçalhos;
- `normality_raw.csv` e `normality_final.csv` — W, p, n e conclusão por coluna;
- `normality_differences_*.csv` — apenas para dados pareados;
- `transformations.csv` — o que foi ou não aplicado e por quê;
- `tests.csv` — estatísticas, valores-p brutos e corrigidos por Holm, efeito e conclusão;
- `summary.txt` — leitura curta dos resultados recomendados;
- `manifest.json` — arquivo de entrada, hash, pares, parâmetros e versão do workflow.

Leia [docs/WORKFLOW.md](docs/WORKFLOW.md) antes de usar dados reais.

## Atalhos compatíveis

Os nomes abaixo continuam disponíveis, mas agora usam as funções seguras do novo programa e gravam resultados ao lado do arquivo de entrada:

- `Shapiro_Comentado.py`
- `log10_Comentado.py`
- `Transformar_Percentual_Comentado.py`
- `Mann_W_Comentado.py`
- `TesteLenvene_Test_T_Test_Welch_Comentado.py`
- `Test_T_Pareado_Comentado.py`
- `Test_Wilcoxon_Comentado.py`

Para uma análise completa, prefira `run_workflow.py`.

## Verificar a instalação

```bash
python -m unittest discover -s tests -v
```

As bases incluídas são sintéticas: servem para testar a organização e o programa, não para sustentar uma conclusão experimental real.
