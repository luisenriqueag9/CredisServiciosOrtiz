from fastapi import APIRouter
from reports.contrato_pdf import generar_contrato_pdf
import os

router = APIRouter(prefix="/contrato", tags=["Contrato"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/{cliente_id}")
def generar_contrato(cliente_id: int, plan_id: int = None):

    ruta = generar_contrato_pdf(cliente_id, plan_id)

    ruta_relativa = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")

    url = f"http://127.0.0.1:8000/files/{ruta_relativa}"

    return {
        "success": True,
        "data": {
            "ruta": ruta,
            "url": url
        }
    }