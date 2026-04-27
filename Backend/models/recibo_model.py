from db.connection import obtener_conexion
import psycopg2
from psycopg2 import errors


def generar_numero_recibo():
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT numero_recibo
            FROM recibos
            ORDER BY id DESC
            LIMIT 1
        """)

        resultado = cursor.fetchone()

        if resultado:
            ultimo = resultado[0]
            numero = int(ultimo.split("-")[1]) + 1
        else:
            numero = 1

        return f"RC-{numero:04}"

    finally:
        cursor.close()
        conn.close()


def existe_recibo_para_pago(pago_id):
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id FROM recibos
            WHERE pago_id = %s
            LIMIT 1
        """, (pago_id,))

        return cursor.fetchone() is not None

    finally:
        cursor.close()
        conn.close()


def guardar_recibo(numero_recibo, pago_id, ruta_pdf):
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO recibos (numero_recibo, pago_id, ruta_pdf)
            VALUES (%s, %s, %s)
            RETURNING id
        """, (numero_recibo, pago_id, ruta_pdf))

        recibo_id = cursor.fetchone()[0]
        conn.commit()

        print(f"💾 Recibo guardado en BD: {numero_recibo}")
        return recibo_id

    except psycopg2.Error as e:
        conn.rollback()

        if isinstance(e, errors.UniqueViolation):
            print("⚠️ Este pago ya tiene un recibo en la BD")
        else:
            print("❌ Error al guardar recibo:", e)

        return None

    finally:
        cursor.close()
        conn.close()

def obtener_recibo_por_pago(pago_id):
    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT numero_recibo, ruta_pdf
            FROM recibos
            WHERE pago_id = %s
            LIMIT 1
        """, (pago_id,))

        resultado = cursor.fetchone()

        if resultado:
            return {
                "numero_recibo": resultado[0],
                "ruta_pdf": resultado[1]
            }

        return None

    finally:
        cursor.close()
        conn.close()