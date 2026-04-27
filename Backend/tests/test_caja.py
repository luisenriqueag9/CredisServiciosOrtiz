from services.credito_service import crear_credito_service, registrar_pago


def prueba_caja():
    try:
        # 🔥 CREAR CRÉDITO NUEVO (ACTIVO)
        credito_id = crear_credito_service(
            cliente_id=1,
            sucursal_id=1,
            monto=5000,
            tasa_interes=10,
            tipo_interes="SIMPLE",
            modalidad_pago="MENSUAL",
            plazo_numero=12,
            fecha_inicio="2026-03-19"
        )

        print("Crédito creado:", credito_id)

        # 🔥 HACER PAGO
        resultado = registrar_pago(
            credito_id=credito_id,
            capital_pagado=500,
            interes_pagado=50,
            metodo_pago="EFECTIVO",
            sucursal_id=1,
            fecha_pago="2026-03-19",
            usuario_id=1
        )

        print("Pago realizado correctamente")
        print("Nuevo saldo:", resultado)

    except Exception as e:
        print("Error:", e)


prueba_caja()