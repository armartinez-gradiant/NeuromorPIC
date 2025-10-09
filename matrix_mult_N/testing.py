import main # type: ignore

import numpy as np
from scipy.stats import ortho_group
from scipy.stats import unitary_group

import interferometer as itf
import time

# Ya no necesitamos importar lumapi aquí porque main.py ya lo hace

dim=4
u = unitary_group.rvs(dim)
# u=np.identity(dim)
start_time = time.time()
# v=main.random_vector(dim,normalize="unit")
v=(1,2,-3,4)/np.sqrt(30)
# v=abs(main.random_vector(dim,normalize="unit"))
# main.mzi_mesh(u)
# main.generate_power_meters(dim)
main.MZI_multiplication(u,v,graph=True)
end_time = time.time()
print(f"Elapsed time: {end_time - start_time:.6f} seconds")