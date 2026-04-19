import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reports.documentos import generar_pagare_pdf

ruta = generar_pagare_pdf(1, 2)

print("Pagaré generado en:", ruta)