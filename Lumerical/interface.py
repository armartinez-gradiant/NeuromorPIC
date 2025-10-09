"""
Lumerical Interface
Handles all interactions with Lumerical API
"""

import imp
import numpy as np
import sys
import os

# Añadir ruta del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar lumapi usando el detector automático
from lumerical_path_detector import auto_detect_and_load_lumapi

print("🔍 Detectando instalación de Lumerical automáticamente...")
lumapi = auto_detect_and_load_lumapi()
print("✓ Lumerical API cargada correctamente\n")


def get_platform_path(platform):
    """
    Get the path to platform-specific files
    
    Args:
        platform: 'sipho' or 'sin'
    
    Returns:
        str: Path to platform folder
    """
    return f"Lumerical/platforms/{platform}"


def heat(inputs):
    """
    Run DEVICE heat simulation
    
    Args:
        inputs: Dictionary with simulation parameters including:
            - platform: 'sipho' or 'sin'
            - min_v: Minimum voltage
            - max_v: Maximum voltage
            - interval_v: Voltage interval
    
    Returns:
        str: Path to generated .mat file
    """
    platform = inputs.get('platform', 'sipho')
    platform_path = get_platform_path(platform)
    
    min_v = inputs['min_v']
    max_v = inputs['max_v']
    interval_v = inputs['interval_v']
    
    # Path to platform-specific .ldev file
    ldev_file = f"{platform_path}/ndoped_heater.ldev"
    
    print(f"⚙ Running DEVICE heat simulation...")
    print(f"  Platform: {platform.upper()}")
    print(f"  File: {ldev_file}")
    print(f"  Voltage range: {min_v}V to {max_v}V (interval: {interval_v}V)")
    
    device = lumapi.DEVICE(ldev_file)
    device.switchtolayout()
    
    # Output filename
    output_filename = f"wgT_{min_v}_{max_v}_{interval_v}_heater.mat"
    device.setnamed("HEAT::temp", "filename", output_filename)
    
    # Set voltage boundary conditions
    v_bc_name = "HEAT::boundary conditions::wire1"
    device.setnamed(v_bc_name, "range start", min_v)
    device.setnamed(v_bc_name, "range stop", max_v)
    device.setnamed(v_bc_name, "range interval", interval_v)
    
    # Run simulation
    device.run()
    
    device.close()
    
    # Return path to cache
    cache_folder = f"./Lumerical/cache_{platform}"
    output_path = f"{cache_folder}/{output_filename}"
    
    print(f"  ✓ Heat simulation complete: {output_path}")
    
    return output_path


def passivebentwg(inputs):
    """
    Run MODE simulation for passive bent waveguide
    
    Args:
        inputs: Dictionary with simulation parameters including:
            - platform: 'sipho' or 'sin'
            - start_wavelength: Start wavelength
            - end_wavelength: End wavelength
    
    Returns:
        str: Path to generated .ldf file
    """
    platform = inputs.get('platform', 'sipho')
    platform_path = get_platform_path(platform)
    
    start_wavelength = inputs['start_wavelength']
    end_wavelength = inputs['end_wavelength']
    
    # Path to platform-specific .lms file
    lms_file = f"{platform_path}/rib_waveguide.lms"
    
    print(f"⚙ Running MODE simulation for passive waveguide...")
    print(f"  Platform: {platform.upper()}")
    print(f"  File: {lms_file}")
    print(f"  Wavelength range: {start_wavelength*1e9:.2f}nm to {end_wavelength*1e9:.2f}nm")
    
    mode = lumapi.MODE(lms_file)
    
    # Disable temperature import
    mode.switchtolayout()
    mode.select("temperature")
    mode.setnamed('temperature', 'enabled', 0)
    
    mode.run()
    
    # Configure analysis
    mode.setanalysis("number of trial modes", 2)
    mode.setanalysis("wavelength", (start_wavelength + end_wavelength) / 2)
    mode.setanalysis("use max index", 1)
    
    # Find modes
    mode.findmodes()
    mode.selectmode(1)
    
    # Run frequency sweep
    mode.setanalysis("track selected mode", 1)
    mode.frequencysweep()
    
    # Save results
    dataname = mode.copydcard("frequencysweep")
    output_filename = f"passivebentwg_{start_wavelength}_{end_wavelength}_passive.ldf"
    mode.savedcard(output_filename, dataname)
    
    mode.close()
    
    # Return path to cache
    cache_folder = f"./Lumerical/cache_{platform}"
    output_path = f"{cache_folder}/{output_filename}"
    
    print(f"  ✓ Passive waveguide simulation complete: {output_path}")
    
    return output_path


def activebentwg(inputs):
    """
    Run MODE simulation for active bent waveguide with thermal effects
    
    Args:
        inputs: Dictionary with simulation parameters including:
            - platform: 'sipho' or 'sin'
            - start_wavelength: Start wavelength
            - end_wavelength: End wavelength
            - min_v: Minimum voltage
            - max_v: Maximum voltage
            - interval_v: Voltage interval
    
    Returns:
        tuple: (str: Path to .ldf file, MODE object)
    """
    platform = inputs.get('platform', 'sipho')
    platform_path = get_platform_path(platform)
    
    start_wavelength = inputs['start_wavelength']
    end_wavelength = inputs['end_wavelength']
    min_v = inputs['min_v']
    max_v = inputs['max_v']
    interval_v = inputs['interval_v']
    
    # Path to platform-specific .lms file
    lms_file = f"{platform_path}/rib_waveguide.lms"
    
    print(f"⚙ Running MODE simulation for active waveguide...")
    print(f"  Platform: {platform.upper()}")
    print(f"  File: {lms_file}")
    print(f"  Wavelength range: {start_wavelength*1e9:.2f}nm to {end_wavelength*1e9:.2f}nm")
    print(f"  Voltage range: {min_v}V to {max_v}V (interval: {interval_v}V)")
    
    mode = lumapi.MODE(lms_file)
    
    # Import temperature map from heat simulation
    mode.switchtolayout()
    mode.select("temperature")
    
    # The temperature file should already be in the cache from heat simulation
    temp_filename = f"wgT_{min_v}_{max_v}_{interval_v}_heater.mat"
    mode.importdataset(temp_filename)
    
    mode.run()
    
    # Configure analysis
    mode.setanalysis("number of trial modes", 2)
    mode.setanalysis("wavelength", (start_wavelength + end_wavelength) / 2)
    mode.setanalysis("use max index", 1)
    
    # Find modes
    mode.findmodes()
    mode.selectmode(1)
    
    # Run frequency sweep
    mode.setanalysis("track selected mode", 1)
    mode.frequencysweep()
    
    # Save results
    dataname = mode.copydcard("frequencysweep")
    output_filename = f"activebentwg_{start_wavelength}_{end_wavelength}_{min_v}_{max_v}_{interval_v}_active.ldf"
    mode.savedcard(output_filename, dataname)
    
    # Don't close mode yet - it will be used for effective_index calculation
    # mode.close() will be called later
    
    # Return path to cache
    cache_folder = f"./Lumerical/cache_{platform}"
    output_path = f"{cache_folder}/{output_filename}"
    
    print(f"  ✓ Active waveguide simulation complete: {output_path}")
    
    return output_path, mode


def effective_index(inputs, lum_mode=None):
    """
    Calculate effective index vs voltage
    
    Args:
        inputs: Dictionary with simulation parameters including:
            - platform: 'sipho' or 'sin'
            - source_wavelength: Laser wavelength
            - min_v: Minimum voltage
            - max_v: Maximum voltage
            - interval_v: Voltage interval
        lum_mode: Optional MODE object from activebentwg (to avoid reopening)
    
    Returns:
        str: Path to generated .txt file
    """
    platform = inputs.get('platform', 'sipho')
    platform_path = get_platform_path(platform)
    
    source_wavelength = inputs['source_wavelength']
    min_v = inputs['min_v']
    max_v = inputs['max_v']
    interval_v = inputs['interval_v']
    
    print(f"⚙ Calculating effective index vs voltage...")
    print(f"  Platform: {platform.upper()}")
    print(f"  Wavelength: {source_wavelength*1e9:.2f}nm")
    print(f"  Voltage range: {min_v}V to {max_v}V (interval: {interval_v}V)")
    
    # Open MODE if not provided
    if lum_mode is None:
        lms_file = f"{platform_path}/rib_waveguide.lms"
        mode = lumapi.MODE(lms_file)
        mode.switchtolayout()
        mode.select("temperature")
        
        # Import temperature data
        temp_filename = f"wgT_{min_v}_{max_v}_{interval_v}_heater.mat"
        mode.importdataset(temp_filename)
        
        mode.run()
        mode.setanalysis("number of trial modes", 2)
        mode.setanalysis("wavelength", source_wavelength)
        mode.setanalysis("use max index", 1)
    else:
        mode = lum_mode
    
    # Calculate neff for each voltage
    n_points = int((max_v - min_v) / interval_v) + 1
    voltage = np.linspace(min_v, max_v, n_points)
    
    result_str = ""
    
    for v in voltage:
        mode.switchtolayout()
        mode.setnamed('temperature', 'enabled', 1)
        mode.setnamed('temperature', 'V_wire1', v)
        mode.findmodes()
        
        data = mode.getdata('mode1', 'neff')
        neff = data[0][0]
        
        result_str += f"{v} {np.real(neff)} {np.imag(neff)}\n"
    
    # Save results
    output_filename = f"neff_{source_wavelength}_{min_v}_{max_v}_{interval_v}_neff.txt"
    cache_folder = f"./Lumerical/cache_{platform}"
    output_path = f"{cache_folder}/{output_filename}"
    
    with open(output_path, "w") as f:
        f.write(result_str)
    
    mode.close()
    
    print(f"  ✓ Effective index calculation complete: {output_path}")
    
    return output_path


def interconnect(inputs, files):
    """
    Run INTERCONNECT simulation
    
    Args:
        inputs: Dictionary with simulation parameters including:
            - platform: 'sipho' or 'sin'
            - time_window: Simulation time window
            - n_samples: Number of samples
        files: Dictionary with paths to required simulation files:
            - heat: Path to heat simulation .mat
            - passivebentwg: Path to passive waveguide .ldf
            - activebentwg: Path to active waveguide .ldf
            - effective_index: Path to neff .txt
            - interconnect: Path to .icp file
    """
    platform = inputs.get('platform', 'sipho')
    
    time_window = inputs.get('time_window', 5.12e-9)
    n_samples = inputs.get('n_samples', 15360)
    
    icp_file = files['interconnect']
    
    print(f"\n⚙ Running INTERCONNECT simulation...")
    print(f"  Platform: {platform.upper()}")
    print(f"  File: {icp_file}")
    print(f"  Time window: {time_window}s")
    print(f"  Samples: {n_samples}")
    
    print(f"\n  Loading simulation files:")
    for key, value in files.items():
        if key != 'interconnect':
            print(f"    • {key}: {value}")
    
    ic = lumapi.INTERCONNECT(icp_file)
    
    # Restore design mode
    ic.switchtodesign()
    
    # Set time parameters
    ic.setnamed("::Root Element", "time window", time_window)
    ic.setnamed("::Root Element", "number of samples", n_samples)
    
    # TODO: Load simulation files into INTERCONNECT
    # This depends on your specific .icp file structure
    # You may need to configure element parameters here based on files dict
    
    print(f"\n  🚀 Running INTERCONNECT...")
    ic.run()
    
    print(f"  ✓ INTERCONNECT simulation complete!")
    
    # ic.close()  # Uncomment if you want to close after simulation
    
    return ic