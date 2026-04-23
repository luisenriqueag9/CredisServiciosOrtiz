from db.connection import obtener_conexion

def crear_aval(nombre, identidad, telefono=None, direccion=None):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO avales (nombre, identidad, telefono, direccion)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """, (nombre, identidad, telefono, direccion))

        aval_id = cursor.fetchone()[0]
        conn.commit()
        return aval_id

    finally:
        conn.close()


def obtener_aval_por_id(aval_id):

    conn = obtener_conexion()
    try:
        import psycopg2.extras
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT * FROM avales WHERE id = %s", (aval_id,))
        return cursor.fetchone()

    finally:
        conn.close()