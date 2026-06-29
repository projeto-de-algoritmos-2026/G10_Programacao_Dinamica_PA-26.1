# Caixa Eletrônico — Troco com Estoque Limitado

Número da Lista: 4<br>
Conteúdo da Disciplina: Programação Dinâmica<br>

---

## Alunos
|Matrícula | Aluno |
| :-------: | :------------------------------: |
| 23/1038072  |  Gabriel Dantas Bevilaqua Mendes |
| 23/1026483  |  Maria Eduarda de Amorim Galdino |

--- 
## Link do vídeo 

Para acessar a apresentação, clique no link abaixo:

[Assistir ao vídeo](https://youtu.be/D_wObJzOMx0)

--- 

## Sobre 

CLI que simula um caixa eletrônico: dado um estoque de cédulas e um valor de saque, calcula a combinação de notas com **menor quantidade possível** que fecha exatamente o valor, respeitando o estoque disponível. Implementa programação dinâmica ao algoritmo do Coin Change. 

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

### Modo interativo (recomendado para uso manual)

Rodar sem nenhum subcomando abre um menu, como num caixa eletrônico de verdade:

```bash
python3 cli.py
```

```
====================================
          CAIXA ELETRÔNICO
====================================

1. Sacar dinheiro
2. Consultar estoque de notas
0. Sair
Escolha uma opção: 1
Valor a sacar: R$ 235

Saque de R$ 235 realizado com 5 notas:
  2x R$ 100
  1x R$ 20
  1x R$ 10
  1x R$ 5
```

O menu reusa a mesma instância do caixa entre as operações, então o estoque já sai atualizado a cada novo saque, dentro da mesma sessão.

Para usar um estoque diferente do padrão no menu interativo:

```bash
python3 cli.py --estoque meu_estoque.json
```

### Modo direto (um comando por chamada, útil para scripts e testes)

#### Consultar o estoque atual

```bash
python3 cli.py estoque
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

#### Realizar um saque

```bash
python3 cli.py sacar 235
```

```
Saque de R$ 235 realizado com 5 notas:
  2x R$ 100
  1x R$ 20
  1x R$ 10
  1x R$ 5
```

Depois do saque, o arquivo de estoque é atualizado automaticamente — uma nova consulta a `python cli.py estoque` já mostra as notas debitadas.

#### Usando um estoque diferente do padrão

```bash
python3 cli.py sacar 100 --estoque meu_estoque.json
python3 cli.py estoque --estoque meu_estoque.json
```

### Quando o saque não é possível

Se o valor pedido não puder ser formado com o estoque disponível (seja por falta de denominação compatível, seja por estoque insuficiente), a CLI avisa — no menu, sem encerrar a sessão; no modo direto, terminando com código de saída `1` e sem alterar o estoque:

```bash
$ python3 cli.py sacar 3 --estoque data/estoque.json
Saque não realizado: não é possível sacar R$ 3 com o estoque atual
```

## Estrutura do projeto

```
caixa-eletronico/
├── cli.py              # ponto de entrada: menu interativo (padrão) e comandos diretos `sacar`/`estoque`
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
│   └── test_cli.py      # testes de integração: comandos diretos e menu interativo
├── README.md
└── requirements.txt
```

A separação reflete a divisão do trabalho: `core/` contém só o algoritmo, sem nenhuma dependência de I/O ou de formato de arquivo — pode ser testado, reutilizado ou até importado em outro projeto sem trazer nada do resto. `app/` e `cli.py` cuidam de tudo em volta (estoque em disco, parsing de argumentos, formatação de saída).

---

## Testes

Rodar a suíte completa:

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v
```

- **`tests/test_troco.py`** cobre o algoritmo isoladamente: valor zero, caso ótimo, respeito ao estoque, casos impossíveis, validações de entrada, e o caso clássico em que o algoritmo guloso falha.
- **`tests/test_cli.py`** cobre a aplicação ponta a ponta: saque com sucesso, persistência do estoque entre saques sucessivos, mensagens de erro para estoque inexistente/JSON inválido/valor inválido, o comando `estoque`, e o menu interativo (simulando entradas do usuário via `monkeypatch` no `input()`).
