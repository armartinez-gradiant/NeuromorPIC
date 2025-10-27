# matrix_mult_N/testing.py - VERSIÓN DE PRUEBA SIMPLIFICADA

from . import main
from . import mathfs

import numpy as np
from scipy.stats import unitary_group
import time
import sys

sys.path.append(r"C:\Program Files\Lumerical\v251\api\python")
import lumapi

start_time = time.time()

ic = lumapi.INTERCONNECT(hide=False)

# PRUEBA SIMPLE: matriz unitaria 4x4
dim = 4
u = unitary_group.rvs(dim)
v = mathfs.random_vector(dim, normalize="unit")

print(f"Probando con matriz unitaria {dim}x{dim}")
print(f"Matriz es unitaria: {main.is_unitary(u)}")

result = main.MZI_multiplication(u, v, ic=ic, create_circuit=True, graph=False)

end_time = time.time()
print(f"Tiempo transcurrido: {end_time - start_time:.2f}s")
print(f"Resultado: {result}")