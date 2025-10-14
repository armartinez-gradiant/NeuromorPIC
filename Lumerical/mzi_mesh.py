"""
MZI Mesh generation module - Platform aware version
Replica la funcionalidad de matrix_mult_N pero usando componentes específicos
de cada plataforma (SiPho o SiN)
"""

import numpy as np
import interferometer as itf
import cmath
import sys
import os

# Importar el detector automático de Lumerical
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lumerical_path_detector import auto_detect_and_load_lumapi

lumapi = auto_detect_and_load_lumapi()


class MZIMeshSimulator:
    """
    Simulador de MZI Mesh consciente de la plataforma
    """
    
    def __init__(self, platform='sipho', show_interconnect=False):
        """
        Inicializar el simulador con la plataforma deseada
        
        Args:
            platform: 'sipho' o 'sin'
            show_interconnect: Si True, muestra la ventana de INTERCONNECT
        """
        self.platform = platform.lower()
        self.show_interconnect = show_interconnect
        
        # Crear INTERCONNECT desde cero (NO cargar archivo existente)
        print("Creando nueva sesión de INTERCONNECT...")
        self.ic = lumapi.INTERCONNECT(hide=not show_interconnect)
        
        # CRÍTICO: Cambiar a modo diseño
        self.ic.switchtodesign()
        
        # IMPORTANTE: Crear un proyecto nuevo vacío (no usar weight_bank)
        try:
            self.ic.newproject()
            print("✓ Proyecto nuevo vacío creado")
        except:
            # Si newproject() falla, intentar con deleteall para limpiar
            try:
                self.ic.deleteall()
                print("✓ Sesión de INTERCONNECT limpiada")
            except:
                print("⚠ No se pudo limpiar completamente - puede haber elementos residuales")
        
        # Importar la configuración de componentes de la plataforma
        if self.platform == 'sipho':
            from Lumerical.platforms.sipho.components_config import COMPONENTS
        else:
            from Lumerical.platforms.sin.components_config import COMPONENTS
        
        self.components = COMPONENTS
        print(f"✓ MZI Mesh Simulator inicializado para plataforma: {self.platform.upper()}")
        print(f"✓ Nueva sesión de INTERCONNECT creada desde cero")
        if show_interconnect:
            print("✓ INTERCONNECT visible - puedes ver la simulación en tiempo real")
            print("⚠ IMPORTANTE: INTERCONNECT permanecerá abierto después de la simulación")
            print("  Cierra manualmente la ventana cuando termines de analizar los resultados")
    
    def add_phase_shifter(self, name, angle, xpos=0, ypos=0):
        """
        Añade un phase shifter usando el componente específico de la plataforma
        
        Args:
            name: Nombre del componente
            angle: Ángulo de fase (radianes)
            xpos, ypos: Posición en el layout
        """
        comp_type = self.components['phase_shifter']['type']
        
        self.ic.addelement(comp_type)
        self.ic.set("name", name)
        
        # Configurar parámetros específicos según la plataforma
        for param, value in self.components['phase_shifter']['params'].items():
            self.ic.set(param, value)
        
        # Establecer el ángulo
        phase_param = self.components['phase_shifter']['phase_param']
        self.ic.set(phase_param, angle)
        
        self.ic.set("x position", xpos)
        self.ic.set("y position", ypos)
    
    def add_directional_coupler(self, name, coupling_coeff=0.5, conjugate=False, xpos=0, ypos=0):
        """
        Añade un directional coupler usando el componente específico de la plataforma
        
        Args:
            name: Nombre del componente
            coupling_coeff: Coeficiente de acoplamiento (0-1)
            conjugate: Si True, usa configuración conjugada
            xpos, ypos: Posición en el layout
        """
        comp_type = self.components['directional_coupler']['type']
        
        self.ic.addelement(comp_type)
        self.ic.set("name", name)
        
        # Configurar parámetros específicos
        for param, value in self.components['directional_coupler']['params'].items():
            self.ic.set(param, value)
        
        # Establecer coupling coefficient
        coupling_param = self.components['directional_coupler']['coupling_param']
        self.ic.set(coupling_param, coupling_coeff)
        
        if conjugate:
            self.ic.set("conjugate", 1)
        
        self.ic.set("x position", xpos)
        self.ic.set("y position", ypos)
    
    def add_laser(self, name, power, frequency=193.1e12, xpos=0, ypos=0):
        """Añade un láser CW"""
        self.ic.addelement("CW laser")
        self.ic.set("name", name)
        self.ic.set("power", power)
        self.ic.set("frequency", frequency)
        self.ic.set("x position", xpos)
        self.ic.set("y position", ypos)
    
    def add_power_meter(self, name, xpos=0, ypos=0):
        """Añade un power meter"""
        self.ic.addelement("optical power meter")
        self.ic.set("name", name)
        self.ic.set("x position", xpos)
        self.ic.set("y position", ypos)
    
    def retrieve_position(self, element):
        """Retorna la posición de un elemento"""
        return self.ic.getposition(element, "x"), self.ic.getposition(element, "y")
    
    def generate_mzi(self, theta, phi, i, j, xpos=0, ypos=0):
        """
        Genera un MZI completo con la estructura:
        --- phi ---\   /----- 2theta -----\    /--- -theta ---
                    ---                    ----
        -----------/   \------------------/    \--- -theta ---
        
        Args:
            theta, phi: Ángulos de fase del MZI
            i, j: Índices del MZI en el mesh
            xpos, ypos: Posición base en el layout
        """
        # Phase shifter phi
        self.add_phase_shifter(f"phi{i}{j}", phi, xpos=xpos, ypos=ypos)
        
        # Primer coupler
        self.add_directional_coupler(f"coupler{i}{j}1", xpos=150+xpos, ypos=ypos)
        self.ic.connect(f"phi{i}{j}", "output", f"coupler{i}{j}1", "input 1")
        
        # Phase shifter theta (2*theta)
        self.add_phase_shifter(f"theta{i}{j}", 2*theta, xpos=300+xpos, ypos=ypos)
        self.ic.connect(f"coupler{i}{j}1", "output 1", f"theta{i}{j}", "input")
        
        # Segundo coupler (conjugado)
        self.add_directional_coupler(f"coupler{i}{j}2", conjugate=True, xpos=450+xpos, ypos=ypos)
        self.ic.connect(f"theta{i}{j}", "output", f"coupler{i}{j}2", "input 1")
        self.ic.connect(f"coupler{i}{j}1", "output 2", f"coupler{i}{j}2", "input 2")
        
        # Phase shifters -theta de salida
        self.add_phase_shifter(f"otheta{i}{j}1", -theta, xpos=600+xpos, ypos=ypos)
        self.add_phase_shifter(f"otheta{i}{j}2", -theta, xpos=600+xpos, ypos=100+ypos)
        
        self.ic.connect(f"coupler{i}{j}2", "output 1", f"otheta{i}{j}1", "input")
        self.ic.connect(f"coupler{i}{j}2", "output 2", f"otheta{i}{j}2", "input")
    
    def build_mesh(self, unitary_matrix, xpos=0, ypos=0, visualize=False):
        """
        Construye un mesh de MZI a partir de una matriz unitaria
        
        Args:
            unitary_matrix: Matriz unitaria numpy
            xpos, ypos: Posición inicial del mesh
            visualize: Si True, muestra el diagrama del mesh
        """
        # Descomponer la matriz
        I = itf.square_decomposition(unitary_matrix)
        thetas = np.array([bs.theta for bs in I.BS_list], dtype=float)
        phis = np.array([bs.phi for bs in I.BS_list], dtype=float)
        
        if visualize:
            I.draw()
            print(I.BS_list)
        
        dim = unitary_matrix.shape[0]
        L = dim - 2
        count = 0
        k = 0
        
        if L < 0:
            return
        
        print(f"Generando {len(thetas)} MZIs para matriz {dim}×{dim}...")
        
        # Generar todos los MZIs
        for i in range(L + 1):
            j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
            
            if i == dim/2:
                k += 1
            if i > dim/2:
                k += 2
            
            for j in range(j_max + 1):
                self.generate_mzi(
                    thetas[count], phis[count], i, j,
                    xpos=i*1000 - j*500 - k*500 + xpos,
                    ypos=j*300 + k*300 + ypos
                )
                count += 1
        
        print("Conectando MZIs del mesh...")
        # Conectar los MZIs
        self._connect_mesh(dim, L)
        print("✓ Mesh construido exitosamente")
    
    def _connect_mesh(self, dim, L):
        """
        Conecta todos los MZIs del mesh
        Lógica completa extraída de matrix_mult_N
        """
        if dim % 2 == 0:  # Meshes pares
            for i in range(L + 1):
                j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
                
                for j in range(j_max + 1):
                    if i < (L+1)//2:  # Iteraciones impares excepto central
                        if j == 0:  # Fila superior
                            self.ic.connect(f"otheta{i}{j}1", "output", f"phi{i+1}{j}", "input")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}", "input")
                        else:  # Elementos interiores
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}", "input")
                    
                    if i == (L+1)//2:  # Iteración central
                        if j == 0:
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j}", "input")
                        elif j < j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j}", "input")
                        
                        if j == j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-1}1", "input 2")
                    
                    if i > (L+1)//2 and i < L:
                        if j > 0 and j < j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}", "input")
                        
                        if j == j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1", "input 2")
                    
                    if i == L and j != 0:
                        self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
        
        else:  # Meshes impares
            for i in range(L + 1):
                j_max = 2 * min(i, L - i) + (1 if i > (L // 2) else 0)
                
                for j in range(j_max + 1):
                    if i < (L+1)//2:
                        if j == 0:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"phi{i+1}{j}", "input")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}", "input")
                        else:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j+1}", "input")
                    
                    if i == (L+1)//2:
                        if j > 0 and j < j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}", "input")
                        
                        if j == j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1", "input 2")
                    
                    if i > (L+1)//2 and i < L:
                        if j > 0 and j < j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"phi{i+1}{j-1}", "input")
                        
                        if j == j_max:
                            self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
                            self.ic.connect(f"otheta{i}{j}2", "output", f"coupler{i+1}{j-2}1", "input 2")
                    
                    if i == L and j != 0:
                        self.ic.connect(f"otheta{i}{j}1", "output", f"coupler{i}{j-1}1", "input 2")
    
    def _connect_lasers_to_mesh(self, dim):
        """Conecta los láseres de entrada al mesh"""
        j = 0
        count = 0
        for i in range(dim//2):
            self.ic.connect(f"CW{count}", "output", f"phi{i}{j}", "input")
            count += 1
            self.ic.connect(f"CW{count}", "output", f"coupler{i}{j}1", "input 2")
            count += 1
            j += 2
        
        if dim % 2 == 1:
            self.ic.connect(f"CW{count}", "output", f"coupler{dim//2}{j-1}1", "input 2")
    
    def _add_power_meters(self, dim):
        """Añade power meters a las salidas del mesh"""
        count = 0
        
        # Primer power meter
        comp = f"otheta{(dim-1)//2}01"
        x, y = self.retrieve_position(comp)
        self.add_power_meter("pm0", x+100, y)
        self.ic.connect(comp, "output", "pm0", "input")
        count += 1
        
        # Si dim es impar, añadir otro
        if dim % 2 == 1:
            comp = f"otheta{(dim-1)//2}02"
            x, y = self.retrieve_position(comp)
            self.add_power_meter("pm1", x+100, y)
            self.ic.connect(comp, "output", "pm1", "input")
            count += 1
        
        # Loop a través de los MZIs centrales
        for i in range(dim//2 - 1):
            comp = f"otheta{(dim-1)//2+i+1}01"
            x, y = self.retrieve_position(comp)
            self.add_power_meter(f"pm{count}", x+100, y)
            self.ic.connect(comp, "output", f"pm{count}", "input")
            count += 1
            
            comp = f"otheta{(dim-1)//2+i+1}02"
            x, y = self.retrieve_position(comp)
            self.add_power_meter(f"pm{count}", x+100, y)
            self.ic.connect(comp, "output", f"pm{count}", "input")
            count += 1
        
        # Último MZI
        comp = f"otheta{dim-2}12"
        x, y = self.retrieve_position(comp)
        self.add_power_meter(f"pm{count}", x+100, y)
        self.ic.connect(comp, "output", f"pm{count}", "input")
    
    def _get_results(self, dim):
        """Obtiene los resultados de los power meters"""
        def dBm_to_W(x):
            return 10**(x/10)/1000
        
        return [
            (dBm_to_W(self.ic.getresult(f"pm{i}", "sum/power")),
             self.ic.getresult(f"pm{i}", "mode 1/angle"))
            for i in range(dim)
        ]
    
    def matrix_multiplication(self, unitary_matrix, input_vector, visualize=False):
        """
        Realiza multiplicación matricial óptica: resultado = U @ v
        
        Args:
            unitary_matrix: Matriz unitaria U
            input_vector: Vector de entrada v
            visualize: Si True, muestra el mesh
            
        Returns:
            dict: {
                'measured': resultados medidos del mesh,
                'theoretical': resultados teóricos,
                'errors': errores relativos
            }
        """
        dim = unitary_matrix.shape[0]
        v_theoretical = unitary_matrix @ input_vector
        
        print(f"\n{'='*60}")
        print(f"Multiplicación Matricial Óptica: {dim}×{dim}")
        print(f"{'='*60}")
        
        # Generar láseres con las potencias del vector de entrada al cuadrado
        v = np.array(input_vector, dtype=float)
        print("Generando láseres de entrada...")
        for i in range(len(input_vector)):
            self.add_laser(f"CW{i}", v[i]**2, xpos=0, ypos=i*300)
        
        # Construir el mesh
        self.build_mesh(unitary_matrix, xpos=100, visualize=visualize)
        
        # Conectar láseres al mesh
        print("Conectando láseres al mesh...")
        self._connect_lasers_to_mesh(dim)
        
        # Añadir power meters
        print("Añadiendo power meters...")
        self._add_power_meters(dim)
        
        # Ejecutar simulación
        print("Ejecutando simulación INTERCONNECT...")
        self.ic.run()
        print("✓ Simulación completada")
        
        # Obtener resultados
        print("Obteniendo resultados...")
        results = self._get_results(dim)
        
        # Calcular resultado teórico en forma polar
        v_res_sq_polar = [(abs(z), cmath.phase(z)) for z in v_theoretical**2]
        
        # Calcular error
        errors = []
        for i in range(dim):
            mag_error = abs(results[i][0] - v_res_sq_polar[i][0]) / (v_res_sq_polar[i][0] + 1e-10)
            phase_error = abs(results[i][1] - v_res_sq_polar[i][1])
            errors.append((mag_error, phase_error))
        
        print(f"\n{'='*60}")
        print("RESULTADOS")
        print(f"{'='*60}")
        print("Resultado Teórico (|v|², fase):")
        for i, (mag, phase) in enumerate(v_res_sq_polar):
            print(f"  [{i}]: {mag:.6f}, {phase:.4f} rad")
        
        print("\nResultado del Mesh (|v|², fase):")
        for i, (mag, phase) in enumerate(results):
            print(f"  [{i}]: {mag:.6f}, {phase:.4f} rad")
        
        print("\nError relativo (mag, fase):")
        for i, (mag_err, phase_err) in enumerate(errors):
            print(f"  [{i}]: {mag_err*100:.2f}%, {phase_err:.4f} rad")
        print(f"{'='*60}\n")
        
        return {
            'measured': results,
            'theoretical': v_res_sq_polar,
            'errors': errors
        }
    
    def save_design(self, filename):
        """
        Guarda el diseño actual en un archivo .icp
        
        Args:
            filename: Ruta del archivo donde guardar (ej: "mi_mesh.icp")
        """
        self.ic.save(filename)
        print(f"✓ Diseño guardado en: {filename}")


    def close(self):
        """Cierra la sesión de INTERCONNECT"""
        try:
            if hasattr(self, 'ic') and self.ic is not None:
                if self.show_interconnect:
                    print("\n⚠ INTERCONNECT sigue abierto (close() llamado pero show_interconnect=True)")
                    # NO cerrar si show_interconnect=True
                else:
                    self.ic.close()
                    print("✓ Sesión de INTERCONNECT cerrada")
                    self.ic = None
        except Exception as e:
            print(f"⚠ Error al cerrar INTERCONNECT: {e}")

    def __del__(self):
        """Destructor - asegurar cierre al eliminar el objeto"""
        try:
            if hasattr(self, 'ic') and self.ic is not None and not self.show_interconnect:
                try:
                    self.ic.close()
                except:
                    pass
        except:
            pass        


    def __del__(self):
        """
        Destructor - asegurar que INTERCONNECT se cierre al eliminar el objeto
        Esto previene procesos huérfanos
        """
        try:
            # Solo cerrar si show_interconnect era False
            # Si era True, el usuario debe cerrar manualmente
            if hasattr(self, 'ic') and self.ic is not None and not self.show_interconnect:
                try:
                    self.ic.close()
                except:
                    pass  # Ignorar errores en el destructor
        except:
            pass  # Siempre ignorar errores en __del__            

