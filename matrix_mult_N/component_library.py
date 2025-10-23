"""
Librería de componentes fotónicos auxiliares
"""

import numpy as np


def amplifier(name, gain, ic, xpos=0, ypos=0, noise=False):
    """
    Crea un amplificador óptico
    
    Args:
        name: Nombre del amplificador
        gain: Ganancia lineal
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición
        noise: Si incluir ruido
    """
    ic.addelement("Optical Amplifier")
    ic.set("name", name)
    ic.set("gain", 10 * np.log10(gain))  # Convertir a dB
    ic.set("x position", xpos)
    ic.set("y position", ypos)
    
    if not noise:
        ic.setnamed(name, "noise", 0)