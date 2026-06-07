from fastapi import APIRouter, HTTPException
from reports.reportes_financieros.reporte_general_pdf import generar_reporte_general_pdf
from reports.reportes_financieros.reporte_gastos_pdf import generar_reporte_gastos_pdf
from reports.reportes_financieros.reporte_cobros_pdf import generar_reporte_cobros_pdf
import os

router = APIRouter(prefix="/reportes", tags=["Reportes"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/general")
def reporte_general(mes: int, anio: int):
    try:
        ruta = generar_reporte_general_pdf(mes, anio)

        ruta_rel = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")

        return {
            "success": True,
            "url": f"http://127.0.0.1:8000/files/{ruta_rel}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/gastos")
def reporte_gastos(mes: int, anio: int):
    try:
        ruta = generar_reporte_gastos_pdf(mes, anio)

        ruta_rel = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")

        return {
            "success": True,
            "url": f"http://127.0.0.1:8000/files/{ruta_rel}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/cobros")
def reporte_cobros(mes: int, anio: int, sucursal_id: int = None):
    try:
        ruta = generar_reporte_cobros_pdf(mes, anio, sucursal_id)

        ruta_rel = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")

        return {
            "success": True,
            "url": f"http://127.0.0.1:8000/files/{ruta_rel}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/resumen")
def resumen_financiero():
    from db.connection import obtener_conexion
    import psycopg2.extras

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # INGRESOS (pagos)
        cursor.execute("""
            SELECT 
                COALESCE(SUM(monto_pagado), 0) as total_ingresos,
                COALESCE(SUM(capital_pagado), 0) as total_capital,
                COALESCE(SUM(interes_pagado), 0) as total_intereses
            FROM pagos
        """)
        ingresos = cursor.fetchone()

        # GASTOS
        cursor.execute("""
            SELECT COALESCE(SUM(monto), 0) as total_gastos
            FROM gastos
        """)
        gastos = cursor.fetchone()

        total_ingresos = ingresos["total_ingresos"]
        total_capital = ingresos["total_capital"]
        total_intereses = ingresos["total_intereses"]
        total_gastos = gastos["total_gastos"]

        utilidad = total_ingresos - total_gastos

        return {
            "success": True,
            "data": {
                "total_ingresos": total_ingresos,
                "total_capital": total_capital,
                "total_intereses": total_intereses,
                "total_gastos": total_gastos,
                "utilidad": utilidad
            }
        }

    finally:
        conn.close()

@router.get("/mensual")
def ingresos_mensuales():
    from db.connection import obtener_conexion
    import psycopg2.extras

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
            SELECT 
                TO_CHAR(fecha_pago, 'YYYY-MM') as mes,
                SUM(monto_pagado) as total
            FROM pagos
            GROUP BY mes
            ORDER BY mes
        """)

        data = cursor.fetchall()

        return {
            "success": True,
            "data": data
        }

    finally:
        conn.close()

@router.get("/resumen-mensual")
def resumen_mensual(mes: int, anio: int):
    from reports.reportes_financieros.reporte_general_pdf import (
        obtener_total_cobros,
        obtener_total_gastos
    )

    total_ingresos = obtener_total_cobros(mes, anio)
    total_gastos = obtener_total_gastos(mes, anio)
    utilidad = total_ingresos - total_gastos

    return {
        "success": True,
        "data": {
            "ingresos": total_ingresos,
            "gastos": total_gastos,
            "utilidad": utilidad
        }
    }

@router.get("/mensual-completo")
def mensual_completo():
    from db.connection import obtener_conexion
    import psycopg2.extras

    conn = obtener_conexion()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cursor.execute("""
            SELECT 
                TO_CHAR(p.fecha_pago, 'YYYY-MM') as mes,
                SUM(p.monto_pagado) as ingresos
            FROM pagos p
            GROUP BY mes
        """)
        ingresos = cursor.fetchall()

        cursor.execute("""
            SELECT 
                TO_CHAR(fecha, 'YYYY-MM') as mes,
                SUM(monto) as gastos
            FROM gastos
            GROUP BY mes
        """)
        gastos = cursor.fetchall()

        data = {}

        for i in ingresos:
            data[i["mes"]] = {
                "mes": i["mes"],
                "ingresos": i["ingresos"],
                "gastos": 0
            }

        for g in gastos:
            if g["mes"] in data:
                data[g["mes"]]["gastos"] = g["gastos"]
            else:
                data[g["mes"]] = {
                    "mes": g["mes"],
                    "ingresos": 0,
                    "gastos": g["gastos"]
                }

        return {
            "success": True,
            "data": list(data.values())
        }

    finally:
        conn.close()