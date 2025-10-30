"""
CONFIGURACIÓN ÚNICA: Importar elemento 'optical relu' a tu librería
Este script solo necesitas ejecutarlo UNA VEZ
"""

import sys
import os

print("=" * 70)
print(" CONFIGURACIÓN: Importar 'optical relu' a INTERCONNECT")
print("=" * 70)
print()

# Cargar lumapi
try:
    try:
        from lumerical_path_detector import auto_detect_and_load_lumapi
        lumapi = auto_detect_and_load_lumapi()
        print("✅ lumapi cargado con auto-detección")
    except ImportError:
        sys.path.append(r"C:\Program Files\Lumerical\v251\api\python")
        sys.path.append(r"C:\Program Files\ANSYS Inc\v251\Lumerical\api\python")
        import lumapi
        print("✅ lumapi cargado con path manual")
except ImportError as e:
    print(f"❌ Error: No se pudo cargar lumapi: {e}")
    sys.exit(1)

# Buscar relu.icp
relu_paths = [
    "matrix_mult_N/relu.icp",
    "../matrix_mult_N/relu.icp",
    "./relu.icp"
]

relu_path = None
for path in relu_paths:
    if os.path.exists(path):
        relu_path = os.path.abspath(path)
        break

if not relu_path:
    print("❌ No se encontró matrix_mult_N/relu.icp")
    print("\nUbicaciones buscadas:")
    for p in relu_paths:
        print(f"  - {p}")
    sys.exit(1)

print(f"✅ Encontrado: {relu_path}")
print()

print("=" * 70)
print(" INSTRUCCIONES - Sigue estos pasos:")
print("=" * 70)
print("""
Este script abrirá relu.icp en INTERCONNECT para que puedas copiar
el elemento 'optical relu' a tu librería personal.

PASOS:

1. Se abrirá INTERCONNECT con relu.icp
2. Verás un elemento llamado "optical relu" en el layout
3. Selecciona el elemento (clic sobre él)
4. Presiona Ctrl+C (o Edit → Copy)
5. Cierra INTERCONNECT (guardando si pregunta)
6. Se abrirá otro INTERCONNECT vacío
7. Presiona Ctrl+V (o Edit → Paste)
8. El elemento ahora está en tu librería
9. Cierra INTERCONNECT

Después de esto, NUNCA más necesitarás hacer este proceso.

""")

input("Presiona Enter cuando estés listo para comenzar...")

print("\n🔧 Abriendo relu.icp en INTERCONNECT...")
try:
    # Abrir relu.icp
    ic1 = lumapi.INTERCONNECT(filename=relu_path, hide=False)
    print("✅ relu.icp abierto")
    print("\n👉 AHORA:")
    print("   1. Selecciona el elemento 'optical relu' (clic sobre él)")
    print("   2. Presiona Ctrl+C para copiar")
    print("   3. Cierra INTERCONNECT")
    
    input("\nPresiona Enter cuando hayas copiado y cerrado INTERCONNECT...")
    
    try:
        ic1.close()
    except:
        pass  # Ya puede estar cerrado
    
    print("\n🔧 Abriendo INTERCONNECT vacío...")
    ic2 = lumapi.INTERCONNECT(hide=False)
    print("✅ INTERCONNECT vacío abierto")
    print("\n👉 AHORA:")
    print("   1. Presiona Ctrl+V para pegar")
    print("   2. El elemento aparecerá en el layout")
    print("   3. Cierra INTERCONNECT (puedes guardar o no, no importa)")
    
    input("\nPresiona Enter cuando hayas pegado y cerrado INTERCONNECT...")
    
    try:
        ic2.close()
    except:
        pass
    
    print("\n" + "=" * 70)
    print(" ✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 70)
    print("""
El elemento 'optical relu' ahora está en tu librería de INTERCONNECT.

NUNCA más necesitarás hacer este proceso.

Ahora puedes ejecutar:
    python test_neural_network.py

Y funcionará sin problemas.
""")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n🔧 ALTERNATIVA MANUAL:")
    print(f"""
1. Abre INTERCONNECT manualmente
2. File → Open → {relu_path}
3. Selecciona el elemento 'optical relu'
4. Ctrl+C (copiar)
5. Cierra el archivo
6. En INTERCONNECT vacío: Ctrl+V (pegar)
7. Cierra INTERCONNECT

Después ejecuta: python test_neural_network.py
""")