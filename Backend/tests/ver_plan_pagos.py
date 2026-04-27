import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import obtener_conexion

con = obtener_conexion()
cur = con.cursor()

cur.execute("""
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'plan_pagos'
""")

for col in cur.fetchall():
    print(col[0])

con.close()