from services.plan_service import generar_plan, calcular_cuota_francesa
from services.guardar_plan import guardar_plan_en_bd
from reports.plan_pdf import generar_plan_pagos_pdf
from models.credito_model import crear_credito, obtener_credito_activo_cliente
from models.cliente_model import obtener_o_crear_cliente
from datetime import datetime
from reports.pagare_pdf import generar_pagare_pdf
from reports.contrato_pdf import generar_contrato_pdf
from models.aval_model import crear_aval
from models.garantia_model import crear_garantia


def crear_credito_completo(credito, cliente):

    fecha_inicio = credito.get("fecha_inicio")
    if not fecha_inicio:
        raise ValueError("La fecha de inicio es obligatoria")

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

    tipo_periodo = credito.get("tipo_periodo", "MENSUAL")
    tipo_plan = credito.get("tipo_plan", "CUOTA_FIJA")
    garantia = "PAGARÉ FIRMADO"

    # 🔥 CLIENTE
    cliente_id = obtener_o_crear_cliente(
        cliente["nombre"],
        cliente["dni"],
        cliente["sucursal"],
        cliente.get("telefono"),
        cliente.get("direccion")
    )

    # 🔥 AVAL (CORRECTO)
    aval_data = credito.get("aval")
    aval_id = None

    if aval_data:
        aval_id = crear_aval(
            aval_data["nombre"],
            aval_data["identidad"],
            aval_data.get("telefono"),
            aval_data.get("direccion")
        )

    # 🔥 VALIDACIÓN REFINANCIAMIENTO
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

    saldo_actual = credito["monto"]

    cuota = calcular_cuota_francesa(
        credito["monto"],
        credito["tasa"],
        credito["cuotas"],
        tipo_periodo
    )

    total_con_interes = cuota * credito["cuotas"]

    # 🔥 CREAR CRÉDITO CON AVAL
    credito_id = crear_credito(
        cliente_id,
        1,
        credito["monto"],
        credito["tasa"],
        tipo_periodo,
        tipo_plan,
        credito["cuotas"],
        fecha_inicio,
        total_con_interes,
        saldo_actual,
        aval_id,
        None,
        garantia   # 👈 NUEVO
    )

    garantias = credito.get("garantias", [])

    for g in garantias:
        crear_garantia(
            credito_id,
            g.get("tipo"),
            g.get("descripcion")
        )

    # 🔥 PLAN DE PAGOS
    plan = generar_plan(
        credito["monto"],
        credito["tasa"],
        credito["cuotas"],
        fecha_inicio,
        tipo_periodo
    )

    for c in plan:
        c["estado"] = "PENDIENTE"

    guardar_plan_en_bd(plan, credito_id)

    # 🔥 PDFS
    ruta_pdf = generar_plan_pagos_pdf(credito_id)
    pagare_pdf = generar_pagare_pdf(cliente_id, credito_id)
    contrato_pdf = generar_contrato_pdf(cliente_id, credito_id)

    return {
        "credito_id": credito_id,
        "plan_pdf": ruta_pdf.replace("\\", "/"),
        "pagare_pdf": pagare_pdf.replace("\\", "/"),
        "contrato_pdf": contrato_pdf.replace("\\", "/")
    }