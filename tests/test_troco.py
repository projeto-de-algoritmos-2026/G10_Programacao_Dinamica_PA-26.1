import pytest

from core.troco import calcular_troco


def _total(combinacao: dict[int, int]) -> int:
    return sum(d * q for d, q in combinacao.items())


def _n_notas(combinacao: dict[int, int]) -> int:
    return sum(combinacao.values())


def test_valor_zero_retorna_combinacao_vazia():
    assert calcular_troco(0, {50: 10, 20: 5}) == {}


def test_saque_simples_usa_menor_numero_de_notas():
    estoque = {100: 5, 50: 5, 20: 5, 10: 5}
    resultado = calcular_troco(180, estoque)
    assert resultado is not None
    assert _total(resultado) == 180
    # 100 + 50 + 20 + 10 = 4 notas é o ótimo
    assert _n_notas(resultado) == 4


def test_respeita_estoque_limitado():
    # Sem estoque suficiente de 50s, precisa usar 20s
    estoque = {50: 1, 20: 10}
    resultado = calcular_troco(90, estoque)
    assert resultado is not None
    assert _total(resultado) == 90
    assert resultado.get(50, 0) <= 1
    for d, q in resultado.items():
        assert q <= estoque[d]


def test_impossivel_retorna_none():
    # Só temos notas de 20; valor 35 é impossível
    estoque = {20: 10}
    assert calcular_troco(35, estoque) is None


def test_estoque_insuficiente_retorna_none():
    # Precisaria de 5 notas de 50, mas só há 2
    estoque = {50: 2}
    assert calcular_troco(250, estoque) is None


def test_estoque_vazio_para_valor_positivo():
    assert calcular_troco(50, {}) is None
    assert calcular_troco(50, {50: 0}) is None


def test_valor_negativo_levanta():
    with pytest.raises(ValueError):
        calcular_troco(-10, {50: 1})


def test_denominacao_invalida_levanta():
    with pytest.raises(ValueError):
        calcular_troco(50, {0: 5})
    with pytest.raises(ValueError):
        calcular_troco(50, {-10: 5})


def test_quantidade_negativa_levanta():
    with pytest.raises(ValueError):
        calcular_troco(50, {50: -1})


def test_prefere_nota_grande_quando_possivel():
    # 100 com {50: 5, 20: 5, 10: 5} deve usar 2x50, não 5x20
    resultado = calcular_troco(100, {50: 5, 20: 5, 10: 5})
    assert resultado is not None
    assert _n_notas(resultado) == 2
    assert resultado == {50: 2}


def test_caso_em_que_guloso_falha():
    # Caso clássico onde o guloso quebra: denominações {4, 3, 1}, valor 6.
    # Guloso pegaria 4+1+1 = 3 notas; ótimo é 3+3 = 2 notas.
    resultado = calcular_troco(6, {4: 10, 3: 10, 1: 10})
    assert resultado is not None
    assert _n_notas(resultado) == 2
    assert _total(resultado) == 6


def test_nao_modifica_estoque_de_entrada():
    estoque = {50: 5, 20: 5}
    snapshot = dict(estoque)
    calcular_troco(120, estoque)
    assert estoque == snapshot


def test_solucao_unica_forcada():
    # Único jeito de fechar 30 com {20:1, 10:1, 5:2} é 20+10
    resultado = calcular_troco(30, {20: 1, 10: 1, 5: 2})
    assert resultado == {20: 1, 10: 1}
