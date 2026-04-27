from datetime import timedelta


def calcular_cuota_francesa(monto, tasa_anual, cuotas, tipo_periodo):
    
    if tipo_periodo == "MENSUAL":
        tasa_periodo = (tasa_anual / 100) / 12
    elif tipo_periodo == "SEMANAL":
        tasa_periodo = (tasa_anual / 100) / 52
    else:
        raise ValueError("Tipo de periodo no válido")

    if tasa_periodo == 0:
        return monto / cuotas

    cuota = (monto * tasa_periodo) / (1 - (1 + tasa_periodo) ** (-cuotas))

    return cuota


def generar_plan(monto, tasa, cuotas, fecha_inicio, tipo_periodo):

    plan = []
    saldo = monto

    if tipo_periodo == "MENSUAL":
        tasa_periodo = (tasa / 100) / 12
        dias = 30
    elif tipo_periodo == "SEMANAL":
        tasa_periodo = (tasa / 100) / 52
        dias = 7
    else:
        raise ValueError("Tipo de periodo no válido")

    cuota = calcular_cuota_francesa(monto, tasa, cuotas, tipo_periodo)

    for i in range(1, cuotas + 1):

        interes = saldo * tasa_periodo

        if i == cuotas:
            capital = saldo
            cuota_real = capital + interes
            saldo = 0
        else:
            capital = cuota - interes
            cuota_real = cuota
            saldo -= capital

        plan.append({
            "numero_cuota": i,
            "fecha_pago": fecha_inicio + timedelta(days=dias * i),
            "cuota": round(cuota_real, 2),
            "interes": round(interes, 2),
            "capital": round(capital, 2),
            "saldo": round(saldo, 2)
        })

    return plan

def calcular_resumen(monto, tasa, cuotas, tipo_plan, tipo_periodo):

    if tipo_plan == "CUOTA_FIJA":

        cuota = calcular_cuota_francesa(monto, tasa, cuotas, tipo_periodo)

        total_pagar = cuota * cuotas
        total_interes = total_pagar - monto

    elif tipo_plan == "CAPITAL_FIJO":

        if tipo_periodo == "MENSUAL":
            tasa_periodo = (tasa / 100) / 12
        elif tipo_periodo == "SEMANAL":
            tasa_periodo = (tasa / 100) / 52
        else:
            raise ValueError("Tipo de periodo no válido")

        capital = monto / cuotas
        total_interes = 0
        total_pagar = 0

        for i in range(cuotas):
            interes = (monto - (capital * i)) * tasa_periodo
            total_interes += interes
            total_pagar += capital + interes

        cuota = total_pagar / cuotas

    elif tipo_plan == "LIBRE":

        return {
            "mensaje": "El plan LIBRE no permite calcular cuota fija",
            "cuotas": cuotas
        }

    else:
        raise ValueError("Tipo de plan no válido")

    return {
        "cuota": round(cuota, 2),
        "total_pagar": round(total_pagar, 2),
        "total_interes": round(total_interes, 2),
        "cuotas": cuotas,
        "tipo_plan": tipo_plan
    }