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

        # 🔥 GUARDAR URLs EN BD
        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE creditos
            SET plan_url = %s,
                pagare_url = %s,
                contrato_url = %s
            WHERE id = %s
        """, (
            build_url(resultado["plan_pdf"]),
            build_url(resultado["pagare_pdf"]),
            build_url(resultado["contrato_pdf"]),
            resultado["credito_id"]
        ))

        conn.commit()
        conn.close()

        return {
            "success": True,
            "data": {
                "credito_id": resultado["credito_id"],
                "plan_url": build_url(resultado["plan_pdf"]),
                "pagare_url": build_url(resultado["pagare_pdf"]),
                "contrato_url": build_url(resultado["contrato_pdf"])
            },
            "message": "Crédito procesado correctamente"
        }

    except HTTPException:
        raise

    except Exception as e:
        print("🔥 ERROR BACKEND:", str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno: {str(e)}"
        )


# ==============================
# 📊 RESUMEN DE CRÉDITO (OPTIMIZADO)
# ==============================
@router.get("/{credito_id}/resumen")
def resumen_credito(credito_id: int):

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 🔹 DATOS DEL CRÉDITO
        cursor.execute("""
            SELECT 
                cr.id,
                cr.monto,
                cr.tasa_interes,
                cr.modalidad_pago,
                cr.saldo_actual,
                cr.estado,
                cr.plan_url,
                cr.pagare_url,
                cr.contrato_url,
                c.id AS cliente_id,
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

        # 🔹 RESUMEN PAGOS
        cursor.execute("""
            SELECT 
                COALESCE(SUM(capital_pagado),0) AS capital,
                COALESCE(SUM(interes_pagado),0) AS interes,
                COALESCE(SUM(monto_pagado),0) AS total
            FROM pagos
            WHERE credito_id = %s
        """, (credito_id,))

        pagos = cursor.fetchone()

        # 🔹 CUOTAS
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE estado = 'PAGADA') AS pagadas,
                COUNT(*) FILTER (WHERE estado = 'PENDIENTE') AS pendientes
            FROM plan_pagos
            WHERE credito_id = %s
        """, (credito_id,))

        cuotas = cursor.fetchone()

        # 🔥 🔥 HISTORIAL DE PAGOS (BIEN UBICADO)
        cursor.execute("""
            SELECT 
                id,
                monto_pagado,
                capital_pagado,
                interes_pagado,
                fecha_pago
            FROM pagos
            WHERE credito_id = %s
            ORDER BY fecha_pago DESC
        """, (credito_id,))

        historial = cursor.fetchall()

        return {
            "success": True,
            "data": {
                "credito": {
                    "id": credito["id"],
                    "monto": credito["monto"],
                    "tasa_interes": credito["tasa_interes"],
                    "modalidad_pago": credito["modalidad_pago"],
                    "saldo_actual": credito["saldo_actual"],
                    "estado": credito["estado"]
                },
                "cliente": {
                    "id": credito["cliente_id"],
                    "nombre": credito["nombre"],
                    "identidad": credito["identidad"],
                    "telefono": credito["telefono"]
                },
                "pagos": pagos,
                "cuotas": cuotas,
                "pagos_list": historial,
                "documentos": {
                    "plan_url": credito["plan_url"],
                    "pagare_url": credito["pagare_url"],
                    "contrato_url": credito["contrato_url"]
                }
            }
        }

    finally:
        conn.close()


# ==============================
# 📋 LISTAR CRÉDITOS
# ==============================
@router.get("/")
@router.get("/")
def listar_creditos(desde: str = None, estado: str = None):
    from models.credito_model import listar_creditos_activos

    data = listar_creditos_activos(desde, estado)

    return {
        "success": True,
        "data": data
    }


# ==============================
# 👤 CRÉDITOS POR CLIENTE
# ==============================
@router.get("/cliente/{cliente_id}")
def obtener_creditos_por_cliente(cliente_id: int):

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
            SELECT 
                id,
                monto,
                tasa_interes,
                plazo_numero AS cuotas,
                saldo_actual,
                estado,
                fecha_inicio
            FROM creditos
            WHERE cliente_id = %s
            ORDER BY id DESC
        """, (cliente_id,))

        data = cursor.fetchall()

        return {
            "success": True,
            "data": data
        }

    finally:
        conn.close()