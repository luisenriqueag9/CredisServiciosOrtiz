from fastapi import APIRouter, HTTPException
from services.simulador import simular_plan
from reports.plan_pdf import generar_plan_simulado_pdf

router = APIRouter(prefix="/planes", tags=["Planes"])


@router.post("/simular")
def simular(data: dict):
    try:
        credito = data.get("credito")

        if not credito:
            raise ValueError("Debe enviar el objeto 'credito'")

        monto = credito.get("monto")
        tasa = credito.get("tasa")
        cuotas = credito.get("cuotas")
        fecha_inicio = credito.get("fecha_inicio")

        if not monto or not tasa or not cuotas:
            raise ValueError("Datos incompletos para simular el plan")

        plan = simular_plan(
            monto,
            tasa,
            cuotas,
            fecha_inicio
        )

        return {
            "success": True,
            "data": plan,
            "message": "Simulación generada correctamente"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simular/pdf")
def simular_pdf(data: dict):
    try:
        credito = data.get("credito")

        if not credito:
            raise ValueError("Debe enviar el objeto 'credito'")

        monto = credito.get("monto")
        tasa = credito.get("tasa")
        cuotas = credito.get("cuotas")
        fecha_inicio = credito.get("fecha_inicio")

        if not monto or not tasa or not cuotas:
            raise ValueError("Datos incompletos para generar el PDF")

        ruta = generar_plan_simulado_pdf(
            monto,
            tasa,
            cuotas,
            fecha_inicio
        )

        url = f"http://127.0.0.1:8000/files/{ruta}"

        return {
            "success": True,
            "data": {
                "ruta": ruta,
                "url": url
            },
            "message": "PDF de simulación generado"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))