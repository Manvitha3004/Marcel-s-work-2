import difflib, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

root = Path('d:/Personal Projects/Marcel\'s-work-2/verification/taskB')
root.mkdir(parents=True, exist_ok=True)
orig_path = Path(r"D:\Personal Projects\marcel's work\oscillator_verification.py")
original = orig_path.read_text(encoding='utf-8')

old_block = '''    if A is eta_A or getattr(A, "__name__", "") == "eta_A":
        a = eta_A(t_arr)
        return a * ETA * (1.0 / np.cosh(np.sin(t_arr)) ** 2) * np.cos(t_arr)
    return np.zeros_like(t_arr, dtype=float)
'''
new_block = '''    if A is manufactured_a or getattr(A, "__name__", "") == "manufactured_a":
        return manufactured_ap(t_arr)
    if A is eta_A or getattr(A, "__name__", "") == "eta_A":
        a = eta_A(t_arr)
        return a * ETA * (1.0 / np.cosh(np.sin(t_arr)) ** 2) * np.cos(t_arr)
    return np.zeros_like(t_arr, dtype=float)
'''
minimal = original.replace(old_block, new_block)
strict = minimal.replace('    return np.zeros_like(t_arr, dtype=float)\n', '    raise ValueError(f"Unsupported A function: {A!r}")\n', 1)

v01 = root / 'v0.1.1'
v01.mkdir(exist_ok=True)
(v01 / 'oscillator_verification_minimal_fix.py').write_text(minimal, encoding='utf-8')
(v01 / 'oscillator_verification.py').write_text(strict, encoding='utf-8')

# diff patch
patch = ''.join(difflib.unified_diff(original.splitlines(True), minimal.splitlines(True), fromfile='original', tofile='minimal_fix'))
(v01 / 'diff.patch').write_text(patch, encoding='utf-8')

# Results JSON blocked due required hash mismatch
blocked = {
    'status': 'BLOCKED',
    'reason': 'results.json does not match the required SHA-256 hash 2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf; the original file hash remains aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d and Task B is stopped before any full-grid reproduction.',
    'dispatch_check': {
        'A_prime_manufactured_a_0': 0.0,
        'manufactured_ap_0': 0.48121182505960347,
        'expected': 0.48121182505960347,
    },
    'hashes': {
        'oscillator_verification.py': {'expected': '8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea', 'actual': '8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea', 'status': 'MATCH'},
        'results.json': {'expected': '2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf', 'actual': 'aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d', 'status': 'MISMATCH'},
    },
    'gates': {'cumulative_gate': {'value': 1e-6, 'status':'BLOCKED'}, 'pointwise_gate': {'value': 'BLOCKED_UNSPECIFIED', 'status':'BLOCKED'}},
    'reproducibility': {'stop_reason': 'results.json hash mismatch before original-grid reproduction; original output file intentionally not modified.'}
}
(root / 'results.json').write_text(json.dumps(blocked, indent=2), encoding='utf-8')

# prereg JSON
prereg = {
    'N_grid': [100, 200, 400, 800, 1600, 3200, 6400, 12800],
    'cumulative_gate': 1e-6,
    'pointwise_gate': 'BLOCKED_UNSPECIFIED',
    'seed': 0,
    'timestamp_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
    'status': 'BLOCKED',
    'note': 'Pointwise gate was not specified before execution; full grid not run because the required results.json hash mismatch blocked Task B.'
}
prereg_path = root / 'prereg.json'
prereg_path.write_text(json.dumps(prereg, indent=2), encoding='utf-8')
prereg_sha = hashlib.sha256(prereg_path.read_bytes()).hexdigest()
(root / 'prereg.sha256').write_text(prereg_sha + '  prereg.json\n', encoding='utf-8')

# A tiny verification PDF stub for B claim table (blocked status)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(root / 'taskB_verification.pdf'), pagesize=letter)
flow = [Paragraph('Task B verification (BLOCKED)', styles['Title']), Spacer(1, 12),
        Table([
            ['Claim', 'Verdict', 'Evidence'],
            ['A_prime dispatch', 'REFUTED', 'A_prime(manufactured_a, 0.0)=0.0, manufactured_ap(0.0)=0.48121182505960347'],
            ['results.json expected hash', 'REFUTED', 'expected 207491... actual aeac34...'],
            ['Full-grid reproduction', 'BLOCKED', 'Original results.json mismatched before any N>800 run and file modification was forbidden']
        ], colWidths=[170, 80, 280]),
        Spacer(1, 12),
        Paragraph('Task B is blocked by the hash mismatch described above. No original files were modified.', styles['BodyText'])]
style = TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#D9EAF7')),('GRID',(0,0),(-1,-1),0.5, colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')])
flow[2].setStyle(style)
doc.build(flow)
