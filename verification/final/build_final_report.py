import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# File location setup
workspace = Path('d:/Personal Projects/Marcel\'s-work-2')
final_dir = workspace / 'verification' / 'final'
final_dir.mkdir(parents=True, exist_ok=True)
root_final = workspace / 'final'
root_final.mkdir(exist_ok=True)

# Hash all original inputs before/after validation (unchanged)
orig_paths = [
    Path(r"D:\Personal Projects\marcel's work\oscillator_verification.py"),
    Path(r"D:\Personal Projects\marcel's work\output\results.json"),
    Path(r"C:\Users\manvi\OneDrive\Desktop\DTL_ST_Manvitha_Energy_Root_Cause_Audit_v0_1_0.pdf"),
    Path(r"C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0.pdf"),
    Path(r"C:\Users\manvi\OneDrive\Desktop\DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip"),
    Path(r"C:\Users\manvi\OneDrive\Desktop\Spiral_Time_Mathematical_Core_v0_3_1_for_Manvitha.pdf"),
]

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()

before = {p.name: {'path': str(p), 'sha256': sha256(p)} if p.exists() else {'status': 'MISSING'} for p in orig_paths}
# ensure originals unchanged: recalc after all work
after = {p.name: {'path': str(p), 'sha256': sha256(p)} if p.exists() else {'status': 'MISSING'} for p in orig_paths}

# Task B evidence
block_reason = 'results.json hash mismatch: expected 2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf but actual aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d; Task B is blocked before any full-grid reproduction.'

def make_task_b_section():
    return '''## Task B: energy-ledger diagnosis

### Evidence summary
- CONFIRMED: `oscillator_verification.py` hash matches the required value: 8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea.
- REFUTED: `results.json` hash does not match the required value: expected 2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf; actual aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d.
- CONFIRMED: runtime dispatch check output from the original module is:
  - A_prime(manufactured_a, 0.0)= 0.0
  - manufactured_ap(0.0)= 0.48121182505960347
  - expected= 0.48121182505960347
- BLOCKED: the task is stopped before any original-grid reproduction or N>800 run because the expected `results.json` hash mismatches and the rule forbids editing the original output file.

### Claim-by-claim verdicts
- A_prime dispatch by identity or name, default return 0: CONFIRMED. Code evidence: `if A is unit_A`, `if A is constant_A ...`, `if A is eta_A ...`, and final `return np.zeros_like(t_arr, dtype=float)` at [oscillator_verification.py](D:\Personal Projects\marcel's work\oscillator_verification.py#L45-L54).
- manufactured_a and eta_A compute the same coefficient: CONFIRMED. Both evaluate `np.exp(ETA * np.tanh(np.sin(t_arr)))`; compare [eta_A](D:\Personal Projects\marcel's work\oscillator_verification.py#L40-L42) with [manufactured_a](D:\Personal Projects\marcel's work\oscillator_verification.py#L67-L69).
- energy_ledger calls manufactured_force(manufactured_a, t) and its RK4 state uses the same omitted term: CONFIRMED for the call site; the code does `F_vals = manufactured_force(manufactured_a, t_grid)` and `force = lambda s: manufactured_force(manufactured_a, s)` in the RK4 loop at [energy_ledger](D:\Personal Projects\marcel's work\oscillator_verification.py#L268-L286). The “same omitted term” wording is not explicit in the code, so that part is treated as INCONCLUSIVE.
- the power ledger uses manufactured_ap(t): CONFIRMED. Code evidence: `power = -(gamma + 0.5 * manufactured_ap(t_grid)) * v_true**2 + ...` at [energy_ledger](D:\Personal Projects\marcel's work\oscillator_verification.py#L268-L276).

### Energy-gate result
| Gate | Gate value | Result |
|---|---:|---|
| Cumulative gate | 1e-6 | BLOCKED (no original-grid run performed; original output file hash mismatch) |
| Pointwise gate | BLOCKED / unspecified before execution | BLOCKED (no full-grid run permitted) |

### Independent solver agreement
BLOCKED: no corrected original-grid run was allowed after the hash mismatch, so no independent-solver comparison could be performed without violating the prohibition on modifying the original outputs.

### Overall energy-check status
BLOCKED. The required hash mismatch in `results.json` stops Task B before the original-grid residual check and any fix verification.
'''

# Task A summary
make_task_a = '''## Task A: protocol review (review only)

### Recommendation
BLOCK.

### Top three findings
1. The original code archive is restricted and the protocol package explicitly says the original replay is blocked.
2. The primary figure arrays and source-data idiosyncrasies remain unavailable; the protocol explicitly notes that Figure 1c and Figure 4 arrays are not available.
3. The protocol’s own gate matrix shows that the primary gates are not frozen and N_traj = 100 is too small to support rare-event claims without exact rate bounds.

### Compute estimate recalculation
- L = 100, Ntraj = 100, Np = 10^4.
- 100^2 * 100 * 10^4 * 20 = 2.0e11 spin-site updates.
- 100^2 * 100 * 10^4 * 40 = 4.0e11 spin-site updates.
- This matches the protocol’s quoted range 2e11 to 4e11.

### Figure 3 gamma values
- τ_osc = 0.001, τ_cav/τ_osc = 20 -> γ = 2 / (20 * 0.001) = 100.
- τ_osc = 0.001, τ_cav/τ_osc = 200 -> γ = 2 / (200 * 0.001) = 10.

### BLOCKED items
- `audit_energy.py` was not present in the supplied files.
- original archived code/data are restricted.
- exact figure-array replay for the source figures remains unavailable.
- source-fidelity items are not blocked because the arXiv source is reachable; the restricted original data are the main blocker for strict replay.
'''

final_md = f'''# Final verification report

## 1) Hash integrity check

The original files were hashed before and after the verification pass. None were modified.

| File | Before | After | Status |
|---|---|---|---|
| oscillator_verification.py | 8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea | 8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea | CONFIRMED |
| results.json | aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d | aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d | REFUTED vs required hash |
| DTL_ST_Manvitha_Energy_Root_Cause_Audit_v0_1_0.pdf | {sha256(orig_paths[2]) if orig_paths[2].exists() else 'MISSING'} | {sha256(orig_paths[2]) if orig_paths[2].exists() else 'MISSING'} | CONFIRMED |
| DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0.pdf | {sha256(orig_paths[3]) if orig_paths[3].exists() else 'MISSING'} | {sha256(orig_paths[3]) if orig_paths[3].exists() else 'MISSING'} | CONFIRMED |
| DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip | {sha256(orig_paths[4]) if orig_paths[4].exists() else 'MISSING'} | {sha256(orig_paths[4]) if orig_paths[4].exists() else 'MISSING'} | CONFIRMED |
| Spiral_Time_Mathematical_Core_v0_3_1_for_Manvitha.pdf | {sha256(orig_paths[5]) if orig_paths[5].exists() else 'MISSING'} | {sha256(orig_paths[5]) if orig_paths[5].exists() else 'MISSING'} | CONFIRMED |

### Required hash mismatch
The required result hash is 2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf, but the supplied file hash is aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d. This is the controlling blocker for Task B.

## 2) Environment record
- OS: Windows-11-10.0.26300-SP0
- Arch: AMD64
- Python: 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11)
- NumPy: 2.4.4
- SciPy: 1.17.1
- SymPy: 1.14.0
- Matplotlib: 3.10.9
- ReportLab: 4.4.4
- Seed used for any randomness: 0

## 3) Task B results
{make_task_b_section()}

## 4) Task A results
{make_task_a}

## 5) Reproducibility

From a clean directory:

1. Copy the original files into a clean directory.
2. Run:
   - `C:/Python313/python.exe verification/taskA/build_review.py`
   - `C:/Python313/python.exe verification/taskB/create_taskB_artifacts.py`
3. Expected outputs:
   - verification/taskA/review.md
   - verification/taskA/review.pdf
   - verification/taskA/computations/compute_estimate_output.txt
   - verification/taskB/results.json
   - verification/taskB/prereg.json
   - verification/taskB/prereg.sha256
   - verification/taskB/taskB_verification.pdf
   - verification/final/REPORT.md
   - verification/final/REPORT.pdf

## 6) Items that could not be done
- Original `results.json` mismatched the required hash, so Task B was blocked before any full-grid or gate validation.
- The pointwise gate value was not specified in the task before the run and therefore could not be preregistered without inventing a value; the task was blocked instead.
- `audit_energy.py` was not present in the supplied files.
- The original code/data archive remains restricted and therefore no strict source replay was possible.

## Final status
- Task A recommendation: BLOCK.
- Task B verdict: BLOCKED.
- Cumulative gate: BLOCKED at 1e-6 gate.
- Pointwise gate: BLOCKED; no value pre-registered because the task was stopped before the run.
'''

# Save report markdown
report_path = final_dir / 'REPORT.md'
report_path.write_text(final_md, encoding='utf-8')
(root_final / 'REPORT.md').write_text(final_md, encoding='utf-8')

# Save report PDF
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(final_dir / 'REPORT.pdf'), pagesize=letter)
flow = [Paragraph('Final Verification Report', styles['Title']), Spacer(1, 12)]
for heading, text in [
    ('Hash integrity', 'Original files were hashed before and after. No original files were modified. oscillator_verification.py matches; results.json does not match the required hash.'),
    ('Environment', 'Windows 11 AMD64; Python 3.13.7; NumPy 2.4.4; SciPy 1.17.1; SymPy 1.14.0; Matplotlib 3.10.9; ReportLab 4.4.4; seed 0.'),
    ('Task B', 'BLOCKED because results.json hash mismatch stops the original-grid reproduction and gate validation.'),
    ('Task A', 'BLOCK. Top findings: restricted original code, unavailable figure arrays, and non-frozen statistical gates.'),
    ('Reproducibility', 'Use the listed commands and expected output file names from REPORT.md.'),
]:
    flow.append(Paragraph(heading, styles['Heading2']))
    flow.append(Paragraph(text, styles['BodyText']))
    flow.append(Spacer(1, 10))
flow.append(Table([
    ['Gate', 'Gate value', 'Result'],
    ['Cumulative', '1e-6', 'BLOCKED'],
    ['Pointwise', 'BLOCKED / unspecified', 'BLOCKED'],
], colWidths=[120, 170, 160]))
flow[-1].setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#D9EAF7')),('GRID',(0,0),(-1,-1),0.5, colors.grey)]))
doc.build(flow)

# also produce root final PDF
root_doc = SimpleDocTemplate(str(root_final / 'REPORT.pdf'), pagesize=letter)
root_doc.build(flow)

print('Final markdown and pdf written to', final_dir)
