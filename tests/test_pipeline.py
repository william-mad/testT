"""Focused checks for the two supplied workflows and the main safety guard."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import pandas as pd

from stats_workflow.io import read_wide_table
from stats_workflow.pipeline import run_workflow
from stats_workflow.schema import WorkflowValidationError
from stats_workflow.transforms import apply_arcsine_sqrt, apply_log10


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_independent_workflow_creates_complete_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_workflow(
                ROOT / "data/independent/base_workflow_independente.txt",
                "independent",
                temporary,
            )
            output = result["run_directory"]
            self.assertEqual(len(result["tests"]), 21)  # 7 variables × Levene, Welch, Mann–Whitney
            self.assertEqual(len(result["tests"].query("recommended == True")), 7)
            self.assertTrue((output / "manifest.json").is_file())
            self.assertTrue((output / "summary.txt").is_file())
            data, pairs, _ = read_wide_table(output / "transformed_data.tsv")
            self.assertEqual(len(pairs), 7)
            self.assertEqual(data.shape, (60, 14))

    def test_paired_workflow_checks_differences_and_tests(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_workflow(
                ROOT / "data/paired/base_workflow_pareado.txt",
                "paired",
                temporary,
            )
            self.assertEqual(len(result["tests"]), 14)  # 7 variables × paired t, Wilcoxon
            self.assertEqual(len(result["final_difference_normality"]), 7)
            self.assertTrue((result["run_directory"] / "normality_differences_final.csv").is_file())

    def test_percentage_all_is_explicit_and_recorded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = run_workflow(
                ROOT / "data/independent/base_workflow_independente.txt",
                "independent",
                temporary,
                log10_mode="off",
                percentage_mode="all",
            )
            applied = result["transformations"].query("applied == True")
            self.assertEqual(applied["variable"].tolist(), ["Teor_agua_%"])

    def test_mismatched_adjacent_variables_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            malformed = Path(temporary) / "malformed.txt"
            malformed.write_text(
                "Controle\tTratamento\nAltura_cm\tBiomassa_mg\n1\t2\n3\t4\n5\t6\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(WorkflowValidationError, "não formam um par"):
                run_workflow(malformed, "independent", temporary)

    def test_log10_refuses_zero_instead_of_mixing_scales(self) -> None:
        data, pairs, _ = read_wide_table(
            ROOT / "data/independent/base_workflow_independente.txt"
        )
        data.iloc[0, 0] = 0
        with self.assertRaisesRegex(WorkflowValidationError, "zero ou negativos"):
            apply_log10(data, pairs, {"Altura_cm"})

    def test_percentage_transform_refuses_values_outside_range(self) -> None:
        data, pairs, _ = read_wide_table(
            ROOT / "data/independent/base_workflow_independente.txt"
        )
        data.iloc[0, 8] = 101
        with self.assertRaisesRegex(WorkflowValidationError, "fora de 0–100"):
            apply_arcsine_sqrt(data, pairs, {"Teor_agua_%"})


if __name__ == "__main__":
    unittest.main()
