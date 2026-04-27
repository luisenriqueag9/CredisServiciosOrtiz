from Backend.reports.old.generador_pdf import generar_pdf_plan

plan = [
    {
        "numero_cuota": 1,
        "fecha_pago": "01-04-2026",
        "cuota": 2500,
        "interes": 500,
        "capital": 2000,
        "saldo": 8000,
        "estado": "PENDIENTE"
    },
    {
        "numero_cuota": 2,
        "fecha_pago": "01-05-2026",
        "cuota": 2500,
        "interes": 400,
        "capital": 2100,
        "saldo": 5900,
        "estado": "PAGADA"
    }
]

datos_cliente = {
    "contrato": "CRED-001",
    "nombre": "Luis Enrique Ortiz",
    "dni": "0801199701234",
    "sucursal": "Choloma",
    "capital": 10000,
    "tasa": 5
}

generar_pdf_plan(plan, datos_cliente, "plan_prueba.pdf")
print("PDF generado correctamente")