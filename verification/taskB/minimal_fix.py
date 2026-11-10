from pathlib import Path

src = Path(r"D:\Personal Projects\marcel's work\oscillator_verification.py").read_text(encoding='utf-8')
old = '''    if A is eta_A or getattr(A, "__name__", "") == "eta_A":
        a = eta_A(t_arr)
        return a * ETA * (1.0 / np.cosh(np.sin(t_arr)) ** 2) * np.cos(t_arr)
    return np.zeros_like(t_arr, dtype=float)
'''
new = '''    if A is manufactured_a or getattr(A, "__name__", "") == "manufactured_a":
        return manufactured_ap(t_arr)
    if A is eta_A or getattr(A, "__name__", "") == "eta_A":
        a = eta_A(t_arr)
        return a * ETA * (1.0 / np.cosh(np.sin(t_arr)) ** 2) * np.cos(t_arr)
    return np.zeros_like(t_arr, dtype=float)
'''
fixed = src.replace(old, new)
out = Path('d:/Personal Projects/Marcel\'s-work-2/verification/taskB/v0.1.1/oscillator_verification_fixed.py')
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(fixed, encoding='utf-8')
print('WROTE', out)
print('---DIFF---')
import difflib
print(''.join(difflib.unified_diff(src.splitlines(True), fixed.splitlines(True), fromfile='original', tofile='minimal_fix')))
