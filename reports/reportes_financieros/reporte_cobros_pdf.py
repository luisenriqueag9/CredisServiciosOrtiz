import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from db.connection import obtener_conexion
from datetime import datetime


def obtener_datos_cobros(sucursal_id=None):
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
        WHERE DATE(p.fecha_pago) >= DATE_TRUNC('month', CURRENT_DATE)
        """

        if sucursal_id:
            query += " AND p.sucursal_id = %s"
            cursor.execute(query, (sucursal_id,))
        else:
            cursor.execute(query)

        rows = cursor.fetchall()
        return rows

    finally:
        conn.close()


def obtener_totales(sucursal_id=None):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            COALESCE(SUM(capital_pagado),0),
            COALESCE(SUM(interes_pagado),0),
            COALESCE(SUM(monto_pagado),0)
        FROM pagos
        WHERE DATE(fecha_pago) >= DATE_TRUNC('month', CURRENT_DATE)
        """

        if sucursal_id:
            query += " AND sucursal_id = %s"
            cursor.execute(query, (sucursal_id,))
        else:
            cursor.execute(query)

        return cursor.fetchone()

    finally:
        conn.close()


def generar_pdf(sucursal_id=None):
    doc = SimpleDocTemplate("reporte_cobros.pdf", pagesize=letter)
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

    datos = obtener_datos_cobros(sucursal_id)

    tabla_data = [
        ["NOMBRE", "CAPITAL", "INTERESES", "TOTAL CUOTA", "SALDO", "FECHA"]
    ]

    for row in datos:
        tabla_data.append([
            row[0],
            f"L {row[1]:,.2f}",
            f"L {row[2]:,.2f}",
            f"L {row[3]:,.2f}",
            f"L {row[4]:,.2f}",
            row[5].strftime('%d/%m/%Y')
        ])

    totales = obtener_totales(sucursal_id)

    tabla_data.append([
        "TOTAL",
        f"L {totales[0]:,.2f}",
        f"L {totales[1]:,.2f}",
        f"L {totales[2]:,.2f}",
        "",
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

    print("PDF generado correctamente")


if __name__ == "__main__":
    generar_pdf()