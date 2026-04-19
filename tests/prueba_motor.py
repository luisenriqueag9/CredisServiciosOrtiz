from Backend.finance.motor_financiero import MotorFinanciero
from datetime import datetime
from Backend.services.guardar_plan import guardar_plan_en_bd
from Backend.reports.generador_pdf import generar_pdf_plan

motor = MotorFinanciero()

fecha_otorgamiento = datetime(2026, 2, 15)

plan = motor.sistema_frances(
    capital=10000,
    tasa=5,
    cuotas=12,
    fecha_inicio=fecha_otorgamiento,
    tipo_periodo="MENSUAL"
)

# 🔵 Guardar en BD
credito_id = 2
guardar_plan_en_bd(plan, credito_id)

# 🔵 PDF
datos_cliente = {
    "contrato": "CTR-001",
    "nombre": "Juan Perez",
    "dni": "0801-2000-12345",
    "capital": 10000,
    "tasa": 5,
    "sucursal": "Choloma"
}

generar_pdf_plan(plan, datos_cliente, "plan_cliente.pdf")

print("Plan guardado y PDF generado correctamente.")
