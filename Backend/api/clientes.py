from fastapi import APIRouter
from db.connection import obtener_conexion
import psycopg2.extras

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/")
def listar_clientes():
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM clientes ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data


@router.post("/")
def crear_cliente(cliente: dict):
    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes (nombre, identidad, telefono, direccion, sucursal_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (
        cliente["nombre"],
        cliente["identidad"],
        cliente.get("telefono"),
        cliente.get("direccion"),
        cliente.get("sucursal_id", 1)
    ))

    nuevo_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    return {"id": nuevo_id}
@router.get("/{cliente_id}")
def obtener_cliente(cliente_id: int):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
    cliente = cursor.fetchone()

    conn.close()

    if not cliente:
        return {"error": "Cliente no encontrado"}

    return cliente

@router.put("/{cliente_id}")
def actualizar(cliente_id: int, datos: dict):
    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("""
        UPDATE clientes
        SET nombre = %s,
            telefono = %s,
            direccion = %s,
            sucursal_id = %s
        WHERE id = %s
        RETURNING *
    """, (
        datos["nombre"],
        datos.get("telefono"),
        datos.get("direccion"),
        datos.get("sucursal_id", 1),
        cliente_id
    ))

    cliente = cursor.fetchone()
    conn.commit()
    conn.close()

    return cliente