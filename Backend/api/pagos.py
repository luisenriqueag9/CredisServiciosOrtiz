from fastapi import APIRouter, HTTPException
from services.pagos_service import registrar_pago_inteligente

router = APIRouter(prefix="/pagos", tags=["Pagos"])


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