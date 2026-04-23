from services.plan_service import generar_plan
from datetime import datetime

def simular_plan(monto, tasa, cuotas, fecha_inicio):

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    plan = generar_plan(monto, tasa, cuotas, fecha_inicio, tipo_periodo)

    for cuota in plan:
        fecha = cuota["fecha_pago"]
        if isinstance(fecha, datetime):
            cuota["fecha_pago"] = fecha.strftime("%d-%m-%Y")

    return plan