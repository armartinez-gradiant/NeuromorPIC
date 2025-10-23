"""
Paquete para multiplicación matricial óptica
"""

from .main import (
    create_matrix_icp,
    MZI_multiplication,
    general_MZI_multiplication
)

from .matrix_operations import (
    theoretical_mzi_mult,
    decompose_matrix_svd,
    is_unitary,
    validate_matrix_vector,
    compute_theoretical_result
)

from .circuit_builder import (
    mzi_mesh,
    general_mzi_mesh,
    neural_network_layer,
    optical_neural_network,
    generate_lasers,
    redefine_lasers,
    generate_power_meters,
    get_results,
    redefine_mesh,
    connect_inputs_to_mesh
)

from .mzi_generator import (
    generate_mzi,
    mzi_diagonal,
    generate_amplifiers,
    generate_non_linearities
)

from . import mathfs

__all__ = [
    'create_matrix_icp',
    'MZI_multiplication',
    'general_MZI_multiplication',
    'theoretical_mzi_mult',
    'decompose_matrix_svd',
    'is_unitary',
    'validate_matrix_vector',
    'compute_theoretical_result',
    'mzi_mesh',
    'general_mzi_mesh',
    'neural_network_layer',
    'optical_neural_network',
    'generate_lasers',
    'redefine_lasers',
    'generate_power_meters',
    'get_results',
    'redefine_mesh',
    'connect_inputs_to_mesh',
    'generate_mzi',
    'mzi_diagonal',
    'generate_amplifiers',
    'generate_non_linearities',
    'mathfs'
]