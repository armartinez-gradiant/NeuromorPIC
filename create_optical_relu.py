"""
Creador de Elemento "Optical ReLU" para INTERCONNECT
Este script crea automáticamente el elemento personalizado necesario
para las redes neuronales ópticas
"""

import sys
import os

print("=" * 70)
print("CREADOR DE ELEMENTO: Optical ReLU")
print("=" * 70)

# Cargar lumapi
try:
    try:
        from lumerical_path_detector import auto_detect_and_load_lumapi
        lumapi = auto_detect_and_load_lumapi()
        print("✅ lumapi cargado con auto-detección")
    except ImportError:
        sys.path.append(r"C:\Program Files\Lumerical\v251\api\python")
        import lumapi
        print("✅ lumapi cargado con path manual")
except ImportError as e:
    print(f"❌ Error: No se pudo cargar lumapi: {e}")
    sys.exit(1)

print("\n" + "─" * 70)
print("INSTRUCCIONES PARA CREAR 'Optical ReLU' MANUALMENTE")
print("─" * 70)

instructions = """
Lamentablemente, los elementos scripted personalizados no se pueden crear
programáticamente desde Python. Debes crearlos manualmente en INTERCONNECT.

PASOS PARA CREAR "Optical ReLU":

1. Abre Lumerical INTERCONNECT

2. Ve al menú:
   Element Library → Create New → Scripted Element

3. En el diálogo que aparece:
   - Name: optical relu
   - Type: Unidirectional (muy importante)
   - Ports: 1 input, 1 output
   
4. Copia el siguiente código en el editor del elemento:

"""

relu_code = '''%% Optical ReLU Implementation
%% Aplica rectificación a la amplitud de la señal óptica

function [output] = optical_relu(input)
    % Obtener señal de entrada
    signal_in = getresult("input", "signal");
    
    % Extraer amplitud y fase
    amplitude = abs(signal_in);
    phase = angle(signal_in);
    
    % ReLU: rectificar solo amplitudes negativas a cero
    % (En óptica, la "amplitud negativa" se interpreta como amplitud baja)
    threshold = 0;
    rectified = max(threshold, amplitude);
    
    % Reconstruir señal compleja
    signal_out = rectified .* exp(1i * phase);
    
    % Enviar señal de salida
    setresult("output", signal_out);
end
'''

alternative_code = '''%% Optical ReLU - Versión Simplificada
%% Para usar si la versión anterior da problemas

% Obtener señal
in_signal = get("input");

% Aplicar ReLU a la intensidad
intensity = abs(in_signal).^2;
intensity_relu = max(0, intensity);

% Reconstruir con fase original
phase = angle(in_signal);
amplitude_out = sqrt(intensity_relu);

% Salida
out_signal = amplitude_out .* exp(1i * phase);
set("output", out_signal);
'''

print(instructions)
print("─" * 70)
print("CÓDIGO DEL ELEMENTO (Opción 1 - Preferida):")
print("─" * 70)
print(relu_code)

print("\n" + "─" * 70)
print("CÓDIGO ALTERNATIVO (Opción 2 - Si la primera falla):")
print("─" * 70)
print(alternative_code)

print("\n" + "─" * 70)
print("5. Guarda el elemento (botón Save)")
print("6. Cierra el editor")
print("7. El elemento 'optical relu' ahora estará disponible en tu librería")
print("─" * 70)

print("\n" + "=" * 70)
print("VERIFICACIÓN")
print("=" * 70)

try:
    # Abrir INTERCONNECT para facilitar el proceso
    print("\n🔄 Abriendo INTERCONNECT para que puedas crear el elemento...")
    ic = lumapi.INTERCONNECT(hide=False)
    print("✅ INTERCONNECT abierto")
    
    print("\n📋 Ahora sigue los pasos de arriba en el INTERCONNECT que se abrió")
    print("   Una vez creado el elemento, cierra INTERCONNECT y el test funcionará.")
    
    print("\n💡 TIPS:")
    print("   - El elemento debe llamarse EXACTAMENTE 'optical relu' (minúsculas)")
    print("   - Tipo: Unidirectional")
    print("   - Si no funciona el primer código, prueba el alternativo")
    print("   - Guarda tu librería después de crear el elemento")
    
    input("\n[Presiona Enter cuando hayas terminado de crear el elemento]")
    
    ic.close()
    print("✅ INTERCONNECT cerrado")
    
except Exception as e:
    print(f"⚠️  Error: {e}")

print("\n" + "=" * 70)
print("RESUMEN")
print("=" * 70)
print("""
✅ Pasos completados:
   1. Instrucciones mostradas
   2. Código proporcionado
   
⏭️  Siguiente paso:
   Ejecuta: python test_neural_network.py
   
   Si todo está correcto, el test creará y simulará la red neuronal.
""")

print("🎉 Listo para continuar!\n")