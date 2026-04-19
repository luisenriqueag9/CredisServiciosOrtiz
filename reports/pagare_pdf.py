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
            SELECT monto, tasa_interes, plazo_numero, fecha_inicio
            FROM creditos
            WHERE id = %s
        """, (credito_id,))

        row = cur.fetchone()

        if not row:
            con.close()
            raise ValueError("Crédito no encontrado")

        monto, tasa, cuotas, fecha_inicio = row
    else:
        monto = 0
        tasa = 0
        cuotas = 0
        fecha_inicio = fecha

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
    pdf.set_font("Times", "", 12)

    pdf.cell(0, 8, f"PAGARÉ POR {_fmt_money(monto)}", ln=1, align="C")
    pdf.ln(5)

    texto = (
        f"Yo, {nombre}, mayor de edad, con número de identidad {dni}, con domicilio en "
        f"{direccion or '__________'}, declaro que DEBO Y PAGARÉ INCONDICIONALMENTE a {EMPRESA}, "
        f"representado por el Sr. {REPRESENTANTE}, la cantidad de {_fmt_money(monto)}, en la ciudad de "
        f"{lugar}, {depto}. "
        f"Este pagaré es un título ejecutivo, autónomo y transmisible por simple endoso.\n\n"

        f"Vencimiento y forma de pago: Me obligo a pagar el capital e intereses de acuerdo con el plan de "
        f"pagos convenido con EL ACREEDOR, en sus oficinas o en la cuenta que éste designe, a más tardar en "
        f"la fecha de vencimiento de cada obligación.\n\n"

        f"Intereses: El presente pagaré devengará un interés {periodo} del {tasa:.2f}% calculado sobre el "
        f"saldo pendiente. En caso de mora, reconoceré y pagaré un interés moratorio del 3% mensual "
        f"adicional sobre las sumas vencidas desde el día siguiente al vencimiento y hasta su íntegro pago.\n\n"

        f"Aceleración: El incumplimiento de dos cuotas consecutivas o cualquier falta grave faculta a "
        f"{EMPRESA} para declarar vencida la totalidad de la obligación y exigir el pago inmediato del saldo "
        f"total adeudado, sin necesidad de requerimiento previo.\n\n"

        f"Garantías y gastos: Me constituyo responsable del pago de todos los gastos razonables de cobranza, "
        f"costas y honorarios que se generen por el incumplimiento. La garantía ofrecida para este pagaré "
        f"podrá hacerse efectiva conforme a la ley.\n\n"

        f"Notificaciones y jurisdicción: Acepto como domicilio el señalado en este instrumento y autorizo a "
        f"{EMPRESA} a notificarme por los medios de contacto registrados. Para la interpretación y ejecución "
        f"del presente pagaré, me someto a los tribunales competentes del domicilio del Acreedor.\n\n"

        f"En fe de lo anterior, firmo el presente pagaré en la ciudad de {lugar}, departamento de {depto}, "
        f"Honduras, a los {fecha.day} días del mes de {mes_es} del año {fecha.year}."
    )

    pdf.multi_cell(0, 6, texto)
    pdf.ln(10)

    pdf.cell(0, 6, "Firma ____________________", ln=1)
    pdf.cell(0, 6, nombre, ln=1)

    pdf.output(ruta)

    return ruta