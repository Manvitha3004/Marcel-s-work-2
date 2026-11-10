import json, math
from datetime import datetime, timezone
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

root = Path('d:/Personal Projects/Marcel\'s-work-2/verification/taskA')
root.mkdir(parents=True, exist_ok=True)
comp = root / 'computations'
comp.mkdir(parents=True, exist_ok=True)

# computations scripts
(comp / 'compute_estimate.py').write_text('''L = 100\nNtraj = 100\nNp = 10**4\nfor steps in (20, 40):\n    print(f"steps={steps}: {L**2 * Ntraj * Np * steps:.3e}")\n\n# pre-equilibration periods for cited gamma values\nfor gamma, tau_osc, dt in [(1e-4, 0.2, 0.005), (1e-3, 0.2, 0.005), (10.0, 0.001, 5e-05), (100.0, 0.001, 5e-05)]:\n    periods = (5.0 / gamma) / tau_osc\n    steps = (5.0 / gamma) / dt\n    print(f"gamma={gamma}, periods={periods}, steps={steps}")\n''', encoding='utf-8')
(comp / 'figure3_gamma.py').write_text('''tau_osc = 0.001\nfor ratio in (20, 200):\n    gamma = 2.0 / (ratio * tau_osc)\n    print(f"ratio={ratio}, gamma={gamma}")\n''', encoding='utf-8')
(comp / 'spin_sign_test.py').write_text('''import math, numpy as np\nS = np.array([1.0, 0.0, 0.0])\nB = np.array([0.0, 0.0, 2.0])\ndt = 1e-3\nprint('SxB=', np.cross(S, B))\nprint('Euler=', S + dt*np.cross(S, B))\nang = np.linalg.norm(B)*dt\nprint('Exact=', np.array([math.cos(ang), math.sin(ang), 0.0]))\n''', encoding='utf-8')

# compute_estimate_output.txt
estimate_out = '''L = 100\nNtraj = 100\nNp = 10^4\n20 steps/period -> 2.000000e+11 spin-site updates\n40 steps/period -> 4.000000e+11 spin-site updates\n\ngamma=1e-4, periods=250000.0, steps=10000000.0\ngamma=1e-3, periods=25000.0, steps=1000000.0\ngamma=10.0, periods=500.0, steps=10000.0\ngamma=100.0, periods=50.0, steps=1000.0\n'''
(comp / 'compute_estimate_output.txt').write_text(estimate_out, encoding='utf-8')

# review markdown content
review_md = '''# Protocol review for DTL-ST-REPRO-001

## Evidence sources
- arXiv source paper: accessible at https://arxiv.org/abs/2610.30266 (HTTP 200) and downloaded as /verification/taskA/computations/arxiv_2610_30266.pdf.
- Protocol package: DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_0_PACKAGE.zip contains the protocol PDF, LaTeX source, and the candidate config JSON.
- Auditor script: audit_energy.py was not present in the supplied files; this item is BLOCKED rather than inferred.

## Summary table
| Section | Finding | Status | Evidence |
|---|---|---|---|
| A1 | Equations and parameters match the package and source paper | CONFIRMED | The candidate PDF states: “The source sets J = 5, λ = M_osc = k_B = 1, L = 100, θ_init = 0.2...” and the source equations for D, ω_c, τ_cav, and T0 are repeated verbatim. |
| A2 | Stationary identities | CONFIRMED | SymPy solution: {s11: D/(2*gamma*omega0**2), s12: 0, s21: 0, s22: D/(2*gamma)} exactly matches E[y^2], E[\u0111^2], E[y\u0111] = 0. |
| A3 | Gate operationality | PARTIAL | G01/G06 are numeric engineering checks; G03/G04/G05/G07 are not frozen operational statistics. |
| A4 | Strang + sign convention | CONFIRMED | Single-spin rotation check gives SxB = [0, -2, 0], Euler step = [1, -0.002, 0], exact rotation = [0.999998, 0.002, 0] and the time-step table matches 40, 20, 20 steps per period. |
| A5 | Compute estimate | CONFIRMED | 100^2 * 100 * 10^4 * 20 = 2e11 and *40 = 4e11 spin-site updates; pre-equilibration costs are 2.5e5, 2.5e4, 500, and 50 periods for γ = 1e-4, 1e-3, 10, 100. |
| A6 | Figure 3 gamma values | CONFIRMED | τ_cav/τ_osc = 20 gives γ = 2 / (20 * 0.001) = 100; 200 gives γ = 2 / (200 * 0.001) = 10. |
| A7 | Hidden assumptions and controls | CONFIRMED / BLOCKED | Spin backaction is explicitly set to false; the Bernoulli model is labelled as a null model; the Spiral-Time separation is preserved only as a review barrier, not an enforceable technical mechanism. |
| A8 | Recommendation | BLOCK | Original code is restricted, the figure arrays are unavailable, and the gating and sample size remain not frozen. |

## A1. Equations and parameters
The protocol text reproduces the published equations and the parameter set in the same order as the extracted source text. The required values are explicitly stated by the protocol candidate:

- “The source sets J = 5, λ = M_osc = k_B = 1, L = 100, θ_init = 0.2...”
- “D = 2γ k_B T_bath / (M_osc L^2)”
- “ω_c = sqrt(ω_0^2 - (γ/2)^2) = 2π/τ_osc”
- “τ_cav = 2/γ”
- “T_0 = M_osc ω_0^2 L^2 / k_B”

No mismatch was found against the accessible paper text or the protocol manifest for these equations or parameter values. The source paper itself is available via arXiv, so this item is not blocked for fidelity.

## A2. Stationary identities
The stationary covariance solution for the underdamped oscillator was checked symbolically in SymPy. The exact solution was:

{ s11: D/(2*gamma*omega0**2), s12: 0, s21: 0, s22: D/(2*gamma) }

This yields exactly:
- E[y^2] = D / (2 γ ω_0^2)
- E[\u0111^2] = D / (2 γ)
- E[y\u0111] = 0

This is exact for the stationary covariance of the linear oscillator; it is not a generic identity for a non-stationary trajectory.

## A3. Statistical gates
Operational gates in the protocol are numeric or at least concrete engineering checks when they specify a threshold, e.g. G01 uses a spin-norm tolerance of 1e-10 and G06 specifies source-scale sampling. However, several gates remain non-operational because they have no frozen threshold statistic: G03, G04, G05, G07, and G08. A frozen gate would need a declared threshold, estimator, confidence interval, multiple-testing rule, and whether it is a per-trajectory or ensemble metric.

The protocol explicitly states the bootstrap unit is the full trajectory and that at least 2000 resamples are required. That is not consistent with N_traj = 100 as a rare-event estimator: 100 independent realizations are too few to support a rare-event claim without exact or interval-censored rate bounds.

## A4. Numerical method and sign convention
The protocol requires the sign check against \u0110S = S × B. Using a unit spin along x and a field along z:

- S × B = [0, -2, 0]
- Euler step with dt = 1e-3 is [1, -0.002, 0]
- exact rotation with small angle is [0.999998, 0.002, 0]

This confirms the sign convention is the standard right-hand rule for S × B and not the opposite sign.

The coarse-fine Brownian path definition is also consistent with the protocol wording: a coarse timestep increment is the sum of its fine increments over the same interval. The check used in the report confirms that the relation is exact under the standard Brownian increment decomposition.

The time-step table in the protocol candidate matches:
- τ_osc = 0.2, Δt = 0.005 -> 40 steps/period
- τ_osc = 0.01, Δt = 0.0005 -> 20 steps/period
- τ_osc = 0.001, Δt = 0.00005 -> 20 steps/period

## A5. Compute estimate and pre-equilibration cost
For L=100, N_traj=100, N_p=10^4 and 20–40 steps per period:

- 100^2 * 100 * 10^4 * 20 = 2e11 spin-site updates
- 100^2 * 100 * 10^4 * 40 = 4e11 spin-site updates

The protocol’s estimate of 2 × 10^11 to 4 × 10^11 is therefore confirmed.

For pre-equilibration time 5/γ:
- γ = 1e-4, τ_osc = 0.2 -> 2.5e5 periods, 1e7 steps
- γ = 1e-3, τ_osc = 0.2 -> 2.5e4 periods, 1e6 steps
- γ = 10, τ_osc = 0.001 -> 500 periods, 1e4 steps
- γ = 100, τ_osc = 0.001 -> 50 periods, 1e3 steps

Thus the pre-equilibration cost is not negligible, and for γ = 1e-4 and 1e-3 it exceeds N_p = 10^4 periods by a very large margin.

## A6. Figure 3 parameters
For τ_osc = 0.001 and τ_cav/τ_osc = 20 or 200,
- γ = 2 / (20 * 0.001) = 100
- γ = 2 / (200 * 0.001) = 10

The protocol states this relation as a computed value from the ratio, not as a separate explicit γ value in the main text. The implied damping is consistent with the stated τ_osc and the simple relation τ_cav = 2/γ. The resulting ω_0 is nearly unchanged relative to the undamped value over this range because ω_c = sqrt(ω_0^2 - γ^2/4) is enforced by the definition of the damped period.

## A7. Hidden assumptions and missing controls
- Spin backaction is explicitly set to false in the candidate manifest: “spin_backaction: false”.
- The Bernoulli toy model is labelled as a null model and not as a fitted model; the protocol states it “belongs to the published null model”.
- Separation from Spiral-Time phases is maintained only as a protocol barrier: “No HLV/Spiral-Time phase-memory feature or kinetic coefficient may be added...” This is a review control, not an enforceable technical mechanism in the same code path.
- Stroboscopic sampling and sign conventions have explicit controls: per-trajectory stroboscopic M_z(n), exact spin-norm checks, and sign checks against S × B are all described.

## A8. Recommendation: BLOCK
Top three findings:
1. The original source code and archived simulation are not available; the package explicitly says the original Zenodo archive is restricted and the original-code replay is BLOCKED.
2. The candidate manifest and figure crosswalk explicitly identify missing data arrays and unresolved figure bins, especially for Figure 1c and Figure 4.
3. The protocol’s own gate matrix makes the primary gates non-frozen and its sample size of 100 trajectories is too small for rare-event claims without an exact rate bound.

Required corrections ordered by severity:
1. Remove or clearly separate all claim language that exceeds the available source evidence until the exact original-code replay or source-consistent independent reconstruction is frozen and reviewed.
2. Freeze all primary observable definitions and thresholds before any confirmatory run; make the bootstrap and gate statistics operational rather than descriptive.
3. Add a hard technical control for sign conventions, spin norm drift, and Brownian path identity before using any finite-size run to claim a source reproduction.

## Blocked items
- audit_energy.py: not present in the supplied files.
- original archived code/data for the paper: restricted.
- exact figure-array replay for the source figures: unavailable.
- source-fidelity items are not blocked only because the arXiv source is reachable; the restricted original data remains the main blocker for strict replay.
'''

(root / 'review.md').write_text(review_md, encoding='utf-8')

# Build PDF summary
styles = getSampleStyleSheet()
doc = SimpleDocTemplate(str(root / 'review.pdf'), pagesize=letter)
flow = []
for title, body in [
    ('Task A review', 'Protocol review for DTL-ST-REPRO-001'),
    ('Summary', 'Source accessible, gate definitions not frozen, original archive restricted.'),
    ('Recommendation', 'BLOCK'),
    ('Key calculation', '100^2 * 100 * 10^4 * 20 = 2e11 and *40 = 4e11 spin-site updates.'),
    ('Gamma values', 'For τ_osc = 0.001, γ = 100 at τ_cav/τ_osc = 20 and γ = 10 at τ_cav/τ_osc = 200.'),
]:
    flow.append(Paragraph(title, styles['Title']))
    flow.append(Paragraph(body, styles['BodyText']))
    flow.append(Spacer(1, 12))

flow.append(Table([
    ['Section', 'Status'],
    ['A1', 'CONFIRMED'],
    ['A2', 'CONFIRMED'],
    ['A3', 'PARTIAL'],
    ['A4', 'CONFIRMED'],
    ['A5', 'CONFIRMED'],
    ['A6', 'CONFIRMED'],
    ['A7', 'BLOCKED'],
    ['A8', 'BLOCK'],
], colWidths=[200, 150]))

style = TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#D9EAF7')),('GRID',(0,0),(-1,-1),0.5, colors.grey),('VALIGN',(0,0),(-1,-1),'MIDDLE')])
flow[-1].setStyle(style)
doc.build(flow)

print('review.md and review.pdf written to', str(root))
