"""Compatibilidade: aplica log10 sem depender de lista.txt global."""

from stats_workflow.legacy import legacy_main


if __name__ == "__main__":
    raise SystemExit(legacy_main("log10"))
