from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from datetime import datetime
import qrcode
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SUCURSALES = {
    "Choloma": "96039778",
    "Choluteca": "31503515"
}

def formato_lempiras(valor):
    return f"L. {valor:,.2f}"

def generar_qr_whatsapp(numero):
    url = f"https://wa.me/504{numero}"
    qr = qrcode.make(url)
    qr_path = "qr_temp.png"
    qr.save(qr_path)
    return qr_path

def agregar_marca_agua(c, doc):
    c.saveState()
    c.setFont("Helvetica", 40)
    c.setFillColorRGB(0.92, 0.92, 0.92)
    c.drawCentredString(300, 400, "CREDIS SERVICIOS ORTIZ")
    c.restoreState()

def generar_pdf_plan(plan, datos_cliente, nombre_archivo):

    doc = SimpleDocTemplate(nombre_archivo, pagesize=pagesizes.A4)
    elementos = []

    styles = getSampleStyleSheet()

    azul_turquesa = colors.HexColor("#00A99D")
    gris_claro = colors.whitesmoke
    verde_pagado = colors.HexColor("#D4EDDA")

    estilo_titulo = ParagraphStyle('titulo', parent=styles['Heading1'], textColor=azul_turquesa)
    estilo_normal = ParagraphStyle('normal', parent=styles['Normal'])

    try:
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo = Image(logo_path, width=2*inch, height=1*inch)
        elementos.append(logo)
        elementos.append(Spacer(1, 10))
    except:
        pass

    elementos.append(Paragraph("<font color='#00A99D'>______________________________________________</font>", styles["Normal"]))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph("PLAN DE PAGOS", estilo_titulo))
    elementos.append(Spacer(1, 10))

    fecha_inicio = datos_cliente["fecha_inicio"]
    if isinstance(fecha_inicio, str):
        fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")

    elementos.append(Paragraph(f"N° Contrato: {datos_cliente['contrato']}", estilo_normal))
    elementos.append(Paragraph(f"Fecha emisión: {fecha_inicio.strftime('%d-%m-%Y')}", estilo_normal))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"Cliente: {datos_cliente['nombre']}", estilo_normal))
    elementos.append(Paragraph(f"DNI: {datos_cliente['dni']}", estilo_normal))
    elementos.append(Paragraph(f"Sucursal: {datos_cliente['sucursal']}", estilo_normal))
    elementos.append(Paragraph(f"Capital otorgado: {formato_lempiras(datos_cliente['capital'])}", estilo_normal))
    elementos.append(Paragraph(f"Tasa aplicada: {datos_cliente['tasa']}%", estilo_normal))
    elementos.append(Spacer(1, 20))

    data = [["Cuota", "Fecha", "Pago", "Interés", "Capital", "Saldo", "Estado"]]

    for cuota in plan:
        data.append([
            cuota["numero_cuota"],
            cuota["fecha_pago"],
            formato_lempiras(cuota["cuota"]),
            formato_lempiras(cuota["interes"]),
            formato_lempiras(cuota["capital"]),
            formato_lempiras(cuota["saldo"]),
            cuota["estado"]
        ])

    tabla = Table(data, repeatRows=1)

    tabla.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul_turquesa),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (2, 1), (-2, -1), 'RIGHT'),
    ])

    for i in range(1, len(data)):
        estado = data[i][6]
        if estado == "PAGADA":
            tabla.setStyle([('BACKGROUND', (0, i), (-1, i), verde_pagado)])
        else:
            tabla.setStyle([('BACKGROUND', (0, i), (-1, i), gris_claro)])

    elementos.append(tabla)

    bloque_final = []
    bloque_final.append(Spacer(1, 80))

    telefono = SUCURSALES.get(datos_cliente["sucursal"], "96039778")
    qr_path = generar_qr_whatsapp(telefono)

    bloque_final.append(Paragraph("Escanea para enviar comprobante por WhatsApp:", estilo_normal))
    bloque_final.append(Spacer(1, 10))
    bloque_final.append(Image(qr_path, width=2*inch, height=2*inch))
    bloque_final.append(Spacer(1, 30))

    try:
        sello_path = os.path.join(ASSETS_DIR, "sello.png")
        sello = Image(sello_path, width=1.8*inch, height=1.8*inch)
        bloque_final.append(sello)
        bloque_final.append(Spacer(1, 20))
    except:
        pass

    bloque_final.append(Paragraph("Firma Autorizada: ________________________________", estilo_normal))
    bloque_final.append(Spacer(1, 20))
    bloque_final.append(Paragraph("CREDIS SERVICIOS ORTIZ - Documento generado automáticamente", styles["Normal"]))

    elementos.append(KeepTogether(bloque_final))

    doc.build(elementos, onFirstPage=agregar_marca_agua, onLaterPages=agregar_marca_agua)

    if os.path.exists(qr_path):
        os.remove(qr_path)