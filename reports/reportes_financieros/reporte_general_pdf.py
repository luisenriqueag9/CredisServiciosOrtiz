import sys
import os
from collections import defaultdict

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from db.connection import obtener_conexion
from datetime import datetime


# ========================
# 🔹 COBROS
# ========================
def obtener_cobros():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            c.nombre,
            p.capital_pagado,
            p.interes_pagado,
            (p.capital_pagado + p.interes_pagado),
            cr.saldo_actual,
            p.fecha_pago
        FROM pagos p
        JOIN creditos cr ON p.credito_id = cr.id
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE DATE(p.fecha_pago) >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        return cursor.fetchall()
    finally:
        conn.close()


# ========================
# 🔹 GASTOS
# ========================
def obtener_gastos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT concepto, monto, fecha
        FROM gastos
        WHERE DATE(fecha) >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        return cursor.fetchall()
    finally:
        conn.close()


# ========================
# 🔹 CREDITOS NUEVOS
# ========================
def obtener_creditos_nuevos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT c.nombre, cr.monto, cr.tasa_interes, cr.fecha_inicio
        FROM creditos cr
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE DATE(cr.fecha_inicio) >= DATE_TRUNC('month', CURRENT_DATE)
        """)
        return cursor.fetchall()
    finally:
        conn.close()
def obtener_total_cobros():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT COALESCE(SUM(capital_pagado + interes_pagado),0)
        FROM pagos
        WHERE DATE(fecha_pago) >= DATE_TRUNC('month', CURRENT_DATE)
        """)

        return cursor.fetchone()[0]

    finally:
        conn.close()


def obtener_total_gastos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT COALESCE(SUM(monto),0)
        FROM gastos
        WHERE DATE(fecha) >= DATE_TRUNC('month', CURRENT_DATE)
        """)

        return cursor.fetchone()[0]

    finally:
        conn.close()

# ========================
# 🔹 TERCEROS
# ========================
def obtener_terceros():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            tc.id,
            tc.entidad,
            tp.capital,
            tp.interes,
            tp.total,
            tp.saldo,
            tp.fecha
        FROM terceros_creditos tc
        JOIN terceros_pagos tp ON tc.id = tp.credito_id
        ORDER BY tc.id, tp.fecha
        """)
        return cursor.fetchall()
    finally:
        conn.close()


# ========================
# 🔹 PDF
# ========================
def generar_reporte_general_pdf(mes, anio):
    from datetime import date

    fecha_reporte = date(anio, mes, 1)
    doc = SimpleDocTemplate("reporte_general.pdf", pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # LOGO
    try:
        logo = Image("assets/logo.png", width=120, height=60)
        elements.append(logo)
    except:
        pass

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("INFORME GENERAL - CREDIS SERVICIOS ORTIZ", styles['Title']))
    elements.append(Paragraph(f"Periodo: {mes}/{anio}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # ========================
    # 🔹 COBROS
    # ========================
    elements.append(Paragraph("COBROS", styles['Heading2']))
    elements.append(Spacer(1, 10))

    cobros = obtener_cobros()
    tabla = [["NOMBRE", "CAPITAL", "INTERESES", "TOTAL", "SALDO", "FECHA"]]

    total = 0
    for r in cobros:
        tabla.append([
            r[0],
            f"L {r[1]:,.2f}",
            f"L {r[2]:,.2f}",
            f"L {r[3]:,.2f}",
            f"L {r[4]:,.2f}",
            r[5].strftime('%d/%m/%Y')
        ])
        total += r[3]

    tabla.append(["TOTAL", "", "", f"L {total:,.2f}", "", ""])

    t = Table(tabla)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0097A7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 20))

    # ========================
    # 🔹 GASTOS
    # ========================
    elements.append(Paragraph("GASTOS", styles['Heading2']))
    elements.append(Spacer(1, 10))

    gastos = obtener_gastos()
    tabla = [["CONCEPTO", "MONTO", "FECHA"]]

    total = 0
    for r in gastos:
        tabla.append([
            r[0],
            f"L {r[1]:,.2f}",
            r[2].strftime('%d/%m/%Y')
        ])
        total += r[1]

    tabla.append(["TOTAL", f"L {total:,.2f}", ""])

    t = Table(tabla)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E53935")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 20))

    # ========================
    # 🔹 CREDITOS NUEVOS
    # ========================
    elements.append(Paragraph("CREDITOS NUEVOS", styles['Heading2']))
    elements.append(Spacer(1, 10))

    nuevos = obtener_creditos_nuevos()
    tabla = [["CLIENTE", "MONTO", "TASA", "FECHA"]]

    for r in nuevos:
        tabla.append([
            r[0],
            f"L {r[1]:,.2f}",
            f"{r[2]}%",
            r[3].strftime('%d/%m/%Y')
        ])

    t = Table(tabla)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E88E5")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(t)
    elements.append(Spacer(1, 20))

    # ========================
    # 🔥 TERCEROS (MEJORADO)
    # ========================
    terceros = obtener_terceros()

    if terceros:
        elements.append(Paragraph("CREDITOS DE TERCEROS", styles['Heading2']))
        elements.append(Spacer(1, 10))

        grupos = defaultdict(list)

        for row in terceros:
            grupos[row[0]].append(row)

        for _, filas in grupos.items():
            entidad = filas[0][1]

            elements.append(Spacer(1, 10))
            elements.append(Paragraph(entidad.upper(), styles['Heading3']))

            tabla = [["CAPITAL", "INTERES", "TOTAL", "SALDO", "FECHA"]]

            for f in filas:
                tabla.append([
                    f"L {f[2]:,.2f}",
                    f"L {f[3]:,.2f}",
                    f"L {f[4]:,.2f}",
                    f"L {f[5]:,.2f}",
                    f[6].strftime('%d/%m/%Y')
                ])

            t = Table(tabla)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#6A1B9A")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ]))

            elements.append(t)
        # ========================
        # 🔥 RESUMEN FINANCIERO
        # ========================
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("RESUMEN FINANCIERO", styles['Heading2']))
        elements.append(Spacer(1, 10))

        total_ingresos = obtener_total_cobros()
        total_gastos = obtener_total_gastos()
        utilidad = total_ingresos - total_gastos

        tabla_resumen = [
            ["CONCEPTO", "MONTO"],
            ["TOTAL INGRESOS", f"L {total_ingresos:,.2f}"],
            ["TOTAL GASTOS", f"L {total_gastos:,.2f}"],
            ["UTILIDAD", f"L {utilidad:,.2f}"]
        ]

        t_resumen = Table(tabla_resumen)

        t_resumen.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#263238")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),

            ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#2E7D32")),
            ('TEXTCOLOR', (0,1), (-1,1), colors.white),

            ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#C62828")),
            ('TEXTCOLOR', (0,2), (-1,2), colors.white),

            ('BACKGROUND', (0,3), (-1,3), colors.HexColor("#1565C0")),
            ('TEXTCOLOR', (0,3), (-1,3), colors.white),

            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))

        elements.append(t_resumen)
    doc.build(elements)
    print("REPORTE GENERAL GENERADO")


if __name__ == "__main__":

    print("\n===== GENERADOR DE REPORTES =====\n")

    print("Seleccione el mes:")
    meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    for i, m in enumerate(meses, start=1):
        print(f"{i}. {m}")

    mes = int(input("\nIngrese el número del mes: "))

    print("\nSeleccione el año:")
    anios = [2024, 2025, 2026, 2027]

    for i, a in enumerate(anios, start=1):
        print(f"{i}. {a}")

    opcion_anio = int(input("\nIngrese opción: "))
    anio = anios[opcion_anio - 1]

    generar_reporte_general_pdf(mes, anio)