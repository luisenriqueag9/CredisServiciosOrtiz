from db.connection import obtener_conexion
import psycopg2.extras


def crear_cliente(nombre, identidad, telefono, direccion, sucursal_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO clientes (nombre, identidad, telefono, direccion, sucursal_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        cursor.execute(query, (nombre, identidad, telefono, direccion, sucursal_id))
        nuevo_id = cursor.fetchone()[0]
        conn.commit()
        return nuevo_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def obtener_cliente_por_id(cliente_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("SELECT * FROM clientes WHERE id = %s;", (cliente_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def listar_clientes():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""
            SELECT * 
            FROM clientes
            WHERE estado = 'ACTIVO'
            ORDER BY id DESC;
        """)
        return cursor.fetchall()
    finally:
        conn.close()


def eliminar_cliente(cliente_id):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            UPDATE clientes
            SET estado = 'INACTIVO',
                fecha_actualizacion = NOW()
            WHERE id = %s
            RETURNING *;
        """

        cursor.execute(query, (cliente_id,))
        resultado = cursor.fetchone()

        conn.commit()
        return resultado

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

def obtener_cliente_por_identidad(identidad):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(
            "SELECT * FROM clientes WHERE identidad = %s;",
            (identidad,)
        )
        return cursor.fetchone()
    finally:
        conn.close()
def actualizar_cliente(cliente_id, datos):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
        UPDATE clientes
        SET nombre = %s,
            telefono = %s,
            direccion = %s,
            sucursal_id = %s,
            fecha_actualizacion = NOW()
        WHERE id = %s
        AND estado = 'ACTIVO'
        RETURNING *;
        """

        cursor.execute(query, (
            datos["nombre"],
            datos.get("telefono"),
            datos.get("direccion"),
            datos["sucursal_id"],
            cliente_id
        ))

        resultado = cursor.fetchone()
        conn.commit()
        return resultado

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()

def obtener_o_crear_cliente(nombre, dni, sucursal):

    cliente = obtener_cliente_por_identidad(dni)

    if cliente:
        return cliente["id"]

    cliente_id = crear_cliente(
        nombre,
        dni,
        "",
        "",
        1
    )

    return cliente_id