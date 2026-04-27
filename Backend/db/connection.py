import psycopg2

def obtener_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5433",
        dbname="credis_servicios_ortiz",
        user="postgres",
        password="ClaveNueva123"
    )