"""
API Principal
Capa intermedia entre GUI y Lumerical
Gestiona simulaciones y caché
"""

import numpy as np
import os
import sys
import json
from pathlib import Path

# Añadir paths necesarios
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Importar módulos del proyecto
from Lumerical import interface
import mathfs

# Importar el nuevo sistema de multiplicación matricial
from matrix_mult_N.main import (
    create_matrix_icp,
    general_MZI_multiplication,
    MZI_multiplication,
    general_mzi_mesh
)
from matrix_mult_N.circuit_builder import (
    generate_lasers,
    connect_inputs_to_mesh,
    redefine_mesh,
    generate_power_meters,
    get_results,
    optical_neural_network
)
from matrix_mult_N.matrix_operations import (
    validate_matrix_vector,
    compute_theoretical_result,
    is_unitary
)


class API:
    """Clase principal de la API"""
    
    def __init__(self):
        """Inicializar API"""
        self.platform = "sipho"  # Plataforma por defecto
        self.cache = {}
        self.cache_file = "API/simulation_cache.json"
        
    def set_platform(self, platform):
        """
        Establece la plataforma de fotónica
        
        Args:
            platform: 'sipho', 'sin', 'ant', etc.
        """
        valid_platforms = ['sipho', 'sin', 'ant']
        if platform.lower() not in valid_platforms:
            raise ValueError(f"Plataforma '{platform}' no válida. Opciones: {valid_platforms}")
        
        self.platform = platform.lower()
        print(f"✓ Plataforma establecida: {self.platform.upper()}")
    
    def load_cache(self):
        """Carga el caché de simulaciones anteriores"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"✓ Caché cargado: {len(self.cache)} entradas")
            except Exception as e:
                print(f"⚠ Error cargando caché: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self):
        """Guarda el caché de simulaciones"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠ Error guardando caché: {e}")
    
    def get_param_suggestions(self):
        """
        Retorna valores sugeridos de parámetros según plataforma
        
        Returns:
            dict: Diccionario con parámetros por defecto
        """
        defaults = {
            'sipho': {
                'min_v': 0,
                'max_v': 5,
                'interval_v': 0.5,
                'min_w': 400e-9,
                'max_w': 600e-9,
                'interval_w': 50e-9,
            },
            'sin': {
                'min_v': 0,
                'max_v': 5,
                'interval_v': 0.5,
                'min_w': 700e-9,
                'max_w': 900e-9,
                'interval_w': 50e-9,
            },
            'ant': {
                'min_v': 0,
                'max_v': 3,
                'interval_v': 0.3,
                'min_w': 450e-9,
                'max_w': 550e-9,
                'interval_w': 25e-9,
            }
        }
        
        return defaults.get(self.platform, defaults['sipho'])
    
    # ========== MÉTODOS LEGACY (mantener por compatibilidad temporal) ==========
    
    def run_heat_simulation(self, min_v, max_v, interval_v):
        """
        LEGACY: Ejecuta simulación DEVICE heat
        
        Args:
            min_v: Voltaje mínimo
            max_v: Voltaje máximo
            interval_v: Intervalo de voltaje
            
        Returns:
            str: Ruta al archivo .mat generado
        """
        inputs = {
            'platform': self.platform,
            'min_v': min_v,
            'max_v': max_v,
            'interval_v': interval_v
        }
        
        result_path = interface.heat(inputs)
        
        # Guardar en caché
        cache_key = f"heat_{self.platform}_{min_v}_{max_v}_{interval_v}"
        self.cache[cache_key] = result_path
        self.save_cache()
        
        return result_path
    
    def run_scatter_simulation(self, min_w, max_w, interval_w):
        """
        LEGACY: Ejecuta simulación FDTD scatter
        
        Args:
            min_w: Ancho mínimo
            max_w: Ancho máximo
            interval_w: Intervalo de ancho
            
        Returns:
            str: Ruta al archivo .mat generado
        """
        inputs = {
            'platform': self.platform,
            'min_w': min_w,
            'max_w': max_w,
            'interval_w': interval_w
        }
        
        result_path = interface.scatter(inputs)
        
        # Guardar en caché
        cache_key = f"scatter_{self.platform}_{min_w}_{max_w}_{interval_w}"
        self.cache[cache_key] = result_path
        self.save_cache()
        
        return result_path
    
    def run_weight_bank_simulation(self, weight_matrix, sim_type='scatter', **kwargs):
        """
        LEGACY: Ejecuta simulación de weight bank
        
        Args:
            weight_matrix: Matriz de pesos
            sim_type: Tipo de simulación ('scatter' o 'heat')
            **kwargs: Parámetros adicionales
            
        Returns:
            dict: Resultados de la simulación
        """
        inputs = {
            'platform': self.platform,
            'weight_matrix': weight_matrix,
            'sim_type': sim_type,
            **kwargs
        }
        
        results = interface.weight_bank(inputs)
        
        return results
    
    # ========== NUEVOS MÉTODOS (matrix_mult_N) ==========
    
    def run_matrix_multiplication(self, unitary_matrix, input_vector, 
                                  visualize=False, show_interconnect=False):
        """
        Ejecuta multiplicación matricial óptica usando MZI mesh
        Para matrices UNITARIAS solamente
        
        Args:
            unitary_matrix: Matriz unitaria (debe ser cuadrada y unitaria)
            input_vector: Vector de entrada
            visualize: Si visualizar la descomposición con interferometer
            show_interconnect: Si mantener INTERCONNECT abierto después
            
        Returns:
            dict: Resultados con vector de salida y métricas
        """
        print("\n" + "="*60)
        print("🔷 EJECUTANDO MULTIPLICACIÓN MATRICIAL (Unitaria)")
        print("="*60)
        
        # Validaciones
        if not mathfs.is_unitary(unitary_matrix):
            raise ValueError(
                "La matriz no es unitaria. Use run_general_matrix_multiplication() "
                "para matrices no unitarias."
            )
        
        validate_matrix_vector(unitary_matrix, input_vector)
        
        dim = unitary_matrix.shape[0]
        print(f"📊 Dimensión: {dim}×{dim}")
        print(f"🎯 Plataforma: {self.platform.upper()}")
        
        # Crear archivo .icp
        icp_folder = Path("matrix_mult_N/circuits")
        icp_folder.mkdir(parents=True, exist_ok=True)
        
        icp_path, created = create_matrix_icp(
            m=dim,
            n=dim,
            folder=icp_folder,
            hide=not show_interconnect
        )
        
        if created:
            print(f"✓ Archivo creado: {icp_path}")
        else:
            print(f"✓ Usando archivo existente: {icp_path}")
        
        # Abrir INTERCONNECT
        print("🔧 Inicializando INTERCONNECT...")
        from lumerical_path_detector import auto_detect_and_load_lumapi
        lumapi = auto_detect_and_load_lumapi()
        
        ic = lumapi.INTERCONNECT(filename=icp_path, hide=not show_interconnect)
        
        try:
            # Ejecutar multiplicación
            print("⚙️  Construyendo circuito MZI mesh...")
            v_mesh = MZI_multiplication(
                u=unitary_matrix,
                v=input_vector,
                ic=ic,
                create_circuit=True,
                graph=visualize
            )
            
            # Calcular resultado teórico
            v_theoretical = compute_theoretical_result(unitary_matrix, input_vector)
            
            # Calcular errores
            v_theoretical_power = np.abs(v_theoretical) ** 2
            error = np.abs(v_mesh - v_theoretical_power)
            avg_error = np.mean(error)
            max_error = np.max(error)
            
            print("\n" + "="*60)
            print("✓ SIMULACIÓN COMPLETADA")
            print("="*60)
            print(f"📈 Error promedio: {avg_error:.6e}")
            print(f"📈 Error máximo: {max_error:.6e}")
            print("="*60 + "\n")
            
            results = {
                'output_vector': v_mesh,
                'theoretical_vector': v_theoretical_power,
                'error': error,
                'avg_error': avg_error,
                'max_error': max_error,
                'platform': self.platform,
                'dimension': dim
            }
            
            return results
            
        finally:
            if not show_interconnect:
                ic.close()
                print("✓ INTERCONNECT cerrado")
    
    def run_general_matrix_multiplication(self, matrix, input_vector,
                                         visualize=False, show_interconnect=False):
        """
        Ejecuta multiplicación matricial óptica usando SVD
        Para matrices GENERALES (unitarias o no unitarias, cuadradas o rectangulares)
        
        Args:
            matrix: Matriz general (puede ser no unitaria, no cuadrada)
            input_vector: Vector de entrada
            visualize: Si visualizar la descomposición
            show_interconnect: Si mantener INTERCONNECT abierto
            
        Returns:
            dict: Resultados con vector de salida y métricas
        """
        print("\n" + "="*60)
        print("🔷 EJECUTANDO MULTIPLICACIÓN MATRICIAL GENERAL (SVD)")
        print("="*60)
        
        # Validaciones
        validate_matrix_vector(matrix, input_vector)
        
        dimU, dimV = matrix.shape
        print(f"📊 Dimensión: {dimU}×{dimV}")
        print(f"🎯 Plataforma: {self.platform.upper()}")
        
        # Verificar si es unitaria
        if is_unitary(matrix):
            print("ℹ️  La matriz es unitaria, pero se usará SVD de todas formas")
        
        # Crear archivo .icp
        icp_folder = Path("matrix_mult_N/circuits")
        icp_folder.mkdir(parents=True, exist_ok=True)
        
        icp_path, created = create_matrix_icp(
            m=dimU,
            n=dimV,
            folder=icp_folder,
            hide=not show_interconnect
        )
        
        if created:
            print(f"✓ Archivo creado: {icp_path}")
        else:
            print(f"✓ Usando archivo existente: {icp_path}")
        
        # Abrir INTERCONNECT
        print("🔧 Inicializando INTERCONNECT...")
        from lumerical_path_detector import auto_detect_and_load_lumapi
        lumapi = auto_detect_and_load_lumapi()
        
        ic = lumapi.INTERCONNECT(filename=icp_path, hide=not show_interconnect)
        
        try:
            # Ejecutar multiplicación con SVD
            print("⚙️  Construyendo circuito con descomposición SVD...")
            v_mesh = general_MZI_multiplication(
                u=matrix,
                v=input_vector,
                ic=ic,
                graph=visualize
            )
            
            # Calcular resultado teórico
            v_theoretical = compute_theoretical_result(matrix, input_vector)
            
            # Calcular errores
            v_theoretical_power = np.abs(v_theoretical) ** 2
            error = np.abs(v_mesh - v_theoretical_power)
            avg_error = np.mean(error)
            max_error = np.max(error)
            
            print("\n" + "="*60)
            print("✓ SIMULACIÓN COMPLETADA")
            print("="*60)
            print(f"📈 Error promedio: {avg_error:.6e}")
            print(f"📈 Error máximo: {max_error:.6e}")
            print("="*60 + "\n")
            
            results = {
                'output_vector': v_mesh,
                'theoretical_vector': v_theoretical_power,
                'error': error,
                'avg_error': avg_error,
                'max_error': max_error,
                'platform': self.platform,
                'dimension': f"{dimU}×{dimV}"
            }
            
            return results
            
        finally:
            if not show_interconnect:
                ic.close()
                print("✓ INTERCONNECT cerrado")
    
    def run_optical_neural_network(self, input_vector, weight_matrices,
                                   show_interconnect=False):
        """
        Ejecuta red neuronal óptica de múltiples capas
        
        Args:
            input_vector: Vector de entrada
            weight_matrices: Lista de matrices (pesos de cada capa)
            show_interconnect: Si mantener INTERCONNECT abierto
            
        Returns:
            dict: Resultados con salidas por capa y métricas
        """
        print("\n" + "="*60)
        print("🧠 EJECUTANDO RED NEURONAL ÓPTICA")
        print("="*60)
        
        num_layers = len(weight_matrices)
        print(f"📊 Número de capas: {num_layers}")
        print(f"📊 Dimensiones:")
        for i, W in enumerate(weight_matrices):
            print(f"   Capa {i+1}: {W.shape[0]}×{W.shape[1]}")
        print(f"🎯 Plataforma: {self.platform.upper()}")
        
        # Validar dimensiones entre capas
        for i in range(len(weight_matrices) - 1):
            if weight_matrices[i].shape[0] != weight_matrices[i+1].shape[1]:
                raise ValueError(
                    f"Dimensiones incompatibles entre capas {i+1} y {i+2}: "
                    f"{weight_matrices[i].shape} y {weight_matrices[i+1].shape}"
                )
        
        # Validar entrada con primera capa
        validate_matrix_vector(weight_matrices[0], input_vector)
        
        # Crear archivo .icp grande
        max_dim = max([max(W.shape) for W in weight_matrices])
        icp_folder = Path("matrix_mult_N/circuits")
        icp_folder.mkdir(parents=True, exist_ok=True)
        
        icp_path, created = create_matrix_icp(
            m=max_dim * 2,  # Multiplicador para tener espacio
            n=max_dim * 2,
            folder=icp_folder,
            hide=not show_interconnect
        )
        
        if created:
            print(f"✓ Archivo creado: {icp_path}")
        else:
            print(f"✓ Usando archivo existente: {icp_path}")
        
        # Abrir INTERCONNECT
        print("🔧 Inicializando INTERCONNECT...")
        from lumerical_path_detector import auto_detect_and_load_lumapi
        lumapi = auto_detect_and_load_lumapi()
        
        ic = lumapi.INTERCONNECT(filename=icp_path, hide=not show_interconnect)
        
        try:
            # Ejecutar red neuronal
            print("⚙️  Construyendo red neuronal óptica completa...")
            optical_neural_network(
                v=input_vector,
                m=weight_matrices,
                ic=ic,
                inference=False
            )
            
            print("\n" + "="*60)
            print("✓ RED NEURONAL CONSTRUIDA Y SIMULADA")
            print("="*60 + "\n")
            
            # Extraer resultados (por ahora simplificado)
            results = {
                'success': True,
                'num_layers': num_layers,
                'platform': self.platform,
                'message': 'Red neuronal óptica simulada exitosamente'
            }
            
            return results
            
        finally:
            if not show_interconnect:
                ic.close()
                print("✓ INTERCONNECT cerrado")
    
    # ========== MÉTODO DE COMPATIBILIDAD ==========
    
    def run_mzi_mesh(self, unitary_matrix, input_vector, 
                     visualize=False, show_interconnect=False):
        """
        COMPATIBILIDAD: Redirige al nuevo método run_matrix_multiplication
        Este método se mantiene para compatibilidad con código antiguo
        
        Args:
            unitary_matrix: Matriz unitaria
            input_vector: Vector de entrada
            visualize: Si visualizar
            show_interconnect: Si mostrar INTERCONNECT
            
        Returns:
            dict: Resultados de la simulación
        """
        print("⚠️  AVISO: run_mzi_mesh() está deprecado.")
        print("    Use run_matrix_multiplication() en su lugar.\n")
        
        return self.run_matrix_multiplication(
            unitary_matrix=unitary_matrix,
            input_vector=input_vector,
            visualize=visualize,
            show_interconnect=show_interconnect
        )