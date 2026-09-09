"""Small interactive adapters that keep the original script names usable."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .io import read_wide_table, write_wide_table
from .normality import shapiro_by_column, shapiro_paired_differences
from .schema import WorkflowValidationError
from .tests import run_independent_tests, run_paired_tests
from .transforms import apply_arcsine_sqrt, apply_log10, plan_transformations


def _input_path() -> Path:
    return Path(input("Digite o nome do arquivo de entrada: ").strip()).expanduser()


def _report_path(source: Path, suffix: str) -> Path:
    return source.with_name(f"{source.stem}_{suffix}")


def _write_text_report(frame: pd.DataFrame, path: Path) -> None:
    path.write_text(frame.to_string(index=False) + "\n", encoding="utf-8")


def _run_shapiro(source: Path) -> Path:
    data, pairs, source = read_wide_table(source)
    results = shapiro_by_column(data, pairs, 0.05)
    csv_path = _report_path(source, "shapiro.csv")
    results.to_csv(csv_path, index=False, encoding="utf-8")
    non_normal = results[results["status"] == "rejects_normality"]
    list_path = _report_path(source, "lista_nao_normal.txt")
    list_path.write_text(
        "\n".join(f"{row.group_a} - {row.variable}" for row in non_normal.itertuples()) + "\n",
        encoding="utf-8",
    )
    print(results[["group_a", "variable", "n", "statistic_w", "pvalue", "conclusion"]].to_string(index=False))
    print(f"\nRelatório: {csv_path}\nLista: {list_path}")
    return csv_path


def _run_log10(source: Path) -> Path:
    data, pairs, source = read_wide_table(source)
    normality = shapiro_by_column(data, pairs, 0.05)
    variables, _ = plan_transformations(pairs, normality, "auto", "off")
    transformed, audit = apply_log10(data, pairs, variables)
    output = _report_path(source, "log10.txt")
    write_wide_table(transformed, output)
    pd.DataFrame(audit).to_csv(_report_path(source, "log10_transformations.csv"), index=False)
    print(f"Log10 aplicado a: {', '.join(sorted(variables)) or 'nenhuma variável'}.\nSaída: {output}")
    return output


def _run_percentage(source: Path) -> Path:
    data, pairs, source = read_wide_table(source)
    percentage_variables = {pair.variable for pair in pairs if "%" in pair.variable}
    transformed, audit = apply_arcsine_sqrt(data, pairs, percentage_variables)
    output = _report_path(source, "transformada.txt")
    write_wide_table(transformed, output)
    pd.DataFrame(audit).to_csv(_report_path(source, "percent_transformations.csv"), index=False)
    print(f"Transformação de porcentagem aplicada. Saída: {output}")
    return output


def _run_independent(source: Path, include: set[str], suffix: str) -> Path:
    data, pairs, source = read_wide_table(source)
    normality = shapiro_by_column(data, pairs, 0.05)
    results = run_independent_tests(data, pairs, normality, 0.05)
    selected = results[results["test"].isin(include)]
    output = _report_path(source, suffix)
    _write_text_report(selected, output)
    print(f"Relatório: {output}")
    return output


def _run_paired(source: Path, include: set[str], suffix: str) -> Path:
    data, pairs, source = read_wide_table(source)
    differences = shapiro_paired_differences(data, pairs, 0.05)
    results = run_paired_tests(data, pairs, differences, 0.05)
    selected = results[results["test"].isin(include)]
    output = _report_path(source, suffix)
    _write_text_report(selected, output)
    print(f"Relatório: {output}")
    return output


def legacy_main(action: str) -> int:
    """Entry point used by the original filenames."""
    try:
        source = _input_path()
        if action == "shapiro":
            _run_shapiro(source)
        elif action == "log10":
            _run_log10(source)
        elif action == "percentage":
            _run_percentage(source)
        elif action == "mann":
            _run_independent(source, {"Mann–Whitney U (independente)"}, "Resultado_Mann_Whitney.txt")
        elif action == "welch":
            _run_independent(source, {"Levene (diagnóstico)", "t de Welch (independente)"}, "Resultado_Levene_t_Welch.txt")
        elif action == "paired_t":
            _run_paired(source, {"t pareado"}, "Resultado_Test_Pareado.txt")
        elif action == "wilcoxon":
            _run_paired(source, {"Wilcoxon pareado"}, "Resultado_Wilcoxon.txt")
        else:
            raise ValueError(f"Ação desconhecida: {action}")
    except (WorkflowValidationError, ValueError, OSError) as exc:
        print(f"Erro: {exc}")
        return 2
    input("Pressione Enter para fechar o programa...")
    return 0
