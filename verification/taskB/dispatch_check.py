import importlib.util
from pathlib import Path

module_path = Path(r"D:\Personal Projects\marcel's work\oscillator_verification.py")
spec = importlib.util.spec_from_file_location('oscillator_verification', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

print('A_prime(manufactured_a, 0.0)=', module.A_prime(module.manufactured_a, 0.0))
print('manufactured_ap(0.0)=', module.manufactured_ap(0.0))
print('expected=', 0.48121182505960347)
