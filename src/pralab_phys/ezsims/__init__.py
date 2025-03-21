import numpy as np
from scipy.special import ellipk
from scipy.optimize import brentq

def calc_coplanar_gap(S, eps_r, h, Z=50) -> float:
    """
    Parameters:
    - S: width of the signal conductor
    - eps_r: relative permittivity of the substrate
    - h: height of the substrate
    - Z: target characteristic impedance (default 50 Ohms)

    Returns:
    - Gap width
    """
    
    def effective_permittivity(k):
        """
        Calculate the effective permittivity for a given k.
        
        Parameters:
        - k: ratio of gap width to total width
        
        Returns:
        - Effective permittivity as a float
        """
        gap_width = (S/k - S) / 2
        part_of_formula = np.tanh(1.785 * np.log(h/gap_width) + 1.75)
        correction_factor = k * gap_width / h * (0.04 - 0.7 * k + 0.01 * (1 - 0.1 * eps_r) * (0.25 + k))
        return (eps_r + 1) / 2 * (part_of_formula + correction_factor)

    def impedance_difference(k):
        """
        Calculate the difference between the calculated and target impedance.
        
        Parameters:
        - k: ratio of gap width to total width
        
        Returns:
        - Difference in impedance as a float
        """
        effective_eps = effective_permittivity(k)**0.5
        k_complement = (1 - k**2)**0.5
        calculated_impedance = 30 * np.pi / effective_eps * ellipk(k_complement) / ellipk(k)
        return calculated_impedance - Z

    # Find the ratio k that results in the target impedance Z
    k_initial_guess = brentq(effective_permittivity, 0.0001, 0.9999) + 0.00001
    k_optimal = brentq(impedance_difference, k_initial_guess, 0.9999)
    
    # Calculate and return the optimal gap width based on the optimal k
    return (S / k_optimal - S) / 2

# Example usage
S = 3.0  # width of the signal conductor
eps_r = 2.2  # relative permittivity of the substrate
h = 1.5  # height of the substrate
Z_target = 50  # target characteristic impedance
gap_width = gen_coplanar_gap(S, eps_r, h, Z_target)
print(f"Optimal gap width: {gap_width}")