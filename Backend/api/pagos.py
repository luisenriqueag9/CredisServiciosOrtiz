from fastapi import APIRouter, HTTPException
from services.pagos_service import (
    registrar_pago_inteligente,
    simular_pago_inteligente
)

router = APIRouter(prefix="/pagos", tags=["Pagos"])


# =========================
#  PAGO REAL
# =========================
@router.post("/rapido")
def pago_rapido(data: dict):
    try:
        credito_id = data.get("credito_id")
        monto = data.get("monto")

        if not credito_id or not monto:
            raise ValueError("Debe enviar credito_id y monto")

        resultado = registrar_pago_inteligente(
            credito_id,
            monto
        )

        return {
            "success": True,
            "data": resultado,
            "message": "Pago registrado correctamente"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# =========================
# 🧠 SIMULACIÓN (CORRECTA)
# =========================
@router.post("/simular")
def simular_pago(data: dict):
    try:
        credito_id = data.get("credito_id")
        monto = data.get("monto")

        if not credito_id or not monto:
            raise ValueError("Debe enviar credito_id y monto")

        resultado = simular_pago_inteligente(
            credito_id,
            monto
        )

        return {
            "success": True,
            "data": resultado,
            "message": "Simulación correcta"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/")
@router.get("")
def listar_pagos(desde: str = None, cliente_id: int = None):
    from db.connection import obtener_conexion
    import psycopg2.extras

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        query = """
            SELECT 
                p.id,
                p.fecha_pago,
                p.monto_pagado,
                p.capital_pagado,
                p.interes_pagado,
                c.nombre AS cliente_nombre,
                c.id AS cliente_id
            FROM pagos p
            JOIN creditos cr ON cr.id = p.credito_id
            JOIN clientes c ON c.id = cr.cliente_id
        """

        params = []
        condiciones = []

        if desde:
            condiciones.append("p.fecha_pago >= %s")
            params.append(desde)

        if cliente_id is not None:
            condiciones.append("c.id = %s")
            params.append(cliente_id)

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)

        query += " ORDER BY p.fecha_pago DESC"

        cursor.execute(query, params)
        pagos = cursor.fetchall()

        return {
            "success": True,
            "data": pagos
        }

    finally:
        conn.close()