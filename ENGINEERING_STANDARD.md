# STANDAR ENGINEERING
# **HOM (Hijaiyyah Operating Machine)**
## Versi 1.0 — March 2026

### Repository: `github.com/hybittech/HOM`

---

## 1. IDENTITAS REPOSITORY

| Field | Nilai |
|---|---|
| **Organization** | hybittech |
| **Repository** | HOM |
| **Nama Sistem** | Hijaiyyah Operating Machine |
| **Fungsi** | Core computational system + GUI engine untuk Matematika Hijaiyyah |
| **Bahasa Utama** | Python 3.11+ |
| **Layout** | `src/` layout (PEP 517 / PEP 621) |
| **Entry Point** | `python -m hijaiyyah` |
| **Lisensi** | Proprietary — All Rights Reserved (© 2026 HMCL) |

---

## 2. POSISI DALAM EKOSISTEM

```text
GitHub Organization: hybittech/
│
├── HOM                        ← repo ini
│   Core computational system + GUI engine
│   Berisi: L0–L7, HC, H-ISA, HCVM, GUI, Audit
│
├── hijaiyyah-mathematics      ← terpisah
│   Teori formal, buku, paper, spesifikasi
│   Berisi: naskah Bab I–V, Origin Protocol, glosarium
│
├── hybit-web                  ← masa depan
│   Frontend / web interface
│
└── hybit-spec                 ← masa depan
    Spesifikasi formal standar terbuka
```

### Aturan Pemisahan

| Aturan | Penjelasan |
|---|---|
| HOM ≠ hijaiyyah-mathematics | sistem ≠ teori |
| HOM berisi kode | hijaiyyah-mathematics berisi naskah |
| HOM berdiri sendiri | bisa di-clone dan dijalankan tanpa repo lain |

---

## 3. STRUKTUR DIREKTORI RESMI

```text
HOM/
│
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── .gitignore
├── .editorconfig
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
│
├── src/
│   └── hijaiyyah/
│       ├── __init__.py
│       ├── __main__.py
│       ├── version.py
│       ├── config.py
│       ├── constants.py
│       ├── errors.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── master_table.py
│       │   ├── codex_entry.py
│       │   ├── codex.py
│       │   ├── hybit.py
│       │   ├── guards.py
│       │   ├── checksum.py
│       │   ├── rom.py
│       │   └── dataset.py
│       │
│       ├── algebra/
│       │   ├── __init__.py
│       │   ├── vectronometry.py
│       │   ├── differential.py
│       │   ├── integral.py
│       │   ├── geometry.py
│       │   └── exomatrix_analysis.py
│       │
│       ├── language/
│       │   ├── __init__.py
│       │   ├── tokens.py
│       │   ├── lexer.py
│       │   ├── parser.py
│       │   ├── ast_nodes.py
│       │   ├── evaluator.py
│       │   ├── grammar.py
│       │   └── builtins.py
│       │
│       ├── hisa/
│       │   ├── __init__.py
│       │   ├── opcodes.py
│       │   ├── registers.py
│       │   ├── machine.py
│       │   ├── compiler.py
│       │   └── assembler.py
│       │
│       ├── skeleton/
│       │   ├── __init__.py
│       │   ├── skeletonizer.py
│       │   ├── contractor.py
│       │   └── csgi.py
│       │
│       ├── integrity/
│       │   ├── __init__.py
│       │   ├── injectivity.py
│       │   ├── audit.py
│       │   └── seal.py
│       │
│       ├── theorems/
│       │   ├── __init__.py
│       │   ├── decomposition.py
│       │   ├── mod4_gate.py
│       │   ├── pythagorean.py
│       │   ├── energy_norm.py
│       │   └── test_suite.py
│       │
│       ├── crypto/
│       │   ├── __init__.py
│       │   ├── hashing.py
│       │   ├── signing.py
│       │   ├── certificate.py
│       │   └── guard_filter.py
│       │
│       ├── net/
│       │   ├── __init__.py
│       │   ├── codec.py
│       │   ├── json_format.py
│       │   └── server.py
│       │
│       ├── release/
│       │   ├── __init__.py
│       │   └── synchronizer.py
│       │
│       └── gui/
│           ├── __init__.py
│           ├── app.py
│           ├── theme.py
│           ├── state.py
│           │
│           ├── tabs/
│           │   ├── __init__.py
│           │   ├── letter_explorer.py
│           │   ├── master_table.py
│           │   ├── theorems.py
│           │   ├── string_integral.py
│           │   ├── audit.py
│           │   ├── five_fields.py
│           │   ├── geometry.py
│           │   ├── ide.py
│           │   ├── hisa_machine.py
│           │   ├── bytecode.py
│           │   ├── hcvm.py
│           │   ├── csgi.py
│           │   ├── export.py
│           │   └── release.py
│           │
│           └── widgets/
│               ├── __init__.py
│               ├── summary_panel.py
│               ├── result_table.py
│               └── detail_view.py
│
├── data/
│   ├── hm28.json
│   ├── hm28.csv
│   ├── hm28_manifest.json
│   ├── hm28.rom
│   └── kfgqpc_seal/
│       └── glyphs/
│
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   │   ├── __init__.py
│   │   ├── test_master_table.py
│   │   ├── test_codex_entry.py
│   │   ├── test_guards.py
│   │   └── test_rom.py
│   ├── test_algebra/
│   │   ├── __init__.py
│   │   ├── test_vectronometry.py
│   │   ├── test_differential.py
│   │   ├── test_integral.py
│   │   ├── test_geometry.py
│   │   └── test_exomatrix.py
│   ├── test_language/
│   │   ├── __init__.py
│   │   ├── test_lexer.py
│   │   ├── test_parser.py
│   │   └── test_evaluator.py
│   ├── test_hisa/
│   │   ├── __init__.py
│   │   ├── test_opcodes.py
│   │   ├── test_machine.py
│   │   └── test_compiler.py
│   ├── test_integrity/
│   │   ├── __init__.py
│   │   ├── test_injectivity.py
│   │   └── test_seal.py
│   ├── test_theorems/
│   │   ├── __init__.py
│   │   └── test_full_suite.py
│   └── test_integration/
│       ├── __init__.py
│       └── test_end_to_end.py
│
├── docs/
│   ├── architecture.md
│   ├── hc_language.md
│   ├── hisa_spec.md
│   ├── csgi_spec.md
│   ├── hcvm_spec.md
│   ├── release_policy.md
│   └── changelog.md
│
├── examples/
│   ├── hello.hc
│   ├── five_fields.hc
│   ├── string_analysis.hc
│   ├── banking_integrity.hc
│   └── iot_guard.hc
│
├── scripts/
│   ├── run_gui.py
│   ├── build_rom.py
│   ├── verify_release.py
│   └── benchmark.py
│
├── tools/
│   ├── codex_calculator.py
│   ├── table_verifier.py
│   └── rom_generator.py
│
└── release/
    └── HL-18E-v1.0/
        ├── MANIFEST.json
        ├── CERTIFICATE.json
        └── RELEASE_NOTES.md
```

---

## 4. FILE KONFIGURASI WAJIB

---

### 4.1 `pyproject.toml`

```toml
[project]
name = "hijaiyyah-hom"
version = "1.0.0"
description = "Hijaiyyah Operating Machine — Core Computational System"
authors = [
    { name = "Maulana Amratulloh" },
    { name = "Hijaiyyah Mathematics Computational Laboratory (HMCL)" }
]
requires-python = ">=3.11"
license = { text = "Proprietary" }

dependencies = [
    "numpy>=1.24",
    "networkx>=3.0",
    "pillow>=10.0",
    "scipy>=1.10",
]

[project.scripts]
hom = "hijaiyyah.__main__:main"

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.1",
    "mypy>=1.0",
]

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pyright]
include = ["src", "tests", "tools", "scripts"]
extraPaths = ["src"]
typeCheckingMode = "basic"
reportMissingImports = true
reportMissingModuleSource = false
pythonVersion = "3.11"
executionEnvironments = [
    { root = ".", extraPaths = ["src"] }
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
```

---

### 4.2 `requirements.txt`

```text
numpy>=1.24
networkx>=3.0
pillow>=10.0
scipy>=1.10
```

---

### 4.3 `requirements-dev.txt`

```text
pytest>=7.0
pytest-cov>=4.0
ruff>=0.1
mypy>=1.0
```

---

### 4.4 `.gitignore`

```text
__pycache__/
*.pyc
*.pyo
*.egg-info/
dist/
build/
.eggs/
venv/
.venv/
.env
*.log
*.swp
*.swo
.DS_Store
Thumbs.db
.idea/
.vscode/
*.rom.bak
```

---

### 4.5 `.editorconfig`

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 4

[*.md]
trim_trailing_whitespace = false

[*.toml]
indent_size = 2

[*.json]
indent_size = 2
```

---

## 5. ENTRY POINT

### `src/hijaiyyah/__main__.py`

```python
# -*- coding: utf-8 -*-
"""Entry point for HOM (Hijaiyyah Operating Machine)."""


def main():
    from hijaiyyah.gui.app import HOMApp
    app = HOMApp()
    app.run()


if __name__ == "__main__":
    main()
```

---

### `src/hijaiyyah/__init__.py`

```python
# -*- coding: utf-8 -*-
"""Hijaiyyah Mathematics — HOM Core Package."""

from .version import __version__

__all__ = ["__version__"]
```

---

### `src/hijaiyyah/version.py`

```python
# -*- coding: utf-8 -*-
"""Version information for HOM."""

__version__ = "1.0.0"
__release__ = "HM-28-v1.0-HC18D"
```

---

## 6. CARA MENJALANKAN

### 6.1 Development mode

```bash
cd HOM
pip install -e ".[dev]"
python -m hijaiyyah
```

### 6.2 Production mode

```bash
pip install .
hom
```

### 6.3 Testing

```bash
pytest
```

### 6.4 Linting

```bash
ruff check src/
```

### 6.5 Type checking

```bash
pyright
```

---

## 7. ATURAN CODING

---

### 7.1 Bahasa dan encoding

| Aturan | Nilai |
|---|---|
| Encoding file | UTF-8 |
| Line ending | LF |
| Max line length | 100 karakter |
| Python version | 3.11+ |
| Docstring style | Google style |
| Type hints | wajib untuk function signatures |

---

### 7.2 Penamaan

| Objek | Konvensi | Contoh |
|---|---|---|
| File/modul | `snake_case` | `master_table.py` |
| Kelas | `PascalCase` | `MasterTable` |
| Fungsi/method | `snake_case` | `get_by_char()` |
| Konstanta | `UPPER_SNAKE` | `H28_ALPHABET` |
| Variabel lokal | `snake_case` | `entry_count` |
| Private | `_prefix` | `_load()` |
| Dunder | `__name__` | `__init__()` |

---

### 7.3 Import

```python
# stdlib first
import hashlib
import json
from typing import Dict, List, Optional

# third-party
import numpy as np

# internal
from hijaiyyah.core.master_table import MasterTable
from hijaiyyah.core.codex_entry import CodexEntry
```

Jangan gunakan:
```python
from module import *
```

---

### 7.4 Docstring setiap file

Setiap file Python wajib memiliki docstring di baris pertama:

```python
# -*- coding: utf-8 -*-
"""
Module description.
"""
```

---

### 7.5 Error handling

Gunakan exception kustom:

```python
from hijaiyyah.errors import HijaiyyahError
```

Bukan `raise Exception(...)`.

---

## 8. ATURAN ARSITEKTUR

---

### 8.1 Pemisahan layer

| Layer | Fungsi | Boleh mengakses |
|---|---|---|
| `core/` | data formal, codex, guard | tidak ada layer lain |
| `algebra/` | operasi Bab II | `core/` |
| `integrity/` | audit, injectivity | `core/` |
| `theorems/` | theorem checks | `core/`, `algebra/` |
| `language/` | HC lexer, parser, evaluator | `core/`, `algebra/` |
| `hisa/` | ISA machine | `core/` |
| `skeleton/` | CSGI | `core/` |
| `crypto/` | hash, sign | `core/` |
| `net/` | data exchange | `core/`, `crypto/` |
| `release/` | versioning | `core/`, `crypto/` |
| `gui/` | tampilan | semua layer |

### 8.2 Prinsip utama

| Prinsip | Penjelasan |
|---|---|
| GUI tidak boleh menghitung | logika domain harus di service/algebra/core |
| Core tidak boleh import GUI | dependency satu arah |
| Setiap modul harus bisa diuji tanpa GUI | pure function > side effect |
| Setiap tab GUI harus file terpisah | satu tab = satu file |

---

## 9. ATURAN TESTING

---

### 9.1 Wajib ada test untuk:

| Modul | Test minimum |
|---|---|
| `core/master_table` | jumlah entri, panjang vektor, guard, injektivitas |
| `algebra/*` | satu test per fungsi utama |
| `language/lexer` | tokenisasi dasar, Hijaiyyah literal, error case |
| `language/parser` | parse let, fn, if, method call |
| `integrity/` | injectivity, seal |
| `theorems/` | full suite 13 test |

### 9.2 Golden test
Untuk output yang harus stabil, gunakan golden file:

```text
tests/golden/
    letter_ba.json
    string_bsm.json
    theorem_results.json
```

---

## 10. ATURAN GIT

---

### 10.1 Branching

| Branch | Fungsi |
|---|---|
| `main` | stable release |
| `dev` | development aktif |
| `feature/*` | fitur baru |
| `fix/*` | perbaikan bug |
| `release/*` | persiapan rilis |

### 10.2 Commit message

Format:

```text
[module] short description

- detail 1
- detail 2
```

Contoh:

```text
[core] fix master table guard validation

- added checksum verification on load
- added topology guard for Ks/Kc
```

### 10.3 Yang tidak boleh di-commit

| File/Folder | Alasan |
|---|---|
| `__pycache__/` | cache Python |
| `*.pyc` | bytecode |
| `venv/` | environment lokal |
| `.env` | secrets |
| `dist/` | build output |
| `build/` | build output |
| `*.log` | log runtime |
| `.vscode/` | setting lokal |

---

## 11. ATURAN RELEASE

---

### 11.1 Release checklist

Sebelum release:

1. semua test PASS,
2. SHA-256 master table dihitung ulang,
3. MANIFEST.json diperbarui,
4. RELEASE_NOTES.md ditulis,
5. version.py diperbarui,
6. CHANGELOG.md diperbarui,
7. tag git dibuat.

### 11.2 Versioning

Gunakan **Semantic Versioning**:

```text
MAJOR.MINOR.PATCH
```

Contoh:
- `1.0.0` — rilis pertama
- `1.1.0` — fitur baru
- `1.0.1` — bugfix

### 11.3 Tag

```bash
git tag -a v1.0.0 -m "HOM v1.0.0 — Initial Release"
git push origin v1.0.0
```

---

## 12. ATURAN DOKUMENTASI

---

### 12.1 Wajib ada di `docs/`:

| File | Isi |
|---|---|
| `architecture.md` | L0–L7, flow, diagram |
| `hc_language.md` | sintaks, tipe, contoh |
| `hisa_spec.md` | ISA, opcode, register |
| `csgi_spec.md` | pipeline skeleton |
| `hcvm_spec.md` | VM model |
| `release_policy.md` | kebijakan rilis |
| `changelog.md` | catatan perubahan |

### 12.2 README.md wajib berisi:

1. judul dan deskripsi singkat,
2. cara install,
3. cara menjalankan,
4. cara testing,
5. struktur direktori,
6. lisensi,
7. link ke dokumentasi.

---

## 13. ATURAN KEAMANAN

---

### 13.1 File `SECURITY.md`

Isi minimal:
- cara melaporkan kerentanan,
- kebijakan penanganan.

### 13.2 Tidak boleh di-commit:

| Data | Alasan |
|---|---|
| API key | sensitif |
| Private key | sensitif |
| Password | sensitif |
| `.env` file | berisi secrets |

### 13.3 Guard ≠ kriptografi penuh

Ini harus dipahami seluruh tim:
- guard = validasi struktural,
- HGSS = crypto layer,
- keduanya **bukan** pengganti PKI/TLS/SSL untuk komunikasi jaringan.

---

## 14. WORKFLOW GITHUB

---

### 14.1 Inisialisasi

```bash
git init
git add .
git commit -m "[init] HOM core system initialized"
git remote add origin https://github.com/hybittech/HOM.git
git branch -M main
git push -u origin main
```

### 14.2 CI minimal (GitHub Actions)

Buat file `.github/workflows/test.yml`:

```yaml
name: Test Suite

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest --tb=short -q

      - name: Lint
        run: ruff check src/
```

---

## 15. CHECKLIST SEBELUM PUSH PERTAMA

| No | Item | Status |
|---|---|---|
| 1 | `README.md` ada dan informatif | ☐ |
| 2 | `LICENSE` ada | ☐ |
| 3 | `.gitignore` ada dan benar | ☐ |
| 4 | `pyproject.toml` lengkap | ☐ |
| 5 | `src/hijaiyyah/__main__.py` berfungsi | ☐ |
| 6 | `src/hijaiyyah/__init__.py` ada | ☐ |
| 7 | `src/hijaiyyah/version.py` ada | ☐ |
| 8 | `src/hijaiyyah/core/master_table.py` berfungsi | ☐ |
| 9 | `tests/test_core/test_master_table.py` PASS | ☐ |
| 10 | `python -m hijaiyyah` berjalan | ☐ |
| 11 | Tidak ada file sensitif di repo | ☐ |
| 12 | Tidak ada `__pycache__` di repo | ☐ |

---

## 16. RINGKASAN SATU HALAMAN

### Repo ini:
- **nama**: `hybittech/HOM`
- **isi**: core system + GUI Matematika Hijaiyyah
- **layout**: `src/` layout (PEP 517)
- **entry**: `python -m hijaiyyah`
- **test**: `pytest`
- **lint**: `ruff`
- **type**: `pyright`
- **CI**: GitHub Actions

### Prinsip utama:
1. **GUI terpisah dari logic** — GUI hanya merender,
2. **Core tidak import GUI** — dependency satu arah,
3. **Setiap modul bisa diuji sendiri** — tanpa GUI,
4. **Setiap tab satu file** — modular,
5. **Test wajib ada** — sebelum push,
6. **Commit message standar** — `[module] description`,
7. **Release terstruktur** — manifest, certificate, tag.

---
