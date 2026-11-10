from pathlib import Path

path = Path(r"D:\Personal Projects\marcel's work\oscillator_verification.py")
text = path.read_text(encoding='utf-8')
lines = text.splitlines()
for name in ['A_prime', 'manufactured_a', 'eta_A', 'manufactured_ap', 'manufactured_force', 'energy_ledger']:
    print(f'## {name}')
    for i, line in enumerate(lines, start=1):
        if f'def {name}' in line:
            start = max(1, i - 1)
            end = min(len(lines), i + 30)
            for j in range(start, end + 1):
                print(f'{j:03d}: {lines[j-1]}')
            break
    else:
        print('NOT FOUND')
    print()
