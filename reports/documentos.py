# documentos.py (FPDF, con look & feel profesional en 1 hoja)
import os
from services.plan_service import generar_plan
from datetime import datetime
from fpdf import FPDF
from psycopg2.extras import RealDictCursor


try:
    from pagos import obtener_saldo_actual
except Exception:
    obtener_saldo_actual = None

# ===================== CONFIG DEL NEGOCIO =====================
EMPRESA               = "CREDIS SERVICIOS ORTIZ"
EMPRESA_REPRESENTANTE = "WALTHER ORTIZ"
EMPRESA_DIRECCION     = "Barrio El Centro, Calle Principal"
EMPRESA_CIUDAD        = "Pespire, Choluteca, Honduras"
EMPRESA_WHATSAPP      = "+504 9603-9778"
EMPRESA_CORREO        = "cso.contacto@gmail.com"
LOGO_PATH             = "assets/logo.png"   # pon tu logo aquí (fondo transparente recomendado)

OUT_RECIBOS_DIR   = "docs/recibos"
OUT_PLANES_DIR    = "docs/planes"
OUT_CONTRATOS_DIR = "docs/contratos"
OUT_PAGARES_DIR   = "docs/pagares"
for _d in (OUT_RECIBOS_DIR, OUT_PLANES_DIR, OUT_CONTRATOS_DIR, OUT_PAGARES_DIR):
    os.makedirs(_d, exist_ok=True)

# ===================== CONEXIÓN =====================
from db.connection import obtener_conexion

def _cx():
    return obtener_conexion()

# ===================== UTILS =====================
def _fmt_money(x) -> str:
    try:
        return f"L. {float(x):,.2f}"
    except Exception:
        return str(x)

def limpiar_nombre(nombre):
    return nombre.replace(" ", "_").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")
def _obtener_datos_cliente(cliente_id: int):
    con = _cx()
    from psycopg2.extras import RealDictCursor
    cur = con.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT id, nombre, identidad, telefono, direccion
        FROM clientes
        WHERE id = %s
    """, (cliente_id,))

    row = cur.fetchone()
    con.close()
    return row
def _obtener_plan_basico(plan_id: int):
    con = _cx(); cur = con.cursor()
    cur.execute("""
        SELECT monto, tasa, periodo, cuotas, fecha_inicio, sistema
          FROM plan_pagos WHERE id=%s
    """, (plan_id,))
    p = cur.fetchone()
    if not p:
        con.close()
        return None
    monto, tasa, periodo, cuotas, fecha_inicio, sistema = p
    cur.execute("""
        SELECT cuota FROM plan_cuotas
         WHERE plan_id=%s ORDER BY num_cuota ASC LIMIT 1
    """, (plan_id,))
    r = cur.fetchone()
    cuota_prom = float(r[0]) if r else None
    con.close()
    return float(monto), float(tasa), (periodo or "mensual"), int(cuotas or 0), (fecha_inicio or ""), (sistema or ""), cuota_prom

# Meses en español (para fechas largas)
_MESES_ES = {
    "01":"enero","02":"febrero","03":"marzo","04":"abril","05":"mayo","06":"junio",
    "07":"julio","08":"agosto","09":"septiembre","10":"octubre","11":"noviembre","12":"diciembre"
}

# ===== Helper de firmas en 3 filas (sigue disponible por si lo quieres) =====
def _firmas_tres_filas(pdf, etiquetas_y_nombres):
    pdf.set_font("Times", "", 12)
    filas = len(etiquetas_y_nombres)
    alto_bloque = 12 * filas + 18
    rest = pdf.h - pdf.b_margin - pdf.get_y()
    if rest < alto_bloque:
        pdf.set_y(pdf.h - pdf.b_margin - alto_bloque)
    for etiqueta, nombre in etiquetas_y_nombres:
        pdf.ln(6)
        pdf.cell(0, 7, "_" * 80, ln=1, align="C")
        if nombre and "____" not in (nombre or ""):
            pdf.cell(0, 6, str(nombre), ln=1, align="C")
        pdf.set_font("Times", "", 10)
        pdf.cell(0, 5, etiqueta, ln=1, align="C")
        pdf.set_font("Times", "", 12)
        pdf.ln(2)

# ===== NUEVO Helper: 2 firmas arriba (lado a lado) + 1 firma abajo centrada =====
def _firmas_dos_arriba_una_abajo(pdf, prestatario, aval, representante):
    """
    Dos firmas arriba (izq: prestatario, der: aval) y una firma abajo centrada.
    Garantiza que todo el bloque quede en la misma hoja respetando márgenes.
    """
    alto_bloque = 62
    resto = pdf.h - pdf.b_margin - pdf.get_y()
    if resto < alto_bloque:
        pdf.set_y(pdf.h - pdf.b_margin - alto_bloque)

    pdf.set_font("Times", "", 12)

    x_izq = pdf.l_margin
    x_der = pdf.w - pdf.r_margin
    ancho = x_der - x_izq
    col_w = ancho / 2.0

    # Dos firmas superiores (línea)
    y0 = pdf.get_y() + 6
    pdf.set_xy(x_izq, y0);          pdf.cell(col_w, 7, "_" * 30, ln=0, align="C")
    pdf.set_xy(x_izq + col_w, y0);  pdf.cell(col_w, 7, "_" * 30, ln=1, align="C")

    # Nombres
    y1 = y0 + 7
    if prestatario and "____" not in prestatario:
        pdf.set_xy(x_izq, y1);          pdf.cell(col_w, 6, str(prestatario), ln=0, align="C")
    if aval and "____" not in aval:
        pdf.set_xy(x_izq + col_w, y1);  pdf.cell(col_w, 6, str(aval), ln=1, align="C")

    # Etiquetas
    pdf.set_font("Times", "", 10)
    y2 = y1 + 6
    pdf.set_xy(x_izq, y2);          pdf.cell(col_w, 5, "Firma y huella del Deudor/Prestatario", ln=0, align="C")
    pdf.set_xy(x_izq + col_w, y2);  pdf.cell(col_w, 5, "Firma del Aval", ln=1, align="C")

    # Firma inferior (representante) centrada
    pdf.set_font("Times", "", 12)
    y3 = y2 + 10
    pdf.set_xy(x_izq, y3);          pdf.cell(ancho, 7, "_" * 30, ln=1, align="C")
    if representante and "____" not in representante:
        pdf.cell(0, 6, str(representante), ln=1, align="C")
    pdf.set_font("Times", "", 10)
    pdf.cell(0, 5, f"Firma del Representante de {EMPRESA}", ln=1, align="C")
    pdf.ln(2)

# ===================== BASE PDF (encabezado/pie MUY PRO) =====================
class _PDFBase(FPDF):
    header_title = ""   # cada documento lo define
    # márgenes cómodos para 1 hoja
    L = 14; T = 18; R = 14; B = 16

    def header(self):
        self.set_margins(self.L, self.T, self.R)
        y0 = 8
        # Logo
        if os.path.exists(LOGO_PATH):
            try:
                self.image(LOGO_PATH, x=self.L, y=y0, w=22)
            except Exception:
                pass

        # Datos de empresa al lado derecho
        self.set_xy(self.L + 26, y0)
        self.set_font("Times", "B", 13)
        self.cell(0, 6, EMPRESA, ln=1)
        self.set_font("Times", "", 10)
        self.set_text_color(80, 80, 80)
        self.set_x(self.L + 26)
        self.cell(0, 5, EMPRESA_DIRECCION, ln=1)
        self.set_x(self.L + 26)
        self.cell(0, 5, EMPRESA_CIUDAD, ln=1)
        self.set_x(self.L + 26)
        self.cell(0, 5, f"WhatsApp: {EMPRESA_WHATSAPP}  ·  {EMPRESA_CORREO}", ln=1)
        self.set_text_color(0, 0, 0)

        # Separador
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.4)
        self.line(self.L, 30, self.w - self.R, 30)

        # Subtítulo centrado (si aplica)
        if self.header_title:
            self.set_y(32)
            self.set_font("Times", "B", 15)
            self.cell(0, 8, self.header_title, ln=1, align="C")
            self.ln(1)
        else:
            self.ln(2)

    def footer(self):
        # línea superior del pie
        self.set_y(-18)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.4)
        self.line(self.L, self.get_y(), self.w - self.R, self.get_y())

        self.set_y(-15)
        self.set_font("Times", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, f"WhatsApp: {EMPRESA_WHATSAPP} · {EMPRESA_CIUDAD}", align="L")
        self.cell(0, 5, f"Página {self.page_no()}/{{nb}}", align="R")
        self.set_text_color(0, 0, 0)

# =========================================================
# ===============  RECIBO DE PAGO (PDF)  =================
# =========================================================
def generar_recibo_pago(pago_id: int) -> str:
    con = _cx()
    cur = con.cursor()

    cur.execute("""
        SELECT p.id, p.fecha, p.total, p.capital, p.interes, p.cliente_id
          FROM pagos p
         WHERE p.id = %s
    """, (pago_id,))
    pago = cur.fetchone()
    if not pago:
        con.close()
        raise ValueError("Pago no encontrado")

    pid, fecha, total, capital, interes, cliente_id = pago
    cli = _obtener_datos_cliente(cliente_id)
    if not cli:
        con.close()
        raise ValueError("Cliente no encontrado")

    cid = cli["id"]
    nombre = cli["nombre"]
    telefono = cli["telefono"]
    direccion = cli["direccion"]
    dni = cli["identidad"]

    cur.execute("""
        SELECT pc.plan_id, pc.num_cuota
          FROM plan_cuotas pc
         WHERE pc.pago_id = %s
    """, (pid,))
    vinc = cur.fetchone()
    plan_id, num_cuota = (vinc[0], vinc[1]) if vinc else (None, None)

    saldo_despues = None
    saldo_antes = None
    if obtener_saldo_actual is not None:
        try:
            saldo_despues = float(obtener_saldo_actual(cliente_id) or 0.0)
            saldo_antes = saldo_despues + float(capital or 0.0)
        except Exception:
            pass

    con.close()

    ruta = os.path.join(OUT_RECIBOS_DIR, f"recibo_{pid}.pdf")

    class PDFRecibo(_PDFBase):
        header_title = "RECIBO DE PAGO"

    pdf = PDFRecibo("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, margin=pdf.B)

    # Datos del cliente
    pdf.set_font("Times", "", 11)
    pdf.cell(0, 6, f"Cliente: {nombre} (ID {cid})", ln=1)
    pdf.cell(0, 6, f"DNI: {dni}    Tel: {telefono or '-'}", ln=1)
    pdf.multi_cell(0, 6, f"Dirección: {direccion or '-'}")
    if correo:
        pdf.cell(0, 6, f"Correo: {correo}", ln=1)
    if plan_id is not None and num_cuota is not None:
        pdf.cell(0, 6, f"Plan ID: {plan_id}  |  Cuota #: {num_cuota}", ln=1)
    pdf.ln(2)

    # Datos del pago
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 7, f"Recibo No.: {pid}    Fecha: {fecha}", ln=1)
    pdf.set_font("Times", "", 11)
    pdf.cell(0, 6, f"Capital: {_fmt_money(capital)}", ln=1)
    pdf.cell(0, 6, f"Interés: {_fmt_money(interes)}", ln=1)
    pdf.set_font("Times", "B", 12)
    pdf.cell(0, 8, f"TOTAL PAGADO: {_fmt_money(total)}", ln=1)
    pdf.ln(2)

    # Saldos (si tenemos)
    if (saldo_antes is not None) and (saldo_despues is not None):
        pdf.set_font("Times", "", 11)
        pdf.cell(0, 6, f"Saldo antes del pago:  {_fmt_money(saldo_antes)}", ln=1)
        pdf.cell(0, 6, f"Saldo después del pago: {_fmt_money(saldo_despues)}", ln=1)
        pdf.ln(2)

    # Nota y firma
    pdf.set_font("Times", "", 10)
    pdf.multi_cell(0, 5, "Gracias por su pago. Este documento puede usarse como comprobante oficial.")
    pdf.ln(12)
    pdf.cell(0, 6, "Firma y sello ________________________________", ln=1)

    pdf.output(ruta)
    return ruta

# =========================================================
# ===============  PLAN DE PAGOS (PDF)  ==================
# =========================================================
def generar_plan_pagos_pdf(plan_id: int) -> str:
    con = _cx()
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
            cr.fecha_inicio,
            cr.estado
        FROM plan_pagos p
        JOIN creditos cr ON cr.id = p.credito_id
        JOIN clientes c ON c.id = cr.cliente_id
        WHERE p.id = %s
    """, (plan_id,))

    hd = cur.fetchone()
    if not hd:
        con.close()
        raise RuntimeError("No existe el plan indicado.")

    (pid, cliente_id, nombre, dni, tel,
     monto, tasa, periodo, cuotas, fecha_inicio, estado) = hd

    # 🔥 GENERAR PLAN CON TU MOTOR
    plan_generado = generar_plan(
        monto=float(monto),
        tasa=float(tasa),
        cuotas=int(cuotas),
        fecha_inicio=datetime.now()
    )

    cuotas_rows = []

    for cuota in plan_generado:
        cuotas_rows.append((
            cuota["numero_cuota"],
            cuota["fecha_pago"].strftime("%d-%m-%Y"),
            cuota["capital"],
            cuota["interes"],
            cuota["cuota"],
            cuota["saldo"],
            "PENDIENTE"
        ))

    con.close()

    # 📁 Carpeta por cliente
    nombre_archivo = limpiar_nombre(nombre)
    carpeta_cliente = os.path.join(OUT_PLANES_DIR, nombre_archivo)
    os.makedirs(carpeta_cliente, exist_ok=True)

    ruta = os.path.join(
        carpeta_cliente,
        f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    class PDFPlan(_PDFBase):
        header_title = "PLAN DE PAGOS"

    pdf = PDFPlan("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, margin=pdf.B)

    # Encabezado
    pdf.set_font("Times", "", 11)
    pdf.cell(0, 6, f"Plan ID: {pid}", ln=1)
    pdf.cell(0, 6, f"Cliente: {nombre} (ID {cliente_id})", ln=1)
    pdf.cell(0, 6, f"DNI: {dni}   Tel: {tel or '-'}", ln=1)
    pdf.cell(0, 6, f"Modalidad: {periodo}   Inicio: {fecha_inicio}", ln=1)
    pdf.cell(0, 6, f"Monto: {_fmt_money(monto)}   Tasa: {float(tasa):.4f}%   Cuotas: {cuotas}", ln=1)
    pdf.ln(3)

    # Tabla
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Times", "B", 10)
    headers = ["#", "Vence", "Capital", "Interés", "Cuota", "Saldo", "Pag."]
    widths = [10, 25, 28, 28, 28, 28, 12]

    for h, w in zip(headers, widths):
        pdf.cell(w, 8, h, border=1, align="C", fill=True)
    pdf.ln()

    pdf.set_font("Times", "", 10)

    tot_cap = tot_int = tot_cuo = 0.0

    for (num, fecha, cap, inte, cuo, saldo, pag) in cuotas_rows:
        tot_cap += float(cap)
        tot_int += float(inte)
        tot_cuo += float(cuo)

        vals = [
            str(num),
            fecha,
            f"{float(cap):,.2f}",
            f"{float(inte):,.2f}",
            f"{float(cuo):,.2f}",
            f"{float(saldo):,.2f}",
            "Sí" if pag else "No"
        ]

        aligns = ["C", "C", "R", "R", "R", "R", "C"]

        for v, w, a in zip(vals, widths, aligns):
            pdf.cell(w, 7, v, border=1, align=a)

        pdf.ln()

    # Totales
    pdf.set_font("Times", "B", 10)
    pdf.cell(widths[0] + widths[1], 8, "Totales", border=1, align="R")
    pdf.cell(widths[2], 8, f"{tot_cap:,.2f}", border=1, align="R")
    pdf.cell(widths[3], 8, f"{tot_int:,.2f}", border=1, align="R")
    pdf.cell(widths[4], 8, f"{tot_cuo:,.2f}", border=1, align="R")
    pdf.cell(widths[5] + widths[6], 8, "", border=1)
    pdf.ln(8)

    pdf.set_font("Times", "", 9)
    pdf.multi_cell(0, 5, "Plan de pagos generado automáticamente.")

    pdf.output(ruta)

    return ruta

# =========================================================
# ==================  PAGARÉ (PDF)  ======================
# =========================================================
def generar_pagare_pdf(cliente_id: int, plan_id: int | None = None,
                       lugar: str = "PESPIRE", depto: str = "CHOLUTECA",
                       fecha: datetime | None = None) -> str:
    """
    Pagaré en Times 12 con logo/datos, 1 hoja: se reservan y ajustan espacios para que
    el bloque de firmas quede en la misma página.
    """
    fecha = fecha or datetime.now()

    con = _cx(); cur = con.cursor()
    cli = _obtener_datos_cliente(cliente_id)
    if not cli:
        con.close()
        raise RuntimeError("Cliente no encontrado.")
    cid = cli["id"]
    nombre = cli["nombre"]
    telefono = cli["telefono"]
    direccion = cli["direccion"]
    dni = cli["identidad"]

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

    nombre_archivo = limpiar_nombre(nombre)
    carpeta_cliente = os.path.join(OUT_PAGARES_DIR, nombre_archivo)
    os.makedirs(carpeta_cliente, exist_ok=True)

    ruta = os.path.join(carpeta_cliente, f"pagare_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf")

    class PDFPagare(_PDFBase):
        header_title = "PAGARÉ"

    pdf = PDFPagare("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, margin=pdf.B)

    # Título grande con monto
    pdf.set_font("Times", "B", 15)
    pdf.cell(0, 8, f"PAGARÉ POR {_fmt_money(monto)}", ln=1, align="C")
    pdf.ln(1)

    # Cuerpo compacto
    pdf.set_font("Times", "", 12)
    line_h = 5.1
    representante = EMPRESA_REPRESENTANTE
    mes_es = _MESES_ES.get(fecha.strftime("%m"), fecha.strftime("%B")).upper()

    texto = (
         f"Yo, {nombre}, mayor de edad, con número de identidad {dni}, con domicilio en "
        f"{direccion or '__________'}, declaro que DEBO Y PAGARÉ INCONDICIONALMENTE a {EMPRESA}, "
        f"representado por el Sr. {representante}, la cantidad de {_fmt_money(monto)}, en la ciudad de "
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
    pdf.multi_cell(0, line_h, texto, align="J")

    # Firmas: dos arriba (prestatario/aval) y una abajo (representante)
    _firmas_dos_arriba_una_abajo(
        pdf,
        prestatario=nombre,
        aval="__________________________",
        representante=EMPRESA_REPRESENTANTE,
    )

    pdf.output(ruta)
    return ruta

# =========================================================
# =============  CONTRATO DE CRÉDITO (PDF)  ==============
# =========================================================
def generar_contrato_credito(cliente_id: int, plan_id: int | None = None,
                             garantia: str = "PAGARÉ FIRMADO",
                             lugar: str = "PESPIRE", depto: str = "CHOLUTECA",
                             fecha: datetime | None = None) -> str:
    """
    Contrato en Times 12 con logo/datos y firmas en una hoja (si el texto lo permite).
    """
    fecha = fecha or datetime.now()

    con = _cx(); cur = con.cursor()
    cli = _obtener_datos_cliente(cliente_id)
    if not cli:
        con.close(); raise RuntimeError("Cliente no encontrado.")
    cid = cli["id"]
    nombre = cli["nombre"]
    telefono = cli["telefono"]
    direccion = cli["direccion"]
    dni = cli["identidad"]

    # Leer garantía del cliente si existe la columna y no se pasó por parámetro
    garantia_db = None
    try:
        con2 = _cx(); cur2 = con2.cursor()
        cur2.execute("SELECT garantia FROM clientes WHERE id=%s", (cliente_id,))
        rowg = cur2.fetchone()
        con2.close()
        if rowg:
            garantia_db = rowg[0]
    except Exception:
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

    nombre_archivo = limpiar_nombre(nombre)
    carpeta_cliente = os.path.join(OUT_CONTRATOS_DIR, nombre_archivo)
    os.makedirs(carpeta_cliente, exist_ok=True)

    ruta = os.path.join(carpeta_cliente, f"contrato_{fecha.strftime('%Y%m%d_%H%M%S')}.pdf")

    class PDFContrato(_PDFBase):
        header_title = "CONTRATO DE CRÉDITO"

    pdf = PDFContrato("P", "mm", "Letter")
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(False, margin=pdf.B)

    # Intro
    pdf.set_font("Times", "", 12)
    lh = 5.3
    representante = EMPRESA_REPRESENTANTE

    intro = (
        f"En la ciudad de {lugar}, departamento de {depto}, República de Honduras, a los {fecha.day} días "
        f"del mes de {fecha.strftime('%B').upper()} del año {fecha.year}, comparecen: {EMPRESA}, debidamente "
        f"representado por el Sr. {representante} (en adelante, \"EL ACREEDOR\"); y {nombre}, con identidad "
        f"{dni}, domiciliado(a) en {direccion or '__________'} (en adelante, \"EL DEUDOR\"). Ambas partes, con "
        f"plena capacidad para contratar y obligarse, convienen celebrar el presente Contrato de Crédito Personal, "
        f"que se regirá por las siguientes cláusulas:"
    )
    pdf.multi_cell(0, lh, intro, align="J")
    pdf.ln(1)

    # Normalizar el periodo para texto
    _per = (periodo or "mensual").strip().lower()
    periodo_txt = "mensual" if _per.startswith("mensu") else "semanal"
    periodo_plural = "mensuales" if periodo_txt == "mensual" else "semanales"


    # Cláusulas (con espacio extra entre ellas)
    def clausula(titulo, texto):
        pdf.set_font("Times", "B", 12); pdf.cell(0, lh, titulo, ln=1)
        pdf.set_font("Times", "", 12); pdf.multi_cell(0, lh, texto, align="J"); pdf.ln(2)

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
    

    # Firmas: dos arriba (prestatario/aval) y una abajo (representante)
    _firmas_dos_arriba_una_abajo(
        pdf,
        prestatario=nombre,
        aval="__________________________",
        representante=representante,
    )

    pdf.output(ruta)
    return ruta
