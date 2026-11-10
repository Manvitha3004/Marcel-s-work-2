L = 100
Ntraj = 100
Np = 10**4
for steps in (20, 40):
    print(f"steps={steps}: {L**2 * Ntraj * Np * steps:.3e}")

# pre-equilibration periods for cited gamma values
for gamma, tau_osc, dt in [(1e-4, 0.2, 0.005), (1e-3, 0.2, 0.005), (10.0, 0.001, 5e-05), (100.0, 0.001, 5e-05)]:
    periods = (5.0 / gamma) / tau_osc
    steps = (5.0 / gamma) / dt
    print(f"gamma={gamma}, periods={periods}, steps={steps}")
