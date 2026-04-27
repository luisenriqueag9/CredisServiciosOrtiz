from fastapi import APIRouter, HTTPException
from services.flujo_credito import crear_credito_completo
from db.connection import obtener_conexion
import psycopg2.extras
import os

router = APIRouter(prefix="/creditos", tags=["Creditos"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = "http://127.0.0.1:8000/files"


# 🔧 Helper para construir URLs públicas
def build_url(ruta: str):
    ruta_rel = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")
    return f"{BASE_URL}/{ruta_rel}"


# ==============================
# 🚀 CREAR CRÉDITO COMPLETO
# ==============================
@router.post("/procesar")
def procesar_credito(data: dict):
    try:
        credito = data.get("credito")
        cliente = data.get("cliente")

        if not credito or not cliente:
            raise HTTPException(
                status_code=400,
                detail="Debe enviar 'credito' y 'cliente'"
            )

        resultado = crear_credito_completo(credito, cliente)

        return {
            "success": True,
            "data": {
                "credito_id": resultado["credito_id"],
                "plan_pdf": resultado["plan_pdf"],
                "pagare_pdf": resultado["pagare_pdf"],
                "contrato_pdf": resultado["contrato_pdf"],
                "plan_url": build_url(resultado["plan_pdf"]),
                "pagare_url": build_url(resultado["pagare_pdf"]),
                "contrato_url": build_url(resultado["contrato_pdf"])
            },
            "message": "Crédito procesado correctamente"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


# ==============================
# 📊 RESUMEN DE CRÉDITO
# ==============================
@router.get("/{credito_id}/resumen")
def resumen_credito(credito_id: int):

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 🔹 Datos del crédito + cliente
        cursor.execute("""
            SELECT 
                cr.id,
                cr.monto,
                cr.tasa_interes,
                cr.modalidad_pago,
                cr.saldo_actual,
                cr.estado,
                c.nombre,
                c.identidad,
                c.telefono
            FROM creditos cr
            JOIN clientes c ON cr.cliente_id = c.id
            WHERE cr.id = %s
        """, (credito_id,))

        credito = cursor.fetchone()

        if not credito:
            return {
                "success": False,
                "message": "Crédito no encontrado"
            }

        # 🔹 Totales de pagos
        cursor.execute("""
            SELECT 
                COALESCE(SUM(capital_pagado),0) AS capital,
                COALESCE(SUM(interes_pagado),0) AS interes,
                COALESCE(SUM(monto_pagado),0) AS total
            FROM pagos
            WHERE credito_id = %s
        """, (credito_id,))

        pagos = cursor.fetchone()

        # 🔹 Estado de cuotas
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE estado = 'PAGADA') AS pagadas,
                COUNT(*) FILTER (WHERE estado = 'PENDIENTE') AS pendientes
            FROM plan_pagos
            WHERE credito_id = %s
        """, (credito_id,))

        cuotas = cursor.fetchone()

        return {
            "success": True,
            "data": {
                "credito": credito,
                "pagos": pagos,
                "cuotas": cuotas
            }
        }

    finally:
        conn.close()

@router.get("/")
def listar_creditos():

    from models.credito_model import listar_creditos_activos

    data = listar_creditos_activos()

    return {
        "success": True,
        "data": data
    }