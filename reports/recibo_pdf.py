import os
from datetime import datetime
from fpdf import FPDF
from db.connection import obtener_conexion
from reports.utils_pdf import _fmt_money
from models.recibo_model import (
    obtener_recibo_por_pago,
    generar_numero_recibo,
    guardar_recibo
)

OUT_RECIBOS_DIR = "docs/recibos"
os.makedirs(OUT_RECIBOS_DIR, exist_ok=True)

def _cx():
    return obtener_conexion()

class _PDFBase(FPDF):
    def header(self):
        try:
            # Logo centrado
            self.image("assets/logo.png", x=80, y=10, w=50)
        except:
            pass

        self.ln(25)

        # Nombre de la empresa en el azul del logo
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 169, 236) # Azul del logo
        self.cell(0, 6, "CREDIS SERVICIOS ORTIZ", 0, 1, "C")

        self.set_font("Helvetica", "", 10)
        self.set_text_color(100, 100, 100) # Gris para el eslogan
        self.cell(0, 5, "Creciendo Juntos Formamos un Mejor Futuro", 0, 1, "C")

        self.ln(3)

        # Línea horizontal en el azul del logo
        self.set_draw_color(0, 169, 236)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())

        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

def generar_recibo_pago(pago_id: int) -> dict:
    con = _cx()
    cur = con.cursor()

    cur.execute("""
        SELECT p.id, p.fecha_pago, p.monto_pagado, p.capital_pagado, 
               p.interes_pagado, p.credito_id, cr.saldo_actual
        FROM pagos p
        JOIN creditos cr ON p.credito_id = cr.id
        WHERE p.id = %s
    """, (pago_id,))
    pago = cur.fetchone()

    if not pago:
        con.close()
        raise ValueError("Pago no encontrado")

    pid, fecha, total, capital, interes, credito_id, saldo = pago

    cur.execute("""
        SELECT c.nombre, c.identidad, c.telefono, c.direccion
        FROM creditos cr
        JOIN clientes c ON cr.cliente_id = c.id
        WHERE cr.id = %s
    """, (credito_id,))
    cliente = cur.fetchone()

    if not cliente:
        con.close()
        raise ValueError("Cliente no encontrado")

    con.close()
    nombre, identidad, telefono, direccion = cliente
    numero_recibo = generar_numero_recibo()
    cliente_nombre = nombre.replace(" ", "_")

    ruta = f"docs/recibos/{cliente_nombre}/{numero_recibo}.pdf"
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    pdf = _PDFBase()
    pdf.add_page()
    
    # --- DATOS DEL CLIENTE EN UNA SOLA COLUMNA ---
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)
    fecha_str = fecha.strftime("%d/%m/%Y %H:%M")

    pdf.cell(0, 6, f"Cliente: {nombre}", 0, 1)
    pdf.cell(0, 6, f"DNI: {identidad}", 0, 1)
    pdf.cell(0, 6, f"Dirección: {direccion or '-'}", 0, 1)
    pdf.cell(0, 6, f"Tel: {telefono or '-'}", 0, 1)
    pdf.cell(0, 6, f"Fecha: {fecha_str}", 0, 1)

    pdf.ln(8)

    # Título del recibo
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 169, 236) # Azul del logo
    pdf.cell(0, 10, f"RECIBO DE PAGO No. {numero_recibo}", 0, 1, "C")

    pdf.ln(4)

    # --- TABLA CENTRADA ---
    # Ancho total de tabla = 100 (Concepto) + 40 (Monto) = 140
    # Margen para centrar: (210 - 140) / 2 = 35
    margin_x = 35
    
    pdf.set_fill_color(0, 169, 236) # Azul del logo
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 11)

    pdf.set_x(margin_x)
    pdf.cell(100, 8, "CONCEPTO", 1, 0, "C", True)
    pdf.cell(40, 8, "MONTO", 1, 1, "C", True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)

    pdf.set_x(margin_x)
    pdf.cell(100, 8, "Capital", 1)
    pdf.cell(40, 8, _fmt_money(capital), 1, 1, "R")

    pdf.set_x(margin_x)
    pdf.cell(100, 8, "Interés", 1)
    pdf.cell(40, 8, _fmt_money(interes), 1, 1, "R")

    # Fila de Total
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(230, 245, 255) # Azul muy claro para destacar
    pdf.set_x(margin_x)
    pdf.cell(100, 10, "TOTAL PAGADO", 1, 0, "C", True)
    pdf.cell(40, 10, _fmt_money(total), 1, 1, "C", True)

    pdf.ln(6)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, f"SALDO PENDIENTE: {_fmt_money(saldo)}", 0, 1, "C")

    # --- SELLO Y FIRMA DIGITAL ---
    pdf.ln(10)
    y_actual = pdf.get_y()
    try:
        pdf.image("assets/sello.png", x=85, y=y_actual, w=40)
    except:
        pass

    pdf.ln(45) # Espacio para que el texto baje y no tape el sello

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 5, "Walther Ortiz", 0, 1, "C")
    
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Representante de Credis Servicios Ortiz", 0, 1, "C")

    pdf.output(ruta)
    guardar_recibo(numero_recibo, pago_id, ruta)

    return {
        "ruta": ruta,
        "url": f"http://127.0.0.1:8000/files/{ruta}"
    }