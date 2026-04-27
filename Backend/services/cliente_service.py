from models.cliente_model import (
    crear_cliente,
    obtener_cliente_por_id,
    listar_clientes,
    eliminar_cliente,
    obtener_cliente_por_identidad,
    actualizar_cliente
)


def registrar_cliente(nombre, identidad, telefono, direccion, sucursal_id):

    if not nombre or nombre.strip() == "":
        raise ValueError("El nombre es obligatorio.")

    if sucursal_id is None:
        raise ValueError("La sucursal es obligatoria.")

    if identidad:
        existente = obtener_cliente_por_identidad(identidad)
        if existente:
            raise ValueError("Ya existe un cliente con esa identidad.")

    nuevo_id = crear_cliente(nombre, identidad, telefono, direccion, sucursal_id)
    return nuevo_id


def obtener_cliente(cliente_id):
    if not cliente_id:
        raise ValueError("ID inválido.")

    return obtener_cliente_por_id(cliente_id)


def listar_todos_los_clientes():
    return listar_clientes()


def eliminar_cliente_por_id(cliente_id):
    if not cliente_id:
        raise ValueError("ID inválido.")

    eliminar_cliente(cliente_id)

def actualizar_cliente_service(cliente_id, datos):
    cliente = obtener_cliente_por_id(cliente_id)

    if not cliente:
        raise ValueError("Cliente no existe.")

    if cliente["estado"] != "ACTIVO":
        raise ValueError("No se puede modificar un cliente inactivo.")

    if "identidad" in datos:
        raise ValueError("La identidad no puede modificarse.")

    if not datos.get("nombre"):
        raise ValueError("El nombre es obligatorio.")

    if not datos.get("sucursal_id"):
        raise ValueError("La sucursal es obligatoria.")

    return actualizar_cliente(cliente_id, datos)