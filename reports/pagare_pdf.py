from datetime import datetime
import os
from reports.base_pdf import PDFBase
from reports.utils_pdf import _fmt_money, limpiar_nombre
from db.connection import obtener_conexion

OUT_PAGARES_DIR = "docs/pagares"
os.makedirs(OUT_PAGARES_DIR, exist_ok=True)

EMPRESA = "CREDIS SERVICIOS ORTIZ"
REPRESENTANTE = "WALTHER ORTIZ"

MESES_ES = {
    "01": "ENERO", "02": "FEBRERO", "03": "MARZO",
    "04": "ABRIL", "05": "MAYO", "06": "JUNIO",
    "07": "JULIO", "08": "AGOSTO", "09": "SEPTIEMBRE",
    "10": "OCTUBRE", "11": "NOVIEMBRE", "12": "DICIEMBRE"
}


def _cx():
    return obtener_conexion()


def _obtener_cliente(cliente_id):
    con = _cx()
    cur = con.cursor()

    cur.execute("""
        SELECT nombre, identidad, telefono, direccion
        FROM clientes
        WHERE id = %s
    """, (cliente_id,))

    row = cur.fetchone()
    con.close()
    return row


class PDFPagare(PDFBase):
    header_title = "PAGARÉ"


def generar_pagare_pdf(cliente_id, credito_id=None):

    fecha = datetime.now()
    lugar = "Pespire"
    depto = "Choluteca"
    periodo = "mensual"

    con = _cx()
    cur = con.cursor()

    cliente = _obtener_cliente(cliente_id)

    if not cliente:
        con.close()
        raise ValueError("Cliente no encontrado")

    nombre, dni, telefono, direccion = cliente

    if credito_id:
        cur.execute("""
            SELECT 
                cr.monto, 
                cr.tasa_interes, 
                cr.plazo_numero, 
                cr.fecha_inicio,
                a.nombre,
                a.identidad
            FROM creditos cr
            LEFT JOIN avales a ON cr.aval_id = a.id
            WHERE cr.id = %s
        """, (credito_id,))

        row = cur.fetchone()

        if not row:
            con.close()
            raise ValueError("Crédito no encontrado")

        monto, tasa, cuotas, fecha_inicio, aval_nombre, aval_dni = row
        if not aval_nombre:
            aval_nombre = "__________________"
            aval_dni = "__________________"
    else:
        monto = 0
        tasa = 0
        cuotas = 0
        fecha_inicio = fecha
        aval_nombre = "__________________"
        aval_dni = "__________________"

    con.close()

    mes_es = MESES_ES[fecha.strftime("%m")]

    carpeta = os.path.join(OUT_PAGARES_DIR, limpiar_nombre(nombre))
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(
        carpeta,
        f"pagare_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    pdf = PDFPagare()
    pdf.add_page()

    # 🔥 QUITAR TÍTULO GRANDE (no usamos header_title visualmente)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0, 8, f"PAGARÉ POR {_fmt_money(monto)}", ln=1, align="C")

    pdf.ln(3)

    pdf.set_font("Times", "", 11)

    texto = (
        f"Yo, {nombre}, mayor de edad, de estado civil SOLTERO, de nacionalidad HONDUREÑA, "
        f"con número de identidad {dni} y domicilio en {direccion or '__________'}, por medio del presente "
        f"declaro que DEBO Y PAGARÉ INCONDICIONALMENTE a {EMPRESA}, representado por el Sr. {REPRESENTANTE}, "
        f"la cantidad de {_fmt_money(monto)}, en la ciudad de {lugar}, {depto}.\n\n"

        f"Este pagaré devengará una tasa de interés mensual del {tasa:.2f}% y me obligo a cumplir con el pago "
        f"del capital e intereses de acuerdo con las condiciones establecidas. Como garantía para el presente "
        f"pagaré, comprometo todos mis bienes presentes y futuros. En caso de incumplimiento en el pago de "
        f"intereses y/o capital en los plazos acordados, {EMPRESA} tendrá derecho a dar por vencida la totalidad "
        f"de la obligación sin necesidad de requerimiento previo.\n\n"

        f"Asimismo, asumo la responsabilidad de cubrir los gastos derivados del incumplimiento de este título, "
        f"incluyendo cualquier recargo o costos legales que puedan generarse. Renuncio expresamente a toda diligencia "
        f"de requerimiento judicial o extrajudicial y acepto someterme al domicilio que {EMPRESA} o su tenedor legítimo señale.\n\n"

        f"Declaro que la falta de ejercicio de las acciones derivadas de este pagaré por parte de {EMPRESA} no constituye "
        f"renuncia a sus derechos, y que el plazo de presentación de este título quedará sujeto a criterio exclusivo de "
        f"la entidad acreedora.\n\n"

        f"Este pagaré se rige por las disposiciones pertinentes del Código de Comercio de Honduras.\n\n"

        f"En fe de lo anterior, firmo el presente pagaré en la ciudad de {lugar}, departamento de {depto}, "
        f"Honduras, a los {fecha.day:02d} días del mes de {mes_es} del año {fecha.year}."
    )

    # 🔥 REDUCIR ESPACIO PARA QUE TODO QUEPA
    pdf.multi_cell(0, 5, texto)

    # 🔥 SUBIR FIRMAS (menos espacio)
    pdf.ln(8)

    pdf.set_font("Times", "", 10)

    # --- CLIENTE Y AVAL ---
    pdf.cell(90, 5, "__________________________________", align="C")
    pdf.cell(90, 5, "__________________________________", ln=1, align="C")

    pdf.cell(90, 5, nombre, align="C")
    pdf.cell(90, 5, aval_nombre, ln=1, align="C")

    pdf.cell(90, 5, f"ID: {dni}", align="C")
    pdf.cell(90, 5, f"ID: {aval_dni}", ln=1, align="C")

    pdf.cell(90, 5, "PRESTATARIO", align="C")
    pdf.cell(90, 5, "AVAL", ln=1, align="C")

    # 🔥 ESPACIO CONTROLADO
    pdf.ln(10)

    # --- FIRMA EMPRESA CENTRADA ---
    # --- FIRMA EMPRESA CENTRADA REAL ---
    pdf.ln(8)

    pdf.set_font("Times", "", 10)

    y_firma = pdf.get_y()

    # Línea centrada
    pdf.cell(0, 5, "_________________________________", ln=1, align="C")

    # Nombre
    pdf.cell(0, 5, REPRESENTANTE, ln=1, align="C")

    # Cargo
    pdf.cell(0, 5, "REPRESENTANTE LEGAL", ln=1, align="C")

    # Empresa
    pdf.cell(0, 5, EMPRESA, ln=1, align="C")

    # --- SELLO A LA PAR (NO ENCIMA) ---
    try:
        pdf.image(
            "assets/sello.png",
            x=130,          # 👉 mueve horizontalmente (135–150)
            y=y_firma - 12,  # 👉 alineado con la línea
            w=45
        )
    except:
        pass

    pdf.output(ruta)
    return ruta