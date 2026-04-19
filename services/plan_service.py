from datetime import timedelta

def generar_plan(monto, tasa, cuotas, fecha_inicio):

    plan = []

    saldo = monto
    tasa_decimal = tasa / 100

    cuota_fija = (monto + (monto * tasa_decimal)) / cuotas

    for i in range(1, cuotas + 1):

        interes = saldo * tasa_decimal / cuotas
        capital = cuota_fija - interes
        saldo -= capital

        plan.append({
            "numero_cuota": i,
            "fecha_pago": fecha_inicio + timedelta(days=30*i),
            "cuota": round(cuota_fija, 2),
            "interes": round(interes, 2),
            "capital": round(capital, 2),
            "saldo": round(max(saldo, 0), 2)
        })

    return plan