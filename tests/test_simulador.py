import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.simulador import simular_plan

plan = simular_plan(10000, 10, 12, "2026-04-01")

for cuota in plan:
    print(cuota)