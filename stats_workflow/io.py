"""Input/output helpers for the workflow's tab-separated wide tables."""

from __future__ import annotations

import ast
import csv
import hashlib
from pathlib import Path

import pandas as pd

from .schema import WorkflowValidationError, validate_wide_table


def _read_first_row(path: Path, encoding: str) -> list[str]:
    with path.open("r", encoding=encoding, newline="") as handle:
        row = next(csv.reader(handle, delimiter="\t"), None)
    if not row:
        raise WorkflowValidationError("O arquivo está vazio.")
    return row


def _is_serialized_pair(value: str) -> bool:
    try:
        candidate = ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return False
    return isinstance(candidate, tuple) and len(candidate) == 2


def _choose_encoding(path: Path) -> str:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            _read_first_row(path, encoding)
            return encoding
        except UnicodeDecodeError:
            continue
    raise WorkflowValidationError("Não foi possível ler o arquivo em UTF-8 ou latin-1.")


def read_wide_table(path: str | Path):
    """Read either a normal two-row header or a legacy serialized-tuple header."""
    source = Path(path).expanduser()
    if not source.is_file():
        raise WorkflowValidationError(f"Arquivo não encontrado: {source}")
    if source.suffix.lower() not in {".txt", ".tsv", ".csv"}:
        raise WorkflowValidationError("Use um arquivo .txt, .tsv ou .csv separado por TAB.")

    encoding = _choose_encoding(source)
    first_row = _read_first_row(source, encoding)
    is_legacy_one_header = all(_is_serialized_pair(value.strip()) for value in first_row if value.strip())

    if is_legacy_one_header:
        raw = pd.read_csv(source, sep="\t", header=0, decimal=",", encoding=encoding)
        columns: list[tuple[str, str]] = []
        for name in raw.columns:
            try:
                group, variable = ast.literal_eval(str(name))
            except (SyntaxError, ValueError) as exc:
                raise WorkflowValidationError(
                    f"Cabeçalho inválido: '{name}'."
                ) from exc
            columns.append((str(group), str(variable)))
        raw.columns = pd.MultiIndex.from_tuples(columns, names=["grupo", "variavel"])
    else:
        raw = pd.read_csv(source, sep="\t", header=[0, 1], decimal=",", encoding=encoding)

    keep = [
        col
        for col in raw.columns
        if not any(str(part).strip().lower().startswith("unnamed") for part in col)
    ]
    raw = raw.loc[:, keep]
    data, pairs = validate_wide_table(raw)
    return data, pairs, source


def write_wide_table(data: pd.DataFrame, path: str | Path) -> Path:
    """Write a validated table preserving the two header rows and decimal commas."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(destination, sep="\t", decimal=",", index=False, encoding="utf-8")
    return destination


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()
