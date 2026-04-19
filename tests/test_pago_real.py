import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.pago_model import crear_pago, obtener_pago_por_id
from Backend.reports.old.generador_recibo import generar_recibo_pdf
from datetime import datetime

credito_id = 2
plan_pago_id = 2
sucursal_id = 1

fecha_pago = datetime.strptime("2026-03-20", "%Y-%m-%d")

pago_id = crear_pago(
    credito_id=credito_id,
    plan_pago_id=plan_pago_id,
    fecha_pago=fecha_pago,
    monto_total=500,
    interes_pagado=50,
    capital_pagado=450,
    metodo_pago="EFECTIVO",
    sucursal_id=sucursal_id
)

if not pago_id:
    print("Error al registrar pago")
    exit()

print("Pago registrado ID:", pago_id)

pago = obtener_pago_por_id(pago_id)

fecha = pago["fecha_pago"]
if isinstance(fecha, str):
    fecha = datetime.strptime(fecha, "%Y-%m-%d")

datos = {
    "numero_recibo": f"RC-{pago['id']}",
    "numero": pago["numero_cuota"],
    "cliente": pago["nombre"],
    "capital": pago["capital_pagado"],
    "interes": pago["interes_pagado"],
    "total": pago["total"],
    "saldo": pago["saldo_actual"],
    "estado": "PAGADO",
    "fecha": fecha.strftime('%d/%m/%Y'),
    "concepto": f"Pago cuota {pago['numero_cuota']}",
    "sucursal": pago["sucursal"]
}

generar_recibo_pdf(datos, "recibo_real.pdf")

print("RECIBO GENERADO")