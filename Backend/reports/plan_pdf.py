import os
from datetime import datetime, date
from fpdf import FPDF
from services.plan_service import generar_plan
from db.connection import obtener_conexion
from reports.utils_pdf import _fmt_money, limpiar_nombre

class _PDFBase(FPDF):
    L = 14; T = 18; R = 14; B = 16

    def header(self):
        try:
            self.image("assets/logo.png", x=82, y=10, w=50)
        except:
            pass

        self.set_margins(self.L, self.T, self.R)
        self.ln(25)

        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 169, 236)
        self.cell(0, 8, "CREDIS SERVICIOS ORTIZ", ln=1, align="C")
        
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, "PLAN DE PAGOS", ln=1, align="C")
        
        self.ln(2)
        self.set_draw_color(0, 169, 236)
        self.set_line_width(0.5)
        self.line(14, self.get_y(), 202, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generar_plan_pagos_pdf(plan_id: int) -> str:
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT 
            cr.id, cr.cliente_id, c.nombre, c.identidad, c.telefono,
            cr.monto, cr.tasa_interes, cr.modalidad_pago,
            cr.plazo_numero, cr.fecha_inicio, cr.tipo_interes
        FROM creditos cr
        JOIN clientes c ON c.id = cr.cliente_id
        WHERE cr.id = %s
    """, (plan_id,))

    row = cur.fetchone()
    if not row:
        con.close()
        raise ValueError("Plan no encontrado")

    (pid, cliente_id, nombre, dni, tel,
     monto, tasa, modalidad, cuotas, fecha_inicio, tipo_periodo) = row

    if isinstance(fecha_inicio, date) and not isinstance(fecha_inicio, datetime):
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())

    plan = generar_plan(
        float(monto),
        float(tasa),
        int(cuotas),
        fecha_inicio,
        tipo_periodo
    )

    con.close()

    nombre_archivo = limpiar_nombre(nombre)
    carpeta = os.path.join("docs/planes/reales", nombre_archivo)
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    pdf = _PDFBase("P", "mm", "Letter")
    pdf.add_page()

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(0, 0, 0)

    pdf.cell(0, 6, f"Cliente: {nombre}", ln=1)
    pdf.cell(0, 6, f"DNI: {dni}", ln=1)
    pdf.cell(0, 6, f"Tel: {tel or '-'}", ln=1)
    pdf.cell(0, 6, f"Monto: {_fmt_money(monto)}", ln=1)
    pdf.cell(0, 6, f"Tasa: {tasa}%", ln=1)
    pdf.cell(0, 6, f"Cuotas: {cuotas}", ln=1)

    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 10)
    headers = ["#", "Fecha", "Capital", "Interés", "Cuota", "Saldo"]
    widths = [12, 32, 36, 36, 36, 36]

    pdf.set_fill_color(0, 169, 236)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for i, c in enumerate(plan):
        fecha = c["fecha_pago"]
        if isinstance(fecha, datetime):
            fecha = fecha.strftime("%d-%m-%Y")

        fill = i % 2 == 0
        pdf.set_fill_color(245, 250, 255)

        pdf.cell(widths[0], 7, str(c["numero_cuota"]), 1, 0, "C", fill)
        pdf.cell(widths[1], 7, fecha, 1, 0, "C", fill)
        pdf.cell(widths[2], 7, _fmt_money(c["capital"]), 1, 0, "R", fill)
        pdf.cell(widths[3], 7, _fmt_money(c["interes"]), 1, 0, "R", fill)
        pdf.cell(widths[4], 7, _fmt_money(c["cuota"]), 1, 0, "R", fill)
        pdf.cell(widths[5], 7, _fmt_money(c["saldo"]), 1, 1, "R", fill)

    pdf.ln(15)
    pdf.output(ruta)

    return ruta


def generar_plan_simulado_pdf(monto, tasa, cuotas, fecha_inicio):

    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    plan = generar_plan(monto, tasa, cuotas, fecha_inicio, "MENSUAL")

    carpeta = "docs/planes/simulados"
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, f"plan_simulado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    pdf = _PDFBase("P", "mm", "Letter")
    pdf.add_page()

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Monto: {_fmt_money(monto)}", ln=1)
    pdf.cell(0, 6, f"Tasa: {tasa}%", ln=1)
    pdf.cell(0, 6, f"Cuotas: {cuotas}", ln=1)

    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 10)
    headers = ["#", "Fecha", "Capital", "Interés", "Cuota", "Saldo"]
    widths = [12, 32, 36, 36, 36, 36]

    pdf.set_fill_color(0, 169, 236)
    pdf.set_text_color(255, 255, 255)
    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(0, 0, 0)

    for i, c in enumerate(plan):
        fecha = c["fecha_pago"]
        if isinstance(fecha, datetime):
            fecha = fecha.strftime("%d-%m-%Y")

        fill = i % 2 == 0
        pdf.set_fill_color(245, 250, 255)

        pdf.cell(widths[0], 7, str(c["numero_cuota"]), 1, 0, "C", fill)
        pdf.cell(widths[1], 7, fecha, 1, 0, "C", fill)
        pdf.cell(widths[2], 7, _fmt_money(c["capital"]), 1, 0, "R", fill)
        pdf.cell(widths[3], 7, _fmt_money(c["interes"]), 1, 0, "R", fill)
        pdf.cell(widths[4], 7, _fmt_money(c["cuota"]), 1, 0, "R", fill)
        pdf.cell(widths[5], 7, _fmt_money(c["saldo"]), 1, 1, "R", fill)

    pdf.output(ruta)

    return ruta