from models.pago_model import obtener_pago_por_id as get_pago_model

def obtener_pago_por_id(pago_id):
    return get_pago_model(pago_id)