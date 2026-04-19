from datetime import datetime, timedelta
import calendar


class MotorFinanciero:

    def convertir_tasa(self, tasa):
        return tasa / 100

    def generar_fechas(self, fecha_inicio, cuotas, tipo_periodo):
        fechas = []
        fecha_actual = fecha_inicio

        for i in range(cuotas):

            if tipo_periodo == "MENSUAL":
                mes = fecha_actual.month + 1
                año = fecha_actual.year

                if mes > 12:
                    mes = 1
                    año += 1

                ultimo_dia_mes = calendar.monthrange(año, mes)[1]
                dia = min(fecha_inicio.day, ultimo_dia_mes)

                fecha_actual = fecha_actual.replace(year=año, month=mes, day=dia)

            elif tipo_periodo == "SEMANAL":
                fecha_actual += timedelta(days=7)

            fechas.append(fecha_actual)

        return fechas

    def sistema_frances(self, capital, tasa, cuotas, fecha_inicio, tipo_periodo):
        tasa = self.convertir_tasa(tasa)

        if tasa == 0:
            cuota = capital / cuotas
        else:
            cuota = capital * (tasa * (1 + tasa) ** cuotas) / ((1 + tasa) ** cuotas - 1)

        saldo = capital
        plan = []
        fechas = self.generar_fechas(fecha_inicio, cuotas, tipo_periodo)

        for numero in range(1, cuotas + 1):
            interes = saldo * tasa
            capital_pagado = cuota - interes
            saldo -= capital_pagado

            if saldo < 0:
                saldo = 0

            plan.append({
                "numero_cuota": numero,
                "fecha_pago": fechas[numero - 1].strftime("%d-%m-%Y"),
                "cuota": round(cuota, 2),
                "interes": round(interes, 2),
                "capital": round(capital_pagado, 2),
                "saldo": round(saldo, 2),
                "estado": "PENDIENTE"
            })

        return plan

    def sistema_aleman(self, capital, tasa, cuotas, fecha_inicio, tipo_periodo):
        tasa = self.convertir_tasa(tasa)
        capital_fijo = capital / cuotas
        saldo = capital
        plan = []
        fechas = self.generar_fechas(fecha_inicio, cuotas, tipo_periodo)

        for numero in range(1, cuotas + 1):
            interes = saldo * tasa
            cuota = capital_fijo + interes
            saldo -= capital_fijo

            if saldo < 0:
                saldo = 0

            plan.append({
                "numero_cuota": numero,
                "fecha_pago": fechas[numero - 1].strftime("%d-%m-%Y"),
                "cuota": round(cuota, 2),
                "interes": round(interes, 2),
                "capital": round(capital_fijo, 2),
                "saldo": round(saldo, 2),
                "estado": "PENDIENTE"
            })

        return plan

    def modalidad_libre(self, saldo_actual, tasa, pago):
        tasa = self.convertir_tasa(tasa)

        interes = saldo_actual * tasa
        pago_minimo = interes

        if pago < pago_minimo:
            raise ValueError("El pago no cubre el interés del período.")

        capital_pagado = pago - interes
        nuevo_saldo = saldo_actual - capital_pagado

        if nuevo_saldo < 0:
            nuevo_saldo = 0

        return {
            "interes": round(interes, 2),
            "capital_pagado": round(capital_pagado, 2),
            "nuevo_saldo": round(nuevo_saldo, 2)
        }

    def registrar_pago(self, plan, numero_cuota):
        for cuota in plan:
            if cuota["numero_cuota"] == numero_cuota:
                cuota["estado"] = "PAGADA"
                break
        return plan

