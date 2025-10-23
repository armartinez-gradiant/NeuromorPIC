#### Some mathematic oriented functions will be here to keep the code tidy
import numpy as np
from typing import Optional, Literal, Union
import cmath


def random_vector(
    n: int,
    as_complex: bool = False,
    distribution: Literal['normal', 'uniform'] = 'normal',
    scale: float = 1.0,
    seed: Optional[int] = None,
    dtype: Optional[Union[np.dtype, str]] = None,
    normalize: Optional[Union[str, float]] = None,
) -> np.ndarray:
    """
    Generate a random vector (real or complex).

    Parameters
    ----------
    n : int
        Length of the vector.
    as_complex : bool, default False
        If True, returns a complex vector; otherwise real.
    distribution : {'normal', 'uniform'}, default 'normal'
        Distribution of samples:
          - 'normal': Gaussian.
              * Real: N(0, scale^2)
              * Complex: Re, Im ~ N(0, (scale^2)/2) → E[|z|^2] = scale^2 (circularly symmetric).
          - 'uniform': Each component drawn independently from [-scale, scale].
            (For complex, both real and imaginary parts use this range.)
    scale : float, default 1.0
        Scale parameter (std for 'normal'; half-range for 'uniform').
    seed : int or None, default None
        Seed for reproducibility.
    dtype : numpy dtype or str or None, default None
        Output dtype. Defaults to float64 for real and complex128 for complex.
    normalize : None, 'l2'/'unit', or float, default None
        Optional post-scaling:
          - 'l2' or 'unit': scale the vector to unit L2 norm.
          - float value p: scale so that mean power (mean(|x|^2)) equals p.

    Returns
    -------
    np.ndarray
        A vector of shape (n,) of type float or complex.
    """
    rng = np.random.default_rng(seed)

    if distribution == 'normal':
        if as_complex:
            s = scale / np.sqrt(2.0)  # so E|z|^2 = scale^2
            x = rng.normal(0.0, s, size=n)
            y = rng.normal(0.0, s, size=n)
            out = x + 1j * y
        else:
            out = rng.normal(0.0, scale, size=n)
    elif distribution == 'uniform':
        if as_complex:
            x = rng.uniform(-scale, scale, size=n)
            y = rng.uniform(-scale, scale, size=n)
            out = x + 1j * y
        else:
            out = rng.uniform(-scale, scale, size=n)
    else:
        raise ValueError("distribution must be 'normal' or 'uniform'")

    # Default dtypes
    if dtype is None:
        dtype = np.complex128 if as_complex else np.float64
    out = out.astype(dtype, copy=False)

    # Optional normalization
    if normalize is not None:
        if normalize in ('l2', 'unit'):
            norm = np.linalg.norm(out)
            if norm > 0:
                out = out / norm
        elif isinstance(normalize, (int, float)):
            target_power = float(normalize)
            power = np.mean(np.abs(out) ** 2)
            if power > 0:
                out = out * np.sqrt(target_power / power)
        else:
            raise ValueError("normalize must be None, 'l2'/'unit', or a number (target average power).")

    return out

from typing import Iterable, List, Tuple, Union
import cmath, math

def complex_to_polar(
    vec: Iterable[complex],
    mod_only_if_zero_phase: bool = False,
    zero_tol: float = 1e-12,
    square_modulus: bool = False
) -> List[Union[float, Tuple[float, float]]]:
    """
    Convert complex numbers to polar form.

    If mod_only_if_zero_phase is True and the phase is (near) zero
    within zero_tol, return only the modulus for that element.
    Otherwise, return (modulus, phase) where phase is in (-pi, pi].

    If square_modulus is True, replace the modulus r by r**2 in the
    returned value(s) while preserving the original phase.

    Note: When mod_only_if_zero_phase=True, the output list may contain
    a mix of floats (modulus only) and (modulus, phase) tuples.

    Warning: Enabling square_modulus does *not* correspond to squaring
    the complex number (which would double the phase). It only squares
    the magnitude while keeping the original phase.
    """
    result: List[Union[float, Tuple[float, float]]] = []
    for z in vec:
        modulus, phase = cmath.polar(z)  # (r, phi) with phi in (-pi, pi]
        r_out = modulus * modulus if square_modulus else modulus
        if mod_only_if_zero_phase and math.isclose(phase, 0.0, abs_tol=zero_tol):
            result.append(r_out)
        else:
            result.append((r_out, phase))
    return result



def dBm_to_W(x):
    return 10**(x/10)/1000


def is_unitary(U, tol=1e-10, strict=False):
    """
    Check if a matrix U is unitary (U†U = I and UU† = I within tolerance).

    Parameters
    ----------
    U : array-like
        Input matrix (will be converted to a NumPy array).
    tol : float, optional
        Absolute tolerance for closeness checks (default: 1e-10).
    strict : bool, optional
        If True, raise ValueError when U is not square.
        If False, return False when U is not square.

    Returns
    -------
    bool
        True if U is unitary within tolerance, else False.

    Raises
    ------
    ValueError
        If strict is True and U is not 2D or not square.
    """
    U = np.asarray(U)

    # Must be 2D
    if U.ndim != 2:
        raise ValueError("U must be a 2D array/matrix.")

    m, n = U.shape
    # Must be square to be unitary
    if m != n:
        if strict:
            raise ValueError(f"Unitary matrices must be square (got {m}x{n}).")
        return False

    # Check both U†U = I and UU† = I (more robust numerically)
    I = np.eye(n, dtype=U.dtype)
    return (np.allclose(U.conj().T @ U, I, atol=tol) and
            np.allclose(U @ U.conj().T, I, atol=tol))


def T_mn(theta, phi, m, n, N):
    """
    Creates the matrix T^(m,n)(theta, phi) of size N x N.

    Parameters:
    - theta: angle theta (in radians)
    - phi: angle phi (in radians)
    - m, n: indices (0-based) of the 2x2 submatrix to modify
    - N: dimension of the square matrix (N x N)

    Returns:
    - A complex numpy matrix of shape (N, N)
    """
    # Initialize an identity matrix of size N x N
    T = np.eye(N, dtype=complex)

    # Calculate the complex exponential e^(i * phi)
    eiphi = np.exp(1j * phi)

    # Modify the 2x2 submatrix at rows and columns m and n
    T[m, m] = eiphi * np.cos(theta)
    T[m, n] = -np.sin(theta)
    T[n, m] = eiphi * np.sin(theta)
    T[n, n] = np.cos(theta)

    return T