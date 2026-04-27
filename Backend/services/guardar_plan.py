from db.connection import obtener_conexion
from datetime import datetime

def guardar_plan_en_bd(plan, credito_id):

    conn = obtener_conexion()
    cursor = conn.cursor()

    for cuota in plan:
        cursor.execute("""
            INSERT INTO plan_pagos
            (
                credito_id,
                numero_cuota,
                fecha_vencimiento,
                capital_programado,
                interes_programado,
                monto_cuota,
                saldo_restante_programado,
                estado,
                fecha_creacion
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            credito_id,
            cuota["numero_cuota"],
            cuota["fecha_pago"],
            cuota["capital"],
            cuota["interes"],
            cuota["cuota"],
            cuota["saldo"],
            "PENDIENTE",
            datetime.now()
        ))

    conn.commit()
    cursor.close()
    conn.close()
