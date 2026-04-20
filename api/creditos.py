from fastapi import APIRouter, HTTPException
from services.flujo_credito import crear_credito_completo
import os

router = APIRouter(prefix="/creditos", tags=["Creditos"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.post("/procesar")
def procesar(data: dict):
    try:
        credito = data["credito"]
        cliente = data["cliente"]

        resultado = crear_credito_completo(credito, cliente)

        def build_url(ruta):
            ruta_rel = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")
            return f"http://127.0.0.1:8000/files/{ruta_rel}"

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

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Campo faltante: {str(e)}"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@router.get("/{credito_id}/resumen")
def resumen_credito(credito_id: int):

    from db.connection import obtener_conexion
    import psycopg2.extras

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

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
        conn.close()
        return {"success": False, "message": "Crédito no encontrado"}

    cursor.execute("""
        SELECT 
            COALESCE(SUM(capital_pagado),0) AS capital,
            COALESCE(SUM(interes_pagado),0) AS interes,
            COALESCE(SUM(monto_pagado),0) AS total
        FROM pagos
        WHERE credito_id = %s
    """, (credito_id,))

    pagos = cursor.fetchone()

    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE estado = 'PAGADA') AS pagadas,
            COUNT(*) FILTER (WHERE estado = 'PENDIENTE') AS pendientes
        FROM plan_pagos
        WHERE credito_id = %s
    """, (credito_id,))

    cuotas = cursor.fetchone()

    conn.close()

    return {
        "success": True,
        "data": {
            "credito": credito,
            "pagos": pagos,
            "cuotas": cuotas
        }
    }