import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from db.connection import obtener_conexion
from datetime import datetime


def obtener_gastos(mes, anio):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT concepto, monto, fecha
        FROM gastos
        WHERE EXTRACT(MONTH FROM fecha) = %s
        AND EXTRACT(YEAR FROM fecha) = %s
        """, (mes, anio))

        return cursor.fetchall()

    finally:
        conn.close()


def obtener_total(mes, anio):
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        SELECT COALESCE(SUM(monto),0)
        FROM gastos
        WHERE EXTRACT(MONTH FROM fecha) = %s
        AND EXTRACT(YEAR FROM fecha) = %s
        """, (mes, anio))

        return cursor.fetchone()[0]

    finally:
        conn.close()


def generar_reporte_gastos_pdf(mes, anio):

    ruta = f"docs/reportes/reporte_gastos_{mes}_{anio}.pdf"
    os.makedirs("docs/reportes", exist_ok=True)

    doc = SimpleDocTemplate(ruta, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("CREDIS SERVICIOS ORTIZ", styles['Title']))
    elements.append(Paragraph("Reporte de Gastos", styles['Heading2']))
    elements.append(Paragraph(f"Periodo: {mes}/{anio}", styles['Normal']))
    elements.append(Spacer(1, 20))

    datos = obtener_gastos(mes, anio)

    tabla_data = [["CONCEPTO", "MONTO", "FECHA"]]

    total = 0
    for row in datos:
        tabla_data.append([
            row[0],
            f"L {row[1]:,.2f}",
            row[2].strftime('%d/%m/%Y')
        ])
        total += row[1]

    tabla_data.append([
        "TOTAL",
        f"L {total:,.2f}",
        ""
    ])

    table = Table(tabla_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E53935")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#FFEBEE")),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))

    elements.append(table)

    doc.build(elements)

    return ruta