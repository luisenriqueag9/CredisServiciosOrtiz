from services.plan_service import generar_plan
from services.guardar_plan import guardar_plan_en_bd
from reports.documentos import generar_plan_pagos_pdf
from datetime import datetime
import os

def crear_credito_completo(credito, cliente):

    fecha_inicio = credito["fecha_inicio"]

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    plan = generar_plan(
        credito["monto"],
        credito["tasa"],
        credito["cuotas"],
        fecha_inicio
    )

    for cuota in plan:
        cuota["estado"] = "PENDIENTE"

    guardar_plan_en_bd(plan, credito["id"])

    nombre_cliente = cliente["nombre"].replace(" ", "_")

    ruta_carpeta = f"docs/planes/{nombre_cliente}"

    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)

    ruta_pdf = f"{ruta_carpeta}/plan_{credito['id']}.pdf"

    datos_cliente = {
        "nombre": cliente["nombre"],
        "dni": cliente["dni"],
        "sucursal": cliente["sucursal"],
        "capital": credito["monto"],
        "tasa": credito["tasa"],
        "contrato": f"C-{credito['id']}",
        "fecha_inicio": fecha_inicio
    }

    ruta_pdf = generar_plan_pagos_pdf(credito["id"])

    return ruta_pdf