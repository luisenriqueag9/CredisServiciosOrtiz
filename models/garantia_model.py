from db.connection import obtener_conexion


def crear_garantia(credito_id, tipo, descripcion):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO garantias (credito_id, tipo, descripcion)
            VALUES (%s, %s, %s)
        """, (credito_id, tipo, descripcion))

        conn.commit()

    finally:
        conn.close()


def obtener_garantias_credito(credito_id):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT tipo, descripcion
            FROM garantias
            WHERE credito_id = %s
        """, (credito_id,))

        return cursor.fetchall()

    finally:
        conn.close()