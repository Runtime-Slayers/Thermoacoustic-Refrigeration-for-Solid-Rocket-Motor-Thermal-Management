"""
Thermoacoustic Refrigeration for Solid Rocket Motor Thermal Management
Standing-Wave Heat Pump Design Using Rott's Linear Theory
"""
import numpy as np

def rott_standing_wave(f=400.0, T_mean=800.0, p0=5e6, x_stack=0.1,
                       L_stack=0.05, gas="N2"):
    """
    Rott linear thermoacoustic model for stack performance.
    Returns: acoustic power, heat pumped per cycle
    """
    # Nitrogen-like properties at high T
    gamma = 1.4
    R = 296.8  # J/(kg·K) N2
    rho = p0 / (R * T_mean)
    c   = np.sqrt(gamma * p0 / rho)
    lam = c / f  # wavelength
    omega = 2 * np.pi * f

    # Stack positioned at x_stack from closed end
    # Pressure and velocity at stack centre (quarter-wave resonator)
    p1_mag = p0 * 0.01   # drive ratio 1%
    u1_mag = p1_mag / (rho * c) * np.sin(2 * np.pi * x_stack / lam)

    # Temperature gradient (Rott)
    kappa = 0.03  # W/(m·K) thermal conductivity
    dT_dx_crit = T_mean * omega / (2 * c)   # critical gradient
    # Imposed temperature difference
    dT_dx = dT_dx_crit * 0.8  # operate below critical

    # Heat flux (simplified Rott)
    A_stack = np.pi * (0.005)**2  # cross-section 5mm radius
    Q_cold = 0.5 * rho * u1_mag**2 * T_mean * L_stack / (2 * f * kappa) * A_stack
    W_acoustic = 0.5 * p1_mag * u1_mag * A_stack * np.cos(0)

    COP = abs(Q_cold) / (abs(W_acoustic) + 1e-9)
    return {"Q_cold_W": float(Q_cold), "W_acoustic_W": float(W_acoustic),
            "COP": float(COP), "f_Hz": f, "c_ms": c, "dT_dx": dT_dx}

def optimize_stack_position(f=400, N=50, T_mean=800, p0=5e6):
    positions = np.linspace(0.01, 0.24, N)
    results = [rott_standing_wave(f, T_mean, p0, x) for x in positions]
    cops = [r["COP"] for r in results]
    best_idx = np.argmax(cops)
    return positions[best_idx], results[best_idx]

def regenerator_effectiveness(mesh_density=90, wire_d=50e-6, T_hot=900, T_cold=400):
    """Estimate regenerator thermal effectiveness."""
    vol_void = 1 - np.pi / 4 * (wire_d * mesh_density)**2
    vol_void = max(0.1, min(0.9, vol_void))
    NTU = 15 * vol_void   # simplified
    eff = NTU / (NTU + 1)
    return float(eff)

if __name__ == "__main__":
    print("Running Rott linear theory thermoacoustic model...")
    result = rott_standing_wave()
    print(f"  Frequency     : {result['f_Hz']} Hz")
    print(f"  Speed of sound: {result['c_ms']:.1f} m/s")
    print(f"  Q_cold        : {result['Q_cold_W']:.4f} W")
    print(f"  W_acoustic    : {result['W_acoustic_W']:.4f} W")
    print(f"  COP           : {result['COP']:.3f}")
    best_x, best_r = optimize_stack_position()
    print(f"  Optimal stack pos: {best_x*100:.1f} cm  COP={best_r['COP']:.3f}")
    eff = regenerator_effectiveness()
    print(f"  Regenerator effectiveness: {eff:.3f}")
    print("Thermoacoustic design complete.")
