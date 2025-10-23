"""
Generadores de componentes individuales para circuitos fotónicos
Incluye MZIs, phase shifters, amplificadores, etc.
"""

import numpy as np


def generate_mzi(theta, phi, i, j, k, ic, xpos=0, ypos=0, diagonal=False):
    """
    Genera un MZI (Mach-Zehnder Interferometer) individual
    
    Args:
        theta: Ángulo theta del MZI
        phi: Ángulo phi del MZI
        i, j, k: Índices de posición en el mesh
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición en el layout
        diagonal: Si es parte de un mesh diagonal
    """
    # Coupler 1
    ic.addelement("Waveguide Coupler Unidirectional")
    ic.set("name", f"coupler{i}{j}{k}1")
    ic.set("x position", xpos)
    ic.set("y position", ypos)
    ic.set("coupling coefficient 1", np.sin(theta / 2) ** 2)

    # Phase shifter (phi)
    ic.addelement("Optical Phase Shift Unidirectional")
    ic.set("name", f"phi{i}{j}{k}")
    ic.set("phase shift", phi)
    ic.set("x position", xpos + 250)
    ic.set("y position", ypos)

    # Coupler 2
    ic.addelement("Waveguide Coupler Unidirectional")
    ic.set("name", f"coupler{i}{j}{k}2")
    ic.set("x position", xpos + 500)
    ic.set("y position", ypos)
    ic.set("coupling coefficient 1", np.sin(theta / 2) ** 2)

    # Phase shifters de salida (otheta)
    ic.addelement("Optical Phase Shift Unidirectional")
    ic.set("name", f"otheta{i}{j}{k}1")
    ic.set("x position", xpos + 700)
    ic.set("y position", ypos)

    if not diagonal:
        ic.addelement("Optical Phase Shift Unidirectional")
        ic.set("name", f"otheta{i}{j}{k}2")
        ic.set("x position", xpos + 700)
        ic.set("y position", ypos + 100)

    # Conexiones internas del MZI
    ic.connect(f"coupler{i}{j}{k}1", "output 1", f"phi{i}{j}{k}", "input")
    ic.connect(f"phi{i}{j}{k}", "output", f"coupler{i}{j}{k}2", "input 1")
    ic.connect(f"coupler{i}{j}{k}1", "output 2", f"coupler{i}{j}{k}2", "input 2")
    ic.connect(f"coupler{i}{j}{k}2", "output 1", f"otheta{i}{j}{k}1", "input")
    
    if not diagonal:
        ic.connect(f"coupler{i}{j}{k}2", "output 2", f"otheta{i}{j}{k}2", "input")


def redefine_MZI(i, j, k, theta, phi, ic, delta1=0, delta2=0):
    """
    Redefine los parámetros de un MZI existente
    
    Args:
        i, j, k: Índices del MZI
        theta, phi: Nuevos ángulos
        ic: Handle de INTERCONNECT
        delta1, delta2: Fases de salida
    """
    ic.setnamed(f"coupler{i}{j}{k}1", "coupling coefficient 1", np.sin(theta / 2) ** 2)
    ic.setnamed(f"coupler{i}{j}{k}2", "coupling coefficient 1", np.sin(theta / 2) ** 2)
    ic.setnamed(f"phi{i}{j}{k}", "phase shift", phi)
    ic.setnamed(f"otheta{i}{j}{k}1", "phase shift", delta1)
    ic.setnamed(f"otheta{i}{j}{k}2", "phase shift", delta2)


def mzi_diagonal(v, k, ic, xpos=0, ypos=0):
    """
    Genera un mesh diagonal de MZIs (para matriz diagonal en SVD)
    
    Args:
        v: Vector diagonal
        k: Índice de capa
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    dim = np.shape(v)[0]
    theta = np.zeros(dim)
    
    for i in range(dim):
        if abs(v[i]) <= 1:
            theta[i] = np.arccos(v[i])
        else:
            theta[i] = 0
    
    for i in range(dim):
        generate_mzi(theta[i], phi=0, i=i, j=0, k=k, ic=ic, 
                    xpos=xpos, ypos=ypos + i * 300, diagonal=True)


def generate_amplifiers(d, k, ic, xpos=0, ypos=0):
    """
    Genera amplificadores ópticos
    
    Args:
        d: Vector de ganancias
        k: Índice de capa
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    from .component_library import amplifier
    
    dim = np.shape(d)[0]
    for i in range(dim):
        amplifier(f"amp{i}{k}", d[i], ic, xpos=xpos, ypos=ypos + i * 300, noise=False)


def generate_non_linearities(dim, k, ic, xpos=0, ypos=0):
    """
    Genera capa de no linealidades (ReLU óptico)
    Requiere tener en la librería el elemento "Optical Relu"
    
    Args:
        dim: Número de canales
        k: Índice de capa
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición base
    """
    for i in range(dim):
        ic.addelement("optical relu")
        ic.set("name", f"relu{i}{k}")
        ic.set("x position", xpos)
        ic.set("y position", ypos + i * 200)


def laser(name, power, phase, ic, xpos=0, ypos=0):
    """
    Genera un láser CW
    
    Args:
        name: Nombre del láser
        power: Potencia de salida
        phase: Fase inicial
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición
    """
    ic.addelement("CW Laser")
    ic.set("name", name)
    ic.set("power", power)
    ic.set("phase", phase)
    ic.set("x position", xpos)
    ic.set("y position", ypos)


def power_meter(name, ic, xpos=0, ypos=0):
    """
    Genera un medidor de potencia
    
    Args:
        name: Nombre del medidor
        ic: Handle de INTERCONNECT
        xpos, ypos: Posición
    """
    ic.addelement("Optical Power Meter")
    ic.set("name", name)
    ic.set("x position", xpos)
    ic.set("y position", ypos)