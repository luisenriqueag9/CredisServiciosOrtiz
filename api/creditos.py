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