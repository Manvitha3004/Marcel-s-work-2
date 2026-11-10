from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak

workspace = Path(r"D:\Personal Projects\Marcel's-work-2")
final_dir = workspace / 'verification' / 'final'
final_dir.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
body = styles['BodyText']
body.leading = 14

summary_md = '''# Overall Verification Results

## Executive summary
This document consolidates the complete verification record for Task A (protocol review) and Task B (energy-ledger diagnosis). It records the exact evidence, the blockers, the numerical checks, and the root-cause finding for the oscillator dispatch bug.

## Scope
- Task A: review-only protocol assessment of DTL-ST-REPRO-001
- Task B: energy-ledger diagnosis against the supplied oscillator package
- Constraint: do not modify the originals; preserve hash integrity and stop on blocker conditions

## Final status
- Task A recommendation: BLOCK
- Task B verdict: BLOCKED
- Root cause in original script: confirmed dispatch bug in A_prime for manufactured_a
- Controlling blocker: results.json hash mismatch vs the required canonical hash

## Environment
- OS: Windows 11 AMD64
- Python: 3.13.7
- NumPy: 2.4.4
- SciPy: 1.17.1
- SymPy: 1.14.0
- Matplotlib: 3.10.9
- ReportLab: 4.4.4
- Random seed: 0

## Hash integrity
The original oscillator verification script hash matches the required value:
- oscillator_verification.py: 8d7fd2612e37ab3a30a08ba4829295c0c7415819486e3a96adcc1f78e8fca5ea

The output artifact hash does not match the required canonical value:
- expected: 2074913e8d2e87048d9a9e419257586cfc02f7005789d90ba9ecf94e8efc99cf
- actual: aeac34a0e92fb2e81051c873e94fc39a823be86f435cd42c0ebc578b8675952d

This mismatch is the principal blocker for Task B because the task requires the original outputs and forbids modifying them after the verification gate.

## Root-cause finding
The original oscillator script contains a dispatch bug in A_prime. The function recognizes unit_A, constant_A, and eta_A but does not recognize manufactured_a. The final branch returns zeros when none of those identities match, so the manufactured forcing branch quietly disappears.

Evidence from the running code:
- A_prime(manufactured_a, 0.0) = 0.0
- manufactured_ap(0.0) = 0.48121182505960347
- expected derivative = 0.48121182505960347

This is a direct runtime proof that the dispatch is wrong and that the manufactured branch should return manufactured_ap(t_arr).

## Minimal correction
The fix is a missing branch in A_prime:

if A is manufactured_a or getattr(A, "__name__", "") == "manufactured_a":
    return manufactured_ap(t_arr)

This aligns the branch selection with the manufactured solution and removes the erroneous zero fallback.

## Task A findings
Task A was a review-only protocol assessment for DTL-ST-REPRO-001 and the recommendation is BLOCK.

Key findings:
1. The original code archive is restricted and the protocol package explicitly says the original replay is blocked.
2. The primary figure arrays and source-data idiosyncrasies remain unavailable; Figure 1c and Figure 4 arrays are not available.
3. The protocol's gate matrix shows that the primary gates are not frozen and N_traj = 100 is too small for rare-event claims without exact rate bounds.

## Detailed computations
- L = 100, Ntraj = 100, Np = 10^4
- 100^2 * 100 * 10^4 * 20 = 2.0e11 spin-site updates
- 100^2 * 100 * 10^4 * 40 = 4.0e11 spin-site updates
- For τ_osc = 0.001 and τ_cav/τ_osc = 20 -> γ = 100
- For τ_osc = 0.001 and τ_cav/τ_osc = 200 -> γ = 10

## Task B status
Task B remains BLOCKED despite the clear root cause. The required hash mismatch on the original results artifact prevents valid completion of the original-grid validation. The rule forbids modifying the original outputs, so no false green result can be produced.

## Overall conclusion
The technical diagnosis is clear: the original code has a real dispatch bug, and that bug is fully demonstrated by the runtime check. The verification process itself is also clear: the result-file hash gate prevents a legitimate Task B pass, so the correct status is BLOCKED with documented evidence, not a failed scientific claim.
'''

# Build PDF document
out_path = final_dir / 'OVERALL_RESULTS.pdf'
md_path = final_dir / 'OVERALL_RESULTS.md'
md_path.write_text(summary_md, encoding='utf-8')

doc = SimpleDocTemplate(str(out_path), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
story = []

story.append(Paragraph('Overall Verification Results', styles['Title']))
story.append(Spacer(1, 12))

sections = [
    ('Executive summary', 'This document consolidates the complete verification record for Task A and Task B, including the blocker status, environment record, root-cause diagnosis, and computational checks.'),
    ('Hash integrity', 'The source script hash matches the required value. The supplied results.json hash does not match the canonical required value, which blocks Task B.'),
    ('Root cause', 'The function A_prime fails to treat manufactured_a as a recognized branch and falls through to a zero return path.'),
    ('Task A findings', 'Recommendation is BLOCK. The original archive is restricted, primary figure arrays are unavailable, and the main protocol gates are not frozen.'),
    ('Task B status', 'Blocked because the controlled output artifact hash mismatch shuts down any valid original-grid validation.'),
    ('Conclusion', 'The bug is proven; the verification gate is also proven. The proper status is BLOCKED with evidence, not a false pass.')
]

for title, text in sections:
    story.append(Paragraph(title, styles['Heading2']))
    story.append(Paragraph(text, body))
    story.append(Spacer(1, 10))

story.append(Paragraph('Key evidence table', styles['Heading2']))
rows = [
    ['Item', 'Result'],
    ['oscillator_verification.py hash', 'CONFIRMED'],
    ['results.json hash', 'MISMATCH'],
    ['A_prime(manufactured_a, 0.0)', '0.0'],
    ['manufactured_ap(0.0)', '0.48121182505960347'],
    ['Expected derivative', '0.48121182505960347'],
    ['Task A recommendation', 'BLOCK'],
    ['Task B verdict', 'BLOCKED'],
]

table = Table(rows, colWidths=[260, 220])
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D9EAF7')),
    ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
]))
story.append(table)
story.append(PageBreak())

# detailed write-up
for heading in ['Environment', 'Hash integrity', 'Root-cause finding', 'Task A findings', 'Task B status', 'Conclusion']:
    story.append(Paragraph(heading, styles['Heading1']))
    story.append(Paragraph(summary_md.split(f'## {heading}')[1].split('\n\n## ')[0] if f'## {heading}' in summary_md else 'Contained in overall summary above.', body))
    story.append(Spacer(1, 10))

# final section for direct evidence
story.append(Paragraph('Direct evidence summary', styles['Heading2']))
story.append(Paragraph('A_prime(manufactured_a, 0.0) = 0.0', body))
story.append(Paragraph('manufactured_ap(0.0) = 0.48121182505960347', body))
story.append(Paragraph('expected derivative = 0.48121182505960347', body))
story.append(Paragraph('Therefore the branch selection is incorrect and the zero-return fallback is the cause of the observed defect.', body))

# compute estimate table
story.append(Paragraph('Compute estimate checks', styles['Heading2']))
calc_rows = [
    ['Expression', 'Value'],
    ['L = 100, Ntraj = 100, Np = 10^4', 'baseline'],
    ['100^2 * 100 * 10^4 * 20', '2.0e11'],
    ['100^2 * 100 * 10^4 * 40', '4.0e11'],
    ['τ_osc = 0.001, τ_cav/τ_osc = 20', 'γ = 100'],
    ['τ_osc = 0.001, τ_cav/τ_osc = 200', 'γ = 10'],
]
calc_table = Table(calc_rows, colWidths=[300, 180])
calc_table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EAF2D3')),
    ('GRID', (0, 0), (-1, -1), 0.7, colors.grey),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
]))
story.append(calc_table)

# final note
story.append(Spacer(1, 18))
story.append(Paragraph('Final determination: verified root cause, verified blocker, TASK B remains BLOCKED.', styles['Heading2']))

doc.build(story)
print(f'Wrote {out_path} and {md_path}')
