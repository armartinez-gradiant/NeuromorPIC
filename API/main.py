"""
API Module
Acts as the middleman between GUI/CLI and Lumerical
Manages cache, platform selection, and simulation orchestration
"""

import os
from pprint import pprint
from Lumerical import interface

class API:

    def __init__(self):
        self.init = True
        self.platform = 'sipho'  # Default platform
        self._active_simulator = None
    
    def set_platform(self, platform):
        """
        Set the platform to use (sipho or sin)
        
        Args:
            platform: 'sipho' or 'sin'
        """
        if platform.lower() not in ['sipho', 'sin']:
            raise ValueError(f"Invalid platform: {platform}. Must be 'sipho' or 'sin'")
        
        self.platform = platform.lower()
        print(f"✓ Platform set to: {self.platform.upper()}")

    def get_cache_folder(self):
        """
        Get the cache folder path for the current platform
        
        Returns:
            str: Path to the cache folder
        """
        return f"./Lumerical/cache_{self.platform}"

    def load_cache(self):
        """
        Load cached simulations from the platform-specific cache folder
        """
        cache_folder = self.get_cache_folder()
        
        if not os.path.exists(cache_folder):
            print(f"⚠ Warning: Cache folder '{cache_folder}' does not exist. Creating it...")
            os.makedirs(cache_folder)
        
        # Define cache files
        cache_files = {
            'heat': f"{cache_folder}/heat.json",
            'passivebentwg': f"{cache_folder}/passivebentwg.json",
            'activebentwg': f"{cache_folder}/activebentwg.json",
            'neff': f"{cache_folder}/neff.json"
        }
        
        # Initialize empty cache lists
        self.heat = []
        self.passivebentwg = []
        self.activebentwg = []
        self.neff = []
        
        # Load each cache file if it exists
        import json
        
        for cache_type, cache_path in cache_files.items():
            try:
                if os.path.exists(cache_path):
                    with open(cache_path, 'r') as f:
                        data = json.load(f)
                        setattr(self, cache_type, data)
                    print(f"  ✓ Loaded {len(data)} {cache_type} simulations")
                else:
                    # Crear archivo vacío si no existe
                    print(f"  ⚠ {cache_type}.json no existe, creando archivo vacío...")
                    with open(cache_path, 'w') as f:
                        json.dump([], f)
                    setattr(self, cache_type, [])
            except json.JSONDecodeError as e:
                print(f"  ❌ Error al leer {cache_path}: {e}")
                print(f"     Creando archivo vacío...")
                with open(cache_path, 'w') as f:
                    json.dump([], f)
                setattr(self, cache_type, [])
            except Exception as e:
                print(f"  ❌ Error inesperado con {cache_path}: {e}")
                setattr(self, cache_type, [])
        
        print(f"✓ Cache loaded from: {cache_folder}")
        print(f"  • Total simulations: {self.get_total_simulations()}")

    def get_total_simulations(self):
        """
        Get the total number of cached simulations
        
        Returns:
            int: Total number of simulations in cache
        """
        return len(self.heat) + len(self.passivebentwg) + len(self.activebentwg) + len(self.neff)

    def get_cache_stats(self):
        """
        Get detailed cache statistics
        
        Returns:
            dict: Dictionary with cache statistics
        """
        return {
            'heat': len(self.heat),
            'passivebentwg': len(self.passivebentwg),
            'activebentwg': len(self.activebentwg),
            'neff': len(self.neff),
            'total': self.get_total_simulations()
        }

    def get_param_suggestions(self):
        """
        Get parameter suggestions based on the current platform
        
        Returns:
            dict: Dictionary with suggested default parameters
        """
        defaults = {
            'source_wavelength': '1.55e-6',
            'wavelength_window': '20e-9',
            'constant_v': '10.0',
            'min_v': '0.0',
            'max_v': '20.0',
            'interval_v': '0.2',
            'time_window': '5.12e-9',
            'n_samples': '15360',
            'output_dir': './results'
        }
        
        # Ajustes específicos por plataforma si es necesario
        if self.platform == 'sin':
            # SiN puede tener parámetros ligeramente diferentes
            # (ajustar si es necesario según las especificaciones)
            pass
        
        return defaults

    def get_heat_sim(self):
        cached_to_use = None
        for cached in self.heat:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("✓ Using cached heat simulation: " + cached_to_use['filename'])
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new heat simulation...")
            filename = interface.heat(self.inputs)
            return filename

    def get_passivebentwg_sim(self):
        cached_to_use = None
        for cached in self.passivebentwg:
            if (self.inputs['source_wavelength'] <= cached['laser_wavelength']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("✓ Using cached passivebentwg simulation: " + cached_to_use['filename'])
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new passivebentwg simulation...")
            filename = interface.passivebentwg(self.inputs)
            return filename

    def get_activebentwg_sim(self):
        cached_to_use = None
        for cached in self.activebentwg:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v'] and
                self.inputs['source_wavelength'] <= cached['laser_wavelength']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("✓ Using cached activebentwg simulation: " + cached_to_use['filename'])
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new activebentwg simulation...")
            filename, mode = interface.activebentwg(self.inputs)
            # this can then be used for neff calc, rather than reconfiguring a sim
            self.lum_mode = mode
            return filename

    def get_effective_index_sim(self):
        cached_to_use = None
        for cached in self.neff:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v'] and
                self.inputs['source_wavelength'] <= cached['laser_wavelength']):
                cached_to_use = cached
                break

        lum_mode = self.lum_mode if hasattr(self, 'lum_mode') else None
        if cached_to_use:
            print("✓ Using cached effective_index simulation: " + cached_to_use['filename'])
            # if lum_mode is defined we should close it to minimize resources
            # (since this sim is cached, so we dont need it)
            if lum_mode is not None:
                lum_mode.close()
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new effective_index simulation...")
            return interface.effective_index(self.inputs, lum_mode)

    def get_interconnect_sim(self):
        # INTERCONNECT file is platform-specific
        platform_path = f"Lumerical/platforms/{self.platform}/weight_bank.icp"
        print(f"📁 Using INTERCONNECT file: {platform_path}")
        return platform_path

    def cleanup(self):
        """Limpia todos los recursos activos de simulación"""
        try:
            if hasattr(self, '_active_simulator') and self._active_simulator is not None:
                print("\n🧹 Limpiando simulador activo...")
                try:
                    self._active_simulator.close()
                    print("✓ Simulador cerrado correctamente")
                except Exception as e:
                    print(f"⚠ Error al cerrar simulador: {e}")
                finally:
                    self._active_simulator = None
        except Exception as e:
            print(f"⚠ Error durante cleanup: {e}")

    def __del__(self):
        """Destructor - asegurar que se limpien recursos"""
        try:
            self.cleanup()
        except:
            pass

    def run(self, inputs):
        print("\n" + "="*70)
        print("🚀 RUNNING SIMULATION")
        print("="*70)
        print(f"Platform: {self.platform.upper()}")
        print(f"Cache folder: {self.get_cache_folder()}")
        print("\nAPI inputs:")
        pprint(inputs)
        print("="*70 + "\n")
        
        self.inputs = inputs

        files = {
            'heat': self.get_heat_sim(),
            'passivebentwg': self.get_passivebentwg_sim(),
            'activebentwg': self.get_activebentwg_sim(),
            'effective_index': self.get_effective_index_sim(),
            'interconnect': self.get_interconnect_sim()
        }

        print("\n📂 Files to be used in simulation:")
        for key, value in files.items():
            print(f"  • {key}: {value}")
        print()

        return interface.interconnect(inputs, files)

    def run_mzi_mesh(self, unitary_matrix, input_vector, visualize=False, show_interconnect=False):
        """
        Ejecuta simulación de MZI Mesh para multiplicación matricial óptica
        
        Args:
            unitary_matrix: Matriz unitaria numpy (N×N)
            input_vector: Vector de entrada numpy (N,)
            visualize: Si True, muestra el diagrama del mesh
            show_interconnect: Si True, muestra la ventana de INTERCONNECT
                
        Returns:
            Resultados de la simulación (dict con measured, theoretical, errors)
        """
        from Lumerical.mzi_mesh import MZIMeshSimulator
        
        print(f"\n{'='*70}")
        print("🔷 RUNNING MZI MESH SIMULATION")
        print(f"{'='*70}")
        print(f"Platform: {self.platform.upper()}")
        print(f"Matrix dimension: {unitary_matrix.shape[0]}×{unitary_matrix.shape[1]}")
        print(f"Input vector length: {len(input_vector)}")
        print(f"Visualize mesh: {visualize}")
        print(f"Show INTERCONNECT: {show_interconnect}")
        print(f"{'='*70}\n")
        
        # Limpiar simulador anterior si existe
        if hasattr(self, '_active_simulator') and self._active_simulator is not None:
            print("🧹 Limpiando simulador anterior...")
            try:
                self._active_simulator.close()
            except:
                pass
            self._active_simulator = None
        
        # Crear simulador con la plataforma actual
        simulator = MZIMeshSimulator(platform=self.platform, show_interconnect=show_interconnect)
        
        # Ejecutar multiplicación matricial
        results = simulator.matrix_multiplication(
            unitary_matrix, 
            input_vector, 
            visualize=visualize
        )
        
        # Guardar referencia al simulador si INTERCONNECT debe permanecer abierto
        if show_interconnect:
            self._active_simulator = simulator
            print("\n" + "="*70)
            print("⚠ INTERCONNECT permanece ABIERTO")
            print("="*70)
            print("💡 El simulador permanecerá activo hasta que:")
            print("   • Cierres INTERCONNECT manualmente, o")
            print("   • Cierres la aplicación completa")
            print("="*70 + "\n")
        else:
            # Si no debe mostrar INTERCONNECT, cerrar normalmente
            simulator.close()
        
        print(f"\n{'='*70}")
        print("✓ MZI MESH SIMULATION COMPLETED")
        print(f"{'='*70}\n")
        
        return results