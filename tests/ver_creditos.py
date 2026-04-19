import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import obtener_conexion

con = obtener_conexion()
cur = con.cursor()

cur.execute("SELECT id, cliente_id, monto FROM creditos")

for row in cur.fetchall():
    print(row)

con.close()