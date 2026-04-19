from services import caja_service
from models.credito_model import (
    crear_credito,
    obtener_credito_activo_cliente,
    actualizar_credito_a_refinanciado,
    obtener_credito_por_id,
    actualizar_saldo_credito,
    finalizar_credito
)

from models.cliente_model import obtener_cliente_por_id
from models.pago_model import crear_pago
from datetime import date


def crear_credito_service(cliente_id, sucursal_id, monto,
                           tasa_interes, tipo_interes,
                           modalidad_pago, plazo_numero,
                           fecha_inicio):

    cliente = obtener_cliente_por_id(cliente_id)

    if not cliente:
        raise Exception("El cliente no existe.")

    if cliente["estado"] != "ACTIVO":
        raise Exception("No se puede otorgar crédito a un cliente INACTIVO.")

    if obtener_credito_activo_cliente(cliente_id):
        raise Exception("El cliente ya tiene un crédito ACTIVO.")

    total_con_interes = monto + (monto * tasa_interes / 100)
    saldo_actual = monto

    return crear_credito(
        cliente_id,
        sucursal_id,
        monto,
        tasa_interes,
        tipo_interes,
        modalidad_pago,
        plazo_numero,
        fecha_inicio,
        total_con_interes,
        saldo_actual
    )


def refinanciar_credito(cliente_id, sucursal_id,
                        nueva_tasa, nuevo_plazo,
                        tipo_interes, modalidad_pago,
                        fecha_inicio):

    credito_actual = obtener_credito_activo_cliente(cliente_id)

    if not credito_actual:
        raise Exception("El cliente no tiene crédito ACTIVO para refinanciar.")

    saldo_pendiente = credito_actual["saldo_actual"]

    actualizar_credito_a_refinanciado(credito_actual["id"])

    total_con_interes = saldo_pendiente + (saldo_pendiente * nueva_tasa / 100)

    return crear_credito(
        cliente_id,
        sucursal_id,
        saldo_pendiente,
        nueva_tasa,
        tipo_interes,
        modalidad_pago,
        nuevo_plazo,
        fecha_inicio,
        total_con_interes,
        saldo_pendiente,
        credito_origen_id=credito_actual["id"]
    )

def registrar_pago(credito_id, capital_pagado, interes_pagado,
                   metodo_pago, sucursal_id, fecha_pago, usuario_id):

    credito = obtener_credito_por_id(credito_id)

    if not credito:
        raise Exception("El crédito no existe.")

    if credito["estado"] != "ACTIVO":
        raise Exception("Solo se pueden pagar créditos ACTIVOS.")

    saldo_actual = credito["saldo_actual"]

    if capital_pagado > saldo_actual:
        raise Exception("El capital pagado no puede ser mayor al saldo actual.")

    monto_total = capital_pagado + interes_pagado
    nuevo_saldo = saldo_actual - capital_pagado

    pago_id = crear_pago(
        credito_id,
        fecha_pago,
        monto_total,
        interes_pagado,
        capital_pagado,
        metodo_pago,
        sucursal_id
    )

    actualizar_saldo_credito(credito_id, nuevo_saldo)

    if nuevo_saldo <= 0:
        finalizar_credito(credito_id)

    # 🔥 REGISTRO EN CAJA
    caja_service.registrar_ingreso_pago(
        pago_id,
        credito_id,
        monto_total,
        sucursal_id,
        usuario_id
    )


    return nuevo_saldo