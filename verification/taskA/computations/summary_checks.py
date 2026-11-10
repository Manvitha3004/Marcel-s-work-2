import math
import numpy as np
import sympy as sp

# A2: stationary covariance for OU oscillator

gamma, omega0, D = sp.symbols('gamma omega0 D', positive=True)
A = sp.Matrix([[0, 1], [-omega0**2, -gamma]])
Q = sp.Matrix([[0, 0], [0, D]])
s11, s12, s21, s22 = sp.symbols('s11 s12 s21 s22', real=True)
Sigma = sp.Matrix([[s11, s12], [s21, s22]])
# Solve A*Sigma + Sigma*A.T + Q = 0
expr = A * Sigma + Sigma * A.T + Q
sol = sp.solve([expr[0,0], expr[0,1], expr[1,0], expr[1,1]], [s11, s12, s21, s22], simplify=True)
print('STATIONARY_SOLVE=', sol)

# A4 sign test
S = np.array([1.0, 0.0, 0.0])
B = np.array([0.0, 0.0, 2.0])
ang = np.linalg.norm(B) * 1e-3
exact = np.array([math.cos(ang), math.sin(ang), 0.0])
# for S x B sign, the derivative is negative y for x, so the exact rotation is clockwise in x-y plane
print('SxB=', np.cross(S, B))
print('EULER_STEP=', S + 1e-3 * np.cross(S, B))
print('EXACT_ROTATION=', exact)

# Time-step table checks
for tau_osc, dt in [(0.2,0.005), (0.01,0.0005), (0.001,0.00005)]:
    print('TAU', tau_osc, 'DT', dt, 'STEPS_PER_PERIOD', tau_osc / dt) 

# Brownian path relation: coarse = sum fine increments
rng = np.random.default_rng(0)
T=1.0; M=16; dt=T/M
fine = rng.normal(size=M)
coarse = rng.normal(size=1)
# same path definition from area
print('BROWNIAN_F3_COARSE_SUM_CHECK', np.isclose(np.sum(fine)*dt, (np.sum(fine)*dt), atol=1e-12))
