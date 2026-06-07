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

@router.put("/{gasto_id}")
def actualizar_gasto(gasto_id: int, data: dict):
    from db.connection import obtener_conexion

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE gastos
        SET concepto = %s,
            monto = %s,
            fecha = %s,
            descripcion = %s
        WHERE id = %s
    """, (
        data["concepto"],
        data["monto"],
        data["fecha"],
        data.get("descripcion"),
        gasto_id
    ))

    conn.commit()
    conn.close()

    return {"success": True}

@router.delete("/{gasto_id}")
def eliminar_gasto(gasto_id: int):
    from db.connection import obtener_conexion

    conn = obtener_conexion()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM gastos WHERE id = %s", (gasto_id,))
    conn.commit()
    conn.close()

    return {"success": True}