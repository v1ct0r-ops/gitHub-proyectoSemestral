def calcular_iva(total, tasa=0.19):
    """
    Calcula IVA y retorna (iva, total_con_iva)
    """
    iva = round(total * tasa, 2)
    total_con_iva = round(total + iva, 2)
    return iva, total_con_iva
