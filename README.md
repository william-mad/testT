# testT — scripts de análise estatística em Python

Repositório didático para aprender a organizar dados e aplicar testes estatísticos em Python, com exemplos voltados a medidas biométricas, anatomia vegetal e ecologia.

Os scripts originais continuam na raiz do projeto. As bases e os resultados de exemplo foram organizados em pastas para deixar claro qual arquivo usar em cada etapa.

## Estrutura

```text
.
├── data/
│   ├── independent/    # Controle × Tratamento
│   └── paired/         # Antes × Depois
├── docs/
│   └── WORKFLOW.md     # explicação completa e comandos
├── results/
│   ├── independent/   # saídas para grupos independentes
│   └── paired/        # saídas para dados pareados
├── requirements.txt
└── *.py               # scripts didáticos originais
```

## Instalação

Na pasta do repositório:

```bash
pip install -r requirements.txt
```

As dependências são pandas, scipy e numpy.

## Qual base usar?

| Desenho | Base | Testes apropriados |
|---|---|---|
| Grupos independentes | `data/independent/base_workflow_independente.txt` | Mann–Whitney, Levene e t independente/Welch |
| Mesmas unidades medidas duas vezes | `data/paired/base_workflow_pareado.txt` | t pareado e Wilcoxon |

O Shapiro-Wilk, o log10 e a transformação de porcentagens podem ser aplicados às duas bases.

## Workflow

1. Rode o Shapiro-Wilk na base original.
2. Preserve o `lista.txt` produzido pelo programa.
3. Rode o script de transformação log10.
4. Rode a transformação de porcentagens no arquivo produzido pelo log10.
5. Rode o Shapiro-Wilk novamente no arquivo final.
6. Escolha o teste de acordo com o desenho experimental.

A explicação detalhada está em [docs/WORKFLOW.md](docs/WORKFLOW.md).

## Atenção

As bases incluídas são sintéticas. Elas existem para testar a organização das células, o funcionamento dos scripts e a interpretação dos resultados. Não representam um experimento real.
