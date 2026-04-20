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