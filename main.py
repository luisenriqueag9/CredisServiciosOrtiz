from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from api import recibos
from api import planes
from api import creditos
from api import pagare
from api import contrato

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/files", StaticFiles(directory=BASE_DIR), name="files")

app.include_router(recibos.router)
app.include_router(planes.router)
app.include_router(creditos.router)
app.include_router(pagare.router)
app.include_router(contrato.router)



@app.get("/")
def home():
    return {"mensaje": "API CREDIS SERVICIOS ORTIZ funcionando"}