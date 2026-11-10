from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / 'review' / 'report'
COMPUTATIONS_DIR = ROOT / 'review' / 'computations'

EXPECTED_INPUTS = [
    'DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_1.pdf',
    'DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_1_PACKAGE.zip',
    'verification/taskA/computations/arxiv_2610_30266.pdf',
    'verification/taskA/computations/protocol_candidate.pdf',
    'verification/taskA/review.pdf',
    'verification/taskB/taskB_verification.pdf',
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def read_py_version():
    import numpy, scipy, sympy, matplotlib
    return {
        'python': platform.python_version(),
        'platform': platform.platform(),
        'machine': platform.machine(),
        'numpy': numpy.__version__,
        'scipy': scipy.__version__,
        'sympy': sympy.__version__,
        'matplotlib': matplotlib.__version__,
        'reportlab': __import__('reportlab').__version__,
    }


def hash_manifest():
    rows = []
    for rel in EXPECTED_INPUTS:
        full = ROOT / rel
        if full.exists():
            rows.append((rel, sha256(full)))
        else:
            rows.append((rel, 'MISSING'))
    return rows


def run_command(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True, cwd=str(ROOT))
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def build_package_audit_md():
    qa_script = ROOT / 'verification/taskB/v0.1.1/oscillator_verification_fixed.py'
    script_text = qa_script.read_text(encoding='utf-8') if qa_script.exists() else ''
    checks = [
        ('symbolic_checks', 'Symbolic residual checks; exact zero expectation.', 'exactly 0', 'script function, not pytest test'),
        ('convergence_study', 'Convergence study for A1, A2, A_eta; order check against theory.', 'observed order near 2 for RK2 / 4 for RK4', 'script function, not pytest test'),
        ('energy_ledger', 'Energy-balance residual, thresholds <=1e-6', '<=1e-6', 'script function, not pytest test'),
        ('limiting_case_tests', 'Limiting case A ≡ 1 and A ≡ a against closed-form formulas', '<=1e-10', 'script function, not pytest test'),
        ('bounds_check', 'Coefficient bounds eta in [1/phi, phi]', 'False when eta=1', 'script function, not pytest test'),
        ('stability_study', 'Floquet and monotonicity stability checks', 'problem-specific thresholds', 'script function, not pytest test'),
    ]

    code = []
    code.append('# Package audit')
    code.append('')
    code.append('## Findings')
    code.append('')
    code.append('- REFUTED: The local QA package does not reproduce an 11/11 pass count. The package is a script, not a real pytest suite.')
    code.append('- CONFIRMED: Executing the available QA script produced `overall_verdict`: "FAIL: energy_ledger_residual".')
    code.append('- BLOCKED: The detailed mutation set in the protocol request is not present in the workspace package, so those specific mutation checks cannot be run without the missing package.')
    code.append('')
    code.append('## Test inventory')
    code.append('')
    code.append('| File | Function | What it asserts | Tolerance | Test type |')
    code.append('|---|---|---|---|---|')
    for fn, assertion, tol, kind in checks:
        code.append(f'| verification/taskB/v0.1.1/oscillator_verification_fixed.py | {fn} | {assertion} | {tol} | {kind} |')
    code.append('')
    code.append('## Execution evidence')
    code.append('')
    code.append('```text')
    code.append('Command: .\\.venv\\Scripts\\python.exe verification\\taskB\\v0.1.1\\oscillator_verification_fixed.py')
    code.append('Result: {')
    code.append('  "overall_verdict": "FAIL: energy_ledger_residual"')
    code.append('}')
    code.append('```')
    code.append('')
    code.append('```text')
    code.append('Command: .\\.venv\\Scripts\\python.exe -m pytest -q verification\\taskB\\v0.1.1')
    code.append('Result: no tests ran in 0.01s')
    code.append('```')
    code.append('')
    code.append('## Mutation-test status')
    code.append('')
    code.append('BLOCKED. The requested mutation battery (spin sign, Strang ordering, noise scaling, D factor, oscillator frequency, QR sign) is not present in the available package and no matching source files are available in the workspace.')
    return '\n'.join(code)


def build_summary_csv():
    rows = [
        ['Part 1', 'QA suite inventory', 'REFUTED', 'verification/taskB/v0.1.1/oscillator_verification_fixed.py', 'No pytest tests; the package is a script with functions such as symbolic_checks, convergence_study, energy_ledger.', 'major'],
        ['Part 1', '11/11 reproduction', 'REFUTED', 'command output', 'python -m pytest -q verification/taskB/v0.1.1 -> no tests ran in 0.01s; script run -> overall_verdict FAIL: energy_ledger_residual', 'critical'],
        ['Part 1', 'Mutation battery', 'BLOCKED', 'missing package', 'Requested mutation set not present in workspace; package absent or not matching the spin/Strang package described by the protocol.', 'critical'],
        ['Part 1', 'JSON hash discrepancy', 'BLOCKED', 'missing candidate package', 'Required v0.1.0 hash discrepancy check cannot be verified because the target package/PDF is missing from the workspace.', 'major'],
        ['Part 1', 'Sign-control defect', 'BLOCKED', 'missing candidate package', 'The sign-control validation cannot be checked because the protocol package is absent from the workspace.', 'major'],
        ['Part 2', 'Spin sign and Strang integrator', 'BLOCKED', 'missing candidate package / no source reproduction', 'The requested spin-right-hand sign and Strang implementation checks are not available in the workspace package.', 'critical'],
        ['Part 2', 'Source fidelity', 'BLOCKED', 'verification/taskA/computations/arxiv_2610_30266.pdf', 'Local source PDF is present, but exact source-fidelity cross-checks for all protocol equations and figures are not reproduced in this workspace.', 'major'],
        ['Part 3', 'Statistical gates', 'BLOCKED', 'missing candidate package', 'The protocol statistics package and sequence logic are absent; no direct gate audit possible in this workspace.', 'critical'],
        ['Part 4', 'Feasibility estimate', 'BLOCKED', 'missing package', 'Large-spin simulation inputs and package runtime measurement are not available in the workspace.', 'major'],
        ['Part 5', 'Source fidelity: paper definitions', 'BLOCKED', 'verification/taskA/computations/arxiv_2610_30266.pdf', 'Exact source definitions require the missing protocol package and the full paper extraction workflow; cannot be verified here.', 'major'],
        ['Part 6', 'Protocol integrity', 'BLOCKED', 'missing package', 'Protocol-level integrity checks require the actual v0.1.1 candidate package and PDF, which are absent from this workspace.', 'major'],
    ]
    return rows


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['part', 'item', 'verdict', 'evidence_location', 'value_or_quote', 'severity'])
        writer.writerows(rows)


def build_review_md():
    versions = read_py_version()
    rows = hash_manifest()
    lines = []
    lines.append('# DTL-ST-REPRO-001 Pre-Execution Candidate v0.1.1 — Independent review')
    lines.append('')
    lines.append('## Scope and limitation')
    lines.append('')
    lines.append('The workspace does not contain the actual candidate PDF or package zip named in the request. The available local evidence is the earlier review materials under verification/taskA and the QA package at verification/taskB/v0.1.1. This review therefore treats the requested protocol artifacts as BLOCKED when the evidence is absent and uses the available package script to verify the local claim that a QA suite exists and passes.')
    lines.append('')
    lines.append('## Environment')
    lines.append('')
    lines.append(f'- OS: {platform.platform()}')
    lines.append(f'- CPU: {platform.machine()}')
    lines.append(f'- Python: {versions["python"]}')
    lines.append(f'- NumPy: {versions["numpy"]}')
    lines.append(f'- SciPy: {versions["scipy"]}')
    lines.append(f'- SymPy: {versions["sympy"]}')
    lines.append(f'- Matplotlib: {versions["matplotlib"]}')
    lines.append(f'- ReportLab: {versions["reportlab"]}')
    lines.append('')
    lines.append('## Inputs and hashes')
    lines.append('')
    lines.append('| Input | SHA-256 | Status |')
    lines.append('|---|---|---|')
    for rel, digest in rows:
        status = 'CONFIRMED' if digest != 'MISSING' else 'BLOCKED'
        lines.append(f'| {rel} | {digest} | {status} |')
    lines.append('')
    lines.append('### Evidence')
    lines.append('')
    lines.append('The workspace is missing the candidate PDF and ZIP named in the request; the hash manifest therefore records those inputs as MISSING and marks the missing-file checks as BLOCKED.')
    lines.append('')
    lines.append('## Part 1 — Audit of the local QA package')
    lines.append('')
    lines.append('### 1a. Test inventory')
    lines.append('')
    lines.append('The available QA file is [verification/taskB/v0.1.1/oscillator_verification_fixed.py](../verification/taskB/v0.1.1/oscillator_verification_fixed.py). The functions are script checks, not pytest tests: `symbolic_checks`, `convergence_study`, `energy_ledger`, `limiting_case_tests`, `bounds_check`, and `stability_study` are all plain functions that compute values and then print JSON; there are no test functions under pytest. This is a REFUTED claim to the statement that the package contains an actual 11/11 test suite.')
    lines.append('')
    lines.append('### 1b. Full QA suite execution')
    lines.append('')
    lines.append('Command run: `.venv\\Scripts\\python.exe verification\\taskB\\v0.1.1\\oscillator_verification_fixed.py`')
    lines.append('')
    lines.append('```text')
    lines.append('  "overall_verdict": "FAIL: energy_ledger_residual"')
    lines.append('```')
    lines.append('')
    lines.append('The same package was also checked with pytest: `.venv\\Scripts\\python.exe -m pytest -q verification\\taskB\\v0.1.1` which returned `no tests ran in 0.01s`. The package therefore does not reproduce an 11/11 pass result. Verdict: REFUTED.')
    lines.append('')
    lines.append('### 1c. Mutation test')
    lines.append('')
    lines.append('BLOCKED. The mutation set described in the request targets a spin/Strang package that is not present in the workspace; the available file is only the oscillator verification script. No matching package or test harness for the listed mutation sites was present, so the mutation battery cannot be executed here without fabricating an absent implementation.')
    lines.append('')
    lines.append('### 1d. Text-mode JSON hash discrepancy')
    lines.append('')
    lines.append('BLOCKED. The target v0.1.0 package and JSON files referenced in the claim are absent from the workspace, so the hash discrepancy check cannot be reproduced here. The hash check in the earlier Task B materials is a separate, blocked artifact and is not the requested package.')
    lines.append('')
    lines.append('### 1e. Sign-control defect claim')
    lines.append('')
    lines.append('BLOCKED. The old positive-sine sign-control check is not found in the available local package and no candidate v0.1.1 package was present. The sign-control claim therefore remains unverified.')
    lines.append('')
    lines.append('## Part 2 — Verify physics and numerics')
    lines.append('')
    lines.append('### 2a. Spin sign and rotation')
    lines.append('')
    lines.append('BLOCKED. The spin-update implementation and the requested DTL protocol package were not present in the workspace. The file [verification/taskB/v0.1.1/oscillator_verification_fixed.py](../verification/taskB/v0.1.1/oscillator_verification_fixed.py) is a damped-oscillator verification script and not the spin lattice implementation described in the protocol. No independent rotation or norm-conservation run could be reproduced under the required constraints.')
    lines.append('')
    lines.append('### 2b. Strang convergence')
    lines.append('')
    lines.append('BLOCKED. No deterministic cavity-signal Strang integrator or package source is available in the workspace. The available script does not implement the required DTL many-body spin update or cavity signal integration.')
    lines.append('')
    lines.append('### 2c. Noise and covariance')
    lines.append('')
    lines.append('BLOCKED. The package implementing the stochastic oscillator/noise covariance calculations is not present in the workspace; therefore the Monte Carlo variance and Brownian coarse-graining checks cannot be repeated here.')
    lines.append('')
    lines.append('### 2d. Parameter and equation fidelity')
    lines.append('')
    lines.append('BLOCKED. The required protocol equations and source-paper comparisons cannot be verified without the candidate PDF/ZIP and a full source extraction workflow. The local source PDF is present, but the exact matching of equations and figures to the protocol remains unverified.')
    lines.append('')
    lines.append('### 2e. Warmup and record length')
    lines.append('')
    lines.append('BLOCKED. The candidate package and protocol text are absent. No warmup/record-length check can be computed from the missing implementation.')
    lines.append('')
    lines.append('## Part 3 — Statistical design')
    lines.append('')
    lines.append('BLOCKED. The statistical gate and bootstrap design described in the request is not present in the available workspace package, so no direct P1/P2 gate audit can be executed.')
    lines.append('')
    lines.append('## Part 4 — Feasibility')
    lines.append('')
    lines.append('BLOCKED. The required spin update code for a large L=100, Np=10^4, R=100 simulation is absent, so no measured throughput or memory estimate can be produced from the target implementation.')
    lines.append('')
    lines.append('## Part 5 — Source fidelity')
    lines.append('')
    lines.append('BLOCKED. The local source PDF is present at [verification/taskA/computations/arxiv_2610_30266.pdf](../verification/taskA/computations/arxiv_2610_30266.pdf), but the exact figure and equation cross-checks requested for the protocol are not reproduced in this workspace. The source-fidelity items are therefore blocked.')
    lines.append('')
    lines.append('## Part 6 — Engineering gates and protocol integrity')
    lines.append('')
    lines.append('BLOCKED. The protocol itself is absent, so no gate inventory or integrity analysis can be performed against the missing text. However, the local QA package is plainly not a true 11/11 test suite and is not a valid basis for claiming protocol validation.')
    lines.append('')
    lines.append('## Recommendation')
    lines.append('')
    lines.append('Recommendation: BLOCK')
    lines.append('')
    lines.append('### Top three findings')
    lines.append('1. The local QA package does not contain a real pytest suite and therefore does not reproduce an 11/11 pass count.')
    lines.append('2. The available script itself fails: `overall_verdict: "FAIL: energy_ledger_residual"` when run in the configured environment.')
    lines.append('3. The protocol package and candidate PDF named in the request are missing from the workspace; all protocol-specific checks are therefore BLOCKED.')
    lines.append('')
    return '\n'.join(lines)


def build_review_pdf(markdown_text: str):
    pdf_path = REPORT_DIR / 'review.pdf'
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    story = [Paragraph('DTL-ST-REPRO-001 Independent Review', styles['Title']), Spacer(1, 12)]
    for block in markdown_text.split('\n\n'):
        if not block.strip():
            continue
        if block.startswith('## '):
            story.append(Paragraph(block, styles['Heading2']))
        elif block.startswith('### '):
            story.append(Paragraph(block, styles['Heading3']))
        elif block.startswith('|'):
            continue
        else:
            story.append(Paragraph(block.replace('`', ''), styles['BodyText']))
    doc.build(story)


def build_recommendation_md():
    lines = [
        '# Recommendation',
        '',
        'Recommendation: BLOCK',
        '',
        '## Top three findings',
        '1. The workspace does not contain the candidate PDF or package zip named in the request, so the protocol-specific checks are not reproducible.',
        '2. The local QA package is not a real pytest suite; `pytest -q` reports `no tests ran in 0.01s`.',
        '3. Running the available QA script gives `overall_verdict: "FAIL: energy_ledger_residual"`, which contradicts any 11/11 pass claim.',
        '',
        '## Required corrections (ordered by severity)',
        '1. Provide the actual v0.1.1 candidate PDF and package zip in the workspace before any protocol review can be accepted.',
        '2. Replace the script-based package with a real, discoverable test suite (`pytest` or equivalent) and record exact counts.',
        '3. Fix or re-run the failing energy-ledger check and reattach the used thresholds and output hashes before any freeze.',
        '',
        '## Freeze gate',
        'Yes, an unresolved missing-package issue should prevent a freeze. The current evidence does not support validation of the protocol or the package.',
    ]
    return '\n'.join(lines)


def write_inputs_and_outputs_hashes():
    manifest = hash_manifest()
    input_path = REPORT_DIR / 'inputs.sha256'
    with input_path.open('w', encoding='utf-8') as f:
        for rel, digest in manifest:
            if digest == 'MISSING':
                f.write(f'{digest}  {rel}\n')
            else:
                f.write(f'{digest}  {rel}\n')

    all_files = [
        REPORT_DIR / 'review.md',
        REPORT_DIR / 'review.pdf',
        REPORT_DIR / 'summary.csv',
        REPORT_DIR / 'package_audit.md',
        REPORT_DIR / 'recommendation.md',
        REPORT_DIR / 'inputs.sha256',
        REPORT_DIR / 'outputs.sha256',
        ROOT / 'review' / 'computations' / 'build_review.py',
    ]
    output_path = REPORT_DIR / 'outputs.sha256'
    with output_path.open('w', encoding='utf-8') as f:
        for p in all_files:
            if p.exists():
                f.write(f'{sha256(p)}  {p.relative_to(ROOT).as_posix()}\n')
            else:
                f.write(f'MISSING  {p.relative_to(ROOT).as_posix()}\n')


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    md = build_review_md()
    (REPORT_DIR / 'review.md').write_text(md, encoding='utf-8')
    build_review_pdf(md)
    write_csv(REPORT_DIR / 'summary.csv', build_summary_csv())
    (REPORT_DIR / 'package_audit.md').write_text(build_package_audit_md(), encoding='utf-8')
    (REPORT_DIR / 'recommendation.md').write_text(build_recommendation_md(), encoding='utf-8')
    write_inputs_and_outputs_hashes()
    print('review generated')


if __name__ == '__main__':
    main()
