import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.credito_service import crear_credito_service
from models.credito_model import obtener_credito_por_id

from datetime import date

try:
    nuevo_id = crear_credito_service(
        cliente_id=2,
        sucursal_id=1,
        monto=10000,
        tasa_interes=10,
        tipo_interes="SIMPLE",
        modalidad_pago="MENSUAL",
        plazo_numero=12,
        fecha_inicio=date.today()
    )

    print(f"✅ Crédito creado con ID: {nuevo_id}")

    credito = obtener_credito_por_id(nuevo_id)

    print("📄 Datos del crédito:")
    print(credito)

except Exception as e:
    print("❌ Error:", e)