"""Independent and paired tests plus cautious conclusions and effect sizes."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import levene, mannwhitneyu, ttest_ind, ttest_rel, wilcoxon

from .schema import PairSpec


def _conclusion(pvalue: float, alpha: float) -> str:
    if pd.isna(pvalue):
        return "Teste não executado."
    if pvalue <= alpha:
        return "Há evidência de diferença estatisticamente significativa."
    return "Não há evidência suficiente de diferença estatisticamente significativa."


def _hedges_g(first: pd.Series, second: pd.Series) -> float:
    n1, n2 = len(first), len(second)
    if n1 < 2 or n2 < 2:
        return np.nan
    variance = ((n1 - 1) * first.var(ddof=1) + (n2 - 1) * second.var(ddof=1)) / (n1 + n2 - 2)
    if variance <= 0:
        return np.nan
    d = (first.mean() - second.mean()) / math.sqrt(variance)
    correction = 1 - (3 / (4 * (n1 + n2) - 9))
    return correction * d


def _paired_dz(differences: pd.Series) -> float:
    if len(differences) < 2:
        return np.nan
    deviation = differences.std(ddof=1)
    if deviation == 0 or pd.isna(deviation):
        return np.nan
    return differences.mean() / deviation


def _base_row(pair: PairSpec, test: str, n: int, alpha: float) -> dict:
    return {
        "pair_position": pair.position,
        "variable": pair.variable,
        "group_a": pair.group_a,
        "group_b": pair.group_b,
        "test": test,
        "n": n,
        "statistic": np.nan,
        "pvalue": np.nan,
        "pvalue_holm": np.nan,
        "effect_size": np.nan,
        "effect_size_name": "",
        "recommended": False,
        "conclusion": "",
        "alpha": alpha,
        "note": "",
    }


def _apply_holm(rows: list[dict]) -> None:
    """Holm adjustment separately inside each named family of tests."""
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        if not pd.isna(row["pvalue"]):
            grouped.setdefault(row["test"], []).append(row)
    for family in grouped.values():
        ordered = sorted(family, key=lambda row: row["pvalue"])
        running_max = 0.0
        total = len(ordered)
        for index, row in enumerate(ordered):
            adjusted = min(1.0, (total - index) * row["pvalue"])
            running_max = max(running_max, adjusted)
            row["pvalue_holm"] = running_max


def run_independent_tests(
    data: pd.DataFrame,
    pairs: list[PairSpec],
    final_normality: pd.DataFrame,
    alpha: float,
) -> pd.DataFrame:
    """Run Welch t and Mann–Whitney; Levene is reported only as a diagnostic."""
    rows: list[dict] = []
    for pair in pairs:
        first = data[pair.column_a].dropna()
        second = data[pair.column_b].dropna()
        n = min(len(first), len(second))
        normal_rows = final_normality[final_normality["variable"] == pair.variable]
        normal_for_both = len(normal_rows) == 2 and (normal_rows["status"] == "does_not_reject_normality").all()

        levene_row = _base_row(pair, "Levene (diagnóstico)", n, alpha)
        if len(first) >= 2 and len(second) >= 2:
            statistic, pvalue = levene(first, second, center="median")
            levene_row.update(
                statistic=statistic,
                pvalue=pvalue,
                conclusion=(
                    "Não há evidência forte de variâncias diferentes."
                    if pvalue > alpha
                    else "Há evidência de variâncias diferentes."
                ),
            )
        else:
            levene_row.update(conclusion="Dados insuficientes para Levene.")
        rows.append(levene_row)

        welch_row = _base_row(pair, "t de Welch (independente)", n, alpha)
        if len(first) >= 2 and len(second) >= 2:
            statistic, pvalue = ttest_ind(first, second, equal_var=False)
            welch_row.update(
                statistic=statistic,
                pvalue=pvalue,
                effect_size=_hedges_g(first, second),
                effect_size_name="Hedges g (grupo A - grupo B)",
                recommended=bool(normal_for_both),
                conclusion=_conclusion(pvalue, alpha),
            )
        else:
            welch_row.update(conclusion="Dados insuficientes para t de Welch.")
        rows.append(welch_row)

        mann_row = _base_row(pair, "Mann–Whitney U (independente)", n, alpha)
        if len(first) >= 2 and len(second) >= 2:
            statistic, pvalue = mannwhitneyu(first, second, alternative="two-sided")
            rank_biserial = (2 * statistic / (len(first) * len(second))) - 1
            mann_row.update(
                statistic=statistic,
                pvalue=pvalue,
                effect_size=rank_biserial,
                effect_size_name="correlação rank-biserial (A - B)",
                recommended=not normal_for_both,
                conclusion=_conclusion(pvalue, alpha),
            )
        else:
            mann_row.update(conclusion="Dados insuficientes para Mann–Whitney.")
        rows.append(mann_row)

    _apply_holm(rows)
    return pd.DataFrame(rows)


def run_paired_tests(
    data: pd.DataFrame,
    pairs: list[PairSpec],
    paired_difference_normality: pd.DataFrame,
    alpha: float,
) -> pd.DataFrame:
    """Run paired t and Wilcoxon; recommendation uses normality of differences."""
    rows: list[dict] = []
    for pair in pairs:
        complete = data.loc[:, [pair.column_a, pair.column_b]].dropna()
        first, second = complete[pair.column_a], complete[pair.column_b]
        differences = second - first
        normal_row = paired_difference_normality[
            paired_difference_normality["variable"] == pair.variable
        ]
        normal_differences = (
            len(normal_row) == 1
            and normal_row.iloc[0]["status"] == "does_not_reject_normality"
        )

        t_row = _base_row(pair, "t pareado", len(complete), alpha)
        if len(complete) >= 3:
            statistic, pvalue = ttest_rel(first, second)
            t_row.update(
                statistic=statistic,
                pvalue=pvalue,
                effect_size=_paired_dz(differences),
                effect_size_name="Cohen dz (Depois - Antes)",
                recommended=normal_differences,
                conclusion=_conclusion(pvalue, alpha),
            )
        else:
            t_row.update(conclusion="Menos de 3 pares completos.")
        rows.append(t_row)

        wilcoxon_row = _base_row(pair, "Wilcoxon pareado", len(complete), alpha)
        if len(complete) >= 3:
            try:
                statistic, pvalue = wilcoxon(first, second, alternative="two-sided", zero_method="pratt")
                wilcoxon_row.update(
                    statistic=statistic,
                    pvalue=pvalue,
                    recommended=not normal_differences,
                    conclusion=_conclusion(pvalue, alpha),
                    note="Use a distribuição das diferenças e o contexto do estudo para confirmar a escolha.",
                )
            except ValueError as exc:
                wilcoxon_row.update(conclusion="Wilcoxon não pôde ser calculado.", note=str(exc))
        else:
            wilcoxon_row.update(conclusion="Menos de 3 pares completos.")
        rows.append(wilcoxon_row)

    _apply_holm(rows)
    return pd.DataFrame(rows)
