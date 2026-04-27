from models.caja_model import insertar_movimiento_caja


def registrar_ingreso_pago(pago_id, credito_id, monto, sucursal_id, usuario_id):

    if monto <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    return insertar_movimiento_caja(
        tipo_movimiento='INGRESO',
        concepto='Pago de crédito',
        monto=monto,
        credito_id=credito_id,
        pago_id=pago_id,
        sucursal_id=sucursal_id,
        usuario_id=usuario_id
    )