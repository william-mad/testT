"""Explicit transformations with validation and a readable audit trail."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .schema import PairSpec, WorkflowValidationError


def is_percentage_variable(variable: str) -> bool:
    return "%" in variable


def _non_normal_variables(normality: pd.DataFrame) -> set[str]:
    return set(normality.loc[normality["status"] == "rejects_normality", "variable"])


def plan_transformations(
    pairs: list[PairSpec],
    raw_normality: pd.DataFrame,
    log10_mode: str,
    percentage_mode: str,
) -> tuple[set[str], set[str]]:
    """Choose transformations without matching names by substring or shared files."""
    non_normal = _non_normal_variables(raw_normality)
    variables = {pair.variable for pair in pairs}

    if log10_mode == "off":
        log10_variables: set[str] = set()
    elif log10_mode == "auto":
        log10_variables = {
            variable
            for variable in non_normal
            if variable in variables and not is_percentage_variable(variable)
        }
    elif log10_mode == "all":
        log10_variables = {variable for variable in variables if not is_percentage_variable(variable)}
    else:
        raise WorkflowValidationError(f"Modo log10 desconhecido: {log10_mode}.")

    if percentage_mode == "off":
        percentage_variables: set[str] = set()
    elif percentage_mode == "auto":
        percentage_variables = {
            variable
            for variable in non_normal
            if variable in variables and is_percentage_variable(variable)
        }
    elif percentage_mode == "all":
        percentage_variables = {variable for variable in variables if is_percentage_variable(variable)}
    else:
        raise WorkflowValidationError(f"Modo de porcentagem desconhecido: {percentage_mode}.")

    return log10_variables, percentage_variables


def apply_log10(data: pd.DataFrame, pairs: list[PairSpec], variables: set[str]) -> tuple[pd.DataFrame, list[dict]]:
    transformed = data.copy()
    audit: list[dict] = []
    for pair in pairs:
        selected = pair.variable in variables
        if not selected:
            audit.append({"variable": pair.variable, "operation": "log10", "applied": False, "reason": "not_selected"})
            continue
        for column in (pair.column_a, pair.column_b):
            values = transformed[column].dropna()
            if (values <= 0).any():
                raise WorkflowValidationError(
                    f"Não é seguro aplicar log10 em '{pair.variable}': há valores zero ou negativos. "
                    "Corrija os dados ou escolha uma política explícita antes de transformar."
                )
            transformed[column] = np.log10(transformed[column])
        audit.append({"variable": pair.variable, "operation": "log10", "applied": True, "reason": "selected_from_shapiro"})
    return transformed, audit


def apply_arcsine_sqrt(
    data: pd.DataFrame, pairs: list[PairSpec], variables: set[str]
) -> tuple[pd.DataFrame, list[dict]]:
    transformed = data.copy()
    audit: list[dict] = []
    for pair in pairs:
        selected = pair.variable in variables
        if not selected:
            audit.append({"variable": pair.variable, "operation": "arcsine_sqrt_percent", "applied": False, "reason": "not_selected"})
            continue
        for column in (pair.column_a, pair.column_b):
            values = transformed[column].dropna()
            if ((values < 0) | (values > 100)).any():
                raise WorkflowValidationError(
                    f"A variável '{pair.variable}' foi marcada como porcentagem, mas contém valores fora de 0–100."
                )
            transformed[column] = np.arcsin(np.sqrt(transformed[column] / 100.0))
        audit.append({"variable": pair.variable, "operation": "arcsine_sqrt_percent", "applied": True, "reason": "selected_from_shapiro"})
    return transformed, audit
