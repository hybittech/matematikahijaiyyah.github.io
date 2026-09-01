#!/usr/bin/env python3
import csv
import os
import re

repo_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
csv_path = os.path.join(repo_dir, 'data', 'hm28.csv')
js_path = os.path.join(repo_dir, 'hom-gui', 'src', 'engine', 'masterTable.js')

# Parse CSV (ground truth)
csv_data = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # CSV ordering: Theta_Hat,Na,Nb,Nd,Kp,Kx,Ks,Ka,Kc,Qp,Qx,Qs,Qa,Qc,An,Ak,Aq,H_Star
        # GUI v18 ordering from comment: [Θ̂, Na,Nb,Nd, Kp,Kx,Ks,Ka,Kc, Qp,Qx,Qs,Qa,Qc, H*, AN,AK,AQ]
        v18_csv = [
            int(row['Theta_Hat']),
            int(row['Na']), int(row['Nb']), int(row['Nd']),
            int(row['Kp']), int(row['Kx']), int(row['Ks']), int(row['Ka']), int(row['Kc']),
            int(row['Qp']), int(row['Qx']), int(row['Qs']), int(row['Qa']), int(row['Qc']),
            int(row['H_Star']),
            int(row['An']), int(row['Ak']), int(row['Aq']),
        ]
        csv_data.append({
            'char': row['Huruf'],
            'name': row['Name'],
            'v18': v18_csv,
        })

# Parse JS masterTable
with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

js_entries = []
pattern = r"\{ char: '(.+?)', name: '(.+?)',\s*v18: \[([^\]]+)\] \}"
for m in re.finditer(pattern, js_content):
    char = m.group(1)
    name = m.group(2)
    v18 = [int(x.strip()) for x in m.group(3).split(',')]
    js_entries.append({'char': char, 'name': name, 'v18': v18})

print(f"CSV entries: {len(csv_data)}")
print(f"JS entries: {len(js_entries)}")
print()

# Cross-check
errors = []
for i, (csv_row, js_row) in enumerate(zip(csv_data, js_entries, strict=True)):
    letter_id = i + 1
    if csv_row['char'] != js_row['char']:
        errors.append(
            f"#{letter_id}: CHAR MISMATCH - "
            f"CSV='{csv_row['char']}' vs JS='{js_row['char']}'"
        )
    
    if csv_row['v18'] != js_row['v18']:
        diff_indices = [j for j in range(18) if csv_row['v18'][j] != js_row['v18'][j]]
        labels = [
            'Θ̂', 'Na', 'Nb', 'Nd', 'Kp', 'Kx', 'Ks', 'Ka', 'Kc',
            'Qp', 'Qx', 'Qs', 'Qa', 'Qc', 'AN', 'AK', 'AQ', 'H*',
        ]
        for idx in diff_indices:
            errors.append(
                f"#{letter_id} {csv_row['char']} ({csv_row['name']}): "
                f"{labels[idx]}[{idx}] "
                f"CSV={csv_row['v18'][idx]} vs JS={js_row['v18'][idx]}"
            )

if errors:
    print(f"❌ FOUND {len(errors)} DISCREPANCIES:")
    for e in errors:
        print(f"  {e}")
else:
    print("✅ ALL 28 LETTERS × 18 COMPONENTS MATCH PERFECTLY")

# Also check guard logic correctness
print("\n--- Guard Verification (from CSV data) ---")
guard_errors = []
for i, row in enumerate(csv_data):
    v = row['v18']
    theta, Na, Nb, Nd = v[0], v[1], v[2], v[3]
    Kp, Kx, Ks, Ka, Kc = v[4], v[5], v[6], v[7], v[8]
    Qp, Qx, Qs, Qa, Qc = v[9], v[10], v[11], v[12], v[13]
    Hstar = v[14]
    AN, AK, AQ = v[15], v[16], v[17]
    
    # G1: AN = Na + Nb + Nd
    if AN != Na + Nb + Nd:
        guard_errors.append(f"#{i+1} {row['char']}: G1 FAIL AN={AN} != {Na}+{Nb}+{Nd}={Na+Nb+Nd}")
    
    # G2: AK = Kp + Kx + Ks + Ka + Kc
    sumK = Kp + Kx + Ks + Ka + Kc
    if AK != sumK:
        guard_errors.append(f"#{i+1} {row['char']}: G2 FAIL AK={AK} != {sumK}")
    
    # G3: AQ = Qp + Qx + Qs + Qa + Qc
    sumQ = Qp + Qx + Qs + Qa + Qc
    if AQ != sumQ:
        guard_errors.append(f"#{i+1} {row['char']}: G3 FAIL AQ={AQ} != {sumQ}")
    
    # G4: ρ = Θ̂ - U >= 0, where U = Qx + Qs + Qa + 4*Qc
    U = Qx + Qs + Qa + 4 * Qc
    rho = theta - U
    if rho < 0:
        guard_errors.append(f"#{i+1} {row['char']}: G4 FAIL ρ={rho} < 0")

if guard_errors:
    print(f"❌ Guard errors: {len(guard_errors)}")
    for e in guard_errors:
        print(f"  {e}")
else:
    print("✅ ALL GUARDS G1-G4 PASS FOR 28/28 LETTERS (112/112)")

# Check engine completeness
print("\n--- Engine Module Completeness ---")
required = {
    'masterTable.js': 'Master Table (28×18 codex)',
    'guards.js': 'Guard System (G1-G4)',
    'vektronometry.js': 'VTM - Vektronometry',
    'normivektor.js': 'NMV - Normivektor',
    'aggregametric.js': 'AGM - Aggregametric',
    'intrametric.js': 'ITM - Intrametric',
    'exometric.js': 'EXM - Exometric',
    'symbolicEngine.js': 'Symbolic Engine (unified exports)',
}
engine_dir = r'c:\hijaiyyah-mathematics\hom-gui\src\engine'
engine_dir = os.path.join(repo_dir, 'hom-gui', 'src', 'engine')
for fname, desc in required.items():
    path = os.path.join(engine_dir, fname)
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    status = f"✅ {size} bytes" if exists else "❌ MISSING"
    print(f"  {fname:25s} {desc:45s} {status}")

# Check pages
print("\n--- Page Completeness ---")
pages_dir = os.path.join(repo_dir, 'hom-gui', 'src', 'pages')
for fname in sorted(os.listdir(pages_dir)):
    path = os.path.join(pages_dir, fname)
    size = os.path.getsize(path)
    print(f"  {fname:25s} {size:6d} bytes")

# Check components
print("\n--- Component Completeness ---")
comp_dir = os.path.join(repo_dir, 'hom-gui', 'src', 'components')
for fname in sorted(os.listdir(comp_dir)):
    path = os.path.join(comp_dir, fname)
    size = os.path.getsize(path)
    print(f"  {fname:25s} {size:6d} bytes")
