"""
Semiconductor Physics Module
============================

This module contains functions for semiconductor physics calculations.
"""

import numpy as _np

def intrinsic_carrier_concentration(Nc, Nv, Eg, TL, k=8.617333262e-5):
    """
    Computes the intrinsic carrier concentration (n_ie).

    Parameters
    ----------
    Nc : float
        Effective density of states in the conduction band.
    Nv : float
        Effective density of states in the valence band.
    Eg : float
        Band gap energy (in eV).
    TL : float
        Lattice temperature (in Kelvin).
    k : float, optional
        Boltzmann constant (in eV/K), default is 8.617333262e-5 eV/K.

    Returns
    -------
    float
        Intrinsic carrier concentration (n_ie).

    Examples
    --------
    >>> intrinsic_carrier_concentration(1e19, 1e19, 1.12, 300)
    1.45e10
    """
    return _np.sqrt(Nc * Nv) * _np.exp(-Eg / (2 * k * TL))

# Example usage
# result = intrinsic_carrier_concentration(1e19, 1e19, 1.12, 300)
# print(result)
