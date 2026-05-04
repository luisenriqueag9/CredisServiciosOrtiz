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