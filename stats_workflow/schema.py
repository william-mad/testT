"""Data structures and validation rules for the wide two-row table format."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


class WorkflowValidationError(ValueError):
    """Raised when an input table cannot be analysed safely."""


@dataclass(frozen=True)
class PairSpec:
    """One explicit comparison represented by two adjacent columns."""

    position: int
    group_a: str
    group_b: str
    variable: str
    column_a: tuple[str, str]
    column_b: tuple[str, str]

    @property
    def label(self) -> str:
        return f"{self.variable}: {self.group_a} × {self.group_b}"


def validate_wide_table(data: pd.DataFrame) -> tuple[pd.DataFrame, list[PairSpec]]:
    """Validate numeric data and return an explicit map of comparison pairs.

    The accepted format has two header rows: group/moment then variable.  Columns
    must occur in pairs and both columns in a pair must refer to the same variable.
    This catches the most dangerous accidental column reordering before any test is
    run.
    """
    if not isinstance(data.columns, pd.MultiIndex) or data.columns.nlevels != 2:
        raise WorkflowValidationError(
            "A tabela precisa de duas linhas de cabeçalho: grupo/momento e variável."
        )

    if data.shape[1] == 0:
        raise WorkflowValidationError("A tabela não possui colunas de dados.")
    if data.shape[1] % 2:
        raise WorkflowValidationError(
            "A tabela possui um número ímpar de colunas. Cada variável precisa de um par."
        )

    clean = pd.DataFrame(index=data.index)
    normalized_columns: list[tuple[str, str]] = []
    for original in data.columns:
        group, variable = (str(original[0]).strip(), str(original[1]).strip())
        if not group or group.lower().startswith("unnamed"):
            raise WorkflowValidationError("Há uma coluna sem nome de grupo/momento.")
        if not variable or variable.lower().startswith("unnamed"):
            raise WorkflowValidationError("Há uma coluna sem nome de variável.")

        raw = data[original]
        text = raw.astype(str).str.strip()
        numeric = pd.to_numeric(text.str.replace(",", ".", regex=False), errors="coerce")
        invalid = raw.notna() & text.ne("") & numeric.isna()
        if invalid.any():
            examples = ", ".join(text[invalid].head(3).tolist())
            raise WorkflowValidationError(
                f"A coluna '{group} - {variable}' contém valor não numérico: {examples}."
            )
        key = (group, variable)
        normalized_columns.append(key)
        clean[key] = numeric

    clean.columns = pd.MultiIndex.from_tuples(normalized_columns, names=["grupo", "variavel"])

    pairs: list[PairSpec] = []
    seen_variables: set[str] = set()
    for position in range(0, clean.shape[1], 2):
        column_a = clean.columns[position]
        column_b = clean.columns[position + 1]
        if column_a[1] != column_b[1]:
            raise WorkflowValidationError(
                "As colunas "
                f"{position + 1} e {position + 2} não formam um par: "
                f"'{column_a[1]}' ≠ '{column_b[1]}'. Reorganize-as lado a lado."
            )
        if column_a[0] == column_b[0]:
            raise WorkflowValidationError(
                f"O par '{column_a[1]}' usa o mesmo grupo/momento duas vezes ('{column_a[0]}')."
            )
        if column_a[1] in seen_variables:
            raise WorkflowValidationError(
                f"A variável '{column_a[1]}' aparece em mais de um par. "
                "Use nomes de variável únicos nesta tabela de dois grupos."
            )
        seen_variables.add(column_a[1])
        pairs.append(
            PairSpec(
                position=(position // 2) + 1,
                group_a=column_a[0],
                group_b=column_b[0],
                variable=column_a[1],
                column_a=column_a,
                column_b=column_b,
            )
        )
    return clean, pairs
