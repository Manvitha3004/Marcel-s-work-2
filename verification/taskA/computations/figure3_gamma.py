tau_osc = 0.001
for ratio in (20, 200):
    gamma = 2.0 / (ratio * tau_osc)
    print(f"ratio={ratio}, gamma={gamma}")
