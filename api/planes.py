from fastapi import APIRouter
from services.simulador import simular_plan

router = APIRouter(prefix="/planes", tags=["Planes"])

@router.post("/simular")
def simular(data: dict):
    plan = simular_plan(
        data["monto"],
        data["tasa"],
        data["cuotas"],
        data["fecha_inicio"]
    )

    return {
        "success": True,
        "data": plan,
        "message": "Simulación generada correctamente"
    }