from fastapi import APIRouter
from reports.generador_recibo import generar_recibo_pdf
import os

router = APIRouter(prefix="/recibos", tags=["Recibos"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/{pago_id}")
def generar_recibo(pago_id: int):
    resultado = generar_recibo_pdf(pago_id, f"recibo_{pago_id}.pdf")

    if not resultado or "error" in resultado:
        return {"success": False, "message": "Pago no encontrado"}

    if "ruta_pdf" in resultado:
        ruta_relativa = os.path.relpath(resultado["ruta_pdf"], BASE_DIR).replace("\\", "/")
        resultado["url"] = f"http://127.0.0.1:8000/files/{ruta_relativa}"

    return {
        "success": True,
        "data": resultado
    }