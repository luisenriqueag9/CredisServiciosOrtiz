from datetime import datetime
import os
from reports.base_pdf import PDFBase
from reports.utils_pdf import _fmt_money, limpiar_nombre
from db.connection import obtener_conexion

OUT_CONTRATOS_DIR = "docs/contratos"
os.makedirs(OUT_CONTRATOS_DIR, exist_ok=True)

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
        SELECT id, nombre, identidad, telefono, direccion
        FROM clientes
        WHERE id = %s
    """, (cliente_id,))

    row = cur.fetchone()
    con.close()

    if not row:
        return None

    return {
        "id": row[0],
        "nombre": row[1],
        "identidad": row[2],
        "telefono": row[3],
        "direccion": row[4],
    }


class PDFContrato(PDFBase):
    header_title = "CONTRATO DE CRÉDITO"


def generar_contrato_pdf(cliente_id, credito_id=None,
                         garantia="PAGARÉ FIRMADO",
                         lugar="PESPIRE", depto="CHOLUTECA",
                         fecha=None):

    fecha = fecha or datetime.now()

    con = _cx()
    cur = con.cursor()

    cli = _obtener_cliente(cliente_id)

    if not cli:
        con.close()
        raise RuntimeError("Cliente no encontrado.")

    nombre = cli["nombre"]
    dni = cli["identidad"]
    direccion = cli["direccion"]

    
    monto = 0
    tasa = 0
    n_cuotas = 0
    fecha_inicio = fecha
    aval_nombre = None
    aval_dni = None
    garantia = None
    
    if credito_id is not None:
        cur.execute("""
            SELECT 
                cr.monto, 
                cr.tasa_interes, 
                cr.plazo_numero, 
                cr.fecha_inicio,
                a.nombre,
                a.identidad,
                cr.garantia
            FROM creditos cr
            LEFT JOIN avales a ON cr.aval_id = a.id
            WHERE cr.id = %s
        """, (credito_id,))

        row = cur.fetchone()

        if not row:
            con.close()
            raise RuntimeError("Crédito no encontrado.")

        monto, tasa, n_cuotas, fecha_inicio, aval_nombre, aval_dni, garantia = row
    
    if not garantia:
        garantia = "PAGARÉ FIRMADO"
    elif not garantia.startswith("PAGARÉ FIRMADO"):
        garantia = f"PAGARÉ FIRMADO + {garantia}"
    
    

    if not aval_nombre or not aval_dni:
        aval_nombre = "__________________"
        aval_dni = "__________________"

    periodo = "mensual"

    con.close()

    carpeta = os.path.join(OUT_CONTRATOS_DIR, limpiar_nombre(nombre))
    os.makedirs(carpeta, exist_ok=True)

    ruta = os.path.join(carpeta, f"contrato_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf")

    pdf = PDFContrato("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, margin=15)

    pdf.set_font("Times", "", 12)
    lh = 5.3

    mes_es = MESES_ES[fecha.strftime("%m")]

    intro = (
        f"En la ciudad de {lugar}, departamento de {depto}, República de Honduras, a los {fecha.day} días "
        f"del mes de {mes_es} del año {fecha.year}, comparecen: {EMPRESA}, debidamente "
        f"representado por el Sr. {REPRESENTANTE} (en adelante, \"EL ACREEDOR\"); y {nombre}, con identidad "
        f"{dni}, domiciliado(a) en {direccion if direccion else 'NO ESPECIFICADO'} (en adelante, \"EL DEUDOR\"). Ambas partes, con "
        f"plena capacidad para contratar y obligarse, convienen celebrar el presente Contrato de Crédito Personal, "
        f"que se regirá por las siguientes cláusulas:"
    )

    pdf.multi_cell(0, lh, intro, align="J")
    pdf.ln(2)

    periodo_txt = "mensual"
    periodo_plural = "mensuales"

    def clausula(titulo, texto):
        pdf.set_font("Times", "B", 12)
        pdf.cell(0, lh, titulo, ln=1)
        pdf.set_font("Times", "", 12)
        pdf.multi_cell(0, lh, texto, align="J")
        pdf.ln(2)

    clausula( "PRIMERA: OBJETO",
        f"EL ACREEDOR concede a EL DEUDOR un crédito personal por {_fmt_money(monto)}, destinado a fines "
        f"personales del DEUDOR, bajo las condiciones pactadas en este instrumento.")
    clausula(
    "SEGUNDA: PLAZO Y FORMA DE PAGO",
    f"El plazo total será de {n_cuotas} "
    f"{'cuotas' if n_cuotas != 1 else 'cuota'} {periodo_plural}, a partir del {fecha_inicio}. "
    "Cada cuota comprende capital e intereses ordinarios y deberá cancelarse en las oficinas del ACREEDOR "
    "o mediante depósito/transferencia a la cuenta que éste indique, a más tardar en la fecha de vencimiento."
)

    clausula(
    "TERCERA: INTERESES",
    f"El crédito devengará interés ordinario {periodo_txt} del {tasa:.2f}% sobre el saldo pendiente. "
    "En caso de mora, EL DEUDOR pagará interés moratorio del 3.00% mensual adicional sobre las sumas "
    "vencidas, calculado desde el día siguiente al vencimiento y hasta su íntegro pago."
)

    clausula( "CUARTA: GASTOS Y CARGOS",
        "Todos los impuestos, comisiones bancarias y gastos razonables de cobranza o recuperación generados "
        "por este crédito serán por cuenta del DEUDOR.")
    
    clausula("QUINTA: GARANTÍAS Y AVAL",
    f"Para asegurar el cumplimiento de las obligaciones derivadas del presente contrato, EL DEUDOR otorga como garantía: {garantia}. "
    f"Asimismo, comparece como AVAL el señor {aval_nombre}, con identidad {aval_dni}, quien se constituye en FIADOR SOLIDARIO, "
    f"RENUNCIANDO expresamente a los beneficios de excusión, división y orden, obligándose en los mismos términos que el deudor principal. "
    f"El aval responderá conjunta y solidariamente por el total de la deuda, intereses, gastos, costas y cualquier obligación derivada del presente contrato."
)
    # 🔥 FIRMAS CLIENTE Y AVAL (IGUAL QUE PAGARÉ)
    pdf.ln(8)

    pdf.set_font("Times", "", 10)

    # 🔹 líneas
    pdf.cell(90, 5, "__________________________________", align="C")
    pdf.cell(90, 5, "__________________________________", ln=1, align="C")

    # 🔹 nombres
    pdf.cell(90, 5, nombre, align="C")
    pdf.cell(90, 5, aval_nombre, ln=1, align="C")

    # 🔹 roles
    pdf.cell(90, 5, "DEUDOR", align="C")
    pdf.cell(90, 5, "FIADOR SOLIDARIO", ln=1, align="C")


    # 🔥 ESPACIO CONTROLADO
    pdf.ln(10)


    # 🔥 FIRMA EMPRESA CENTRADA (IGUAL QUE PAGARÉ)
    pdf.ln(6)

    y_firma = pdf.get_y()

    pdf.cell(0, 5, "__________________________________", ln=1, align="C")
    pdf.cell(0, 5, REPRESENTANTE, ln=1, align="C")
    pdf.cell(0, 5, "REPRESENTANTE LEGAL", ln=1, align="C")
    pdf.cell(0, 5, EMPRESA, ln=1, align="C")


    # 🔥 SELLO A LA PAR (NO ENCIMA)
    try:
        pdf.image(
            "assets/sello.png",
            x=130,          # mueve izquierda/derecha
            y=y_firma - 10, # sube/baja alineado con línea
            w=45            # tamaño del sello
        )
    except:
        pass

    pdf.output(ruta)
    return ruta