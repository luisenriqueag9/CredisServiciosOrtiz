import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from db.connection import obtener_conexion
from datetime import datetime


def obtener_gastos():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT concepto, monto, fecha
        FROM gastos
        WHERE DATE(fecha) >= DATE_TRUNC('month', CURRENT_DATE)
        """

        cursor.execute(query)
        return cursor.fetchall()

    finally:
        conn.close()


def obtener_total():
    conn = obtener_conexion()
    try:
        cursor = conn.cursor()

        query = """
        SELECT COALESCE(SUM(monto),0)
        FROM gastos
        WHERE DATE(fecha) >= DATE_TRUNC('month', CURRENT_DATE)
        """

        cursor.execute(query)
        return cursor.fetchone()[0]

    finally:
        conn.close()


def generar_pdf():
    doc = SimpleDocTemplate("reporte_gastos.pdf", pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()

    titulo = Paragraph("INFORME DE GASTOS", styles['Title'])
    elements.append(titulo)

    elements.append(Spacer(1, 20))

    datos = obtener_gastos()

    tabla_data = [["CONCEPTO", "MONTO", "FECHA"]]

    for row in datos:
        tabla_data.append([
            row[0],
            f"L {row[1]:,.2f}",
            row[2].strftime('%d/%m/%Y')
        ])

    total = obtener_total()

    tabla_data.append([
        "TOTAL",
        f"L {total:,.2f}",
        ""
    ])

    table = Table(tabla_data)

    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0097A7")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0F7FA")),
    ])

    table.setStyle(style)

    elements.append(table)

    doc.build(elements)

    print("Reporte de gastos generado")