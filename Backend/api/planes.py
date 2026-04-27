from fastapi import APIRouter, HTTPException
from services.simulador import simular_plan
from reports.plan_pdf import generar_plan_simulado_pdf
from services.plan_service import calcular_resumen

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
        tipo_periodo = credito.get("tipo_periodo")

        if monto is None or tasa is None or cuotas is None:
            raise ValueError("Datos incompletos para simular el plan")

        if not tipo_periodo:
            raise ValueError("Debe indicar el tipo de periodo")

        plan = simular_plan(
            monto,
            tasa,
            cuotas,
            fecha_inicio,
            tipo_periodo
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

        if monto is None or tasa is None or cuotas is None:
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


@router.post("/simular-resumen")
def simular_resumen(data: dict):
    try:
        credito = data.get("credito")

        if not credito:
            raise ValueError("Debe enviar el objeto 'credito'")

        monto = credito.get("monto")
        tasa = credito.get("tasa")
        cuotas = credito.get("cuotas")
        tipo_plan = credito.get("tipo_plan")
        tipo_periodo = credito.get("tipo_periodo")

        if monto is None or tasa is None or cuotas is None:
            raise ValueError("Datos incompletos para simular resumen")

        if not tipo_plan:
            raise ValueError("Debe indicar el tipo de plan")

        if not tipo_periodo:
            raise ValueError("Debe indicar el tipo de periodo")

        resumen = calcular_resumen(
            monto,
            tasa,
            cuotas,
            tipo_plan
        )

        return {
            "success": True,
            "data": {
                "monto": monto,
                "tasa": tasa,
                "tipo_plan": tipo_plan,
                "tipo_periodo": tipo_periodo,
                "cuotas": resumen["cuotas"],
                "cuota": resumen.get("cuota"),
                "total_pagar": resumen.get("total_pagar"),
                "total_interes": resumen.get("total_interes")
            },
            "message": "Resumen generado correctamente"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))