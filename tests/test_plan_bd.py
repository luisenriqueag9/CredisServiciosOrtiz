import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.plan_service import generar_plan
from services.guardar_plan import guardar_plan_en_bd
from datetime import datetime

credito_id = 6

plan = generar_plan(
    monto=10000,
    tasa=5,
    cuotas=5,
    fecha_inicio=datetime.strptime("2026-04-01", "%Y-%m-%d")
)

guardar_plan_en_bd(plan, credito_id)

print("PLAN GUARDADO EN BD")