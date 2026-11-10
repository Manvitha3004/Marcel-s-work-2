import math, numpy as np
S = np.array([1.0, 0.0, 0.0])
B = np.array([0.0, 0.0, 2.0])
dt = 1e-3
print('SxB=', np.cross(S, B))
print('Euler=', S + dt*np.cross(S, B))
ang = np.linalg.norm(B)*dt
print('Exact=', np.array([math.cos(ang), math.sin(ang), 0.0]))
