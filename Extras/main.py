"""
Main script for laser wavelength sweep analysis
Modified to use lumerical_path_detector for automatic Lumerical detection
"""
import sys
import os
import numpy as np
from matplotlib import pyplot as plt

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the modified laser sweep module
import laser_wavelength_sweep as laser_sweep

def plot_results(results):
    """Plot time-domain results"""
    keys = []
    for key, value in results.items():
        keys.append(key)
    print("Result properties")
    print(keys)

    time = results['time']
    amplitude = results['amplitude (a.u.)']

    plt.plot(time, amplitude)
    plt.xlabel("time (s)")
    plt.ylabel("amplitude (a.u.)")
    plt.show()

def plot_transmission(wavelength, drop_transmission, thru_transmission):
    """Plot transmission profiles"""
    plt.figure(figsize=(10, 8))
    
    plt.subplot(2, 1, 1)
    plt.plot(wavelength, thru_transmission, 'b-', linewidth=2)
    plt.ylabel("thru transmission (dBm)", fontsize=12)
    plt.title("Transmission Profiles", fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.plot(wavelength, drop_transmission, 'r-', linewidth=2)
    plt.xlabel("wavelength (m)", fontsize=12)
    plt.ylabel("drop transmission (dBm)", fontsize=12)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def load_results():
    """Load previously saved results from disk"""
    wavelength = np.load("Extras/wavelength.npy")
    drop_transmission = np.load("Extras/drop_transmission.npy")
    thru_transmission = np.load("Extras/thru_transmission.npy")

    return wavelength, drop_transmission, thru_transmission

def save_results(wavelength, drop_transmission, thru_transmission):
    """Save results to disk as numpy arrays"""
    np.save("Extras/wavelength", np.array(wavelength))
    np.save("Extras/drop_transmission", np.array(drop_transmission))
    np.save("Extras/thru_transmission", np.array(thru_transmission))
    print("✓ Results saved to Extras/ directory")

# ========== CONFIGURATION ==========
# if False, runs a new simulation. If True, loads results from disk
load_sim = False
save_data = True

# Simulation config
time_window = 5.12e-09  # seconds
n_samples = 15360

# Sweep config
start_wavelength = 1517e-9  # meters
end_wavelength = 1524e-9    # meters
n_sims = 100

print("\n" + "="*70)
print("LASER WAVELENGTH SWEEP SIMULATION")
print("="*70)
print(f"Start wavelength: {start_wavelength*1e9:.2f} nm")
print(f"End wavelength:   {end_wavelength*1e9:.2f} nm")
print(f"Number of points: {n_sims}")
print(f"Time window:      {time_window*1e9:.3f} ns")
print(f"Number of samples: {n_samples}")
print("="*70 + "\n")

# ========== MAIN EXECUTION ==========
if load_sim:
    print("📂 Loading results from disk...")
    wavelength, drop_transmission, thru_transmission = load_results()
    print("✓ Results loaded successfully\n")
else:
    print("🚀 Starting new simulation...\n")
    ic = laser_sweep.setup(start_wavelength, end_wavelength, n_sims, time_window, n_samples, save_data)
    wavelength, drop_transmission, thru_transmission = laser_sweep.run(ic)
    
    if save_data:
        save_results(wavelength, drop_transmission, thru_transmission)

print("📊 Plotting results...")
plot_transmission(wavelength, drop_transmission, thru_transmission)