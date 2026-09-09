"""Shapiro-Wilk checks with structured, machine-readable results."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import shapiro

from .schema import PairSpec


def _normality_row(
    *,
    group_a: str,
    group_b: str | None,
    variable: str,
    n: int,
    values: pd.Series | np.ndarray,
    alpha: float,
    kind: str,
    position: int,
) -> dict:
    row = {
        "kind": kind,
        "pair_position": position,
        "group_a": group_a,
        "group_b": group_b or "",
        "variable": variable,
        "n": n,
        "statistic_w": np.nan,
        "pvalue": np.nan,
        "status": "not_run",
        "conclusion": "",
    }
    if n < 3:
        row.update(status="insufficient_data", conclusion="Menos de 3 valores válidos.")
        return row
    if n > 5000:
        row["note"] = "Shapiro-Wilk foi calculado, mas o valor-p é menos preciso acima de 5000 observações."
    statistic, pvalue = shapiro(values)
    normal = pvalue > alpha
    row.update(
        statistic_w=statistic,
        pvalue=pvalue,
        status="does_not_reject_normality" if normal else "rejects_normality",
        conclusion=(
            "Não rejeita normalidade." if normal else "Rejeita normalidade."
        ),
    )
    return row


def shapiro_by_column(data: pd.DataFrame, pairs: list[PairSpec], alpha: float) -> pd.DataFrame:
    rows: list[dict] = []
    pair_lookup = {pair.column_a: pair for pair in pairs}
    pair_lookup.update({pair.column_b: pair for pair in pairs})
    for position, column in enumerate(data.columns, start=1):
        pair = pair_lookup[column]
        values = data[column].dropna()
        rows.append(
            _normality_row(
                group_a=column[0],
                group_b=None,
                variable=column[1],
                n=len(values),
                values=values,
                alpha=alpha,
                kind="column",
                position=pair.position,
            )
        )
    return pd.DataFrame(rows)


def shapiro_paired_differences(
    data: pd.DataFrame, pairs: list[PairSpec], alpha: float
) -> pd.DataFrame:
    """Assess normality of within-row differences, the assumption for paired t tests."""
    rows: list[dict] = []
    for pair in pairs:
        complete_pairs = data.loc[:, [pair.column_a, pair.column_b]].dropna()
        differences = complete_pairs[pair.column_b] - complete_pairs[pair.column_a]
        rows.append(
            _normality_row(
                group_a=pair.group_a,
                group_b=pair.group_b,
                variable=pair.variable,
                n=len(differences),
                values=differences,
                alpha=alpha,
                kind="paired_difference",
                position=pair.position,
            )
        )
    return pd.DataFrame(rows)
