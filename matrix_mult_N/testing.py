import main # type: ignore
import mathfs # type: ignore

import numpy as np
from scipy.stats import ortho_group
from scipy.stats import unitary_group

import interferometer as itf
import time
from scipy.linalg import svd
import sys
from lumapi_loader import lumapi
if lumapi is None:
    sys.exit("No se pudo cargar lumapi.")

from main import neural_network_layer

# dim=4
# u = unitary_group.rvs(dim)

start_time = time.time()

# path, create_circuit = main.create_matrix_icp(dim)
# print(path)
ic = lumapi.INTERCONNECT(hide=False)


a1=np.random.rand(8,6)
a2=np.random.rand(3,8)
v=abs(mathfs.random_vector(np.shape(a1)[1],normalize="unit"))
# U,S,Vh=svd(a)
# v_T=main.theoretical_mzi_mult(Vh,v)
# neural_network_layer(a,0,ic)
# main.general_MZI_multiplication(a,v,ic=ic,graph=False)
m=[a1,a2]
main.optical_neural_network(v,m,ic)
end_time = time.time()
# print(f"Elapsed time: {end_time - start_time:.6f} seconds")

# print("Int T", mathfs.complex_to_polar(v_T,square_modulus=True))


# main.general_mzi_mesh(a,0,ic,)