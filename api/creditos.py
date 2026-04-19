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

        credito_id, ruta = crear_credito_completo(credito, cliente)

        ruta_relativa = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")
        url = f"http://127.0.0.1:8000/files/{ruta_relativa}"

        return {
            "success": True,
            "data": {
                "credito_id": credito_id,
                "pdf": ruta,
                "url": url
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