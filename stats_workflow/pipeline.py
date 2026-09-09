"""The end-to-end, auditable statistical workflow."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from . import __version__
from .io import file_sha256, read_wide_table, write_wide_table
from .normality import shapiro_by_column, shapiro_paired_differences
from .tests import run_independent_tests, run_paired_tests
from .transforms import apply_arcsine_sqrt, apply_log10, plan_transformations


def _make_run_directory(base: str | Path) -> Path:
    root = Path(base)
    root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("run_%Y%m%d_%H%M%S")
    candidate = root / timestamp
    suffix = 2
    while candidate.exists():
        candidate = root / f"{timestamp}_{suffix:02d}"
        suffix += 1
    candidate.mkdir()
    return candidate


def _write_csv(frame: pd.DataFrame, path: Path) -> None:
    frame.to_csv(path, index=False, encoding="utf-8")


def _format_pvalue(value: float) -> str:
    if pd.isna(value):
        return "não calculado"
    return f"{value:.4g}"


def _write_summary(
    path: Path,
    *,
    source: Path,
    design: str,
    alpha: float,
    pairs: list,
    transformations: pd.DataFrame,
    tests: pd.DataFrame,
) -> None:
    selected = tests[tests["recommended"]] if not tests.empty else tests
    lines = [
        "RESUMO DO WORKFLOW ESTATÍSTICO",
        "=" * 34,
        f"Entrada: {source}",
        f"Desenho: {'grupos independentes' if design == 'independent' else 'dados pareados'}",
        f"Pares analisados: {len(pairs)}",
        f"Alpha: {alpha}",
        "",
        "Transformações aplicadas:",
    ]
    applied = transformations[transformations["applied"]]
    if applied.empty:
        lines.append("- Nenhuma.")
    else:
        for _, row in applied.iterrows():
            lines.append(f"- {row['variable']}: {row['operation']}")

    lines.extend(["", "Resultados recomendados (p bruto; p Holm):"])
    if selected.empty:
        lines.append("- Nenhum teste teve dados suficientes.")
    else:
        for _, row in selected.iterrows():
            lines.append(
                f"- {row['variable']} — {row['test']}: p={_format_pvalue(row['pvalue'])}; "
                f"p Holm={_format_pvalue(row['pvalue_holm'])}. {row['conclusion']}"
            )
    lines.extend(
        [
            "",
            "Importante: resultado não significativo não prova que grupos são iguais; "
            "indica apenas ausência de evidência suficiente de diferença com estes dados.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_workflow(
    input_path: str | Path,
    design: str,
    output_root: str | Path = "results/generated",
    *,
    alpha: float = 0.05,
    log10_mode: str = "auto",
    percentage_mode: str = "auto",
) -> dict:
    """Run a complete workflow and return paths/results for programmatic reuse.

    ``design`` is ``independent`` for different groups or ``paired`` for repeated
    measurements of the same experimental units.
    """
    if design not in {"independent", "paired"}:
        raise ValueError("design deve ser 'independent' ou 'paired'.")
    if not 0 < alpha < 1:
        raise ValueError("alpha deve estar entre 0 e 1.")

    data, pairs, source = read_wide_table(input_path)
    raw_normality = shapiro_by_column(data, pairs, alpha)
    raw_differences = (
        shapiro_paired_differences(data, pairs, alpha) if design == "paired" else pd.DataFrame()
    )

    log10_variables, percentage_variables = plan_transformations(
        pairs, raw_normality, log10_mode, percentage_mode
    )
    transformed, log10_audit = apply_log10(data, pairs, log10_variables)
    transformed, percentage_audit = apply_arcsine_sqrt(transformed, pairs, percentage_variables)
    transformations = pd.DataFrame(log10_audit + percentage_audit)

    final_normality = shapiro_by_column(transformed, pairs, alpha)
    final_differences = (
        shapiro_paired_differences(transformed, pairs, alpha)
        if design == "paired"
        else pd.DataFrame()
    )
    if design == "independent":
        test_results = run_independent_tests(transformed, pairs, final_normality, alpha)
    else:
        test_results = run_paired_tests(transformed, pairs, final_differences, alpha)

    run_directory = _make_run_directory(output_root)
    write_wide_table(transformed, run_directory / "transformed_data.tsv")
    _write_csv(raw_normality, run_directory / "normality_raw.csv")
    _write_csv(final_normality, run_directory / "normality_final.csv")
    _write_csv(transformations, run_directory / "transformations.csv")
    _write_csv(test_results, run_directory / "tests.csv")
    if design == "paired":
        _write_csv(raw_differences, run_directory / "normality_differences_raw.csv")
        _write_csv(final_differences, run_directory / "normality_differences_final.csv")

    manifest = {
        "workflow_version": __version__,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_file": str(source.resolve()),
        "input_sha256": file_sha256(source),
        "design": design,
        "alpha": alpha,
        "log10_mode": log10_mode,
        "percentage_mode": percentage_mode,
        "selected_log10_variables": sorted(log10_variables),
        "selected_percentage_variables": sorted(percentage_variables),
        "pairs": [
            {
                "position": pair.position,
                "variable": pair.variable,
                "group_a": pair.group_a,
                "group_b": pair.group_b,
            }
            for pair in pairs
        ],
    }
    (run_directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_summary(
        run_directory / "summary.txt",
        source=source,
        design=design,
        alpha=alpha,
        pairs=pairs,
        transformations=transformations,
        tests=test_results,
    )

    return {
        "run_directory": run_directory,
        "raw_normality": raw_normality,
        "final_normality": final_normality,
        "raw_difference_normality": raw_differences,
        "final_difference_normality": final_differences,
        "transformations": transformations,
        "tests": test_results,
    }
