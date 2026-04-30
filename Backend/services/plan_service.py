from datetime import timedelta


# ✅ CUOTA TIPO EXCEL (PAGO)
def calcular_cuota_francesa(monto, tasa, cuotas):

    tasa_periodo = tasa / 100  # 5% mensual

    if tasa_periodo == 0:
        return monto / cuotas

    cuota = (monto * tasa_periodo) / (1 - (1 + tasa_periodo) ** (-cuotas))

    return cuota


# ✅ PLAN DE PAGOS (IGUAL A EXCEL)
def generar_plan(monto, tasa, cuotas, fecha_inicio, tipo_periodo, tipo_plan, pago_mensual=None):

    plan = []
    saldo = monto

    tasa_periodo = tasa / 100
    dias = 30 if tipo_periodo == "MENSUAL" else 7

    # =========================
    # 🔵 CUOTA FIJA
    # =========================
    if tipo_plan == "CUOTA_FIJA":

        cuota = calcular_cuota_francesa(monto, tasa, cuotas)

        for i in range(1, cuotas + 1):

            interes = saldo * tasa_periodo
            capital = cuota - interes
            saldo -= capital

            if saldo < 0:
                saldo = 0

            plan.append({
                "numero_cuota": i,
                "fecha_pago": fecha_inicio + timedelta(days=dias * i),
                "cuota": round(cuota, 2),
                "interes": round(interes, 2),
                "capital": round(capital, 2),
                "saldo": round(saldo, 2)
            })

    # =========================
    # 🟢 CAPITAL FIJO (CON PAGO MENSUAL)
    # =========================
    elif tipo_plan == "CAPITAL_FIJO":

        # 🔥 CASO 1: pago mensual dinámico
        if pago_mensual:

            for i in range(1, 1000):

                interes = saldo * tasa_periodo
                capital = pago_mensual

                if capital >= saldo:
                    capital = saldo
                    cuota = capital + interes
                    saldo = 0
                else:
                    cuota = capital + interes
                    saldo -= capital

                plan.append({
                    "numero_cuota": i,
                    "fecha_pago": fecha_inicio + timedelta(days=dias * i),
                    "cuota": round(cuota, 2),
                    "interes": round(interes, 2),
                    "capital": round(capital, 2),
                    "saldo": round(saldo, 2)
                })

                if saldo <= 0:
                    break

        # 🔵 CASO 2: capital fijo tradicional
        else:

            capital = monto / cuotas

            for i in range(1, cuotas + 1):

                interes = saldo * tasa_periodo

                if i == cuotas:
                    capital = saldo

                cuota = capital + interes
                saldo -= capital

                if saldo < 0:
                    saldo = 0

                plan.append({
                    "numero_cuota": i,
                    "fecha_pago": fecha_inicio + timedelta(days=dias * i),
                    "cuota": round(cuota, 2),
                    "interes": round(interes, 2),
                    "capital": round(capital, 2),
                    "saldo": round(saldo, 2)
                })

    else:
        raise ValueError("Tipo de plan no válido")

    return plan


# ✅ RESUMEN (PARA SIMULADOR)
def calcular_resumen(monto, tasa, cuotas, tipo_plan, tipo_periodo, pago_mensual=None):

    if tipo_plan == "CUOTA_FIJA":

        cuota = calcular_cuota_francesa(monto, tasa, cuotas)

        total_pagar = cuota * cuotas
        total_interes = total_pagar - monto

    elif tipo_plan == "CAPITAL_FIJO":

        tasa_periodo = tasa / 100

        # 🔥 CASO 1: pago mensual (TU NUEVO FLUJO)
        if pago_mensual:

            saldo = monto
            total_interes = 0
            total_pagar = 0
            cuotas = 0
            primera_cuota = None

            while saldo > 0:

                interes = saldo * tasa_periodo
                capital = pago_mensual  # ✅ capital fijo REAL

                if capital >= saldo:
                    capital = saldo
                    cuota = capital + interes
                    saldo = 0
                else:
                    cuota = capital + interes
                    saldo -= capital

                # 🔥 guardar primera cuota
                if primera_cuota is None:
                    primera_cuota = cuota

                total_interes += interes
                total_pagar += cuota
                cuotas += 1

                if cuotas > 1000:
                    raise ValueError("Demasiadas cuotas")

                

        # 🔵 CASO 2: capital fijo clásico
        else:

            if tipo_plan == "CUOTA_FIJA" and not cuotas:
                raise ValueError("Debe indicar cuotas")

            if tipo_plan == "CAPITAL_FIJO" and not pago_mensual:
                raise ValueError("Debe indicar pago mensual")

            capital = monto / cuotas

            total_interes = 0
            total_pagar = 0

            for i in range(cuotas):
                interes = (monto - (capital * i)) * tasa_periodo
                total_interes += interes
                total_pagar += capital + interes

            cuota = total_pagar / cuotas

    else:
        raise ValueError("Tipo de plan no válido")

    return {
        "cuota": round(primera_cuota if tipo_plan == "CAPITAL_FIJO" else cuota, 2) if tipo_plan == "CUOTA_FIJA" else round(primera_cuota or 0, 2),
        "total_pagar": round(total_pagar, 2),
        "total_interes": round(total_interes, 2),
        "cuotas": cuotas,
        "tipo_plan": tipo_plan
    }

def calcular_cuotas_por_pago(monto, tasa, pago_mensual):

    tasa_periodo = tasa / 100
    saldo = monto
    cuotas = 0

    # 🔥 VALIDACIÓN INICIAL
    if pago_mensual <= monto * tasa_periodo:
        raise ValueError("El pago mensual es muy bajo, no cubre los intereses")

    while saldo > 0:
        interes = saldo * tasa_periodo
        capital = pago_mensual - interes

        if capital <= 0:
            raise ValueError("El pago mensual no reduce la deuda")

        saldo -= capital
        cuotas += 1

        if cuotas > 1000:
            raise ValueError("Demasiadas cuotas, revise el pago")

    return cuotas