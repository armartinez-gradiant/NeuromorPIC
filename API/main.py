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
from matrix_mult_N import mathfs  # ← CORREGIDO

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
        self.load_cache()
        
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
        print(f"✓ Plataforma configurada: {self.platform.upper()}")
    
    def get_platform(self):
        """Obtener plataforma actual"""
        return self.platform
    
    def load_cache(self):
        """Cargar caché de simulaciones previas"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.cache = json.load(f)
                print(f"✓ Caché cargada: {len(self.cache)} entradas")
            except Exception as e:
                print(f"⚠️ Error cargando caché: {e}")
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self):
        """Guardar caché de simulaciones"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando caché: {e}")
    
    def get_total_simulations(self):
        """
        Obtiene el número total de simulaciones en caché
        
        Returns:
            int: Número de simulaciones guardadas
        """
        return len(self.cache)

    def run(self, params):
        """
        LEGACY: Ejecuta simulación según parámetros (compatibilidad con sistema antiguo)
        
        Args:
            params: Diccionario con parámetros de simulación
        """
        sim_type = params.get('sim_type', 'scatter')
        
        if sim_type == 'scatter':
            # Simulación scatter (FDTD)
            min_w = float(params.get('min_w', 400e-9))
            max_w = float(params.get('max_w', 600e-9))
            interval_w = float(params.get('interval_w', 50e-9))
            
            print(f"\n🔬 Ejecutando simulación SCATTER")
            print(f"   Ancho: {min_w*1e9:.1f} - {max_w*1e9:.1f} nm")
            print(f"   Intervalo: {interval_w*1e9:.1f} nm")
            
            result_path = self.run_scatter_simulation(min_w, max_w, interval_w)
            print(f"✓ Scatter completado: {result_path}")
            
        elif sim_type == 'heat':
            # Simulación heat (DEVICE)
            heater_sim_type = params.get('heater_sim_type', 'sweep')
            
            if heater_sim_type == 'sweep':
                min_v = float(params.get('min_v', 0))
                max_v = float(params.get('max_v', 5))
                interval_v = float(params.get('interval_v', 0.5))
                
                print(f"\n🔥 Ejecutando simulación HEAT (sweep)")
                print(f"   Voltaje: {min_v} - {max_v} V")
                print(f"   Intervalo: {interval_v} V")
                
                result_path = self.run_heat_simulation(min_v, max_v, interval_v)
                print(f"✓ Heat completado: {result_path}")
                
            elif heater_sim_type == 'constant':
                constant_v = float(params.get('constant_v', 4.5))
                
                print(f"\n🔥 Ejecutando simulación HEAT (constante)")
                print(f"   Voltaje: {constant_v} V")
                
                result_path = self.run_heat_simulation(constant_v, constant_v, 1)
                print(f"✓ Heat completado: {result_path}")
        
        print("\n✓ Todas las simulaciones completadas\n")

    def get_param_suggestions(self):
        """Obtener sugerencias de parámetros para la plataforma actual"""
        defaults = {
            'sipho': {
                'start_wavelength': 1.5e-6,
                'end_wavelength': 1.6e-6,
                'time_window': 5.12e-9,
                'n_samples': 15360
            },
            'sin': {
                'start_wavelength': 1.5e-6,
                'end_wavelength': 1.6e-6,
                'time_window': 5.12e-9,
                'n_samples': 15360
            },
            'ant': {
                'start_wavelength': 1.5e-6,
                'end_wavelength': 1.6e-6,
                'time_window': 5.12e-9,
                'n_samples': 15360
            }
        }
        return defaults.get(self.platform, defaults['sipho'])
    
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
        if not is_unitary(unitary_matrix):
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
            # Ejecutar multiplicación general
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
                'dimension': (dimU, dimV)
            }
            
            return results
            
        finally:
            if not show_interconnect:
                ic.close()
                print("✓ INTERCONNECT cerrado")
    
    # ========== MÉTODOS LEGACY (weight_bank) ==========
    
    def run_weight_bank_simulation(self, weight_matrix, sim_type='scatter', **kwargs):
        """
        LEGACY: Ejecuta simulación de weight bank
        """
        inputs = {
            'platform': self.platform,
            'weight_matrix': weight_matrix,
            'sim_type': sim_type,
            **kwargs
        }
        
        results = interface.weight_bank(inputs)
        
        return results