"""
Constructor de circuitos completos: meshes, conexiones y redes neuronales
VERSIÓN CORREGIDA - Octubre 2025
Corrección de nomenclatura de power meters: pm0, pm1, etc. (sin sufijo de capa)
"""

import numpy as np
from scipy.linalg import svd
import interferometer as itf
from matrix_mult_N.matrix_operations import bs_list_to_vectors, is_unitary
from matrix_mult_N.mzi_generator import (
    generate_mzi, mzi_diagonal, generate_amplifiers, 
    generate_non_linearities, laser, power_meter
)


def generate_lasers(powers, phases, ic, xpos=0, ypos=0):
    """
    Genera un array de láseres para entrada del circuito
    
    Args:
        powers: Array de potencias
        phases: Array de fases
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    dim = len(powers)
    for i in range(dim):
        laser(f"CW{i}", powers[i], phases[i], ic, xpos=xpos, ypos=ypos + i * 300)


def redefine_lasers(powers, phases, ic):
    """
    Redefine parámetros de láseres existentes
    
    Args:
        powers: Nuevas potencias
        phases: Nuevas fases
        ic: Handle de INTERCONNECT
    """
    dim = len(powers)
    for i in range(dim):
        ic.setnamed(f"CW{i}", "power", powers[i])
        ic.setnamed(f"CW{i}", "phase", phases[i])


def generate_power_meters(dim, ic, k=0, diagonal=False, xpos_offset=0):
    """
    Genera medidores de potencia en las salidas.
    
    Los nombres son 'pm{i}' (sin sufijo de capa) para simplicidad.
    
    Args:
        dim: Número de power meters a crear
        ic: Handle de INTERCONNECT
        k: Índice de capa (no se usa en el nombre para mantener consistencia)
        diagonal: Si es para mesh diagonal
        xpos_offset: Offset en posición x
    """
    for i in range(dim):
        name = f"pm{i}"  # Sin sufijo {k}
        power_meter(name, ic, xpos=xpos_offset, ypos=i * 300)


def retrieve_position(element, ic):
    """
    Obtiene la posición de un elemento en el layout
    
    Args:
        element: Nombre del elemento
        ic: Handle de INTERCONNECT
    
    Returns:
        tuple: (x, y) posición
    """
    return ic.getposition(element, "x"), ic.getposition(element, "y")


def get_results(dim, k, ic, mode=None):
    """
    Lee potencia de los Optical Power Meter (OPWM) en INTERCONNECT.

    - Si mode is None -> extrae la potencia TOTAL (OPWM: 'sum/power').
    - Si mode is int  -> extrae 'mode {mode}/power' (p.ej., mode=1 -> TE).
    - Tolera nombres 'pm{i}{k}' y 'pm{i}' para compatibilidad.
    - Convierte datasets (dict/array) en float.
    """
    import numpy as np

    def _first_float(x):
        # Convierte dict/array/escalares a float (primer valor)
        if isinstance(x, dict):
            # toma el primer valor numérico del dict
            for v in x.values():
                arr = np.array(v)
                if np.issubdtype(arr.dtype, np.number) and arr.size > 0:
                    return float(arr.ravel()[0])
            raise ValueError(f"Dataset sin valores numéricos: keys={list(x.keys())}")
        else:
            arr = np.array(x)
            return float(arr.ravel()[0])

    results = np.zeros(dim, dtype=float)

    # Nombre del resultado que queremos leer
    if mode is None:
        preferred = ["sum/power"]
        fallbacks = ["power", "optical power", "P"]
    else:
        preferred = [f"mode {mode}/power"]
        fallbacks = ["power", "optical power", "P"]

    for i in range(dim):
        # 1) Resolver nombre real del medidor (prioriza sin sufijo)
        pm_name = None
        for cand in (f"pm{i}", f"pm{i}{k}"):  # Primero sin sufijo, luego con sufijo
            try:
                _ = ic.getresult(cand)
                pm_name = cand
                break
            except Exception:
                continue
        
        if pm_name is None:
            raise RuntimeError(f"No existe power meter para i={i} (probados 'pm{i}' y 'pm{i}{k}').")

        # 2) Intentar claves preferidas y alternativas
        last_err = None
        value = None

        def try_key(key):
            try:
                data = ic.getresult(pm_name, key)
                return _first_float(data)
            except Exception as e:
                return e

        # a) preferidas
        for key in preferred:
            res = try_key(key)
            if not isinstance(res, Exception):
                value = res
                break
            last_err = res

        # b) alternativas
        if value is None:
            for key in fallbacks:
                res = try_key(key)
                if not isinstance(res, Exception):
                    value = res
                    break
                last_err = res

        if value is None:
            try:
                avail = ic.getresult(pm_name)
                avail_keys = list(avail.keys()) if hasattr(avail, "keys") else avail
            except Exception as e2:
                avail_keys = f"(no se pudo listar: {e2})"

            raise RuntimeError(
                f"No pude extraer {preferred[0]} de '{pm_name}'. "
                f"Alternativas probadas: {fallbacks}. "
                f"Último error: {last_err}. "
                f"Resultados disponibles: {avail_keys}"
            )

        results[i] = value

    return results


def redefine_mesh(u, k, ic):
    """
    Redefine los parámetros de un mesh existente
    VERSIÓN SIMPLIFICADA - Solo redefine thetas y phis, no deltas de salida
    
    Args:
        u: Nueva matriz unitaria
        k: Índice de capa
        ic: Handle de INTERCONNECT
    """
    I = itf.square_decomposition(u)
    thetas, phis, mode1, mode2 = bs_list_to_vectors(I.BS_list)
    
    dim = u.shape[0]
    L = dim - 2
    count = 0
    
    if L < 0:
        return

    for i in range(L + 1):
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        for j in range(j_max + 1):
            from matrix_mult_N.mzi_generator import redefine_MZI
            redefine_MZI(i, j_max - j if j > 0 else j, k, thetas[count], phis[count], ic=ic)
            count += 1


def mzi_mesh(u, ic, k, xpos=0, ypos=0, graph=False, testing=False):
    """
    Genera un MZI mesh completo para matriz unitaria
    
    Args:
        u: Matriz unitaria
        ic: Handle de INTERCONNECT
        k: Índice de capa
        xpos, ypos: Posición base
        graph: Si visualizar con interferometer
        testing: Modo de prueba
    """
    I = itf.square_decomposition(u)
    deltas = I.output_phases
    thetas, phis, mode1, mode2 = bs_list_to_vectors(I.BS_list)

    if graph:
        I.draw()
        print(I.BS_list)

    dim = u.shape[0]
    l = 0
    L = dim - 2
    count = 0
    
    if L < 0:
        return

    # Generar MZIs
    for i in range(L + 1):
        j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)

        if i == dim / 2:
            l += 1
        if i > dim / 2:
            l += 2

        for j in range(j_max + 1):
            generate_mzi(thetas[count], phis[count], i, 
                        j, k, ic=ic, 
                        xpos=i * 1000 - j * 500 - l * 500 + xpos, 
                        ypos=j * 300 + l * 300 + ypos)
            count += 1

    # Conectar MZIs
    _connect_mesh_interior(dim, L, k, ic)


def _connect_mesh_interior(dim, L, k, ic):
    """
    Conecta los MZIs internos del mesh
    VERSIÓN COMPLETAMENTE CORREGIDA - Octubre 2025
    Soporta meshes PARES e IMPARES
    """
    if L < 0:
        return
    
    # MESHES PARES
    if dim % 2 == 0:
        for i in range(L + 1):  
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
            
            for j in range(j_max + 1):
                
                if i < (L+1)//2:
                    if j == 0:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"phi{i+1}{j}{k}", "input")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                    else:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                
                if i == (L+1)//2:
                    if j == 0:
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j}{k}", "input")
                    elif j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-1}{k}1", "input 2")
                
                if i > (L+1)//2 and i < L:
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                if i == L and j != 0:
                    ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
    
    # MESHES IMPARES
    else:
        for i in range(L + 1):  
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
            
            for j in range(j_max + 1):
                
                if i < (L+1)//2:
                    if j == 0:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"phi{i+1}{j}{k}", "input")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                    else:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                
                if i == (L+1)//2:
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                if i > (L+1)//2 and i < L:
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                if i == L and j != 0:
                    ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")


def connect_mesh_to_output(k, ic, dimV, dimS, output):
    """
    Conecta las salidas del mesh a componentes de salida
    
    CORRECCIÓN: Para power meters (output="pm"), NO se usa sufijo de capa
    
    Args:
        k: Índice de capa
        ic: Handle de INTERCONNECT
        dimV: Dimensión de la matriz V
        dimS: Dimensión del vector S
        output: Tipo de componente ("amp", "relu", "pm")
    """
    count = 0
    comp = f"otheta{(dimV - 1) // 2}0{k}1"
    
    # ✅ CORRECCIÓN: Para power meters, usar solo "pm{count}" sin sufijo {k}
    if output == "pm":
        target = f"{output}{count}"
    else:
        target = f"{output}{count}{k}"
    
    ic.connect(comp, "output", target, "input")
    count += 1

    if dimV % 2 == 1:
        comp = f"otheta{(dimV - 1) // 2}0{k}2"
        
        if output == "pm":
            target = f"{output}{count}"
        else:
            target = f"{output}{count}{k}"
        
        ic.connect(comp, "output", target, "input")
        count += 1

    for i in range(dimV // 2 - 1):
        if count < dimS:
            comp = f"otheta{(dimV - 1) // 2 + i + 1}0{k}1"
            
            if output == "pm":
                target = f"{output}{count}"
            else:
                target = f"{output}{count}{k}"
            
            ic.connect(comp, "output", target, "input")
            count += 1

        if count < dimS:
            comp = f"otheta{(dimV - 1) // 2 + i + 1}0{k}2"
            
            if output == "pm":
                target = f"{output}{count}"
            else:
                target = f"{output}{count}{k}"
            
            ic.connect(comp, "output", target, "input")
            count += 1

    # Último MZI
    if count < dimS:
        comp = f"otheta{dimV - 2}1{k}2"
        
        if output == "pm":
            target = f"{output}{count}"
        else:
            target = f"{output}{count}{k}"
        
        ic.connect(comp, "output", target, "input")


def create_and_connect_power_meters(dim, k, ic):
    """
    Crea power meters Y los conecta a las salidas del mesh con posicionamiento correcto
    
    NUEVA FUNCIÓN que reemplaza el flujo de:
      1. generate_power_meters()
      2. connect_mesh_to_output()
    
    Esta función hace ambas cosas: crea cada power meter en la posición correcta
    (a la derecha del elemento de salida) y lo conecta.
    
    Args:
        dim: Dimensión del mesh
        k: Índice de capa
        ic: Handle de INTERCONNECT
    """
    count = 0
    
    # Primer power meter
    comp = f"otheta{(dim - 1) // 2}0{k}1"
    x, y = retrieve_position(comp, ic)
    power_meter(f"pm{count}", ic, xpos=x + 100, ypos=y)
    ic.connect(comp, "output", f"pm{count}", "input")
    count += 1
    
    # Si dim es impar, añadir otro
    if dim % 2 == 1:
        comp = f"otheta{(dim - 1) // 2}0{k}2"
        x, y = retrieve_position(comp, ic)
        power_meter(f"pm{count}", ic, xpos=x + 100, ypos=y)
        ic.connect(comp, "output", f"pm{count}", "input")
        count += 1
    
    # Loop a través de los MZIs centrales
    for i in range(dim // 2 - 1):
        if count < dim:
            comp = f"otheta{(dim - 1) // 2 + i + 1}0{k}1"
            x, y = retrieve_position(comp, ic)
            power_meter(f"pm{count}", ic, xpos=x + 100, ypos=y)
            ic.connect(comp, "output", f"pm{count}", "input")
            count += 1
        
        if count < dim:
            comp = f"otheta{(dim - 1) // 2 + i + 1}0{k}2"
            x, y = retrieve_position(comp, ic)
            power_meter(f"pm{count}", ic, xpos=x + 100, ypos=y)
            ic.connect(comp, "output", f"pm{count}", "input")
            count += 1
    
    # Último MZI si hace falta
    if count < dim:
        comp = f"otheta{dim - 2}1{k}2"
        x, y = retrieve_position(comp, ic)
        power_meter(f"pm{count}", ic, xpos=x + 100, ypos=y)
        ic.connect(comp, "output", f"pm{count}", "input")


def connect_diagonal_to_mesh(k, ic, dimS):
    """
    Conecta mesh diagonal a mesh siguiente
    """
    j = 0
    count = 0
    
    for i in range(dimS // 2):
        ic.connect(f"phase{count}0{k}", "output", f"phi{i}{j}{k + 1}", "input")
        count += 1
        ic.connect(f"phase{count}0{k}", "output", f"coupler{i}{j}{k + 1}1", "input 2")
        count += 1
        j += 2

    if dimS % 2 == 1:
        ic.connect(f"phase{count}0{k}", "output", f"coupler{dimS // 2}{j - 1}{k + 1}1", "input 2")


def connect_inputs_to_mesh(dimU, ic, k=0, input="CW"):
    """
    Conecta entradas (láseres o capa anterior) al mesh
    """
    j = 0
    count = 0
    l = "" if input == "CW" else k - 1

    for i in range(dimU // 2):
        ic.connect(f"{input}{count}{l}", "output", f"phi{i}{j}{k}", "input")
        count += 1
        ic.connect(f"{input}{count}{l}", "output", f"coupler{i}{j}{k}1", "input 2")
        count += 1
        j += 2

    if dimU % 2 == 1:
        ic.connect(f"{input}{count}{l}", "output", f"coupler{dimU // 2}{j - 1}{k}1", "input 2")


def general_mzi_mesh(a, k, ic, xpos=0, ypos=0):
    """
    Genera mesh general que soporta matrices no unitarias (usando SVD)
    """
    if is_unitary(a):
        mzi_mesh(a, ic, k, xpos=xpos, ypos=ypos, graph=False)
    else:
        U, S, Vh = svd(a)
        
        dimU = np.shape(U)[0]
        dimS = np.shape(S)[0]
        dimVh = np.shape(Vh)[0]

        mzi_mesh(Vh, ic, k, xpos=xpos, ypos=ypos, graph=False)
        generate_amplifiers(S ** 2, k, ic, xpos=xpos + 300 + 1100 * dimVh // 2, ypos=0)
        mzi_diagonal(S, k + 1, ic, xpos=xpos + 500 + 1100 * dimVh // 2, ypos=0)

        for i in range(dimS):
            ic.connect(f"amp{i}{k}", "output", f"coupler{i}0{k + 1}1", "input 1")

        connect_mesh_to_output(k, ic, dimV=dimVh, dimS=dimS, output="amp")
        mzi_mesh(U, ic, k + 2, xpos=xpos + 700 + 1100 * dimVh // 2 + 600, ypos=ypos)
        connect_diagonal_to_mesh(k + 1, ic, dimS=dimS)


def neural_network_layer(a, k, ic, xpos=0, ypos=0):
    """
    Crea una capa de red neuronal (lineal + no lineal)
    """
    dims = np.shape(a)
    general_mzi_mesh(a, k, ic, xpos=xpos, ypos=ypos)
    mesh_pos = retrieve_position(f"otheta{dims[0] // 2}0{k + 2}1", ic)
    generate_non_linearities(dims[0], k + 2, ic, xpos=mesh_pos[0] + 200)
    connect_mesh_to_output(k + 2, ic, dimV=dims[0], dimS=dims[0], output="relu")


def optical_neural_network(v, m, ic, inference=False):
    """
    Construye una red neuronal óptica completa de múltiples capas
    """
    dim = [np.shape(m[i]) for i in range(len(m))]
    generate_lasers(v ** 2, np.angle(v), ic)
    neural_network_layer(m[0], k=0, ic=ic, xpos=300)
    connect_inputs_to_mesh(dim[0][1], ic, k=0, input="CW")

    for i in range(1, len(m)):
        x, y = retrieve_position(f"relu0{3 * i - 1}", ic)
        neural_network_layer(m[i], k=3 * i, ic=ic, xpos=x + 300)
        connect_inputs_to_mesh(dim[i][1], ic, k=3 * i, input="relu")