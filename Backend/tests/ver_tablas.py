import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import obtener_conexion

con = obtener_conexion()
cur = con.cursor()

cur.execute("""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
""")

tablas = cur.fetchall()

for t in tablas:
    print(t[0])

con.close()