from fastapi import FastAPI
from services.documentos_service import generar_contrato, generar_pagare
from fastapi.staticfiles import StaticFiles
from reports.generador_recibo import generar_recibo_pdf
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/files", StaticFiles(directory=BASE_DIR), name="files")


@app.get("/")
def home():
    return {"mensaje": "API CREDIS SERVICIOS ORTIZ funcionando"}


@app.get("/recibo/{pago_id}")
def generar_recibo(pago_id: int):
    resultado = generar_recibo_pdf(pago_id, f"recibo_{pago_id}.pdf")

    if not resultado or "error" in resultado:
        return {"error": "Pago no encontrado"}

    if "ruta_pdf" in resultado:
        ruta_relativa = os.path.relpath(resultado["ruta_pdf"], BASE_DIR).replace("\\", "/")
        resultado["url"] = f"http://127.0.0.1:8000/files/{ruta_relativa}"

    return resultado