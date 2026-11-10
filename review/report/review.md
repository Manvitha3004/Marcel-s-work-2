# DTL-ST-REPRO-001 Pre-Execution Candidate v0.1.1 — Independent review

## Scope and limitation

The workspace does not contain the actual candidate PDF or package zip named in the request. The available local evidence is the earlier review materials under verification/taskA and the QA package at verification/taskB/v0.1.1. This review therefore treats the requested protocol artifacts as BLOCKED when the evidence is absent and uses the available package script to verify the local claim that a QA suite exists and passes.

## Environment

- OS: Windows-11-10.0.26300-SP0
- CPU: AMD64
- Python: 3.13.7
- NumPy: 2.5.4
- SciPy: 1.18.1
- SymPy: 1.14.0
- Matplotlib: 3.11.2
- ReportLab: 5.1.0

## Inputs and hashes

| Input | SHA-256 | Status |
|---|---|---|
| DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_1.pdf | MISSING | BLOCKED |
| DTL_ST_REPRO_001_PreExecution_Candidate_v0_1_1_PACKAGE.zip | MISSING | BLOCKED |
| verification/taskA/computations/arxiv_2610_30266.pdf | 8f8157b3a8b6c4f52796d46bdc595915569c6bbc8ba685978e7cca47b9dd999d | CONFIRMED |
| verification/taskA/computations/protocol_candidate.pdf | 86a61586fbf2071e46821652785c7cbe8d91f91f06d6d43e2840bc622780ed22 | CONFIRMED |
| verification/taskA/review.pdf | d9ed3a1f37a2e1d38c0dc8f68f43be0bc5b23b040c5102593efee8317f7342aa | CONFIRMED |
| verification/taskB/taskB_verification.pdf | 3d21bb489b2cf723cd98d3bed2df4fd455c4f6b2d4f1706caadcc5149b62121d | CONFIRMED |

### Evidence

The workspace is missing the candidate PDF and ZIP named in the request; the hash manifest therefore records those inputs as MISSING and marks the missing-file checks as BLOCKED.

## Part 1 — Audit of the local QA package

### 1a. Test inventory

The available QA file is [verification/taskB/v0.1.1/oscillator_verification_fixed.py](../verification/taskB/v0.1.1/oscillator_verification_fixed.py). The functions are script checks, not pytest tests: `symbolic_checks`, `convergence_study`, `energy_ledger`, `limiting_case_tests`, `bounds_check`, and `stability_study` are all plain functions that compute values and then print JSON; there are no test functions under pytest. This is a REFUTED claim to the statement that the package contains an actual 11/11 test suite.

### 1b. Full QA suite execution

Command run: `.venv\Scripts\python.exe verification\taskB\v0.1.1\oscillator_verification_fixed.py`

```text
  "overall_verdict": "FAIL: energy_ledger_residual"
```

The same package was also checked with pytest: `.venv\Scripts\python.exe -m pytest -q verification\taskB\v0.1.1` which returned `no tests ran in 0.01s`. The package therefore does not reproduce an 11/11 pass result. Verdict: REFUTED.

### 1c. Mutation test

BLOCKED. The mutation set described in the request targets a spin/Strang package that is not present in the workspace; the available file is only the oscillator verification script. No matching package or test harness for the listed mutation sites was present, so the mutation battery cannot be executed here without fabricating an absent implementation.

### 1d. Text-mode JSON hash discrepancy

BLOCKED. The target v0.1.0 package and JSON files referenced in the claim are absent from the workspace, so the hash discrepancy check cannot be reproduced here. The hash check in the earlier Task B materials is a separate, blocked artifact and is not the requested package.

### 1e. Sign-control defect claim

BLOCKED. The old positive-sine sign-control check is not found in the available local package and no candidate v0.1.1 package was present. The sign-control claim therefore remains unverified.

## Part 2 — Verify physics and numerics

### 2a. Spin sign and rotation

BLOCKED. The spin-update implementation and the requested DTL protocol package were not present in the workspace. The file [verification/taskB/v0.1.1/oscillator_verification_fixed.py](../verification/taskB/v0.1.1/oscillator_verification_fixed.py) is a damped-oscillator verification script and not the spin lattice implementation described in the protocol. No independent rotation or norm-conservation run could be reproduced under the required constraints.

### 2b. Strang convergence

BLOCKED. No deterministic cavity-signal Strang integrator or package source is available in the workspace. The available script does not implement the required DTL many-body spin update or cavity signal integration.

### 2c. Noise and covariance

BLOCKED. The package implementing the stochastic oscillator/noise covariance calculations is not present in the workspace; therefore the Monte Carlo variance and Brownian coarse-graining checks cannot be repeated here.

### 2d. Parameter and equation fidelity

BLOCKED. The required protocol equations and source-paper comparisons cannot be verified without the candidate PDF/ZIP and a full source extraction workflow. The local source PDF is present, but the exact matching of equations and figures to the protocol remains unverified.

### 2e. Warmup and record length

BLOCKED. The candidate package and protocol text are absent. No warmup/record-length check can be computed from the missing implementation.

## Part 3 — Statistical design

BLOCKED. The statistical gate and bootstrap design described in the request is not present in the available workspace package, so no direct P1/P2 gate audit can be executed.

## Part 4 — Feasibility

BLOCKED. The required spin update code for a large L=100, Np=10^4, R=100 simulation is absent, so no measured throughput or memory estimate can be produced from the target implementation.

## Part 5 — Source fidelity

BLOCKED. The local source PDF is present at [verification/taskA/computations/arxiv_2610_30266.pdf](../verification/taskA/computations/arxiv_2610_30266.pdf), but the exact figure and equation cross-checks requested for the protocol are not reproduced in this workspace. The source-fidelity items are therefore blocked.

## Part 6 — Engineering gates and protocol integrity

BLOCKED. The protocol itself is absent, so no gate inventory or integrity analysis can be performed against the missing text. However, the local QA package is plainly not a true 11/11 test suite and is not a valid basis for claiming protocol validation.

## Recommendation

Recommendation: BLOCK

### Top three findings
1. The local QA package does not contain a real pytest suite and therefore does not reproduce an 11/11 pass count.
2. The available script itself fails: `overall_verdict: "FAIL: energy_ledger_residual"` when run in the configured environment.
3. The protocol package and candidate PDF named in the request are missing from the workspace; all protocol-specific checks are therefore BLOCKED.
