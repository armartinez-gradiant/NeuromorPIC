"""
Constructor de circuitos completos: meshes, conexiones y redes neuronales
VERSIÓN CORREGIDA - Octubre 2025
Corrección principal: _connect_mesh_interior ahora incluye implementación COMPLETA para meshes pares e impares
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

    Cambios:
    - Los nombres pasan a ser 'pm{i}' (sin sufijo de capa) para alinearse con el proyecto actual.
    - Si en tu flujo necesitas múltiples bancos por capa, puedes restaurar el sufijo,
      pero asegúrate de que lectura y creación coincidan.
    """
    for i in range(dim):
        name = f"pm{i}"  # <-- sin {k}, coincide con lo visto en INTERCONNECT (pm0, pm1, ...)
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
    - Tolera nombres 'pm{i}{k}' y 'pm{i}'.
    - Convierte datasets (dict/array) en float.

    Refs:
      - OPWM Results: 'sum/power', 'mode #/power' (docs oficiales).      [1]
      - getresult devuelve datasets (dict) en Python (API).               [2]
      - Uso de getresult/haveresult en INTERCONNECT (comando oficial).    [3]

    [1] citeturn6search24
    [2] citeturn6search26
    [3] citeturn6search17
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
        # Potencia total (OPWM)
        preferred = [ "sum/power" ]   # clave oficial para total
        fallbacks = [ "power", "optical power", "P" ]  # por si usas otros elementos/analyzers
    else:
        preferred = [ f"mode {mode}/power" ]  # p.ej. 'mode 1/power' (TE)
        fallbacks = [ "power", "optical power", "P" ]

    for i in range(dim):
        # 1) Resolver nombre real del medidor
        pm_name = None
        for cand in (f"pm{i}{k}", f"pm{i}"):
            try:
                _ = ic.getresult(cand)  # si no lanza, el objeto existe
                pm_name = cand
                break
            except Exception:
                continue
        if pm_name is None:
            raise RuntimeError(f"No existe power meter para i={i} (probados 'pm{i}{k}' y 'pm{i}').")

        # 2) Intentar claves preferidas y, si no, las alternativas
        last_err = None
        value = None

        # helper para probar una clave
        def try_key(key):
            try:
                data = ic.getresult(pm_name, key)
                return _first_float(data)
            except Exception as e:
                return e  # devolvemos la excepción para reportar si ninguna funciona

        # a) preferidas
        for key in preferred:
            res = try_key(key)
            if not isinstance(res, Exception):
                value = res
                break
            last_err = res

        # b) alternativas (solo si no encontramos preferidas)
        if value is None:
            for key in fallbacks:
                res = try_key(key)
                if not isinstance(res, Exception):
                    value = res
                    break
                last_err = res

        if value is None:
            # lista resultados disponibles para facilitar el debug
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
    
    Nota: Las fases de salida (deltas) se mantienen como fueron generadas originalmente
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
            
            # Simplemente redefinir theta y phi, sin tocar las deltas
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
    # Descomponer matriz con interferometer
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
            generate_mzi(thetas[count], phis[count], i, j, k, ic=ic, 
                        xpos=i * 1000 - j * 500 - l * 500 + xpos, 
                        ypos=j * 300 + l * 300 + ypos)
            count += 1

    # Conectar MZIs
    _connect_mesh_interior(dim, L, k, ic)


def _connect_mesh_interior(dim, L, k, ic):
    """
    Conecta los MZIs internos del mesh
    VERSIÓN COMPLETAMENTE CORREGIDA - Octubre 2025
    Implementación completa basada en Lumerical/mzi_mesh.py probado
    
    Soporta tanto meshes PARES (dim % 2 == 0) como IMPARES (dim % 2 == 1)
    
    Args:
        dim: Dimensión del mesh
        L: L = dim - 2
        k: Índice de capa (para nomenclatura con múltiples meshes)
        ic: Handle de INTERCONNECT
    """
    if L < 0:
        return
    
    # ==================== MESHES PARES (dim % 2 == 0) ====================
    if dim % 2 == 0:
        for i in range(L + 1):  
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
            
            for j in range(j_max + 1):
                
                # 1. Iteraciones ANTES de la central
                if i < (L+1)//2:
                    if j == 0:  # Fila superior
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"phi{i+1}{j}{k}", "input")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                    else:  # Elementos interiores
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                
                # 2. Iteración CENTRAL
                if i == (L+1)//2:
                    if j == 0:  # Primer elemento central
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j}{k}", "input")
                    elif j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-1}{k}1", "input 2")
                
                # 3. Después de la iteración central
                if i > (L+1)//2 and i < L:
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                # 4. Última iteración
                if i == L and j != 0:
                    ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
    
    # ==================== MESHES IMPARES (dim % 2 == 1) ====================
    else:
        for i in range(L + 1):  
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
            
            for j in range(j_max + 1):
                
                # 1. Iteraciones ANTES de la central
                if i < (L+1)//2:
                    if j == 0:  # Fila superior
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"phi{i+1}{j}{k}", "input")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                    else:  # Elementos interiores
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j+1}{k}", "input")
                
                # 2. Iteración CENTRAL (DIFERENTE a meshes pares)
                if i == (L+1)//2:
                    # NOTA: NO hay condición para j==0 en meshes impares (diferencia clave con pares)
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                # 3. Después de la iteración central
                if i > (L+1)//2 and i < L:
                    if j > 0 and j < j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"phi{i+1}{j-1}{k}", "input")
                    
                    if j == j_max:
                        ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")
                        ic.connect(f"otheta{i}{j}{k}2", "output", f"coupler{i+1}{j-2}{k}1", "input 2")
                
                # 4. Última iteración
                if i == L and j != 0:
                    ic.connect(f"otheta{i}{j}{k}1", "output", f"coupler{i}{j-1}{k}1", "input 2")


def connect_mesh_to_output(k, ic, dimV, dimS, output):
    """
    Conecta las salidas del mesh a componentes de salida
    
    Args:
        k: Índice de capa
        ic: Handle de INTERCONNECT
        dimV: Dimensión de la matriz V
        dimS: Dimensión del vector S
        output: Tipo de componente de salida ("amp", "relu", "pm")
    """
    count = 0
    comp = f"otheta{(dimV - 1) // 2}0{k}1"
    ic.connect(comp, "output", f"{output}{count}{k}", "input")
    count += 1

    if dimV % 2 == 1:
        comp = f"otheta{(dimV - 1) // 2}0{k}2"
        ic.connect(comp, "output", f"{output}{count}{k}", "input")
        count += 1

    for i in range(dimV // 2 - 1):
        if count < dimS:
            comp = f"otheta{(dimV - 1) // 2 + i + 1}0{k}1"
            ic.connect(comp, "output", f"{output}{count}{k}", "input")
            count += 1

        if count < dimS:
            comp = f"otheta{(dimV - 1) // 2 + i + 1}0{k}2"
            ic.connect(comp, "output", f"{output}{count}{k}", "input")
            count += 1

    # Último MZI
    if count < dimS:
        comp = f"otheta{dimV - 2}1{k}2"
        ic.connect(comp, "output", f"{output}{count}{k}", "input")


def connect_diagonal_to_mesh(k, ic, dimS):
    """
    Conecta mesh diagonal a mesh siguiente
    
    Args:
        k: Índice de capa
        ic: Handle de INTERCONNECT
        dimS: Dimensión
    """
    j = 0
    count = 0
    
    for i in range(dimS // 2):
        ic.connect(f"phase{count}0{k}", "output", f"phi{i}{j}{k + 1}", "input")
        count += 1
        ic.connect(f"phase{count}0{k}", "output", f"coupler{i}{j}{k + 1}1", "input 2")
        count += 1
        j += 2

    # Si dim es impar
    if dimS % 2 == 1:
        ic.connect(f"phase{count}0{k}", "output", f"coupler{dimS // 2}{j - 1}{k + 1}1", "input 2")


def connect_inputs_to_mesh(dimU, ic, k=0, input="CW"):
    """
    Conecta entradas (láseres o capa anterior) al mesh
    
    Args:
        dimU: Dimensión de entrada
        ic: Handle de INTERCONNECT
        k: Índice de capa
        input: Tipo de entrada ("CW" para láseres, "relu" para ReLU, etc.)
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

    # Si dim es impar
    if dimU % 2 == 1:
        ic.connect(f"{input}{count}{l}", "output", f"coupler{dimU // 2}{j - 1}{k}1", "input 2")


def general_mzi_mesh(a, k, ic, xpos=0, ypos=0):
    """
    Genera mesh general que soporta matrices no unitarias (usando SVD)
    
    Args:
        a: Matriz (puede ser no unitaria)
        k: Índice de capa
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    # Verificar si es unitaria
    if is_unitary(a):
        mzi_mesh(a, ic, k, xpos=xpos, ypos=ypos, graph=False)
    else:
        # Descomponer con SVD
        U, S, Vh = svd(a)
        
        dimU = np.shape(U)[0]
        dimS = np.shape(S)[0]
        dimVh = np.shape(Vh)[0]

        # Primer mesh con Vh
        mzi_mesh(Vh, ic, k, xpos=xpos, ypos=ypos, graph=False)
        
        # Diagonal (amplificadores + MZIs)
        generate_amplifiers(S ** 2, k, ic, xpos=xpos + 300 + 1100 * dimVh // 2, ypos=0)
        mzi_diagonal(S, k + 1, ic, xpos=xpos + 500 + 1100 * dimVh // 2, ypos=0)

        # Conectar amps a MZIs diagonales
        for i in range(dimS):
            ic.connect(f"amp{i}{k}", "output", f"coupler{i}0{k + 1}1", "input 1")

        connect_mesh_to_output(k, ic, dimV=dimVh, dimS=dimS, output="amp")

        # Segundo mesh con U
        mzi_mesh(U, ic, k + 2, xpos=xpos + 700 + 1100 * dimVh // 2 + 600, ypos=ypos)

        # Conectar diagonal a segundo mesh
        connect_diagonal_to_mesh(k + 1, ic, dimS=dimS)


def neural_network_layer(a, k, ic, xpos=0, ypos=0):
    """
    Crea una capa de red neuronal (lineal + no lineal)
    
    Args:
        a: Matriz de pesos de la capa
        k: Índice de capa
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    dims = np.shape(a)
    
    # Capa lineal (mesh)
    general_mzi_mesh(a, k, ic, xpos=xpos, ypos=ypos)
    
    # Obtener posición del último elemento
    mesh_pos = retrieve_position(f"otheta{dims[0] // 2}0{k + 2}1", ic)
    
    # Capa no lineal (ReLU)
    generate_non_linearities(dims[0], k + 2, ic, xpos=mesh_pos[0] + 200)

    # Conectar mesh a ReLUs
    connect_mesh_to_output(k + 2, ic, dimV=dims[0], dimS=dims[0], output="relu")


def optical_neural_network(v, m, ic, inference=False):
    """
    Construye una red neuronal óptica completa de múltiples capas
    
    Args:
        v: Vector de entrada
        m: Lista de matrices (pesos de cada capa)
        ic: Handle de INTERCONNECT
        inference: Modo de inferencia (para futuro)
    """
    dim = [np.shape(m[i]) for i in range(len(m))]
    
    # Generar láseres de entrada
    generate_lasers(v ** 2, np.angle(v), ic)

    # Primera capa
    neural_network_layer(m[0], k=0, ic=ic, xpos=300)
    connect_inputs_to_mesh(dim[0][1], ic, k=0, input="CW")

    # Capas siguientes
    for i in range(1, len(m)):
        x, y = retrieve_position(f"relu0{3 * i - 1}", ic)
        neural_network_layer(m[i], k=3 * i, ic=ic, xpos=x + 300)
        connect_inputs_to_mesh(dim[i][1], ic, k=3 * i, input="relu")