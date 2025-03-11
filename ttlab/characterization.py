"""
Semiconductor Characterization formula
"""

import numpy as _np
import matplotlib.pyplot as _plt

def calculate_ideality_factor(V, I, V_range, temperature=300, plot=False):
    """
    Calculate the ideality factor of a diode from voltage and current data.

    Parameters:
        V (array-like): Voltage data (V).
        I (array-like): Current data (A).
        temperature (float): Temperature in Kelvin.
        V_range (tuple): Voltage range for fitting (min_V, max_V).
        plot (bool): Whether to plot ln(I) vs V with the fitted line.

    Returns:
        float: Ideality factor (n).
    """
    # Constants
    q = 1.602e-19  # Elementary charge (C)
    k = 1.38e-23   # Boltzmann constant (J/K)
    
    # Filter data within the specified voltage range
    mask = (V >= V_range[0]) & (V <= V_range[1])
    V_filtered = V[mask]
    I_filtered = I[mask]
    
    # Ensure no zero or negative currents for log calculation
    I_filtered = I_filtered[I_filtered > 0]
    V_filtered = V_filtered[:len(I_filtered)]
    
    # Calculate ln(I)
    ln_I = _np.log(I_filtered)
    
    # Perform linear regression on ln(I) vs V
    slope, intercept = _np.polyfit(V_filtered, ln_I, 1)
    
    # Calculate ideality factor
    n = q / (slope * k * temperature)
    
    # Plotting
    if plot:
        _plt.figure(figsize=(8, 6))
        _plt.plot(V, _np.log(I), 'o', label='Data')
        _plt.plot(V_filtered, slope * V_filtered + intercept, '-', label=f'Fit (n={n:.2f})',linewidth=3)
        _plt.title('Ideality Factor Calculation', fontsize=16)
        _plt.xlabel('Voltage (V)', fontsize=14)
        _plt.ylabel('ln(Current (I))', fontsize=14)
        _plt.grid(True, linestyle='--', linewidth=0.5)
        _plt.legend(fontsize=12)
        _plt.tight_layout()
        _plt.show()
    
    return n