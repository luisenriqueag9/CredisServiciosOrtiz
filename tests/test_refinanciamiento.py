from services.credito_service import refinanciar_credito
from models.credito_model import obtener_credito_por_id

from datetime import date

try:
    nuevo_id = refinanciar_credito(
        cliente_id=1,
        sucursal_id=1,
        nueva_tasa=8,
        nuevo_plazo=24,
        tipo_interes="SIMPLE",
        modalidad_pago="MENSUAL",
        fecha_inicio=date.today()
    )

    print(f"✅ Crédito refinanciado. Nuevo ID: {nuevo_id}")

    nuevo_credito = obtener_credito_por_id(nuevo_id)

    print("📄 Nuevo crédito:")
    print(nuevo_credito)

except Exception as e:
    print("❌ Error:", e)