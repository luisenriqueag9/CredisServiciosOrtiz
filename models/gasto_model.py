from db.connection import obtener_conexion


def crear_gasto(concepto, monto, fecha, descripcion=None, foto_factura=None, usuario_id=None, sucursal_id=None):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO gastos (concepto, monto, fecha, descripcion, foto_factura, usuario_id, sucursal_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            concepto,
            monto,
            fecha,
            descripcion,
            foto_factura,
            usuario_id,
            sucursal_id
        ))

        conn.commit()

    finally:
        conn.close()


def obtener_gastos(sucursal_id=None):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = "SELECT concepto, monto, fecha FROM gastos WHERE 1=1"

        if sucursal_id:
            query += " AND sucursal_id = %s"
            cursor.execute(query, (sucursal_id,))
        else:
            cursor.execute(query)

        return cursor.fetchall()

    finally:
        conn.close()


def obtener_gasto_detalle(gasto_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT concepto, monto, fecha, descripcion, foto_factura
        FROM gastos
        WHERE id = %s
        """

        cursor.execute(query, (gasto_id,))
        return cursor.fetchone()

    finally:
        conn.close()