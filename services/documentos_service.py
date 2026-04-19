from documentos import generar_contrato_credito, generar_pagare_pdf

def generar_contrato(cliente_id, plan_id):
    return generar_contrato_credito(cliente_id, plan_id)

def generar_pagare(cliente_id, plan_id):
    return generar_pagare_pdf(cliente_id, plan_id)