from fastapi import APIRouter
from reports.pagare_pdf import generar_pagare_pdf
import os

router = APIRouter(prefix="/pagare", tags=["Pagare"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@router.get("/{cliente_id}")
def generar_pagare(cliente_id: int, credito_id: int = None):

    ruta = generar_pagare_pdf(cliente_id, credito_id)

    ruta_relativa = os.path.relpath(ruta, BASE_DIR).replace("\\", "/")

    url = f"http://127.0.0.1:8000/files/{ruta_relativa}"

    return {
        "success": True,
        "data": {
            "ruta": ruta,
            "url": url
        }
    }