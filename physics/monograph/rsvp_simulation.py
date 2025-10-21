"""
rsvp_simulation.py
1D RSVP–Observation Simulator
Implements the coupled scalar (Phi), vector (v), and entropy (S) fields with
observation back–action (Psi). Used in Reflexive Field Dynamics, Chapter 10.
"""

import numpy as np

# --- Spatial grid ---
L = 2 * np.pi
N = 256
dx = L / N
x = np.linspace(0, L, N, endpoint=False)

# --- Parameters ---
alpha0, beta0, gamma0 = 1.0, 1.0, 0.0      # base RSVP coefficients
alpha, beta, kappa, rho = 1.0, 1.0, 1.0, 0.1
kappa_Psi = 0.5                            # observation gain
sigma_learn = 0.0
dt = 1e-3
T = 2.0
steps = int(T / dt)

# --- Initial conditions ---
Phi = np.sin(x)
v = np.zeros_like(x)
S = 0.5 * np.cos(2 * x)
Psi_star = np.zeros_like(x)

# --- Spectral operators (periodic) ---
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
lap = -(k ** 2)

def grad(f): return np.fft.ifft(ik * np.fft.fft(f)).real
def div(f):  return grad(f)  # 1D
def laplacian(f): return np.fft.ifft(lap * np.fft.fft(f)).real

# --- Main simulation loop ---
for n in range(steps):
    # Observation residual
    r = beta * Phi + alpha * S - kappa * div(v) + rho * laplacian(S) - Psi_star

    # Semi-implicit update for S
    rhs_S = S + dt * (-div(Phi * v) + sigma_learn - kappa_Psi * (alpha * r))
    S_hat = np.fft.fft(rhs_S) / (1 + dt * kappa_Psi * rho * (-lap))
    S = np.fft.ifft(S_hat).real

    # Explicit Phi, v updates
    Phi += dt * (alpha0 * div(v) - beta0 * S - kappa_Psi * beta * r)
    v += dt * (-grad(Phi) - kappa_Psi * kappa * grad(r))

    if n % 100 == 0:
        energy = np.mean(Phi ** 2 + v ** 2 + S ** 2)
        print(f"t={n * dt:.3f}, ⟨Φ²+v²+S²⟩={energy:.4e}")

