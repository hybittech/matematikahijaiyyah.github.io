# Security Policy

## Kebijakan Keamanan — HOM (Hijaiyyah Operating Machine)

Dokumen ini menjelaskan kebijakan keamanan, prosedur pelaporan
kerentanan, dan prinsip keamanan yang berlaku untuk proyek HOM.

---

## Daftar Isi

- [Versi yang Didukung](#versi-yang-didukung)
- [Melaporkan Kerentanan](#melaporkan-kerentanan)
- [Proses Penanganan](#proses-penanganan)
- [Prinsip Keamanan Sistem](#prinsip-keamanan-sistem)
- [Arsitektur Keamanan HOM](#arsitektur-keamanan-hom)
- [Apa yang Dilindungi](#apa-yang-dilindungi)
- [Apa yang Tidak Dilindungi](#apa-yang-tidak-dilindungi)
- [Panduan Keamanan untuk Kontributor](#panduan-keamanan-untuk-kontributor)
- [Disclosure Policy](#disclosure-policy)
- [Kontak](#kontak)

---

## Versi yang Didukung

| Versi | Status | Dukungan Keamanan |
|---|---|---|
| 1.0.x | ✅ Aktif | Patch keamanan diberikan |
| < 1.0 | ❌ Tidak didukung | Tidak ada patch |

Hanya versi yang tercantum sebagai **Aktif** yang menerima
pembaruan keamanan. Pengguna versi lama sangat disarankan
untuk memperbarui ke versi terbaru.

---

## Melaporkan Kerentanan

### ⚠️ Jangan Laporkan Kerentanan Melalui Issue Publik

Kerentanan keamanan **tidak boleh** dilaporkan melalui
GitHub Issues publik. Pelaporan publik dapat memberikan
kesempatan kepada pihak yang berniat jahat untuk
mengeksploitasi kerentanan sebelum diperbaiki.

### Cara Melaporkan

#### Opsi 1 — GitHub Security Advisories (Direkomendasikan)

1. Buka halaman **Security** di repository ini.
2. Klik **"Report a vulnerability"**.
3. Isi formulir dengan detail berikut:
   - **Judul**: deskripsi singkat kerentanan
   - **Deskripsi**: penjelasan teknis lengkap
   - **Langkah reproduksi**: cara memicu kerentanan
   - **Dampak**: apa yang bisa terjadi jika dieksploitasi
   - **Versi yang terpengaruh**: versi HOM mana yang terdampak
   - **Saran perbaikan** (jika ada)

#### Opsi 2 — Email Langsung

Jika GitHub Security Advisories tidak tersedia,
kirim laporan ke alamat email yang tercantum di
profil organisasi GitHub **hybittech**.

### Informasi yang Diperlukan

```
Judul:              [Deskripsi singkat]
Komponen:           [core / language / gui / crypto / ...]
Versi:              [1.0.0 / commit hash]
Tingkat Keparahan:  [Critical / High / Medium / Low]

Deskripsi:
[Penjelasan teknis kerentanan]

Langkah Reproduksi:
1. ...
2. ...
3. ...

Dampak:
[Apa yang bisa terjadi jika dieksploitasi]

Bukti / PoC:
[Screenshot, log, atau kode bukti konsep]

Saran Perbaikan:
[Jika ada]
```

---

## Proses Penanganan

### Timeline

| Tahap | Target Waktu |
|---|---|
| **Konfirmasi penerimaan** | 48 jam |
| **Triase awal** | 7 hari |
| **Investigasi dan perbaikan** | 14–30 hari |
| **Rilis patch** | sesuai jadwal rilis atau hotfix |
| **Pengumuman publik** | setelah patch tersedia |

### Alur Penanganan

```
1. Laporan diterima
       │
       ▼
2. Konfirmasi kepada pelapor (48 jam)
       │
       ▼
3. Triase: validasi dan penilaian keparahan
       │
       ├── Critical/High → hotfix track
       └── Medium/Low → rilis reguler
       │
       ▼
4. Investigasi dan pengembangan perbaikan
       │
       ▼
5. Internal testing
       │
       ▼
6. Rilis patch
       │
       ▼
7. Pengumuman publik (Security Advisory)
       │
       ▼
8. Kredit kepada pelapor (jika diizinkan)
```

### Tingkat Keparahan

| Level | Kriteria |
|---|---|
| **Critical** | Eksekusi kode arbitrer, bypass autentikasi penuh |
| **High** | Kebocoran data sensitif, bypass guard, integritas dataset rusak |
| **Medium** | Denial of service, bypass validasi parsial |
| **Low** | Information disclosure minor, UX issue terkait keamanan |

---

## Prinsip Keamanan Sistem

### Prinsip 1 — Integritas Dataset adalah Prioritas Utama

Master Table HM-28-v1.0-HC18D adalah **sumber kebenaran formal**.
Setiap mekanisme yang dapat:
- memodifikasi isi Master Table tanpa otorisasi,
- mengubah SHA-256 seal tanpa melalui proses rilis resmi,
- atau mengelabui guard system,

dianggap sebagai **kerentanan tingkat tinggi**.

### Prinsip 2 — Guard ≠ Kriptografi Penuh

Sistem guard internal HOM (G1–G4, R1–R5) berfungsi sebagai
**validasi struktural lapis pertama**. Guard:

- ✅ mendeteksi inkonsistensi data,
- ✅ menolak codex yang rusak strukturnya,
- ✅ bekerja secara lokal tanpa kunci atau sertifikat,

tetapi guard **tidak** menjamin:

- ❌ autentikasi pengirim,
- ❌ kerahasiaan data,
- ❌ non-repudiation,
- ❌ perlindungan terhadap replay attack,
- ❌ perlindungan terhadap man-in-the-middle.

Untuk kebutuhan keamanan di atas, mekanisme kriptografis
tambahan (TLS, PKI, digital signature) tetap diperlukan.

### Prinsip 3 — Evaluator Bukan Sandbox

HC evaluator dan HCVM saat ini **belum** memiliki
sandboxing yang ketat. Oleh karena itu:

- **jangan** menjalankan kode HC dari sumber yang tidak dipercaya
  tanpa review terlebih dahulu,
- **jangan** mengekspos evaluator langsung ke input jaringan
  tanpa lapisan validasi,
- **jangan** mengasumsikan bahwa evaluator aman terhadap
  input yang sengaja dirancang untuk menyerang.

### Prinsip 4 — Determinisme sebagai Fondasi Keamanan

Seluruh pipeline HOM bersifat deterministik:

```
dataset-seal yang sama + protokol yang sama = hasil yang sama
```

Jika hasil berbeda ditemukan dari input yang sama, itu adalah
indikasi adanya:
- korupsi data,
- modifikasi tidak sah,
- atau bug implementasi.

Determinisme ini sendiri merupakan mekanisme keamanan,
karena memungkinkan **audit forensik** yang reproducible.

---

## Arsitektur Keamanan HOM

### Layer Keamanan

```
┌──────────────────────────────────────────────────┐
│ Layer 4 — Network Security (Future)              │
│ TLS / authentication / authorization             │
├──────────────────────────────────────────────────┤
│ Layer 3 — Cryptographic Integrity (HGSS / L6)    │
│ SHA-256 hashing · digital signatures · seals     │
├──────────────────────────────────────────────────┤
│ Layer 2 — Structural Validation (Guards)          │
│ G1–G4 · R1–R5 · topology guards · ρ ≥ 0         │
├──────────────────────────────────────────────────┤
│ Layer 1 — Data Integrity (Dataset Seal)           │
│ SHA-256 seal · manifest · ROM checksum           │
├──────────────────────────────────────────────────┤
│ Layer 0 — Formal Foundation                       │
│ Deterministic pipeline · integer-only · auditable│
└──────────────────────────────────────────────────┘
```

### Komponen Keamanan

| Komponen | Lokasi | Fungsi |
|---|---|---|
| Guard System | `core/guards.py` | Validasi struktural G1–G4 |
| Exomatrix Audit | `algebra/exomatrix_analysis.py` | Audit R1–R5 |
| Hashing | `crypto/hashing.py` | SHA-256 deterministik |
| Signing | `crypto/signing.py` | Tanda tangan artefak |
| Certificate | `crypto/certificate.py` | Release certificate |
| Guard Filter | `crypto/guard_filter.py` | Penolakan data invalid |
| Seal Verifier | `integrity/seal.py` | Verifikasi dataset seal |

---

## Apa yang Dilindungi

| Aset | Mekanisme Perlindungan |
|---|---|
| **Master Table** | SHA-256 seal + guard validation on load |
| **Codex per huruf** | Guard G1–G4 + checksum internal |
| **Exomatrix** | Audit R1–R5 |
| **Release identity** | Manifest + certificate + SHA-256 |
| **ROM binary** | Checksum verification |
| **Hasil komputasi** | Determinisme pipeline |

---

## Apa yang Tidak Dilindungi

| Aset / Skenario | Status |
|---|---|
| **Kode HC dari sumber tidak dipercaya** | Belum ada sandbox |
| **Komunikasi jaringan** | Belum ada TLS/PKI integration |
| **Autentikasi pengguna** | Belum ada user auth system |
| **Akses file lokal** | Bergantung pada OS permission |
| **Side-channel attacks** | Tidak dalam scope saat ini |
| **Quantum-resistant crypto** | Tidak dalam scope saat ini |

---

## Panduan Keamanan untuk Kontributor

### Yang WAJIB dilakukan

| No | Aturan |
|---|---|
| 1 | **Jangan** commit secrets, API keys, atau private keys |
| 2 | **Jangan** commit file `.env` |
| 3 | **Jangan** hardcode credentials di source code |
| 4 | **Gunakan** `hijaiyyah.errors` untuk exception handling |
| 5 | **Validasi** semua input sebelum diproses |
| 6 | **Jangan** gunakan `eval()` atau `exec()` pada input pengguna |
| 7 | **Jangan** modifikasi Master Table tanpa proses rilis formal |
| 8 | **Jalankan** `ruff check` sebelum commit |
| 9 | **Tulis** test untuk setiap fitur keamanan baru |
| 10 | **Laporkan** jika menemukan cara bypass guard |

### Checklist Keamanan untuk Pull Request

```
- [ ] Tidak ada secrets/credentials yang ter-commit
- [ ] Tidak ada eval()/exec() pada input pengguna
- [ ] Input divalidasi sebelum diproses
- [ ] Guard system tidak dibypass
- [ ] Master Table tidak dimodifikasi
- [ ] SHA-256 seal tidak diubah
- [ ] Exception menggunakan kelas kustom
- [ ] Test keamanan ditambahkan (jika relevan)
```

### File yang Tidak Boleh Ada di Repository

| File/Pattern | Alasan |
|---|---|
| `.env` | berisi environment variables sensitif |
| `*.key` | private keys |
| `*.pem` | certificates/keys |
| `secrets.*` | data sensitif |
| `credentials.*` | login credentials |
| `*.log` | mungkin berisi data sensitif |
| `config.local.*` | konfigurasi lokal |

Pastikan `.gitignore` sudah mencakup semua pola di atas.

---

## Disclosure Policy

### Responsible Disclosure

Kami mengikuti prinsip **responsible disclosure**:

1. Pelapor melaporkan kerentanan secara privat.
2. Tim melakukan investigasi dan perbaikan.
3. Patch dirilis.
4. Pengumuman publik dilakukan **setelah** patch tersedia.
5. Pelapor mendapat kredit (jika diizinkan).

### Timeline Disclosure

| Tahap | Waktu |
|---|---|
| Laporan → patch | Maksimal 90 hari |
| Patch → pengumuman publik | 7 hari setelah patch rilis |
| Force disclosure | 90 hari setelah laporan awal |

Jika perbaikan memerlukan lebih dari 90 hari,
kami akan berkoordinasi dengan pelapor tentang timeline
yang dapat diterima kedua pihak.

### Kredit

Pelapor kerentanan yang valid akan menerima kredit di:
- Security Advisory GitHub,
- CHANGELOG.md,
- dan (jika diizinkan) di acknowledgments.

---

## Kontak

### Untuk Laporan Keamanan

| Metode | Detail |
|---|---|
| **GitHub Security Advisory** | Tab Security di repository ini |
| **Email** | Melalui profil organisasi hybittech |

### Response Time

| Jenis | Target |
|---|---|
| Konfirmasi penerimaan | 48 jam |
| Triase awal | 7 hari |
| Update status | setiap 14 hari |

### Maintainer Keamanan

| Nama | Peran |
|---|---|
| Maulana Amratulloh | Lead Maintainer |

---

## Terima Kasih

Kami menghargai setiap laporan keamanan yang bertanggung jawab.
Keamanan sistem ini bergantung pada kewaspadaan bersama.

---

<div align="center">

**HOM — Hijaiyyah Operating Machine**

© 2026 Hijaiyyah Mathematics Computational Laboratory (HMCL)

</div>
