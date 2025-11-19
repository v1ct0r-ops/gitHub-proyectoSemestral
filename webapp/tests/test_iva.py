from webapp.utils.iva import calcular_iva


def test_calcular_iva():
    iva, total = calcular_iva(1000, tasa=0.19)
    assert iva == 190
    assert total == 1190
