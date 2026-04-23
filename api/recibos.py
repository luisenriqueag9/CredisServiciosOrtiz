from fastapi import APIRouter
from reports.recibo_pdf import generar_recibo_pago
import os

router = APIRouter(prefix="/recibos", tags=["Recibos"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/{pago_id}")
def generar_recibo(pago_id: int):
    try:
        resultado = generar_recibo_pago(pago_id)

        return {
            "success": True,
            "data": resultado
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }