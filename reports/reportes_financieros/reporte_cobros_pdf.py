import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from db.connection import obtener_conexion
from datetime import datetime


def obtener_datos_cobros(mes, anio, sucursal_id=None):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            c.nombre,
            p.capital_pagado,
            p.interes_pagado,
            (p.capital_pagado + p.interes_pagado) AS total_cuota,
            cr.saldo_actual,
            p.fecha_pago
        FROM pagos p
        JOIN creditos cr ON p.credito_id = cr.id
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE EXTRACT(MONTH FROM p.fecha_pago) = %s
        AND EXTRACT(YEAR FROM p.fecha_pago) = %s
        """

        if sucursal_id:
            query += " AND p.sucursal_id = %s"
            cursor.execute(query, (mes, anio, sucursal_id))
        else:
            cursor.execute(query, (mes, anio))

        rows = cursor.fetchall()
        return rows

    finally:
        conn.close()


def obtener_totales(mes, anio, sucursal_id=None):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            COALESCE(SUM(capital_pagado),0),
            COALESCE(SUM(interes_pagado),0),
            COALESCE(SUM(monto_pagado),0)
        FROM pagos
        WHERE EXTRACT(MONTH FROM fecha_pago) = %s
        AND EXTRACT(YEAR FROM fecha_pago) = %s
        """

        if sucursal_id:
            query += " AND sucursal_id = %s"
            cursor.execute(query, (mes, anio, sucursal_id))
        else:
            cursor.execute(query, (mes, anio))

        return cursor.fetchone()

    finally:
        conn.close()


def generar_reporte_cobros_pdf(mes, anio, sucursal_id=None):
    ruta = f"docs/reportes/reporte_cobros_{mes}_{anio}.pdf"
    os.makedirs("docs/reportes", exist_ok=True)

    doc = SimpleDocTemplate(ruta, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    # LOGO
    try:
        logo = Image("assets/logo.png", width=120, height=60)
        elements.append(logo)
    except:
        pass

    elements.append(Spacer(1, 10))

    titulo = Paragraph("INFORME DE COBROS - CREDIS SERVICIOS ORTIZ", styles['Title'])
    elements.append(titulo)

    fecha = Paragraph(f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal'])
    elements.append(fecha)

    elements.append(Spacer(1, 20))

    datos = obtener_datos_cobros(mes, anio, sucursal_id)

    tabla_data = [
        ["NOMBRE", "CAPITAL", "INTERESES", "TOTAL CUOTA", "SALDO", "FECHA"]
    ]
    total_saldo = 0
    for row in datos:
        tabla_data.append([
            row[0],
            f"L {row[1]:,.2f}",
            f"L {row[2]:,.2f}",
            f"L {row[3]:,.2f}",
            f"L {row[4]:,.2f}",
            row[5].strftime('%d/%m/%Y')
        ])

        total_saldo += row[4]

    totales = obtener_totales(mes, anio, sucursal_id)

    tabla_data.append([
    "TOTAL",
    f"L {totales[0]:,.2f}",
    f"L {totales[1]:,.2f}",
    f"L {totales[2]:,.2f}",
    f"L {total_saldo:,.2f}",
    ""
])

    table = Table(tabla_data)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0097A7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),

        ('FONTNAME', (0,1), (-1,-2), 'Helvetica'),
        ('ALIGN', (1,1), (-1,-1), 'RIGHT'),

        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0F7FA")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),

        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ])

    table.setStyle(style)

    elements.append(table)

    doc.build(elements)

    return ruta


if __name__ == "__main__":
    generar_reporte_cobros_pdf(4, 2026)