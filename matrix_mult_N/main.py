"""
Módulo principal para multiplicación matricial óptica
Punto de entrada simplificado que importa de submódulos
VERSIÓN CORREGIDA - Power meters ahora se conectan correctamente
"""

import numpy as np
import os
from pathlib import Path
from typing import Optional, Tuple, Union
import sys

# Añadir ruta de Lumerical al path (solo cuando se necesite)
try:
    from lumerical_path_detector import auto_detect_and_load_lumapi
    lumapi = auto_detect_and_load_lumapi()
except ImportError:
    # Si no se puede cargar, usar detección manual
    sys.path.append(r"C:\Program Files\Lumerical\v251\api\python")
    try:
        import lumapi
    except ImportError:
        lumapi = None  # Se cargará cuando sea necesario

# ===== CORRECCIÓN: Usar importaciones relativas =====
from .matrix_operations import (
    theoretical_mzi_mult,
    decompose_matrix_svd,
    is_unitary,
    validate_matrix_vector,
    compute_theoretical_result
)

from .mzi_generator import (
    generate_mzi,
    mzi_diagonal,
    generate_amplifiers,
    generate_non_linearities
)

from .circuit_builder import (
    mzi_mesh,
    general_mzi_mesh,
    neural_network_layer,
    optical_neural_network,
    generate_lasers,
    redefine_lasers,
    generate_power_meters,
    get_results,
    redefine_mesh,
    connect_inputs_to_mesh,
    connect_mesh_to_output,
    create_and_connect_power_meters  # ← NUEVO: Función integrada para power meters
)

from . import mathfs  # ← CORRECCIÓN: importación relativa


def create_matrix_icp(
    m: int,
    n: Optional[int] = None,
    folder: Union[str, os.PathLike] = ".",
    ic=None,
    hide: bool = True,
) -> Tuple[str, bool]:
    """
    Asegura que existe un archivo INTERCONNECT llamado matrix{m}x{n}.icp
    Si no existe, lo crea guardando el proyecto actual (vacío).

    Args:
        m (int): número de filas (o 'n' si quieres matriz cuadrada n×n).
        n (Optional[int]): número de columnas. Si None, por defecto = m (cuadrada).
        folder (str | PathLike): carpeta destino (por defecto ".").
        ic: handle opcional de Lumerical INTERCONNECT para reusar. Si None, se
            crea una sesión temporal y se cierra.
        hide (bool): si ocultar la GUI de INTERCONNECT al crear sesión.

    Returns:
        Tuple[str, bool]: (ruta_absoluta_al_icp, flag_creado)
            - flag_creado es True si el archivo se creó ahora, False si ya existía.

    Raises:
        ValueError: si m/n no son enteros positivos.
    """
    if m <= 0:
        raise ValueError(f"m debe ser positivo, recibido: {m}")
    if n is None:
        n = m
    if n <= 0:
        raise ValueError(f"n debe ser positivo, recibido: {n}")

    folder = Path(folder).resolve()
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"matrix{m}x{n}.icp"
    path = str(folder / filename)

    # Si ya existe, no hacer nada
    if os.path.isfile(path):
        return path, False

    # Si no existe, crear sesión y guardar
    owns_session = ic is None
    if owns_session:
        ic = lumapi.INTERCONNECT(hide=hide)

    try:
        # INTERCONNECT nuevo abre con proyecto en blanco; solo guardarlo
        ic.save(path)
    finally:
        if owns_session:
            ic.close()

    return path, True


def MZI_multiplication(u, v, ic, create_circuit=True, graph=False):
    """
    Multiplica vector v por matriz unitaria u usando MZI mesh
    
    CORRECCIÓN: Los power meters se crean como pm0, pm1, etc. (sin sufijo de capa)
    y se conectan correctamente usando connect_mesh_to_output()
    
    Args:
        u: Matriz unitaria
        v: Vector de entrada
        ic: Handle de INTERCONNECT
        create_circuit: Si crear el circuito o solo redefinir
        graph: Si visualizar descomposición
    
    Returns:
        np.ndarray: Vector resultado de la multiplicación
    """
    dim = np.shape(u)[0]
    v_theoretical = u @ v
    k = 0
  
    if create_circuit:
        # 1. Generar láseres de entrada
        generate_lasers(v ** 2, np.angle(v), ic)
        
        # 2. Generar el mesh MZI
        mzi_mesh(u, ic=ic, k=k, xpos=100, graph=graph)
        
        # 3. Conectar láseres al mesh
        connect_inputs_to_mesh(dim, ic, k=0, input="CW")
        
        # 4. Redefinir parámetros del mesh
        redefine_mesh(u, 0, ic)
        
        # 5 y 6. ✅ NUEVO: Crear Y conectar power meters con posicionamiento correcto
        # Esta función reemplaza:
        #   - generate_power_meters(dim, ic, 0)
        #   - connect_mesh_to_output(k=0, ic=ic, dimV=dim, dimS=dim, output="pm")
        # Ahora crea cada power meter en la posición correcta (a la derecha de su salida)
        create_and_connect_power_meters(dim, k=0, ic=ic)
    else:
        redefine_lasers(v ** 2, np.angle(v), ic)
        redefine_mesh(u, 0, ic)

    ic.run()
    v_mesh = get_results(dim, 0, ic)
    ic.switchtodesign()
    ic.save()
    
    v_res_sq = mathfs.complex_to_polar(v_theoretical ** 2)
    print("Theory", v_res_sq, "\n", "Mesh", v_mesh)
    
    return v_mesh


def diagsvg(S, dimU, dimV):
    """
    Crea matriz diagonal a partir de valores singulares
    
    Args:
        S: Array de valores singulares
        dimU, dimV: Dimensiones de la matriz diagonal
    
    Returns:
        np.ndarray: Matriz diagonal dimU x dimV
    """
    diagonal_matrix = np.zeros((dimU, dimV))
    min_dim = min(dimU, dimV, len(S))
    for i in range(min_dim):
        diagonal_matrix[i, i] = S[i]
    return diagonal_matrix


def general_MZI_multiplication(u, v, ic, graph=False):
    """
    Multiplica vector v por matriz u (unitaria o no) usando SVD si es necesario
    
    Args:
        u: Matriz (puede ser no unitaria)
        v: Vector de entrada
        ic: Handle de INTERCONNECT
        graph: Si visualizar descomposición
    
    Returns:
        np.ndarray: Vector resultado de la multiplicación
    """
    from scipy.linalg import svd
    
    create_circuit = True
    dimU, dimV = np.shape(u)
    v_theoretical = u @ v
    U, S, Vh = svd(u)
    
    vth1 = Vh @ v
    vth2 = diagsvg(S, dimU, dimV) @ vth1
    vth3 = U @ vth2

    k = 0
    if create_circuit:
        generate_lasers(v ** 2, np.angle(v), ic)
        general_mzi_mesh(u, k, ic=ic, xpos=100)
        
        connect_inputs_to_mesh(dimV, ic, k=0, input="CW")

        redefine_mesh(Vh, 0, ic)
        redefine_mesh(U, 2, ic)
        generate_power_meters(dimV, ic, 0)
        generate_power_meters(dimU, ic, 1, diagonal=True)
        generate_power_meters(dimU, ic, 2)
        
        # ← NOTA: En general_mzi_mesh ya se llama a connect_mesh_to_output internamente
        # para conectar los amps y los meshes, así que aquí no hace falta agregarlo
        # manualmente, pero si tienes problemas también podrías agregarlo aquí
    else:
        redefine_lasers(v ** 2, np.angle(v), ic)
        redefine_mesh(u, 0, ic)

    ic.run()
    v_mesh1 = get_results(dimV, 0, ic)
    v_mesh2 = get_results(dimU, 1, ic)
    v_mesh3 = get_results(dimU, 2, ic)
    
    v_res1 = mathfs.complex_to_polar(vth1, square_modulus=True)
    v_res2 = mathfs.complex_to_polar(v_theoretical, square_modulus=True)
    
    print(
        "Initial vector", v, "\n",
        "Theory", v_res2, "\n",
        "Mesh", v_mesh3, "\n",
        "Theory SVD", vth3 ** 2, "\n",
        "Diagonal SVD", vth2 ** 2, "\n",
        "Diagonal Mesh", v_mesh2, "\n",
        "Int theory", v_res1, "\n",
        "Int mesh", v_mesh1
    )
    
    return v_mesh3


# Re-exportar para mantener compatibilidad
__all__ = [
    'create_matrix_icp',
    'MZI_multiplication',
    'general_MZI_multiplication',
    'mzi_mesh',
    'general_mzi_mesh',
    'neural_network_layer',
    'optical_neural_network',
    'theoretical_mzi_mult',
]