"""
Operaciones matriciales y funciones matemáticas para multiplicación óptica
Incluye descomposición SVD y conversiones
"""

import numpy as np
from scipy.linalg import svd, diagsvd
import interferometer as itf
import sys
import os

# Añadir path del proyecto para importar mathfs
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import mathfs


def bs_list_to_vectors(I):
    """
    Convierte la lista de beam splitters de interferometer a vectores numpy
    
    Args:
        I: Objeto de interferómetro con BS_list
    
    Returns:
        tuple: (theta, phi, mode1, mode2) como arrays numpy
    """
    theta = np.array([bs.theta for bs in I.BS_list], dtype=float)
    phi = np.array([bs.phi for bs in I.BS_list], dtype=float)
    mode1 = np.array([bs.mode1 for bs in I.BS_list], dtype=float)
    mode2 = np.array([bs.mode2 for bs in I.BS_list], dtype=float)
    return theta, phi, mode1, mode2


def theoretical_mzi_mult(u, v):
    """
    Multiplica el vector por cada MZI teóricamente
    Usado principalmente para testing
    
    Args:
        u: Matriz unitaria
        v: Vector de entrada
    
    Returns:
        np.ndarray: Vector resultante después de multiplicación teórica
    """
    I = itf.square_decomposition(u)
    theta, phi, mode1, mode2 = bs_list_to_vectors(I)
    dim = np.shape(v)[0]
    nmzis = dim * (dim - 1) // 2

    for i in range(nmzis):
        v = mathfs.T_mn(theta[i], phi[i], int(mode1[i] - 1), int(mode2[i] - 1), dim) @ v

    return v


def decompose_matrix_svd(matrix):
    """
    Descompone una matriz usando SVD
    
    Args:
        matrix: Matriz a descomponer (puede ser no cuadrada o no unitaria)
    
    Returns:
        tuple: (U, S, Vh) - Descomposición SVD
    """
    U, S, Vh = svd(matrix)
    return U, S, Vh


def is_unitary(matrix, tolerance=1e-10):
    """
    Verifica si una matriz es unitaria
    
    Args:
        matrix: Matriz a verificar
        tolerance: Tolerancia para la comparación
    
    Returns:
        bool: True si la matriz es unitaria
    """
    return mathfs.is_unitary(matrix, tol=tolerance)


def validate_matrix_vector(matrix, vector):
    """
    Valida que la matriz y el vector sean compatibles
    
    Args:
        matrix: Matriz de multiplicación
        vector: Vector de entrada
    
    Raises:
        ValueError: Si las dimensiones no son compatibles
    """
    if len(vector.shape) != 1:
        raise ValueError(f"El vector debe ser unidimensional, tiene shape {vector.shape}")
    
    matrix_cols = matrix.shape[1]
    vector_dim = vector.shape[0]
    
    if matrix_cols != vector_dim:
        raise ValueError(
            f"Dimensiones incompatibles: matriz {matrix.shape} "
            f"no puede multiplicar vector de tamaño {vector_dim}"
        )


def compute_theoretical_result(matrix, vector):
    """
    Calcula el resultado teórico de la multiplicación matriz-vector
    
    Args:
        matrix: Matriz de multiplicación
        vector: Vector de entrada
    
    Returns:
        np.ndarray: Vector resultado teórico
    """
    return matrix @ vector