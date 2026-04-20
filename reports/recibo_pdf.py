import os
from datetime import datetime
from fpdf import FPDF
from db.connection import obtener_conexion
from reports.utils_pdf import _fmt_money
from psycopg2.extras import RealDictCursor
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
        self.set_font("Times", "B", 14)
        self.cell(0, 8, "CREDIS SERVICIOS ORTIZ", ln=1, align="C")
        self.set_font("Times", "B", 12)
        self.cell(0, 8, "RECIBO DE PAGO", ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "", 9)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generar_recibo_pago(pago_id: int) -> dict:

    recibo_existente = obtener_recibo_por_pago(pago_id)

    if recibo_existente:
        return {
            "ruta": recibo_existente,
            "url": f"http://127.0.0.1:8000/files/{recibo_existente}"
        }

    con = _cx()
    cur = con.cursor()

    cur.execute("""
        SELECT 
            p.id, 
            p.fecha_pago, 
            p.monto_pagado, 
            p.capital_pagado, 
            p.interes_pagado, 
            p.credito_id,
            cr.saldo_actual
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

    numero_recibo = generar_numero_recibo()

    ruta = os.path.join(OUT_RECIBOS_DIR, f"{numero_recibo}.pdf")

    pdf = _PDFBase()
    pdf.add_page()
    pdf.set_font("Times", "", 11)

    nombre, identidad, telefono, direccion = cliente

    fecha_str = fecha.strftime("%d/%m/%Y %H:%M")

    pdf.cell(0, 6, f"Cliente: {nombre}", ln=1)
    pdf.cell(0, 6, f"DNI: {identidad}", ln=1)
    pdf.cell(0, 6, f"Tel: {telefono or '-'}", ln=1)
    pdf.cell(0, 6, f"Dirección: {direccion or '-'}", ln=1)
    pdf.ln(5)

    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 7, f"Recibo No.: {numero_recibo}", ln=1)
    pdf.cell(0, 7, f"Fecha: {fecha_str}", ln=1)

    pdf.set_font("Times", "", 11)
    pdf.cell(0, 6, f"Capital: {_fmt_money(capital)}", ln=1)
    pdf.cell(0, 6, f"Interés: {_fmt_money(interes)}", ln=1)

    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, f"TOTAL PAGADO: {_fmt_money(total)}", ln=1)

    pdf.set_font("Times", "", 11)
    pdf.cell(0, 6, f"Saldo pendiente: {_fmt_money(saldo)}", ln=1)

    pdf.ln(10)
    pdf.cell(0, 6, "Firma y sello ____________________", ln=1)

    pdf.output(ruta)

    guardar_recibo(numero_recibo, pago_id, ruta)

    return {
        "ruta": ruta,
        "url": f"http://127.0.0.1:8000/files/{ruta}"
    }