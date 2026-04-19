from datetime import datetime
import os
from reports.base_pdf import PDFBase
from reports.utils_pdf import _fmt_money, limpiar_nombre
from db.connection import obtener_conexion

OUT_CONTRATOS_DIR = "docs/contratos"
os.makedirs(OUT_CONTRATOS_DIR, exist_ok=True)

EMPRESA = "CREDIS SERVICIOS ORTIZ"
REPRESENTANTE = "WALTHER ORTIZ"


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


def generar_contrato_pdf(cliente_id, plan_id=None,
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

    garantia_db = None
    try:
        con2 = _cx()
        cur2 = con2.cursor()
        cur2.execute("SELECT garantia FROM clientes WHERE id=%s", (cliente_id,))
        rowg = cur2.fetchone()
        con2.close()
        if rowg:
            garantia_db = rowg[0]
    except:
        pass

    garantia = garantia or garantia_db or "PAGARÉ FIRMADO"

    if plan_id is not None:
        cur.execute("""
            SELECT monto, tasa_interes, plazo_numero, fecha_inicio
            FROM creditos
            WHERE id = %s
        """, (plan_id,))

        row = cur.fetchone()

        if not row:
            con.close()
            raise RuntimeError("Plan no encontrado.")

        monto = float(row[0] or 0.0)
        tasa = float(row[1] or 0.0)
        n_cuotas = int(row[2] or 0)
        fecha_inicio = row[3]
        periodo = "mensual"
    else:
        monto = 0.0
        tasa = 0.0
        n_cuotas = 0
        fecha_inicio = fecha.strftime("%Y-%m-%d")
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

    intro = (
        f"En la ciudad de {lugar}, departamento de {depto}, República de Honduras, a los {fecha.day} días "
        f"del mes de {fecha.strftime('%B').upper()} del año {fecha.year}, comparecen: {EMPRESA}, debidamente "
        f"representado por el Sr. {REPRESENTANTE} (en adelante, \"EL ACREEDOR\"); y {nombre}, con identidad "
        f"{dni}, domiciliado(a) en {direccion or '__________'} (en adelante, \"EL DEUDOR\"). Ambas partes, con "
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
    clausula("QUINTA: GARANTÍAS",
        f"Para asegurar el cumplimiento de las obligaciones, EL DEUDOR otorga como garantía: {garantia}. "
        "De existir aval, éste se constituye en fiador solidario y principal pagador. En caso de "
        "incumplimiento, EL ACREEDOR podrá hacer efectiva la garantía y exigir el pago total adeudado.")
    
    pdf.ln(10)

    pdf.cell(90, 6, "__________________________", align="C")
    pdf.cell(90, 6, "__________________________", ln=1, align="C")

    pdf.cell(90, 6, nombre, align="C")
    pdf.cell(90, 6, "Aval", ln=1, align="C")

    pdf.ln(10)

    pdf.cell(0, 6, "__________________________", ln=1, align="C")
    pdf.cell(0, 6, REPRESENTANTE, ln=1, align="C")

    pdf.output(ruta)
    return ruta