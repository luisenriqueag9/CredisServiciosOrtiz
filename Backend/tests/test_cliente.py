import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.cliente_service import (
    listar_todos_los_clientes,
    actualizar_cliente_service
)

print("\nLista actual de clientes:")
clientes = listar_todos_los_clientes()

for cliente in clientes:
    print(dict(cliente))

print("\nActualizando cliente ID 4...")

try:
    cliente_actualizado = actualizar_cliente_service(
        4,
        {
            "nombre": "Carlos Mendoza Actualizado",
            "telefono": "99999999",
            "direccion": "Choloma",
            "sucursal_id": 1
        }
    )

    print("Cliente actualizado:")
    print(dict(cliente_actualizado))

except ValueError as e:
    print("⚠ Regla de negocio:", e)

except Exception as e:
    print("❌ Error inesperado:", e)

print("\nLista después de actualización:")
clientes = listar_todos_los_clientes()

for cliente in clientes:
    print(dict(cliente))