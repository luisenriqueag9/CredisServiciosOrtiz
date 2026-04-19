import os
from datetime import datetime
from fpdf import FPDF
from services.plan_service import generar_plan
from db.connection import obtener_conexion
from reports.utils_pdf import _fmt_money, limpiar_nombre


class _PDFBase(FPDF):
    L = 14; T = 18; R = 14; B = 16

    def header(self):
        self.set_margins(self.L, self.T, self.R)
        self.set_y(10)
        self.set_font("Times", "B", 14)
        self.cell(0, 8, "CREDIS SERVICIOS ORTIZ", ln=1, align="C")
        self.set_font("Times", "B", 12)
        self.cell(0, 8, "PLAN DE PAGOS", ln=1, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "", 9)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")


def generar_plan_pagos_pdf(plan_id: int) -> str:

    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT 
            p.id,
            cr.cliente_id,
            c.nombre,
            c.identidad,
            c.telefono,
            cr.monto,
            cr.tasa_interes,
            cr.modalidad_pago,
            cr.plazo_numero,
            cr.fecha_inicio
        FROM plan_pagos p
        JOIN creditos cr ON cr.id = p.credito_id
        JOIN clientes c ON c.id = cr.cliente_id
        WHERE p.id = %s
    """, (plan_id,))

    row = cur.fetchone()

    if not row:
        con.close()
        raise ValueError("Plan no encontrado")

    (pid, cliente_id, nombre, dni, tel,
     monto, tasa, modalidad, cuotas, fecha_inicio) = row

    plan = generar_plan(
        monto=float(monto),
        tasa=float(tasa),
        cuotas=int(cuotas),
        fecha_inicio=datetime.now()
    )

    con.close()

    nombre_archivo = limpiar_nombre(nombre)
    carpeta = os.path.join("docs/planes", nombre_archivo)
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    pdf = _PDFBase("P", "mm", "Letter")
    pdf.add_page()
    pdf.set_font("Times", "", 11)

    tasa_valor = float(tasa)
    tasa_formateada = int(tasa_valor) if tasa_valor == int(tasa_valor) else tasa_valor

    pdf.cell(0, 6, f"Cliente: {nombre}", ln=1)
    pdf.cell(0, 6, f"DNI: {dni}", ln=1)
    pdf.cell(0, 6, f"Monto: {_fmt_money(monto)}", ln=1)
    pdf.cell(0, 6, f"Tasa: {tasa_formateada}%", ln=1)
    pdf.cell(0, 6, f"Cuotas: {cuotas}", ln=1)
    pdf.ln(5)

    pdf.set_font("Times", "B", 10)

    headers = ["#", "Fecha", "Capital", "Interés", "Cuota", "Saldo"]
    widths = [10, 30, 30, 30, 30, 30]

    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, border=1, align="C")
    pdf.ln()

    pdf.set_font("Times", "", 10)

    for c in plan:
        pdf.cell(widths[0], 7, str(c["numero_cuota"]), 1)
        pdf.cell(widths[1], 7, c["fecha_pago"].strftime("%d-%m-%Y"), 1)
        pdf.cell(widths[2], 7, f"{c['capital']:.2f}", 1)
        pdf.cell(widths[3], 7, f"{c['interes']:.2f}", 1)
        pdf.cell(widths[4], 7, f"{c['cuota']:.2f}", 1)
        pdf.cell(widths[5], 7, f"{c['saldo']:.2f}", 1)
        pdf.ln()

    pdf.output(ruta)

    return ruta