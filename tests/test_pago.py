from services.credito_service import registrar_pago
from models.credito_model import obtener_credito_por_id
from datetime import date

try:
    nuevo_saldo = registrar_pago(
        credito_id=4,          # usa el crédito ACTIVO actual
        capital_pagado=0,
        interes_pagado=0,
        metodo_pago="EFECTIVO",
        sucursal_id=1,
        fecha_pago=date.today()
    )

    print("✅ Pago registrado correctamente")
    print("Nuevo saldo:", nuevo_saldo)

    credito = obtener_credito_por_id(4)
    print("Estado actual del crédito:")
    print(credito)

except Exception as e:
    print("❌ Error:", e)