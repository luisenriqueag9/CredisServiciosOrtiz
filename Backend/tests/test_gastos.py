import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.gasto_model import obtener_gastos, obtener_gasto_detalle

print("LISTA GENERAL:")
print(obtener_gastos())

print("\nDETALLE DEL PRIMERO:")
print(obtener_gasto_detalle(1))