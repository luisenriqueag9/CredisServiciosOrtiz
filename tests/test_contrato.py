import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reports.documentos import generar_contrato_credito

ruta = generar_contrato_credito(1, 2)

print("Contrato generado en:", ruta)