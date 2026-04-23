from db.connection import obtener_conexion
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from reports.recibo_pdf import generar_recibo_pago


def registrar_pago_inteligente(credito_id: int, monto: float, metodo_pago="EFECTIVO", sucursal_id=1):

    conn = obtener_conexion()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT saldo_actual, modalidad_pago, estado
            FROM creditos
            WHERE id = %s
        """, (credito_id,))

        credito = cursor.fetchone()

        if not credito:
            raise Exception("Crédito no encontrado")

        saldo_actual, modalidad, estado = credito

        if estado != "ACTIVO":
            raise Exception("El crédito no está activo")

        monto = Decimal(str(monto))
        saldo_actual = Decimal(str(saldo_actual))

        interes_pagado = Decimal("0.00")
        capital_pagado = Decimal("0.00")
        plan_pago_id = None

        if modalidad == "LIBRE":

            raise Exception("El plan LIBRE debe manejarse diferente")

        cursor.execute("""
            SELECT id, monto_cuota, interes_programado, capital_programado
            FROM plan_pagos
            WHERE credito_id = %s AND estado = 'PENDIENTE'
            ORDER BY numero_cuota ASC
            LIMIT 1
        """, (credito_id,))

        cuota = cursor.fetchone()

        if not cuota:
            raise Exception("No hay cuotas pendientes")

        plan_pago_id, cuota_monto, interes_prog, capital_prog = cuota

        cuota_monto = Decimal(str(cuota_monto))
        interes_prog = Decimal(str(interes_prog))
        capital_prog = Decimal(str(capital_prog))

        if monto < interes_prog:
            raise Exception("El pago no cubre el interés mínimo")

        interes_pagado = interes_prog

        excedente = monto - interes_pagado

        capital_pagado = excedente if excedente <= saldo_actual else saldo_actual

        if monto >= cuota_monto:
            cursor.execute("""
                UPDATE plan_pagos
                SET estado = 'PAGADA'
                WHERE id = %s
            """, (plan_pago_id,))

        interes_pagado = interes_pagado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        capital_pagado = capital_pagado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        nuevo_saldo = (saldo_actual - capital_pagado).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if nuevo_saldo < Decimal("0.01"):
            nuevo_saldo = Decimal("0.00")

        cursor.execute("""
            INSERT INTO pagos (
                credito_id,
                plan_pago_id,
                fecha_pago,
                monto_pagado,
                interes_pagado,
                capital_pagado,
                metodo_pago,
                sucursal_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            credito_id,
            plan_pago_id,
            datetime.now(),
            monto,
            interes_pagado,
            capital_pagado,
            metodo_pago,
            sucursal_id
        ))

        pago_id = cursor.fetchone()[0]

        cursor.execute("""
            UPDATE creditos
            SET saldo_actual = %s
            WHERE id = %s
        """, (nuevo_saldo, credito_id))

        if nuevo_saldo == Decimal("0.00"):
            cursor.execute("""
                UPDATE creditos
                SET estado = 'FINALIZADO',
                    fecha_fin = CURRENT_DATE
                WHERE id = %s
            """, (credito_id,))

        conn.commit()

        recibo = generar_recibo_pago(pago_id)

        return {
            "pago_id": pago_id,
            "interes_pagado": float(interes_pagado),
            "capital_pagado": float(capital_pagado),
            "saldo_restante": float(nuevo_saldo),
            "recibo": recibo
        }

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.close()