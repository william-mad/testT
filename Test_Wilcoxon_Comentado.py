"""Compatibilidade: Wilcoxon para medidas pareadas."""

from stats_workflow.legacy import legacy_main


if __name__ == "__main__":
    raise SystemExit(legacy_main("wilcoxon"))
