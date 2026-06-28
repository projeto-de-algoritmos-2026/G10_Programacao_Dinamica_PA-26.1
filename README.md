# Caixa Eletrônico — Troco com Estoque Limitado

CLI que simula um caixa eletrônico: dado um estoque de cédulas e um valor de saque, calcula a combinação de notas com **menor quantidade possível** que fecha exatamente o valor, respeitando o estoque disponível.

---

## Instalação

Requer Python 3.10+ (usa `dict[int, int] | None` nas assinaturas de tipo).

```bash
git clone https://github.com/projeto-de-algoritmos-2026/G10_Programacao_Dinamica_PA-26.1.git
pip install -r requirements.txt
```

A única dependência é o `pytest`, usado para os testes — a aplicação em si não depende de nenhuma biblioteca externa.

## Como usar

O estoque de cédulas é um arquivo JSON no formato `{"denominação": quantidade}`. Já existe um exemplo em `data/estoque.json`:

```json
{
  "100": 10,
  "50": 15,
  "20": 20,
  "10": 20,
  "5": 30,
  "2": 30
}
```

### Consultar o estoque atual

```bash
python cli.py estoque
```

```
Estoque atual (data/estoque.json):
  R$ 100: 10 nota(s)
  R$ 50: 15 nota(s)
  R$ 20: 20 nota(s)
  R$ 10: 20 nota(s)
  R$ 5: 30 nota(s)
  R$ 2: 30 nota(s)
```

### Realizar um saque

```bash
python cli.py sacar 235
```

```
Saque de R$ 235 realizado com 5 notas:
  2x R$ 100
  1x R$ 20
  1x R$ 10
  1x R$ 5
```

Depois do saque, o arquivo de estoque é atualizado automaticamente — uma nova consulta a `python cli.py estoque` já mostra as notas debitadas.

### Usando um estoque diferente do padrão

Por padrão a CLI usa `data/estoque.json`. Para usar outro arquivo (por exemplo, para simular caixas diferentes ou testar manualmente sem afetar o estoque "oficial"):

```bash
python cli.py sacar 100 --estoque meu_estoque.json
python cli.py estoque --estoque meu_estoque.json
```

### Quando o saque não é possível

Se o valor pedido não puder ser formado com o estoque disponível (seja por falta de denominação compatível, seja por estoque insuficiente), a CLI avisa e termina com código de saída `1`, sem alterar o estoque:

```bash
$ python cli.py sacar 3 --estoque data/estoque.json
Saque não realizado: não é possível sacar R$ 3 com o estoque atual
```

## Estrutura do projeto

```
caixa-eletronico/
├── cli.py              # ponto de entrada da CLI (argparse): comandos `sacar` e `estoque`
├── core/
│   ├── __init__.py
│   └── troco.py         # algoritmo de DP (puro, sem I/O) — calcular_troco()
├── app/
│   ├── __init__.py
│   └── caixa.py         # camada de aplicação: estado do estoque, leitura/escrita do JSON
├── data/
│   └── estoque.json     # estoque inicial de exemplo
├── tests/
│   ├── __init__.py
│   ├── test_troco.py    # testes unitários do algoritmo de DP
│   └── test_cli.py      # testes de integração da CLI ponta a ponta
├── README.md
└── requirements.txt
```

A separação reflete a divisão do trabalho: `core/` contém só o algoritmo, sem nenhuma dependência de I/O ou de formato de arquivo — pode ser testado, reutilizado ou até importado em outro projeto sem trazer nada do resto. `app/` e `cli.py` cuidam de tudo em volta (estoque em disco, parsing de argumentos, formatação de saída).

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
- Após 2ª passada: `dp[6] = dp[3] + 1 = 2`. 

Processando `d = 1` (5 cópias): `dp[6]` já vale 2; nenhuma melhora possível usando 1s.

Resultado: `{3: 2}` — duas notas de 3, total 6. Note que o guloso (pegar primeiro a maior, 4) daria `4 + 1 + 1 = 3 notas`, pior que o ótimo `2`.

---

## Testes

Rodar a suíte completa:

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

- **`tests/test_troco.py`** cobre o algoritmo isoladamente: valor zero, caso ótimo, respeito ao estoque, casos impossíveis, validações de entrada, e o caso clássico em que o algoritmo guloso falha.
- **`tests/test_cli.py`** cobre a aplicação ponta a ponta: saque com sucesso, persistência do estoque entre saques sucessivos, mensagens de erro para estoque inexistente/JSON inválido/valor inválido, e o comando `estoque`.