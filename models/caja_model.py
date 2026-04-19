from db.connection import obtener_conexion


def insertar_movimiento_caja(tipo_movimiento, concepto, monto, credito_id, pago_id, sucursal_id, usuario_id):
    
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO caja_movimientos
        (tipo_movimiento, concepto, monto, credito_id, pago_id, sucursal_id, usuario_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """

        cursor.execute(query, (
            tipo_movimiento,
            concepto,
            monto,
            credito_id,
            pago_id,
            sucursal_id,
            usuario_id
        ))

        movimiento_id = cursor.fetchone()[0]

        conn.commit()

        return movimiento_id

    finally:
        conn.close()