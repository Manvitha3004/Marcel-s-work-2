import importlib.util
from pathlib import Path

p = Path(r"D:\Personal Projects\Marcel's-work-2\verification\taskB\v0.1.1\oscillator_verification_fixed.py")
spec = importlib.util.spec_from_file_location('fixed_mod', p)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('A_prime(manufactured_a, 0.0)=', mod.A_prime(mod.manufactured_a, 0.0))
print('manufactured_ap(0.0)=', mod.manufactured_ap(0.0))
print('expected=', 0.48121182505960347)
