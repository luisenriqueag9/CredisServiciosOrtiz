from services.plan_service import generar_plan
from services.guardar_plan import guardar_plan_en_bd
from reports.plan_pdf import generar_plan_pagos_pdf
from models.credito_model import crear_credito, obtener_credito_activo_cliente
from models.cliente_model import obtener_o_crear_cliente
from datetime import datetime

def crear_credito_completo(credito, cliente):

    fecha_inicio = credito["fecha_inicio"]

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    if credito["monto"] <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    if credito["monto"] < 1000:
        raise ValueError("El monto mínimo es 1000")

    if credito["monto"] > 1000000:
        raise ValueError("El monto máximo permitido es 1,000,000")

    if credito["tasa"] <= 0 or credito["tasa"] > 100:
        raise ValueError("La tasa debe estar entre 1 y 100")

    if credito["cuotas"] <= 0 or credito["cuotas"] > 120:
        raise ValueError("Las cuotas deben estar entre 1 y 120")

    if not cliente["nombre"]:
        raise ValueError("El nombre del cliente es obligatorio")

    if not cliente["dni"]:
        raise ValueError("El DNI es obligatorio")

    cliente_id = obtener_o_crear_cliente(
        cliente["nombre"],
        cliente["dni"],
        cliente["sucursal"]
    )

    credito_activo = obtener_credito_activo_cliente(cliente_id)

    if credito_activo:

        monto_original = float(credito_activo["monto"])
        saldo_actual = float(credito_activo["saldo_actual"])

        pagado = monto_original - saldo_actual
        porcentaje_pagado = (pagado / monto_original) * 100

        if porcentaje_pagado < 70:
            raise ValueError("El cliente solo puede refinanciar si ha pagado al menos el 70% del crédito")

        from models.credito_model import actualizar_credito_a_refinanciado

        actualizar_credito_a_refinanciado(credito_activo["id"])

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