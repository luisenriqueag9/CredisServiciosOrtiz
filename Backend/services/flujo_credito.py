from services.plan_service import generar_plan
from services.guardar_plan import guardar_plan_en_bd
from reports.plan_pdf import generar_plan_pagos_pdf
from models.credito_model import crear_credito, obtener_credito_activo_cliente
from models.cliente_model import obtener_o_crear_cliente
from datetime import datetime
from reports.pagare_pdf import generar_pagare_pdf
from reports.contrato_pdf import generar_contrato_pdf
from models.aval_model import crear_aval
from models.garantia_model import crear_garantia
from db.connection import obtener_conexion


def crear_credito_completo(credito, cliente):

    # =============================
    # VALIDACIONES BÁSICAS
    # =============================
    fecha_inicio = credito.get("fecha_inicio")
    if not fecha_inicio:
        raise ValueError("La fecha de inicio es obligatoria")

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    if credito["monto"] <= 0:
        raise ValueError("El monto debe ser mayor a 0")

    if credito["monto"] < 1000:
        raise ValueError("El monto mínimo es 1000")

    if credito["tasa"] <= 0 or credito["tasa"] > 100:
        raise ValueError("La tasa debe estar entre 1 y 100")

    

    if not cliente["nombre"]:
        raise ValueError("El nombre del cliente es obligatorio")

    if not cliente["identidad"]:
        raise ValueError("La identidad es obligatoria")

    tipo_periodo = credito.get("tipo_periodo", "MENSUAL")
    tipo_plan = credito.get("tipo_plan", "CUOTA_FIJA")
    refinanciar = credito.get("refinanciar", False)

    if tipo_plan == "CUOTA_FIJA":
        if credito["cuotas"] <= 0 or credito["cuotas"] > 120:
            raise ValueError("Las cuotas deben estar entre 1 y 120")

    # =============================
    # CLIENTE
    # =============================
    cliente_id = obtener_o_crear_cliente(
        cliente["nombre"],
        cliente["identidad"],
        cliente.get("sucursal", 1),
        cliente.get("telefono"),
        cliente.get("direccion")
    )

    # =============================
    # VALIDAR REFINANCIACIÓN
    # =============================
    credito_activo = obtener_credito_activo_cliente(cliente_id)
    puede_refinanciar = False

    if credito_activo:
        monto_original = float(credito_activo["monto"])
        saldo_actual = float(credito_activo["saldo_actual"])

        pagado = monto_original - saldo_actual
        porcentaje = (pagado / monto_original) * 100

        if porcentaje >= 70:
            puede_refinanciar = True

        # ❌ si intenta refinanciar sin cumplir
        if refinanciar and not puede_refinanciar:
            raise ValueError(
                f"No puede refinanciar. Solo ha pagado {round(porcentaje,2)}% del crédito"
            )

    # =============================
    # SI REFINANCIA
    # =============================
    if refinanciar and credito_activo and puede_refinanciar:
        from models.credito_model import actualizar_credito_a_refinanciado
        actualizar_credito_a_refinanciado(credito_activo["id"])

    # =============================
    # CÁLCULO CUOTA (TIPO EXCEL)
    # =============================
    tasa_periodo = credito["tasa"] / 100

    cuota = (credito["monto"] * tasa_periodo) / (
        1 - (1 + tasa_periodo) ** (-credito["cuotas"])
    )

    total_con_interes = cuota * credito["cuotas"]
    saldo_actual = credito["monto"]


# =============================
# 🔹 CREAR CRÉDITO (CON AVAL)
# =============================
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
        None,   
        None,
        "PAGARÉ FIRMADO"
    )

    # =============================
    # 🔹 GUARDAR GARANTÍAS
    # =============================
    garantias = credito.get("garantias", [])

    for g in garantias:
        crear_garantia(
            credito_id,
            g.get("tipo"),
            g.get("descripcion")
        )

    # =============================
# 🔹 CREAR AVAL (DESPUÉS)
# =============================
    aval = credito.get("aval")
    aval_id = None

    if credito.get("requiere_aval", False):
        if not aval or not aval.get("nombre") or not aval.get("identidad"):
            raise ValueError("Debe ingresar los datos del aval")

    if aval:
        aval_id = crear_aval(
            aval.get("nombre"),
            aval.get("identidad"),
            aval.get("telefono"),
            aval.get("direccion")
            
        )

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE creditos
            SET aval_id = %s
            WHERE id = %s
        """, (aval_id, credito_id))

        conn.commit()
        conn.close()

  
    # =============================
    # PLAN DE PAGOS
    # =============================
    plan = generar_plan(
        credito["monto"],
        credito["tasa"],
        credito.get("cuotas"),
        fecha_inicio,
        tipo_periodo,
        tipo_plan,
        credito.get("pago_mensual")
    )

    for c in plan:
        c["estado"] = "PENDIENTE"

    guardar_plan_en_bd(plan, credito_id)

    ruta_pdf = generar_plan_pagos_pdf(credito_id)
    pagare_pdf = generar_pagare_pdf(cliente_id, credito_id)
    contrato_pdf = generar_contrato_pdf(cliente_id, credito_id)

    return {
    "credito_id": credito_id,
    "plan_pdf": ruta_pdf,
    "pagare_pdf": pagare_pdf,
    "contrato_pdf": contrato_pdf,
    "puede_refinanciar": puede_refinanciar
}