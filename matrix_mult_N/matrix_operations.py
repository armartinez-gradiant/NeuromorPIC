"""
Operaciones matriciales para fotónica
Incluye validaciones, descomposición SVD, etc.
"""

import numpy as np
from typing import Tuple, Optional
from scipy.linalg import svd
from . import mathfs


def theoretical_mzi_mult(u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """
    Calcula la multiplicación teórica U @ v
    
    Args:
        u: Matriz unitaria
        v: Vector de entrada
        
    Returns:
        Vector resultado de U @ v
    """
    return u @ v


def decompose_matrix_svd(matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Descompone una matriz usando SVD: A = U Σ V†
    
    Args:
        matrix: Matriz a descomponer
        
    Returns:
        Tuple (U, Sigma, Vh) donde:
            - U: Matriz unitaria (m×m)
            - Sigma: Valores singulares (diagonal)
            - Vh: Matriz unitaria conjugada transpuesta (n×n)
    """
    U, s, Vh = svd(matrix)
    Sigma = np.diag(s)
    
    return U, Sigma, Vh


def is_unitary(matrix: np.ndarray, tol: float = 1e-10) -> bool:
    """
    Verifica si una matriz es unitaria (U†U = I)
    
    Args:
        matrix: Matriz a verificar
        tol: Tolerancia para la comparación
        
    Returns:
        True si la matriz es unitaria, False en caso contrario
    """
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        return False
    
    n = matrix.shape[0]
    identity = np.eye(n)
    
    product = matrix.conj().T @ matrix
    
    return np.allclose(product, identity, atol=tol)


def validate_matrix_vector(matrix: np.ndarray, vector: np.ndarray) -> None:
    """
    Valida que las dimensiones de matriz y vector sean compatibles
    
    Args:
        matrix: Matriz de transformación
        vector: Vector de entrada
        
    Raises:
        ValueError: Si las dimensiones no son compatibles
    """
    if matrix.ndim != 2:
        raise ValueError(f"La matriz debe ser 2D, recibida: {matrix.ndim}D")
    
    if vector.ndim != 1:
        raise ValueError(f"El vector debe ser 1D, recibido: {vector.ndim}D")
    
    m, n = matrix.shape
    if n != len(vector):
        raise ValueError(
            f"Dimensiones incompatibles: matriz {m}×{n}, vector {len(vector)}"
        )


def compute_theoretical_result(matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    """
    Calcula el resultado teórico de la multiplicación matriz-vector
    
    Args:
        matrix: Matriz de transformación
        vector: Vector de entrada
        
    Returns:
        Vector resultado de matrix @ vector
    """
    validate_matrix_vector(matrix, vector)
    return matrix @ vector


def bs_list_to_vectors(bs_list):
    """
    Convierte una lista de beamsplitters en vectores de thetas, phis y modos
    
    Args:
        bs_list: Lista de objetos beamsplitter del módulo interferometer
        
    Returns:
        Tuple (thetas, phis, mode1, mode2): Vectores numpy con los ángulos y modos
        Nota: mode1 y mode2 son arrays de índices (no se usan en el código actual)
    """
    thetas = np.array([bs.theta for bs in bs_list], dtype=float)
    phis = np.array([bs.phi for bs in bs_list], dtype=float)
    # mode1 y mode2 no se usan realmente, devolver arrays de índices
    mode1 = np.arange(len(bs_list), dtype=int)
    mode2 = np.arange(len(bs_list), dtype=int)
    return thetas, phis, mode1, mode2