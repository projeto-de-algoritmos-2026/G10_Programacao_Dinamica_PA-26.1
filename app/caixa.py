"""
app/caixa.py

Camada de aplicação do caixa eletrônico: cuida do estado do estoque de
cédulas (carregar, persistir e debitar), delegando ao núcleo de DP
(core.troco.calcular_troco) a decisão de QUAIS notas usar em cada saque.

Este módulo não implementa nenhum algoritmo novo — só orquestra I/O em
volta do que já está em core/troco.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from core.troco import calcular_troco


class EstoqueInvalidoError(Exception):
    """Levantado quando o arquivo de estoque tem formato ou conteúdo inválido."""


class SaqueImpossivelError(Exception):
    """Levantado quando não é possível compor o valor pedido com o estoque atual."""


def carregar_estoque(caminho: str | Path) -> dict[int, int]:
    """Lê o estoque de cédulas de um arquivo JSON.

    O arquivo deve conter um objeto mapeando denominação -> quantidade
    disponível, ex.: {"50": 10, "20": 5, "10": 8}.

    Args:
        caminho: caminho do arquivo JSON de estoque.

    Returns:
        Dicionário {denominação: quantidade} com chaves e valores como int.

    Raises:
        FileNotFoundError: se o arquivo não existir.
        EstoqueInvalidoError: se o conteúdo não for um JSON válido no
            formato esperado, ou contiver denominação/quantidade inválida.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"arquivo de estoque não encontrado: {caminho}")

    try:
        bruto = json.loads(caminho.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise EstoqueInvalidoError(f"JSON inválido em '{caminho}': {exc}") from exc

    if not isinstance(bruto, dict):
        raise EstoqueInvalidoError(
            "o estoque deve ser um objeto JSON no formato {denominação: quantidade}"
        )

    estoque: dict[int, int] = {}
    for chave, valor in bruto.items():
        try:
            denominacao = int(chave)
            quantidade = int(valor)
        except (TypeError, ValueError) as exc:
            raise EstoqueInvalidoError(
                f"denominação ou quantidade inválida no estoque: {chave!r} -> {valor!r}"
            ) from exc
        if denominacao <= 0:
            raise EstoqueInvalidoError(f"denominação inválida no estoque: {denominacao}")
        if quantidade < 0:
            raise EstoqueInvalidoError(
                f"quantidade inválida para a denominação {denominacao}: {quantidade}"
            )
        estoque[denominacao] = quantidade

    return estoque


def salvar_estoque(caminho: str | Path, estoque: dict[int, int]) -> None:
    """Persiste o estoque de cédulas em um arquivo JSON.

    As denominações são salvas como string (formato JSON), ordenadas da
    maior para a menor para facilitar leitura manual do arquivo.
    """
    caminho = Path(caminho)
    ordenado = {str(d): q for d, q in sorted(estoque.items(), reverse=True)}
    caminho.write_text(
        json.dumps(ordenado, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def aplicar_saque(
    estoque: dict[int, int], combinacao: dict[int, int]
) -> dict[int, int]:
    """Debita as notas de uma combinação do estoque, sem modificar o original.

    Args:
        estoque: estoque atual.
        combinacao: notas a debitar, no formato {denominação: quantidade}.

    Returns:
        Um novo dicionário de estoque já com as notas debitadas.

    Raises:
        ValueError: se a combinação tentar debitar mais notas de uma
            denominação do que o estoque disponível (não deveria acontecer
            se a combinação vier de calcular_troco com este mesmo estoque,
            mas a verificação evita inconsistência silenciosa).
    """
    novo_estoque = dict(estoque)
    for denominacao, quantidade in combinacao.items():
        disponivel = novo_estoque.get(denominacao, 0)
        if quantidade > disponivel:
            raise ValueError(
                f"tentando debitar {quantidade} nota(s) de R$ {denominacao}, "
                f"mas só há {disponivel} em estoque"
            )
        novo_estoque[denominacao] = disponivel - quantidade
    return novo_estoque


class Caixa:
    """Representa um caixa eletrônico com estoque de cédulas persistido em arquivo.

    Carrega o estoque na criação e, a cada saque bem-sucedido, debita as
    notas usadas e regrava o arquivo — simulando o estado real de um caixa
    entre operações.
    """

    def __init__(self, caminho_estoque: str | Path) -> None:
        self.caminho_estoque = Path(caminho_estoque)
        self.estoque = carregar_estoque(self.caminho_estoque)

    def sacar(self, valor: int) -> dict[int, int]:
        """Realiza um saque: calcula a combinação ótima, debita e persiste o estoque.

        Args:
            valor: valor a sacar.

        Returns:
            A combinação de notas entregues, {denominação: quantidade}.

        Raises:
            ValueError: se o valor for inválido (propagado de calcular_troco).
            SaqueImpossivelError: se não houver combinação possível com o
                estoque atual.
        """
        combinacao = calcular_troco(valor, self.estoque)
        if combinacao is None:
            raise SaqueImpossivelError(
                f"não é possível sacar R$ {valor} com o estoque atual"
            )
        self.estoque = aplicar_saque(self.estoque, combinacao)
        salvar_estoque(self.caminho_estoque, self.estoque)
        return combinacao
