# Panduan Kontribusi — HOM

Terima kasih atas minat Anda untuk berkontribusi pada
**HOM (Hijaiyyah Operating Machine)**.

Dokumen ini menjelaskan prosedur, standar, dan etika kontribusi
yang berlaku untuk proyek ini.

---

## Daftar Isi

- [Status Proyek](#status-proyek)
- [Cara Berkontribusi](#cara-berkontribusi)
- [Pelaporan Masalah (Issues)](#pelaporan-masalah-issues)
- [Mengajukan Perubahan (Pull Request)](#mengajukan-perubahan-pull-request)
- [Standar Kode](#standar-kode)
- [Standar Commit](#standar-commit)
- [Standar Testing](#standar-testing)
- [Arsitektur dan Dependency](#arsitektur-dan-dependency)
- [Apa yang Tidak Boleh Dilakukan](#apa-yang-tidak-boleh-dilakukan)
- [Etika dan Perilaku](#etika-dan-perilaku)
- [Lisensi Kontribusi](#lisensi-kontribusi)
- [Kontak](#kontak)

---

## Status Proyek

HOM saat ini dikelola secara internal oleh
**Hijaiyyah Mathematics Computational Laboratory (HMCL)**.

Kontribusi eksternal **diterima dengan senang hati**, tetapi
tunduk pada proses review dan persetujuan dari maintainer.

Semua kontribusi yang diterima akan menjadi bagian dari proyek
di bawah lisensi yang berlaku.

---

## Cara Berkontribusi

Ada beberapa cara untuk berkontribusi:

### 1. Melaporkan bug atau masalah
Buat **Issue** di repository ini dengan deskripsi yang jelas.

### 2. Mengusulkan fitur
Buat **Issue** dengan label `[feature-request]` dan jelaskan:
- apa yang diusulkan,
- mengapa diperlukan,
- dan bagaimana bisa diimplementasikan.

### 3. Memperbaiki bug
Fork, buat branch, perbaiki, lalu ajukan **Pull Request**.

### 4. Menulis atau memperbaiki dokumentasi
Dokumentasi sama pentingnya dengan kode.

### 5. Menulis test
Menambah test coverage sangat dihargai.

### 6. Review kode
Memberi komentar konstruktif pada Pull Request.

---

## Pelaporan Masalah (Issues)

### Format Issue yang Baik

```
## Judul
[module] Deskripsi singkat masalah

## Deskripsi
Penjelasan lengkap tentang masalah.

## Langkah Reproduksi
1. ...
2. ...
3. ...

## Perilaku yang Diharapkan
...

## Perilaku yang Terjadi
...

## Lingkungan
- OS: ...
- Python: ...
- HOM version: ...

## Screenshot / Log (jika ada)
...
```

### Label Issue

| Label | Arti |
|---|---|
| `bug` | kesalahan yang perlu diperbaiki |
| `feature-request` | usulan fitur baru |
| `documentation` | perbaikan dokumentasi |
| `question` | pertanyaan umum |
| `good-first-issue` | cocok untuk kontributor baru |
| `priority-high` | perlu ditangani segera |

---

## Mengajukan Perubahan (Pull Request)

### Alur Kerja

```
1. Fork repository
2. Clone fork Anda:
   git clone https://github.com/YOUR_USERNAME/HOM.git

3. Buat branch baru:
   git checkout -b feature/nama-fitur
   atau
   git checkout -b fix/nama-perbaikan

4. Lakukan perubahan

5. Jalankan tests:
   pytest

6. Jalankan lint:
   ruff check src/

7. Commit dengan format standar:
   git commit -m "[module] deskripsi perubahan"

8. Push ke fork:
   git push origin feature/nama-fitur

9. Buat Pull Request ke branch `dev`
```

### Aturan Pull Request

| Aturan | Penjelasan |
|---|---|
| Target branch | `dev` (bukan `main`) |
| Satu PR = satu concern | jangan campur banyak perubahan |
| Harus PASS CI | tests dan lint harus hijau |
| Harus ada deskripsi | jelaskan apa yang berubah dan mengapa |
| Harus direview | minimal satu reviewer sebelum merge |

### Template Pull Request

```
## Deskripsi
Apa yang diubah dan mengapa.

## Tipe Perubahan
- [ ] Bug fix
- [ ] Fitur baru
- [ ] Dokumentasi
- [ ] Refactoring
- [ ] Test

## Modul yang Terpengaruh
- [ ] core/
- [ ] algebra/
- [ ] language/
- [ ] gui/
- [ ] tests/
- [ ] docs/

## Checklist
- [ ] Kode mengikuti standar proyek
- [ ] Tests ditambahkan atau diperbarui
- [ ] Semua tests PASS (`pytest`)
- [ ] Lint PASS (`ruff check src/`)
- [ ] Dokumentasi diperbarui (jika relevan)
- [ ] CHANGELOG.md diperbarui (jika signifikan)
```

---

## Standar Kode

### Bahasa dan Encoding

| Standar | Nilai |
|---|---|
| Python | 3.11+ |
| Encoding | UTF-8 |
| Line ending | LF |
| Max line | 100 karakter |
| Indent | 4 spasi |

### Penamaan

| Objek | Konvensi | Contoh |
|---|---|---|
| File | `snake_case` | `master_table.py` |
| Class | `PascalCase` | `MasterTable` |
| Function | `snake_case` | `get_by_char()` |
| Constant | `UPPER_SNAKE` | `H28_ALPHABET` |
| Private | `_prefix` | `_load()` |

### Import

```python
# 1. Standard library
import hashlib
import json
from typing import Dict, List, Optional

# 2. Third-party
import numpy as np

# 3. Internal
from hijaiyyah.core.master_table import MasterTable
from hijaiyyah.core.codex_entry import CodexEntry
```

**Dilarang:**
```python
from module import *
```

### Docstring

Gunakan **Google style**:

```python
def get_by_char(self, ch: str) -> Optional[CodexEntry]:
    """Retrieve a codex entry by its canonical Hijaiyyah character.

    Args:
        ch: A single canonical Hijaiyyah character.

    Returns:
        The CodexEntry if found, None otherwise.

    Raises:
        ValueError: If ch is not a valid character.
    """
```

### Type Hints

**Wajib** pada function signatures:

```python
def compute_distance(h1: CodexEntry, h2: CodexEntry) -> float:
    ...
```

### Error Handling

Gunakan exception kustom dari `hijaiyyah.errors`:

```python
from hijaiyyah.errors import HijaiyyahError, InvalidCodexError

raise InvalidCodexError(f"Guard check failed for {ch}")
```

**Jangan** gunakan `raise Exception(...)` secara langsung.

---

## Standar Commit

### Format

```
[module] deskripsi singkat

- detail perubahan 1
- detail perubahan 2
```

### Contoh

```
[core] fix master table guard validation

- added checksum verification on load
- added topology guard for Ks/Kc → Qc
- fixed canonical normalization for هـ
```

```
[algebra] add compositional angle to vectronometry

- implemented alpha(h) = arctan(A_Q / A_K)
- added edge cases for A_K = 0
- added unit test
```

```
[gui] refactor theorems tab to use Treeview

- replaced text dump with structured table
- added detail panel on selection
- added export report button
```

### Awalan Modul

| Awalan | Modul |
|---|---|
| `[core]` | `src/hijaiyyah/core/` |
| `[algebra]` | `src/hijaiyyah/algebra/` |
| `[language]` | `src/hijaiyyah/language/` |
| `[hisa]` | `src/hijaiyyah/hisa/` |
| `[skeleton]` | `src/hijaiyyah/skeleton/` |
| `[integrity]` | `src/hijaiyyah/integrity/` |
| `[theorems]` | `src/hijaiyyah/theorems/` |
| `[crypto]` | `src/hijaiyyah/crypto/` |
| `[net]` | `src/hijaiyyah/net/` |
| `[release]` | `src/hijaiyyah/release/` |
| `[gui]` | `src/hijaiyyah/gui/` |
| `[tests]` | `tests/` |
| `[docs]` | `docs/` |
| `[infra]` | pyproject.toml, CI, config |
| `[data]` | `data/` |

---

## Standar Testing

### Framework

```
pytest
```

### Lokasi

```
tests/
├── test_core/
├── test_algebra/
├── test_language/
├── test_hisa/
├── test_integrity/
├── test_theorems/
└── test_integration/
```

### Konvensi Penamaan

```
test_*.py          — file test
test_*()           — function test
TestClassName      — class test (opsional)
```

### Menjalankan Tests

```bash
# Semua tests
pytest

# Modul tertentu
pytest tests/test_core/test_master_table.py

# Dengan coverage
pytest --cov=hijaiyyah --cov-report=html

# Dengan output verbose
pytest -v
```

### Aturan Testing

| Aturan | Penjelasan |
|---|---|
| Setiap fitur baru **harus** punya test | tidak ada fitur tanpa test |
| Setiap bugfix **harus** punya regression test | jangan sampai terulang |
| Test harus bisa jalan **tanpa GUI** | pure function testing |
| Test **tidak boleh** bergantung pada network | offline-capable |
| Test **harus** deterministik | tidak random/flaky |

### Test Minimum yang Wajib PASS Sebelum Merge

| Modul | Test Minimum |
|---|---|
| `core/master_table` | 28 entri, vektor 18D, guard, injektivitas |
| `algebra/*` | satu test per fungsi utama |
| `language/lexer` | tokenisasi dasar, Hijaiyyah literal |
| `language/parser` | parse let, fn, if, method call |
| `integrity/` | injectivity, seal |
| `theorems/` | full suite 13 test |

---

## Arsitektur dan Dependency

### Aturan Dependency

```
core/          ← tidak import siapa pun
algebra/       ← import core/
integrity/     ← import core/
theorems/      ← import core/, algebra/
language/      ← import core/, algebra/
hisa/          ← import core/
skeleton/      ← import core/
crypto/        ← import core/
gui/           ← import semua (layer teratas)
```

### Prinsip

| Prinsip | Penjelasan |
|---|---|
| GUI **tidak menghitung** | logika domain di core/algebra |
| Core **tidak import** GUI | dependency satu arah |
| Setiap modul **bisa diuji sendiri** | tanpa GUI |
| Satu tab = satu file | modular |

### Menambah Dependency Baru

Jika Anda perlu menambahkan dependency baru:

1. diskusikan di Issue terlebih dahulu,
2. jelaskan mengapa library itu diperlukan,
3. pastikan lisensinya kompatibel,
4. tambahkan ke `pyproject.toml` (bukan hanya requirements.txt),
5. dan update dokumentasi jika diperlukan.

---

## Apa yang Tidak Boleh Dilakukan

### Dilarang keras:

| Larangan | Alasan |
|---|---|
| Mengubah isi Master Table tanpa persetujuan | merusak dataset seal |
| Mengubah SHA-256 seal | menggugurkan identitas rilis |
| Commit file cache/build | mengotori repository |
| Commit secrets/keys | keamanan |
| Mengubah `version.py` tanpa izin | manajemen rilis |
| Merge langsung ke `main` | harus melalui PR + review |
| Menambah dependency besar tanpa diskusi | bloat + lisensi |
| Mengubah `from module import *` | anti-pattern |

### Dilarang pada level konsep:

| Larangan | Alasan |
|---|---|
| Memperlakukan huruf sebagai bunyi/makna | di luar scope |
| Menjadikan Matematika Hijaiyyah sebagai tafsir | bukan domain ini |
| Mengklaim hybit menggantikan bit | posisi ilmiah salah |
| Mencampur HC dan HL-18Q dalam satu parser | arsitektur berbeda |

---

## Etika dan Perilaku

Semua kontributor wajib mematuhi
[Code of Conduct](CODE_OF_CONDUCT.md) proyek ini.

### Prinsip utama:

1. **Hormati** — perlakukan semua orang dengan hormat.
2. **Konstruktif** — kritik kode, bukan orangnya.
3. **Ilmiah** — argumen berdasarkan fakta, bukan otoritas.
4. **Jujur** — jangan overclaim; bedakan fakta, hipotesis, dan aspirasi.
5. **Inklusif** — proyek ini terbuka untuk semua latar belakang.

### Yang tidak ditoleransi:

- pelecehan dalam bentuk apa pun,
- diskriminasi,
- klaim superioritas budaya/agama yang dipakai sebagai argumen teknis,
- spam atau promosi tidak relevan.

---

## Lisensi Kontribusi

Dengan mengajukan Pull Request ke repository ini,
Anda menyatakan bahwa:

1. Anda memiliki hak atas kode yang Anda kirimkan.
2. Anda setuju bahwa kontribusi Anda menjadi bagian
   dari proyek di bawah lisensi yang berlaku.
3. Anda memahami bahwa proyek ini saat ini dilisensikan
   sebagai **Proprietary — All Rights Reserved**.

Jika Anda memiliki pertanyaan tentang lisensi,
silakan hubungi maintainer sebelum berkontribusi.

---

## Kontak

### Maintainer

| Nama | Peran |
|---|---|
| Maulana Amratulloh | Perancang & Perumus |

### Cara menghubungi

- **Issues**: gunakan [GitHub Issues](https://github.com/hybittech/HOM/issues)
- **Diskusi**: gunakan [GitHub Discussions](https://github.com/hybittech/HOM/discussions)
  (jika tersedia)
- **Email**: hubungi melalui profil organisasi GitHub

### Response time

Kami berusaha merespons:
- **Issues**: dalam 7 hari kerja
- **Pull Requests**: dalam 14 hari kerja

Namun response time dapat bervariasi tergantung kapasitas tim.

---

## Terima Kasih

Setiap kontribusi — sekecil apa pun — sangat berarti bagi
perkembangan Matematika Hijaiyyah dan ekosistem HOM.

Kami menghargai waktu, pikiran, dan niat baik Anda.

---

<div align="center">

**HOM — Hijaiyyah Operating Machine**

© 2026 Hijaiyyah Mathematics Computational Laboratory (HMCL)

</div>
