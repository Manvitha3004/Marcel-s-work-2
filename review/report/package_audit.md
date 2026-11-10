# Package audit

## Findings

- REFUTED: The local QA package does not reproduce an 11/11 pass count. The package is a script, not a real pytest suite.
- CONFIRMED: Executing the available QA script produced `overall_verdict`: "FAIL: energy_ledger_residual".
- BLOCKED: The detailed mutation set in the protocol request is not present in the workspace package, so those specific mutation checks cannot be run without the missing package.

## Test inventory

| File | Function | What it asserts | Tolerance | Test type |
|---|---|---|---|---|
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | symbolic_checks | Symbolic residual checks; exact zero expectation. | exactly 0 | script function, not pytest test |
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | convergence_study | Convergence study for A1, A2, A_eta; order check against theory. | observed order near 2 for RK2 / 4 for RK4 | script function, not pytest test |
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | energy_ledger | Energy-balance residual, thresholds <=1e-6 | <=1e-6 | script function, not pytest test |
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | limiting_case_tests | Limiting case A ≡ 1 and A ≡ a against closed-form formulas | <=1e-10 | script function, not pytest test |
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | bounds_check | Coefficient bounds eta in [1/phi, phi] | False when eta=1 | script function, not pytest test |
| verification/taskB/v0.1.1/oscillator_verification_fixed.py | stability_study | Floquet and monotonicity stability checks | problem-specific thresholds | script function, not pytest test |

## Execution evidence

```text
Command: .\.venv\Scripts\python.exe verification\taskB\v0.1.1\oscillator_verification_fixed.py
Result: {
  "overall_verdict": "FAIL: energy_ledger_residual"
}
```

```text
Command: .\.venv\Scripts\python.exe -m pytest -q verification\taskB\v0.1.1
Result: no tests ran in 0.01s
```

## Mutation-test status

BLOCKED. The requested mutation battery (spin sign, Strang ordering, noise scaling, D factor, oscillator frequency, QR sign) is not present in the available package and no matching source files are available in the workspace.