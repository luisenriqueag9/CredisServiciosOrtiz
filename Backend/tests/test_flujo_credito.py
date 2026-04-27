import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.flujo_credito import crear_credito_completo

credito = {
    "id": 2,
    "monto": 10000,
    "tasa": 10,
    "cuotas": 12,
    "fecha_inicio": "2026-04-01"
}

cliente = {
    "nombre": "Luis Enrique",
    "dni": "0801199712345",
    "sucursal": "Choloma"
}

ruta = crear_credito_completo(credito, cliente)

print("PDF generado en:", ruta)