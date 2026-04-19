from db.connection import obtener_conexion
import psycopg2.extras


def crear_credito(cliente_id, sucursal_id, monto, tasa_interes,
                   tipo_interes, modalidad_pago,
                   plazo_numero, fecha_inicio,
                   total_con_interes, saldo_actual,
                   credito_origen_id=None):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
            INSERT INTO creditos (
                cliente_id,
                sucursal_id,
                monto,
                tasa_interes,
                tipo_interes,
                modalidad_pago,
                plazo_numero,
                fecha_inicio,
                total_con_interes,
                saldo_actual,
                credito_origen_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        cursor.execute(query, (
            cliente_id,
            sucursal_id,
            monto,
            tasa_interes,
            tipo_interes,
            modalidad_pago,
            plazo_numero,
            fecha_inicio,
            total_con_interes,
            saldo_actual,
            credito_origen_id
        ))

        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        return nuevo_id

    finally:
        conn.close()


def obtener_credito_por_id(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT *
            FROM creditos
            WHERE id = %s;
        """

        cursor.execute(query, (credito_id,))
        return cursor.fetchone()

    finally:
        conn.close()


def listar_creditos_activos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT *
            FROM creditos
            WHERE estado = 'ACTIVO'
            ORDER BY fecha_creacion DESC;
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        conn.close()

def obtener_credito_activo_cliente(cliente_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT *
            FROM creditos
            WHERE cliente_id = %s
            AND estado = 'ACTIVO'
            LIMIT 1;
        """

        cursor.execute(query, (cliente_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def actualizar_credito_a_refinanciado(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE creditos
            SET estado = 'REFINANCIADO',
                fecha_fin = CURRENT_DATE
            WHERE id = %s;
        """

        cursor.execute(query, (credito_id,))
        conn.commit()
    finally:
        conn.close()

def actualizar_saldo_credito(credito_id, nuevo_saldo):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE creditos
            SET saldo_actual = %s
            WHERE id = %s;
        """

        cursor.execute(query, (nuevo_saldo, credito_id))
        conn.commit()
    finally:
        conn.close()

def finalizar_credito(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
            UPDATE creditos
            SET estado = 'FINALIZADO',
                fecha_fin = CURRENT_DATE
            WHERE id = %s;
        """

        cursor.execute(query, (credito_id,))
        conn.commit()
    finally:
        conn.close()