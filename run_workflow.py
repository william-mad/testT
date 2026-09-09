"""Execute the complete statistical workflow from the terminal or Pydroid."""

from __future__ import annotations

import argparse
from pathlib import Path

from stats_workflow.pipeline import run_workflow
from stats_workflow.schema import WorkflowValidationError


def _interactive_arguments() -> argparse.Namespace:
    input_path = input("Arquivo de entrada (.txt/.tsv): ").strip()
    print("Desenho experimental: 1 = grupos independentes | 2 = dados pareados")
    choice = input("Escolha [1]: ").strip() or "1"
    design = "independent" if choice == "1" else "paired" if choice == "2" else ""
    alpha_text = input("Alpha [0.05]: ").strip() or "0.05"
    return argparse.Namespace(
        input=input_path,
        design=design,
        output="results/generated",
        alpha=float(alpha_text),
        log10="auto",
        percentage="auto",
        pause=True,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Workflow estatístico: validação, Shapiro, transformações e testes."
    )
    parser.add_argument("--input", help="Arquivo tabulado com duas linhas de cabeçalho.")
    parser.add_argument("--design", choices=["independent", "paired"])
    parser.add_argument("--output", default="results/generated", help="Pasta que receberá uma subpasta de execução.")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--log10", choices=["auto", "off", "all"], default="auto")
    parser.add_argument("--percentage", choices=["auto", "off", "all"], default="auto")
    parser.add_argument("--pause", action="store_true", help="Espera Enter ao final (útil ao abrir por duplo clique).")
    return parser


def main() -> int:
    parser = _parser()
    args = parser.parse_args()
    if not args.input or not args.design:
        args = _interactive_arguments()
    if args.design not in {"independent", "paired"}:
        print("Erro: escolha 1 (independente) ou 2 (pareado).")
        return 2
    try:
        result = run_workflow(
            args.input,
            args.design,
            args.output,
            alpha=args.alpha,
            log10_mode=args.log10,
            percentage_mode=args.percentage,
        )
    except (WorkflowValidationError, ValueError, OSError) as exc:
        print(f"Erro: {exc}")
        return 2

    output = Path(result["run_directory"])
    recommended = result["tests"][result["tests"]["recommended"]]
    print(f"\nConcluído. Resultados: {output}")
    print(f"Testes recomendados: {len(recommended)}")
    print(f"Leia: {output / 'summary.txt'}")
    if args.pause:
        input("\nPressione Enter para fechar...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
