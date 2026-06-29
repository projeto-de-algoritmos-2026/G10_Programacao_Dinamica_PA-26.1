"""
cli.py

Interface de linha de comando do caixa eletrônico simulado.

Modo interativo (padrão, sem nenhum subcomando):
    python cli.py
    python cli.py --estoque data/estoque.json

Modo direto, um comando por chamada (útil para scripts e automação):
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


def _menu_sacar(caixa: Caixa) -> None:
    """Pede o valor ao usuário e tenta realizar o saque, dentro do loop do menu."""
    entrada = input("Valor a sacar: R$ ").strip()
    try:
        valor = int(entrada)
    except ValueError:
        print("Valor inválido — digite um número inteiro.")
        return

    try:
        combinacao = caixa.sacar(valor)
    except ValueError as exc:
        print(f"Erro: {exc}")
        return
    except SaqueImpossivelError as exc:
        print(f"Saque não realizado: {exc}")
        return

    total_notas = sum(combinacao.values())
    plural = "s" if total_notas != 1 else ""
    print()
    print(f"Saque de R$ {valor} realizado com {total_notas} nota{plural}:")
    print(formatar_combinacao(combinacao))


def executar_menu_interativo(caminho_estoque: str) -> int:
    """Abre o menu interativo do caixa eletrônico em loop, até o usuário sair.

    Carrega o estoque uma única vez e reutiliza a mesma instância de Caixa
    entre as operações do menu, já que cada saque atualiza e persiste o
    estoque internamente.
    """
    try:
        caixa = Caixa(caminho_estoque)
    except FileNotFoundError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except EstoqueInvalidoError as exc:
        print(f"Erro no arquivo de estoque: {exc}", file=sys.stderr)
        return 1

    print("=" * 36)
    print("CAIXA ELETRÔNICO".center(36))
    print("=" * 36)

    while True:
        print()
        print("1. Sacar dinheiro")
        print("2. Consultar estoque de notas")
        print("0. Sair")

        try:
            escolha = input("Escolha uma opção: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            print("Até logo!")
            return 0

        if escolha == "1":
            _menu_sacar(caixa)
        elif escolha == "2":
            print()
            print(f"Estoque atual ({caixa.caminho_estoque}):")
            print(formatar_estoque(caixa.estoque))
        elif escolha == "0":
            print("Até logo!")
            return 0
        else:
            print("Opção inválida. Tente novamente.")


def construir_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos da CLI, com os subcomandos disponíveis.

    O subcomando é opcional: se nenhum for passado, a CLI abre o menu
    interativo (usando --estoque no nível raiz). Se um subcomando for
    passado, ele executa direto e retorna — sem abrir o menu.
    """
    parser = argparse.ArgumentParser(
        prog="caixa-eletronico",
        description=(
            "Simulador de caixa eletrônico que calcula o troco com o menor "
            "número de notas possível, respeitando o estoque disponível "
            "(programação dinâmica). Sem subcomando, abre o menu interativo."
        ),
    )
    parser.add_argument(
        "--estoque",
        default=CAMINHO_ESTOQUE_PADRAO,
        help=(
            "caminho do arquivo JSON de estoque usado pelo menu interativo "
            f"(padrão: {CAMINHO_ESTOQUE_PADRAO})"
        ),
    )
    subparsers = parser.add_subparsers(dest="comando")

    parser_sacar = subparsers.add_parser(
        "sacar", help="realiza um saque diretamente, sem abrir o menu"
    )
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
        "estoque", help="mostra o estoque atual de notas, sem abrir o menu"
    )
    parser_estoque.add_argument(
        "--estoque",
        default=CAMINHO_ESTOQUE_PADRAO,
        help=f"caminho do arquivo JSON de estoque (padrão: {CAMINHO_ESTOQUE_PADRAO})",
    )
    parser_estoque.set_defaults(func=comando_estoque)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI.

    Sem subcomando: abre o menu interativo.
    Com subcomando (`sacar`, `estoque`): executa direto e retorna.
    """
    parser = construir_parser()
    args = parser.parse_args(argv)
    if args.comando is None:
        return executar_menu_interativo(args.estoque)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
