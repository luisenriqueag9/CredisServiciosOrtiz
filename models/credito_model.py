from db.connection import obtener_conexion
import psycopg2.extras


def crear_credito(cliente_id, sucursal_id, monto, tasa_interes,
                   tipo_interes, modalidad_pago,
                   plazo_numero, fecha_inicio,
                   total_con_interes, saldo_actual,
                   aval_id=None, credito_origen_id=None,
                   garantia=None):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
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
                aval_id,
                credito_origen_id,
                garantia
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
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
            aval_id,
            credito_origen_id,
            garantia
        ))
                

        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        return nuevo_id

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()


def obtener_credito_por_id(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT *
            FROM creditos
            WHERE id = %s;
        """, (credito_id,))

        return cursor.fetchone()

    finally:
        conn.close()


def listar_creditos_activos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT *
            FROM creditos
            WHERE estado = 'ACTIVO'
            ORDER BY fecha_creacion DESC;
        """)

        return cursor.fetchall()

    finally:
        conn.close()


def obtener_credito_activo_cliente(cliente_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("""
            SELECT *
            FROM creditos
            WHERE cliente_id = %s
            AND estado = 'ACTIVO'
            LIMIT 1;
        """, (cliente_id,))

        return cursor.fetchone()

    finally:
        conn.close()


def actualizar_credito_a_refinanciado(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE creditos
            SET estado = 'REFINANCIADO',
                fecha_fin = CURRENT_DATE
            WHERE id = %s;
        """, (credito_id,))

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()


def actualizar_saldo_credito(credito_id, nuevo_saldo):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE creditos
            SET saldo_actual = %s
            WHERE id = %s;
        """, (nuevo_saldo, credito_id))

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()


def finalizar_credito(credito_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE creditos
            SET estado = 'FINALIZADO',
                fecha_fin = CURRENT_DATE
            WHERE id = %s;
        """, (credito_id,))

        conn.commit()

    except:
        conn.rollback()
        raise

    finally:
        conn.close()