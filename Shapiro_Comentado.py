"""Compatibilidade: Shapiro-Wilk seguro com relatório estruturado."""

from stats_workflow.legacy import legacy_main


if __name__ == "__main__":
    raise SystemExit(legacy_main("shapiro"))
