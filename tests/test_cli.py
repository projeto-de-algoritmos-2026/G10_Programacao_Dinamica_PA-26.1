import json

import pytest

from cli import main


@pytest.fixture
def arquivo_estoque(tmp_path):
    """Cria um arquivo de estoque isolado em diretório temporário para cada teste."""
    caminho = tmp_path / "estoque.json"
    caminho.write_text(json.dumps({"100": 2, "50": 5, "20": 5, "10": 5, "5": 5}))
    return caminho


def test_sacar_sucesso_mostra_combinacao(arquivo_estoque, capsys):
    codigo = main(["sacar", "180", "--estoque", str(arquivo_estoque)])
    saida = capsys.readouterr().out

    assert codigo == 0
    assert "180" in saida
    # 100 + 50 + 20 + 10 = 4 notas é o ótimo
    assert "4 nota" in saida
    assert "1x R$ 100" in saida
    assert "1x R$ 50" in saida


def test_sacar_atualiza_e_persiste_estoque(arquivo_estoque):
    main(["sacar", "100", "--estoque", str(arquivo_estoque)])

    estoque_atualizado = json.loads(arquivo_estoque.read_text())
    # tinha 2 notas de 100, usou 1 para sacar 100
    assert estoque_atualizado["100"] == 1


def test_dois_saques_seguidos_consomem_estoque_corretamente(arquivo_estoque, capsys):
    main(["sacar", "100", "--estoque", str(arquivo_estoque)])
    main(["sacar", "100", "--estoque", str(arquivo_estoque)])
    capsys.readouterr()  # limpa a saída acumulada dos dois saques acima

    estoque_atualizado = json.loads(arquivo_estoque.read_text())
    assert estoque_atualizado["100"] == 0

    # terceiro saque de 100 não pode mais usar nota de 100 (estoque zerado);
    # ainda é possível com 50+50, o que confirma que o estoque foi
    # persistido e relido corretamente entre as chamadas.
    codigo = main(["sacar", "100", "--estoque", str(arquivo_estoque)])
    saida = capsys.readouterr().out

    assert codigo == 0
    assert "2x R$ 50" in saida


def test_sacar_impossivel_retorna_codigo_de_erro(arquivo_estoque, capsys):
    # estoque sem moedas pequenas o suficiente para fechar valores ímpares
    codigo = main(["sacar", "37", "--estoque", str(arquivo_estoque)])
    saida_erro = capsys.readouterr().err

    assert codigo == 1
    assert "não" in saida_erro.lower()


def test_sacar_valor_negativo_retorna_codigo_de_erro(arquivo_estoque, capsys):
    codigo = main(["sacar", "-10", "--estoque", str(arquivo_estoque)])
    saida_erro = capsys.readouterr().err

    assert codigo == 1
    assert "erro" in saida_erro.lower()


def test_sacar_estoque_inexistente_retorna_codigo_de_erro(tmp_path, capsys):
    caminho_inexistente = tmp_path / "nao_existe.json"
    codigo = main(["sacar", "50", "--estoque", str(caminho_inexistente)])
    saida_erro = capsys.readouterr().err

    assert codigo == 1
    assert "não encontrado" in saida_erro.lower()


def test_sacar_estoque_com_json_invalido_retorna_codigo_de_erro(tmp_path, capsys):
    caminho = tmp_path / "estoque.json"
    caminho.write_text("{isso nao e json valido")

    codigo = main(["sacar", "50", "--estoque", str(caminho)])
    saida_erro = capsys.readouterr().err

    assert codigo == 1
    assert "erro" in saida_erro.lower()


def test_sacar_estoque_com_denominacao_invalida_retorna_codigo_de_erro(tmp_path, capsys):
    caminho = tmp_path / "estoque.json"
    caminho.write_text(json.dumps({"0": 5, "-10": 3}))

    codigo = main(["sacar", "50", "--estoque", str(caminho)])
    saida_erro = capsys.readouterr().err

    assert codigo == 1
    assert "erro" in saida_erro.lower()


def test_comando_estoque_mostra_saldo_atual(arquivo_estoque, capsys):
    codigo = main(["estoque", "--estoque", str(arquivo_estoque)])
    saida = capsys.readouterr().out

    assert codigo == 0
    assert "R$ 100" in saida
    assert "R$ 50" in saida
    assert "2 nota" in saida  # 2 notas de 100 no estoque inicial


def test_comando_estoque_reflete_saque_anterior(arquivo_estoque, capsys):
    main(["sacar", "100", "--estoque", str(arquivo_estoque)])
    capsys.readouterr()  # limpa a saída do saque

    main(["estoque", "--estoque", str(arquivo_estoque)])
    saida = capsys.readouterr().out

    assert "R$ 100: 1 nota" in saida
