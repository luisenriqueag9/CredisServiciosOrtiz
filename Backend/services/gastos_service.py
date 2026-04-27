from models.gasto_model import crear_gasto, obtener_gastos, obtener_gasto_detalle

def registrar_gasto(data):

    concepto = data.get("concepto")
    monto = data.get("monto")
    fecha = data.get("fecha")
    descripcion = data.get("descripcion")

    if not concepto or not monto or not fecha:
        raise ValueError("Concepto, monto y fecha son obligatorios")

    if not descripcion:
        raise ValueError("La descripción del gasto es obligatoria")

    crear_gasto(
        concepto,
        monto,
        fecha,
        descripcion,
        data.get("foto_factura"),
        data.get("usuario_id"),
        data.get("sucursal_id")
    )

    return {"message": "Gasto registrado correctamente"}


def listar_gastos(sucursal_id=None):
    return obtener_gastos(sucursal_id)


def detalle_gasto(gasto_id):

    gasto = obtener_gasto_detalle(gasto_id)

    if not gasto:
        raise ValueError("Gasto no encontrado")

    return {
        "id": gasto[0],
        "concepto": gasto[1],
        "monto": float(gasto[2]),
        "fecha": gasto[3],
        "descripcion": gasto[4],
        "factura": gasto[5]
    }