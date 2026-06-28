# Caixa Eletrônico — Troco com Estoque Limitado

CLI que simula um caixa eletrônico: dado um estoque de cédulas e um valor de saque, calcula a combinação de notas com **menor quantidade possível** que fecha exatamente o valor, respeitando o estoque disponível.

> Seções de **Instalação**, **Como usar** e **Estrutura do projeto** serão preenchidas pela Pessoa B.

---

## Como o algoritmo funciona

O problema é uma variação do **coin change** clássico, mas com uma diferença importante: cada denominação tem um **estoque limitado**. Isso é equivalente a um **bounded knapsack** — não dá pra reutilizar a mesma nota infinitas vezes.

### Estado da DP

```
dp[v] = menor número de notas necessárias para formar exatamente o valor v,
        usando no máximo a quantidade disponível de cada denominação.
```

Inicializamos `dp[0] = 0` (zero notas formam o valor zero) e `dp[v] = ∞` para todo `v > 0`.

### Transição

Para cada denominação `d` com estoque `q`, fazemos `q` passadas sobre o vetor `dp`. Em cada passada, percorremos `v` de `valor` até `d` (de trás pra frente) e aplicamos:

```
dp[v] = min(dp[v], dp[v - d] + 1)
```

Iterar de trás pra frente garante que, dentro de uma mesma passada, não reutilizamos a mesma cópia da nota — é o truque padrão do 0/1 knapsack. Repetir a passada `q` vezes permite usar até `q` cópias daquela denominação.

### Reconstrução

Guardamos, em paralelo, um vetor `escolha[v]` com a última denominação que melhorou `dp[v]`. Para descobrir **quais** notas compõem a solução, partimos de `v = valor` e seguimos:

```
enquanto v > 0:
    d = escolha[v]
    usa uma nota de d
    v = v - d
```

### Quando retorna `None`

Se ao final `dp[valor] == ∞`, é impossível formar o valor com o estoque dado (notas não fecham o valor, ou estoque insuficiente).

### Complexidade

- **Tempo:** `O(valor × N)`, onde `N` é o total de notas no estoque (soma das quantidades).
- **Espaço:** `O(valor)` para o vetor `dp` e mais `O(valor)` para `escolha`.

### Exemplo passo a passo

Estoque: `{4: 2, 3: 2, 1: 5}` — valor desejado: `6`.

Estado inicial: `dp = [0, ∞, ∞, ∞, ∞, ∞, ∞]`.

Processando `d = 4` (2 cópias):
- Após 1ª passada: `dp[4] = 1`.
- Após 2ª passada: nada melhora (não dá pra usar 2x4 = 8 ≤ 6).

Processando `d = 3` (2 cópias):
- Após 1ª passada: `dp[3] = 1`.
- Após 2ª passada: `dp[6] = dp[3] + 1 = 2`. ✅

Processando `d = 1` (5 cópias): `dp[6]` já vale 2; nenhuma melhora possível usando 1s.

Resultado: `{3: 2}` — duas notas de 3, total 6. Note que o guloso (pegar primeiro a maior, 4) daria `4 + 1 + 1 = 3 notas`, pior que o ótimo `2`.

---

## Testes

```bash
pip install pytest
pytest tests/test_troco.py -v
```

Os testes cobrem: valor zero, caso ótimo, respeito ao estoque, casos impossíveis, validações de entrada, e o caso clássico em que o algoritmo guloso falha.
