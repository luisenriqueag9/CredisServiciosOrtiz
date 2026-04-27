from db.connection import obtener_conexion


def crear_pago(credito_id, plan_pago_id, fecha_pago, monto_total,
               interes_pagado, capital_pagado,
               metodo_pago, sucursal_id):

    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        # 🔹 1. Validar que la cuota exista y no esté pagada
        cursor.execute("""
            SELECT estado, saldo_restante_programado
            FROM plan_pagos
            WHERE id = %s
        """, (plan_pago_id,))

        cuota = cursor.fetchone()

        if not cuota:
            raise Exception("La cuota no existe")

        if cuota[0] == "PAGADA":
            raise Exception("Esta cuota ya fue pagada")

        saldo_actual = cuota[1]

        # 🔹 2. Insertar pago
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
            fecha_pago,
            monto_total,
            interes_pagado,
            capital_pagado,
            metodo_pago,
            sucursal_id
        ))

        pago_id = cursor.fetchone()[0]

        # 🔥 3. Marcar cuota como PAGADA
        cursor.execute("""
            UPDATE plan_pagos
            SET estado = 'PAGADA'
            WHERE id = %s
        """, (plan_pago_id,))

        # 🔥 4. Actualizar saldo del crédito
        nuevo_saldo = saldo_actual - capital_pagado

        cursor.execute("""
            UPDATE creditos
            SET saldo_actual = %s
            WHERE id = %s
        """, (nuevo_saldo, credito_id))

        # 🔥 5. Si ya terminó → finalizar crédito
        if nuevo_saldo <= 0:
            cursor.execute("""
                UPDATE creditos
                SET estado = 'FINALIZADO',
                    fecha_fin = CURRENT_DATE
                WHERE id = %s
            """, (credito_id,))

        conn.commit()
        return pago_id

    except Exception as e:
        conn.rollback()
        print("ERROR:", e)
        return None

    finally:
        conn.close()
def obtener_pago_por_id(pago_id):
    print("BUSCANDO PAGO ID:", pago_id)
    conn = obtener_conexion()
    try:
        import psycopg2.extras
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cursor.execute("SELECT id FROM pagos")
        print("PAGOS EN BD:", cursor.fetchall())

        query = """
        SELECT 
            p.id,
            p.capital_pagado,
            p.interes_pagado,
            (p.capital_pagado + p.interes_pagado) AS total,
            p.fecha_pago,
            pp.numero_cuota,
            cr.saldo_actual,
            c.nombre,
            s.nombre as sucursal
        FROM pagos p
        LEFT JOIN plan_pagos pp ON p.plan_pago_id = pp.id
        LEFT JOIN creditos cr ON p.credito_id = cr.id
        LEFT JOIN clientes c ON cr.cliente_id = c.id
        LEFT JOIN sucursales s ON cr.sucursal_id = s.id
        WHERE p.id = %s
        """

        cursor.execute(query, (pago_id,))
        resultado = cursor.fetchone()
        print("RESULTADO QUERY:", resultado)

        return resultado

    finally:
        conn.close()