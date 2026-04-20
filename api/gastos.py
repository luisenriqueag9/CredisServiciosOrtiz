from fastapi import APIRouter, HTTPException
from services.gastos_service import registrar_gasto, listar_gastos, detalle_gasto

router = APIRouter(prefix="/gastos", tags=["Gastos"])


@router.post("/")
def crear(data: dict):
    try:
        return {
            "success": True,
            "data": registrar_gasto(data)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/")
def listar(sucursal_id: int = None):
    return {
        "success": True,
        "data": listar_gastos(sucursal_id)
    }


@router.get("/{gasto_id}")
def detalle(gasto_id: int):
    try:
        return {
            "success": True,
            "data": detalle_gasto(gasto_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))