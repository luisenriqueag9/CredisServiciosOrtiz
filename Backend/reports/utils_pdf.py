def _fmt_money(x) -> str:
    try:
        return f"L. {float(x):,.2f}"
    except Exception:
        return str(x)

def limpiar_nombre(nombre):
    return nombre.replace(" ", "_").replace("á","a").replace("é","e").replace("í","i").replace("ó","o").replace("ú","u")

_MESES_ES = {
    "01":"enero","02":"febrero","03":"marzo","04":"abril","05":"mayo","06":"junio",
    "07":"julio","08":"agosto","09":"septiembre","10":"octubre","11":"noviembre","12":"diciembre"
}