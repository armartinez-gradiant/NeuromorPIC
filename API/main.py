import os
from pprint import pprint
from Lumerical import interface

class API:

    def __init__(self):
        self.init = True
        self.platform = 'sipho'  # Default platform
        self.ic_connection = None  # Para mantener INTERCONNECT abierto si es necesario

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
            os.makedirs(cache_folder, exist_ok=True)
        
        wgT = []
        activebentwg = []
        passivebentwg = []
        neff = []

        print(f"📂 Loading cache from: {cache_folder}")

        for root, subdirs, files in os.walk(cache_folder):
            for filename in files:
                # heat sim files
                if filename.startswith("wgT_") and filename.endswith(".mat"):
                    parts = filename.split("_")
                    if len(parts) >= 4:
                        _, min_v, max_v, interval_v = parts[0], parts[1], parts[2], parts[3]
                        wgT.append({
                            "min_v": float(min_v),
                            "max_v": float(max_v),
                            "interval_v": float(interval_v),
                            "filename": filename,
                        })

                elif filename.startswith("neff_") and filename.endswith(".txt"):
                    parts = filename.split("_")
                    if len(parts) >= 5:
                        _, laser_wavelength, min_v, max_v, interval_v = parts[0], parts[1], parts[2], parts[3], parts[4]
                        neff.append({
                            "laser_wavelength": float(laser_wavelength),
                            "min_v": float(min_v),
                            "max_v": float(max_v),
                            "interval_v": float(interval_v),
                            "filename": filename,
                        })

                elif filename.startswith("activebentwg_") and filename.endswith(".ldf"):
                    parts = filename.split("_")
                    if len(parts) >= 6:
                        _, start_wavelength, end_wavelength, min_v, max_v, interval_v = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                        activebentwg.append({
                            "start_wavelength": float(start_wavelength),
                            "end_wavelength": float(end_wavelength),
                            "min_v": float(min_v),
                            "max_v": float(max_v),
                            "interval_v": float(interval_v),
                            "filename": filename,
                        })

                elif filename.startswith("passivebentwg_") and filename.endswith(".ldf"):
                    parts = filename.split("_")
                    if len(parts) >= 3:
                        _, start_wavelength, end_wavelength = parts[0], parts[1], parts[2]
                        passivebentwg.append({
                            "start_wavelength": float(start_wavelength),
                            "end_wavelength": float(end_wavelength),
                            "filename": filename,
                        })
            break

        self.wgT = wgT
        self.activebentwg = activebentwg
        self.passivebentwg = passivebentwg
        self.neff = neff
        
        print(f"  ✓ Loaded: {len(wgT)} heat sims | {len(activebentwg)} active WG | {len(passivebentwg)} passive WG | {len(neff)} neff")

    def get_param_suggestions(self):
        print("📋 Getting parameter suggestions from cache...")
        # fallbacks if no files in cache
        laser_wavelength = 1545e-9
        min_v = 4.5
        max_v = 4.6
        interval_v = 0.001
        wavelength_window = 25e-9

        if len(self.neff) > 0:
            # take last file in cache for suggested values
            last_sim = self.neff[-1]
            laser_wavelength = last_sim['laser_wavelength']
            min_v = last_sim['min_v']
            max_v = last_sim['max_v']
            interval_v = last_sim['interval_v']

        constant_v = min_v if min_v > 0 else 4.5

        return {
            'laser_wavelength': '%.3e' % laser_wavelength,
            'wavelength_window': '%.2e' % wavelength_window,
            'min_v': str(min_v),
            'max_v': str(max_v),
            'interval_v': str(interval_v),
            'constant_v': str(constant_v)
        }

    def get_heat_sim(self):
        cached_to_use = None
        for cached in self.wgT:
            if (self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['interval_v'] >= cached['interval_v']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("✓ Using cached heat simulation: " + cached_to_use['filename'])
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new heat simulation...")
            return interface.heat(self.inputs)

    def get_passivebentwg_sim(self):
        cached_to_use = None
        for cached in self.passivebentwg:
            if (self.inputs['start_wavelength'] >= cached['start_wavelength'] and
                self.inputs['end_wavelength'] <= cached['end_wavelength']):
                cached_to_use = cached
                break

        if cached_to_use:
            print("✓ Using cached passivebentwg simulation: " + cached_to_use['filename'])
            return f"{self.get_cache_folder()}/" + cached_to_use['filename']
        else:
            print("⚙ Running new passivebentwg simulation...")
            return interface.passivebentwg(self.inputs)

    def get_activebentwg_sim(self):
        cached_to_use = None
        for cached in self.activebentwg:
            if (self.inputs['min_v'] >= cached['min_v'] and
                self.inputs['max_v'] <= cached['max_v'] and
                self.inputs['interval_v'] >= cached['interval_v'] and
                self.inputs['start_wavelength'] >= cached['start_wavelength'] and
                self.inputs['end_wavelength'] <= cached['end_wavelength']):
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

        # CRÍTICO: Capturar el objeto ic retornado
        ic = interface.interconnect(inputs, files)
        
        # Si el usuario quiere mantener INTERCONNECT abierto, guardar la referencia
        if inputs.get('keep_interconnect_open', False):
            self.ic_connection = ic
            print("\n✓ INTERCONNECT connection reference saved in API object")
            print("  (This keeps the window open until the program exits)\n")
        # Si no, el objeto se destruirá automáticamente y cerrará INTERCONNECT