# Changelog

Semua perubahan penting pada proyek **HOM (Hijaiyyah Operating Machine)**
didokumentasikan di file ini.

Format ini mengikuti [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
dan proyek ini menggunakan [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-01

### Identitas Rilis

| Field | Nilai |
|---|---|
| Release | HM-28-v1.0-HC18D-B84D025 |
| Dataset | 28 letters × 18 dimensions |
| ROM | 252 bytes (nibble-packed) |
| SHA-256 | `f82d385917ffe32ae2b5711409b1341e90934c52172ae9d0fa68888e3b9c51c8` |
| Status | VERIFIED & SEALED |

---

### Added

#### Fondasi Formal (L0 — Core)
- Master Table HM-28-v1.0-HC18D: dataset formal 28×18 dengan validasi guard saat load
- CodexEntry dataclass dengan 18 komponen integer
- ROM binary 252 bytes (nibble-packed format)
- Guard system G1–G4 dengan validasi structural intrinsik
- Checksum internal: A_N, A_K, A_Q
- Topology guards: Ks > 0 ⇒ Qc ≥ 1, Kc > 0 ⇒ Qc ≥ 1
- Canonical character normalization (ه → هـ)
- Dataset manifest dengan SHA-256 seal
- Constants: H28_ALPHABET, V18_SLOTS, canonical mappings

#### Algebra Engine (Bab II — Lima Bidang)
- `vectronometry.py`: rasio primitif, rasio turning, sudut komposisional,
  norma codex, inner product, cosine similarity, Pythagorean check
- `differential.py`: operator beda total, beda per lapisan, dekomposisi norma,
  gradien Nuqṭah, gradien U, beda kedua, dot-variant detection
- `integral.py`: string integral, add_codex, layer integrals, centroid,
  cumulative trajectory, energy integral, mean theta
- `geometry.py`: Euclidean/Manhattan/Hamming distance, distance decomposition,
  nearest neighbors, k-nearest, support orthogonality, Gram matrix,
  diameter, alphabet centroid, polarization identity check
- `exomatrix_analysis.py`: Exomatrix builder, R1–R5 audit, row sums,
  grand sum, Frobenius energy Φ, energy decomposition, energy table,
  reconstruction from Exomatrix

#### Bahasa Formal (L1 — HC Language)
- Token system dengan 40+ token types termasuk HIJAIYYAH literal
- Lexer dengan dukungan:
  - Unicode NFC normalization
  - Hijaiyyah literal ('ب', 'هـ')
  - String escape sequences (\n, \t, \", \\)
  - Single-line (//) dan block (/* */) comments
  - Float literals
  - Range operators (.. dan ..=)
- Parser recursive-descent untuk:
  - let/const/fn/return/if/else/match/while/for
  - Binary expressions dengan precedence
  - Method calls dan module access (::)
  - Array literals
  - Use statements dengan wildcard dan named imports
- AST nodes: Program, Block, LetStmt, ConstStmt, UseStmt, FnDecl,
  ReturnStmt, IfExpr, WhileStmt, ForStmt, MatchExpr, BinaryExpr,
  UnaryExpr, CallExpr, MethodCall, ModuleAccess, VarRef, Literal,
  ArrayLiteral, RangeExpr
- Grammar EBNF referensi (HC v1.0)
- Evaluator dengan standard library modules:
  - hm::vectronometry
  - hm::differential
  - hm::integral
  - hm::geometry
  - hm::exomatrix
- Built-in functions: load, zero, println, assert, identify, is_hijaiyyah

#### Arsitektur Instruksi (L2 — H-ISA)
- Instruction word format: 32-bit fixed [OP:8][DST:4][S1:4][S2:4][IMM:12]
- Register model: 18 GPR + 4 Codex registers + PC + FLAGS
- Status flags: GUARD, ZERO, OVR
- Opcodes: CLOAD, CADD, VCHK, VDIST, VRHO, CHASH, CSIGN
- Machine state dump dan trace
- Bytecode assembler dan disassembler
- Compiler HC → H-ISA (subset awal)

#### Mesin Virtual (L5 — HCVM)
- Standalone virtual machine (hcvm.py)
- Built-in commands: EMIT, AGGREGATE, COD18, VERIFY_CHECKSUM,
  VERIFY_MOD4, DECOMPOSE, SEAL
- Script execution dari HL-18E source
- Demo scripts: hello, financial, protocol

#### Keamanan (L6 — HGSS)
- Guard filter: penolakan data invalid sebelum proses
- SHA-256 hashing untuk artefak
- Signing stubs
- Certificate generation stubs

#### Format Pertukaran (L7 — HC18DC)
- JSON export dengan ensure_ascii=False
- CSV export
- Manifest JSON export
- Canonical digest (JCS + NFC + SHA-256) spesifikasi awal

#### Protokol HISAB
- Canonical Serialization untuk codex 18D
- Tiga format frame: LETTER (nibble-packed 9 byte), STRING (word-packed 36 byte), MATRIX (25 byte)
- Validasi intrinsik 3-level: Structural (magic/CRC), Guard (geometric constraints), Semantic (dataset cross-ref)
- Deteksi korupsi frame multi-layer 
- Round-trip fidelity dan injectivity verification untuk seluruh 28 huruf

#### CSGI Pipeline
- Zhang-Suen thinning (skeletonizer)
- Skeleton graph contractor
- CSGI graph object dengan JSON export
- 8-neighborhood adjacency enforcement
- Nuqṭah exclusion protocol
- Parameter lock: φ_corner=60°, τ_prune=3px

#### Integrity Engine
- Injectivity verifier (378 unique pairs)
- Quadrant decomposition checker (Θ̂ = U + ρ)
- Mod-4 gate verifier
- Pythagorean vectronometry checker
- Energy-norm inequality checker (Φ > ‖v₁₄‖²)
- Audit runner (guard + checksum + topology)
- Seal verifier (SHA-256 dataset)

#### Theorem Engine
- 13-test theorem suite:
  1. Guard checks (28/28)
  2. Injectivity of v₁₈ (378 pairs)
  3. Turning decomposition Θ̂ = U + ρ
  4. String integral additivity
  5. Pythagorean vectronometry
  6. Frobenius energy inequality
  7. Diameter² = 70
  8. Primitive ratios sum = 1
  9. Polarization identity
  10. Exomatrix R1–R5 audit (140 checks)
  11. Exomatrix reconstruction uniqueness
  12. Anagram invariance
  13. Guard detail R1–R5 all True

#### HOM GUI
- Letter Explorer: profil lengkap per huruf dengan Bab II analytics
- Master Table: tabel interaktif 28×18
- Theorems & Verification: structured Treeview dengan detail panel
- String Codex: notebook dengan Report/Trajectory/Breakdown/Raw tabs
- Audit Console: structured audit dengan Treeview dan detail panel
- Five Fields Workbench: 6 subtabs (Overview + 5 bidang)
- Codex Geometry: 4 subtabs (Overview/Pairwise/Nearest/Global)
- HC IDE: editor + reference panel + output notebook
  (Console/Diagnostics/AST/Bytecode/Result)
- H-ISA Machine: state viewer dengan refresh
- Bytecode Inspector: real-time decoder dengan validasi
- HCVM Console: standalone VM execution
- CSGI Processor: pipeline interaktif
- HISAB Explorer: frame encoder, validation pipeline, corruption detector, round-trip test
- Export: JSON/CSV/manifest
- Release Console: 5 subtabs
  (Overview/Manifest/Certificate/Legal/Sync Log)

#### Infrastruktur Proyek
- `src/` layout (PEP 517 / PEP 621)
- `pyproject.toml` dengan Pyright configuration
- `.editorconfig` untuk konsistensi format
- `.gitignore` lengkap
- GitHub Actions CI (test + lint)
- Entry point: `python -m hijaiyyah` dan `hom` command

#### Dokumentasi
- `README.md` resmi dengan badges dan contoh kode
- `docs/architecture.md` (dokumen arsitektur lengkap)
- Engineering standards document
- Daftar isi buku sampai Bab V
- Glosarium dan notasi lengkap

---

### Verified

| Pemeriksaan | Hasil |
|---|---|
| Theorem tests | 13/13 PASS |
| Guard checks (G1–G4) | 28/28 PASS |
| Exomatrix audit (R1–R5) | 140/140 PASS |
| Injectivity | 378/378 unique pairs |
| Diameter | √70 ≈ 8.367 VERIFIED |
| Energy inequality | 28/28 strict Φ > ‖v₁₄‖² |
| Global Σ Θ̂ | 91 = 52 + 39 VERIFIED |
| HISAB fidelity | 28/28 D(S(h*))=h* VERIFIED |

---

### Known Issues

- GUI architecture masih monolitik (HOMApp single class)
- Beberapa tab masih dominan text dump
- HC vs HL-18Q belum sepenuhnya terpisah
- `comp_angle()` di evaluator perlu alignment dengan definisi Bab II
- `numpy.int64` serialization issue pada CSGI JSON output
- H* channel belum sepenuhnya dilindungi oleh audit relation
- Benchmark formal belum tersedia
- HCPU belum diimplementasikan (status: DESIGNED)

---

### Migration Notes

Ini adalah rilis pertama. Tidak ada migrasi yang diperlukan.

---

### Release Signature

```
Signed:     Maulana Amratulloh
Key ID:     MA-SIG
Release:    HM-28-v1.0-HC18D-B84D025
Seal:       VERIFIED & SEALED
Copyright:  © 2026 HMCL
```

---

## [Unreleased]

### Planned
- Refactor GUI ke arsitektur service layer
- Pemisahan HC dan HL-18Q
- Benchmark suite formal
- Test coverage > 80%
- HC18DC format standardization
- HCPU softcore FPGA prototype
- Web interface (hybit-web)

---

[1.0.0]: https://github.com/hybittech/HOM/releases/tag/v1.0.0
[Unreleased]: https://github.com/hybittech/HOM/compare/v1.0.0...HEAD
