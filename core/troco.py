"""
Algoritmo de troco com estoque limitado de cédulas (bounded coin change).

Estado da DP:
    dp[v] = menor número de notas necessárias para formar exatamente o valor v,
            respeitando o estoque disponível de cada denominação.

Transição:
    Para cada denominação d com estoque q, percorremos os valores possíveis e
    permitimos usar 1..q cópias dessa nota. Para evitar reutilizar a mesma
    cópia mais de uma vez (caso do unbounded coin change), processamos cada
    nota individualmente — equivalente a expandir o estoque em "itens" de um
    0/1 knapsack, mas com a otimização binária para manter a complexidade
    razoável quando o estoque é grande.

    Aqui usamos a abordagem direta: para cada denominação, iteramos o vetor dp
    de trás para frente uma vez por unidade disponível. Isso é simples de ler
    e suficiente para os tamanhos de entrada de um caixa eletrônico real.

Reconstrução:
    Guardamos, para cada dp[v] atualizado, qual denominação foi usada
    (escolha[v]). Para reconstruir a combinação, partimos de v = valor e
    subtraímos a denominação registrada até chegar em 0.

Complexidade:
    Tempo:  O(valor * total_de_notas_no_estoque)
    Espaço: O(valor)
"""

from __future__ import annotations


def calcular_troco(
    valor: int, estoque: dict[int, int]
) -> dict[int, int] | None:
    """Calcula a combinação de cédulas com menor quantidade de notas.

    Args:
        valor: valor inteiro a ser sacado (em unidades da moeda, ex.: reais).
        estoque: mapa denominação -> quantidade disponível dessa nota.

    Returns:
        Um dicionário {denominação: quantidade_usada} representando o saque,
        ou None se for impossível compor o valor com o estoque fornecido.
        Para valor = 0, retorna {} (saque vazio é trivialmente válido).

    Raises:
        ValueError: se valor for negativo, ou se alguma denominação/quantidade
        do estoque for inválida (não positiva).
    """
    if valor < 0:
        raise ValueError("valor não pode ser negativo")
    for d, q in estoque.items():
        if d <= 0:
            raise ValueError(f"denominação inválida: {d}")
        if q < 0:
            raise ValueError(f"quantidade inválida para denominação {d}: {q}")

    if valor == 0:
        return {}

    INF = float("inf")
    dp: list[float] = [INF] * (valor + 1)
    dp[0] = 0
    escolha: list[int] = [0] * (valor + 1)

    denominacoes = sorted((d for d, q in estoque.items() if q > 0), reverse=True)

    for d in denominacoes:
        q_disponivel = estoque[d]
        # Uma "passada" por unidade da nota: equivalente a 0/1 knapsack
        # tratando cada cópia como um item independente.
        for _ in range(q_disponivel):
            for v in range(valor, d - 1, -1):
                if dp[v - d] + 1 < dp[v]:
                    dp[v] = dp[v - d] + 1
                    escolha[v] = d

    if dp[valor] == INF:
        return None

    resultado: dict[int, int] = {}
    v = valor
    while v > 0:
        d = escolha[v]
        resultado[d] = resultado.get(d, 0) + 1
        v -= d

    return resultado
