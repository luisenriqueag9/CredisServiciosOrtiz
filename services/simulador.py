from services.plan_service import generar_plan
from datetime import datetime

def simular_plan(monto, tasa, cuotas, fecha_inicio):

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    plan = generar_plan(monto, tasa, cuotas, fecha_inicio)

    return plan