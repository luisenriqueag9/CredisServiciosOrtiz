from fpdf import FPDF
import os

EMPRESA = "CREDIS SERVICIOS ORTIZ"
EMPRESA_DIRECCION = "Barrio El Centro, Calle Principal"
EMPRESA_CIUDAD = "Pespire, Choluteca, Honduras"
EMPRESA_WHATSAPP = "+504 9603-9778"
EMPRESA_CORREO = "cso.contacto@gmail.com"

LOGO_PATH = "assets/logo.png"


class PDFBase(FPDF):
    header_title = ""

    L = 14
    T = 18
    R = 14
    B = 16

    def header(self):
        self.set_margins(self.L, self.T, self.R)

        if os.path.exists(LOGO_PATH):
            try:
                self.image(LOGO_PATH, x=self.L, y=8, w=22)
            except:
                pass

        self.set_xy(self.L + 26, 8)
        self.set_font("Times", "B", 13)
        self.cell(0, 6, EMPRESA, ln=1)

        self.set_font("Times", "", 10)
        self.set_x(self.L + 26)
        self.cell(0, 5, EMPRESA_DIRECCION, ln=1)

        self.set_x(self.L + 26)
        self.cell(0, 5, EMPRESA_CIUDAD, ln=1)

        self.set_x(self.L + 26)
        self.cell(0, 5, f"WhatsApp: {EMPRESA_WHATSAPP} · {EMPRESA_CORREO}", ln=1)

        self.set_draw_color(200, 200, 200)
        self.line(self.L, 30, self.w - self.R, 30)

        if self.header_title:
            self.set_y(32)
            self.set_font("Times", "B", 15)
            self.cell(0, 8, self.header_title, ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Times", "", 9)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")