"""
cli.py

Interface de linha de comando do caixa eletrônico simulado.

Exemplos:
    python cli.py sacar 235
    python cli.py sacar 235 --estoque data/estoque.json
    python cli.py estoque
"""

from __future__ import annotations

import argparse
import sys

from app.caixa import Caixa, EstoqueInvalidoError, SaqueImpossivelError

CAMINHO_ESTOQUE_PADRAO = "data/estoque.json"


def formatar_combinacao(combinacao: dict[int, int]) -> str:
    """Formata a combinação de notas entregues para exibição no terminal."""
    if not combinacao:
        return "  (nenhuma nota — valor de R$ 0)"
    linhas = [
        f"  {combinacao[d]}x R$ {d}" for d in sorted(combinacao, reverse=True)
    ]
    return "\n".join(linhas)


def formatar_estoque(estoque: dict[int, int]) -> str:
    """Formata o estoque atual de notas para exibição no terminal."""
    if not estoque or all(quantidade == 0 for quantidade in estoque.values()):
        return "  (estoque vazio)"
    linhas = [
        f"  R$ {d}: {estoque[d]} nota(s)" for d in sorted(estoque, reverse=True)
    ]
    return "\n".join(linhas)


def comando_sacar(args: argparse.Namespace) -> int:
    """Executa o comando `sacar`: carrega o estoque, tenta o saque e mostra o resultado."""
    try:
        caixa = Caixa(args.estoque)
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except EstoqueInvalidoError as exc:
        print(f"Erro no arquivo de estoque: {exc}", file=sys.stderr)
        return 1

    try:
        combinacao = caixa.sacar(args.valor)
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except SaqueImpossivelError as exc:
        print(f"Saque não realizado: {exc}", file=sys.stderr)
        return 1

    total_notas = sum(combinacao.values())
    plural = "s" if total_notas != 1 else ""
    print(f"Saque de R$ {args.valor} realizado com {total_notas} nota{plural}:")
    print(formatar_combinacao(combinacao))
    return 0


def comando_estoque(args: argparse.Namespace) -> int:
    """Executa o comando `estoque`: carrega e exibe o estoque atual de notas."""
    try:
        caixa = Caixa(args.estoque)
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except EstoqueInvalidoError as exc:
        print(f"Erro no arquivo de estoque: {exc}", file=sys.stderr)
        return 1

    print(f"Estoque atual ({caixa.caminho_estoque}):")
    print(formatar_estoque(caixa.estoque))
    return 0


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos da CLI, com os subcomandos disponíveis."""
    parser = argparse.ArgumentParser(
        prog="caixa-eletronico",
        description=(
            "Simulador de caixa eletrônico que calcula o troco com o menor "
            "número de notas possível, respeitando o estoque disponível "
            "(programação dinâmica)."
        ),
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_sacar = subparsers.add_parser("sacar", help="realiza um saque")
    parser_sacar.add_argument(
        "valor", type=int, help="valor a sacar, em reais (inteiro)"
    )
    parser_sacar.add_argument(
        "--estoque",
        default=CAMINHO_ESTOQUE_PADRAO,
        help=f"caminho do arquivo JSON de estoque (padrão: {CAMINHO_ESTOQUE_PADRAO})",
    )
    parser_sacar.set_defaults(func=comando_sacar)

    parser_estoque = subparsers.add_parser(
        "estoque", help="mostra o estoque atual de notas"
    )
    parser_estoque.add_argument(
        "--estoque",
        default=CAMINHO_ESTOQUE_PADRAO,
        help=f"caminho do arquivo JSON de estoque (padrão: {CAMINHO_ESTOQUE_PADRAO})",
    )
    parser_estoque.set_defaults(func=comando_estoque)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI. Retorna o código de saída do processo."""
    parser = construir_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
