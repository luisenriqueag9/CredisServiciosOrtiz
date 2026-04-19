from services.plan_service import generar_plan
from services.guardar_plan import guardar_plan_en_bd
from reports.documentos import generar_plan_pagos_pdf
from models.credito_model import crear_credito, obtener_credito_activo_cliente
from models.cliente_model import obtener_o_crear_cliente
from datetime import datetime

def crear_credito_completo(credito, cliente):

    fecha_inicio = credito["fecha_inicio"]

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    cliente_id = obtener_o_crear_cliente(
        cliente["nombre"],
        cliente["dni"],
        cliente["sucursal"]
    )

    credito_activo = obtener_credito_activo_cliente(cliente_id)

    if credito_activo:
        raise ValueError("El cliente ya tiene un crédito activo")

    total_con_interes = credito["monto"] + (credito["monto"] * (credito["tasa"] / 100))
    saldo_actual = credito["monto"]

    credito_id = crear_credito(
        cliente_id,
        1,
        credito["monto"],
        credito["tasa"],
        "MENSUAL",
        "CUOTA_FIJA",
        credito["cuotas"],
        fecha_inicio,
        total_con_interes,
        saldo_actual
    )

    plan = generar_plan(
        credito["monto"],
        credito["tasa"],
        credito["cuotas"],
        fecha_inicio
    )

    for cuota in plan:
        cuota["estado"] = "PENDIENTE"

    guardar_plan_en_bd(plan, credito_id)

    ruta_pdf = generar_plan_pagos_pdf(credito_id)

    return credito_id, ruta_pdf