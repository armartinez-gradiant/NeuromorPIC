# matrix_mult_N/testing.py – Mantener INTERCONNECT abierto hasta Ctrl+C

from . import main
from . import mathfs

import numpy as np
from scipy.stats import unitary_group
import time
import sys
import os
import threading
import signal

# Asegura que Python encuentra lumapi; ajusta a tu versión si cambia la ruta
sys.path.append(r"C:\Program Files\ANSYS Inc\v251\Lumerical\api\python")
import lumapi  # noqa: E402
def main_test():
    start_time = time.time()

    # Lanza INTERCONNECT con GUI visible.
    # IMPORTANTE: No uses 'with ... as ic:' para que NO se cierre al salir del bloque.
    ic = lumapi.INTERCONNECT(hide=False)

    # Guarda esta ruta si quieres conservar el proyecto
    save_path = r"C:\Temp\ultima_ejecucion.icp"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    try:
        # =========================
        # PRUEBA SIMPLE: matriz unitaria 4x4
        # =========================
        dim = 4
        u = unitary_group.rvs(dim)
        v = mathfs.random_vector(dim, normalize="unit")

        print(f"Probando con matriz unitaria {dim}x{dim}")
        print(f"Matriz es unitaria: {main.is_unitary(u)}")

        # Ejecuta tu pipeline. No cierres ni la sesión ni la app aquí.
        result = main.MZI_multiplication(u, v, ic=ic, create_circuit=True, graph=False)

        end_time = time.time()
        print(f"Tiempo transcurrido: {end_time - start_time:.2f}s")
        print(f"Resultado: {result}")

        # === Mantener el proceso vivo hasta que el usuario presione Ctrl+C ===
        print("\n\u2705 INTERCONNECT se dejará ABIERTO.")
        print("   - Revisa la GUI todo lo que quieras.")
        print("   - Cuando quieras cerrar desde Python: pulsa Ctrl+C en esta consola.\n")

        # Bucle de espera “infinito” (interrumpible por Ctrl+C)
        stop = threading.Event()

        def handle_sigint(signum, frame):
            stop.set()

        signal.signal(signal.SIGINT, handle_sigint)
        # Espera hasta que el usuario presione Ctrl+C
        while not stop.is_set():
            stop.wait(timeout=1.0)

    except Exception as e:
        print(f"[Error] {e}")

    finally:
        # Al salir (Ctrl+C o excepción), intenta guardar y CERRAR LIMPIO
        try:
            ic.save(save_path)
            print(f"\nProyecto guardado en: {save_path}")
        except Exception as e_save:
            print(f"[Aviso] No se pudo guardar el proyecto en {save_path}: {e_save}")

        # Cierre explícito de la sesión (equivalente a appClose)
        try:
            ic.close()
            print("Sesión de INTERCONNECT cerrada correctamente.")
        except Exception as e_close:
            print(f"[Aviso] No se pudo cerrar la sesión de INTERCONNECT: {e_close}")


if __name__ == "__main__":
    main_test()