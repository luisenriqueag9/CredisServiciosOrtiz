import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reports.documentos import generar_plan_pagos_pdf

# 🔥 usa un plan_id real (el último que se guardó)
plan_id = 9

ruta = generar_plan_pagos_pdf(plan_id)

print("Plan PDF generado en:", ruta)