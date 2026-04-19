from models.recibo_model import obtener_recibo_por_pago, generar_numero_recibo, guardar_recibo
from models.pago_model import obtener_pago_por_id
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def formato_lempiras(valor):
    return f"L. {valor:,.2f}"


def generar_recibo_pdf(pago_id, nombre_archivo):

    recibo_existente = obtener_recibo_por_pago(pago_id)

    if recibo_existente:
        return {
            "numero_recibo": recibo_existente['numero_recibo'],
            "ruta_pdf": recibo_existente['ruta_pdf'],
            "existe": True
        }

    pago = obtener_pago_por_id(pago_id)

    if not pago:
        return {
            "error": "Pago no encontrado"
        }

    # 🔥 NUEVA LÓGICA POR CLIENTE
    cliente_id = pago.get("cliente_id", pago_id)

    carpeta_cliente = os.path.join(BASE_DIR, "recibos", f"cliente_{cliente_id}")

    if not os.path.exists(carpeta_cliente):
        os.makedirs(carpeta_cliente)

    nombre_archivo = os.path.join(carpeta_cliente, f"recibo_{pago_id}.pdf")

    numero_recibo = generar_numero_recibo()

    datos = {
        "numero_recibo": numero_recibo,
        "numero": pago["numero_cuota"],
        "cliente": pago["nombre"],
        "capital": float(pago["capital_pagado"]),
        "interes": float(pago["interes_pagado"]),
        "total": float(pago["total"]),
        "saldo": float(pago["saldo_actual"]),
        "estado": "PAGADO",
        "fecha": pago["fecha_pago"].strftime("%d/%m/%Y"),
        "concepto": "Pago cuota crédito",
        "sucursal": pago["sucursal"]
    }

    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
    elementos = []
    styles = getSampleStyleSheet()

    azul = colors.HexColor("#00A99D")

    estilo_titulo = ParagraphStyle(
        'titulo',
        parent=styles['Heading1'],
        textColor=azul
    )

    try:
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        logo = Image(logo_path, width=2*inch, height=1*inch)
        elementos.append(logo)
        elementos.append(Spacer(1, 10))
    except:
        pass

    elementos.append(Paragraph("RECIBO DE PAGO", estilo_titulo))
    elementos.append(Spacer(1, 10))

    elementos.append(Paragraph(f"N° Recibo: {datos['numero_recibo']}", styles["Normal"]))
    elementos.append(Paragraph(f"Fecha: {datos['fecha']}", styles["Normal"]))
    elementos.append(Paragraph(f"Cliente: {datos['cliente']}", styles["Normal"]))
    elementos.append(Paragraph(f"Sucursal: {datos['sucursal']}", styles["Normal"]))
    elementos.append(Spacer(1, 20))

    data = [
        ["N°", "CAPITAL", "INTERÉS", "TOTAL", "SALDO", "ESTADO", "FECHA"],
        [
            datos["numero"],
            formato_lempiras(datos["capital"]),
            formato_lempiras(datos["interes"]),
            formato_lempiras(datos["total"]),
            formato_lempiras(datos["saldo"]),
            datos["estado"],
            datos["fecha"]
        ]
    ]

    tabla = Table(data)

    tabla.setStyle([
        ('BACKGROUND', (0, 0), (-1, 0), azul),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 1), (-2, -1), 'RIGHT'),
    ])

    elementos.append(tabla)
    elementos.append(Spacer(1, 20))

    elementos.append(Paragraph(f"Concepto: {datos['concepto']}", styles["Normal"]))
    elementos.append(Spacer(1, 40))

    try:
        sello_path = os.path.join(ASSETS_DIR, "sello.png")
        sello = Image(sello_path, width=2*inch, height=2*inch)
        elementos.append(sello)
        elementos.append(Spacer(1, 10))
    except:
        pass

    elementos.append(Paragraph("Documento válido sin firma manuscrita", styles["Normal"]))
    elementos.append(Paragraph("CREDIS SERVICIOS ORTIZ", styles["Normal"]))

    doc.build(elementos)

    guardar_recibo(numero_recibo, pago_id, nombre_archivo)

    print(f"✅ RECIBO GENERADO Y GUARDADO: {numero_recibo}")

    return {
        "numero_recibo": numero_recibo,
        "ruta_pdf": nombre_archivo,
        "existe": False
    }