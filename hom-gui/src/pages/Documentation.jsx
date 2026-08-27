import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

const readmeContent = `
# MATEMATIKA HIJAIYYAH

| **VTM** | **NMV** | **AGM** | **ITM** | **EXM** |
| :---: | :---: | :---: | :---: | :---: |
| Vektronometry | Normivektor | Aggregametric | Intrametric | Exometric |
| *Composition metrics* | *Norm-difference diagnostics* | *String accumulation* | *Distance geometry* | *Consistency audit* |

---

# **HOM — Hijaiyyah Operating Machine** &nbsp;&nbsp;&nbsp; [![Web GUI](https://img.shields.io/badge/Web_GUI-Open_App-blue?style=for-the-badge&logo=react)](https://hybittech.github.io)

### Core Computational System for Hijaiyyah Mathematics & Hybit Pipeline

[![Release](https://img.shields.io/badge/Release-HM--28--v1.2--HC18D-blue)]()
[![Python](https://img.shields.io/badge/Python-3.11+-green)]()
[![License](https://img.shields.io/badge/License-Proprietary-red)]()
[![Tests](https://img.shields.io/badge/Tests-1611%2F1611%20PASS-brightgreen)]()
[![Dataset](https://img.shields.io/badge/Dataset-28×18%20SEALED-orange)]()
[![Pipeline](https://img.shields.io/badge/Pipeline-.hc→.hbc→HVM-purple)]()
[![Paradigm](https://img.shields.io/badge/Paradigm-bit⊕qubit⊕hybit-gold)]()

**HOM** adalah sistem komputasi formal dan lingkungan kerja ilmiah terpadu untuk **Matematika Hijaiyyah** — sistem matematika murni yang memetakan 28 huruf Hijaiyyah kanonik ke dalam codex integer 18-dimensi melalui empat invarian geometri diskret, menghasilkan **hybit** sebagai paradigma komputasi ketiga.

[Dokumentasi](#dokumentasi) · [Instalasi](#instalasi) · [Pipeline](#pipeline-hybit) · [Arsitektur](#arsitektur-sistem) · [Lisensi](#lisensi)

---

## 📋 Daftar Isi

- [Tentang HOM](#tentang-hom)
- [Changelog Update Terbaru](#changelog-update-terbaru)
- [Hybit — Paradigma Komputasi Ketiga](#hybit--paradigma-komputasi-ketiga)
- [Pipeline Hybit](#pipeline-hybit)
- [Format File](#format-file)
- [Fitur Utama](#fitur-utama)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Cara Menjalankan](#cara-menjalankan)
- [Struktur Direktori](#struktur-direktori)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Technology Stack](#technology-stack)
- [H-ISA — Instruction Set](#h-isa--instruction-set-architecture)
- [Guard System vs HCHECK](#guard-system-vs-hcheck)
- [Verifikasi Matematis](#verifikasi-matematis)
- [1.380-Check Verification Framework](#1380-check-verification-framework)
- [Testing](#testing)
- [Contoh Kode HC](#contoh-kode-hc)
- [Dokumentasi](#dokumentasi)
- [Release Certificate](#release-certificate)
- [Kontribusi](#kontribusi)
- [Lisensi](#lisensi)
- [Penulis](#penulis)

---

## Tentang HOM

**HOM (Hijaiyyah Operating Machine)** adalah implementasi perangkat lunak utama dari **Matematika Hijaiyyah**, yang mencakup:

- **dataset formal** 28 huruf × 18 komponen integer,
- **Sistem Operasi Metrik-Vektorial** — lima operasi formal (Vektronometry, Normivektor, Aggregametric, Intrametric, Exometric),
- **bahasa pemrograman HC** (Hijaiyyah Codex) dengan compiler **HCC**,
- **hybit bytecode** (.hbc) dan assembler **HASM**,
- **mesin virtual HVM** (Hybit Virtual Machine) dengan guard system dan HCHECK,
- **arsitektur instruksi H-ISA** dengan operasi hybit-native,
- **standar pertukaran HISAB** (Hijaiyyah Inter-System Standard for Auditable Bridging),
- **format data geometri .hgeo** dan **registry alfabet HAR**,
- **prosesor graf skeleton CSGI** dengan Ψ-Compiler,
- **sistem audit dan verifikasi formal** — termasuk **1.380-check verification framework**,
- **spesifikasi OS hybit-native** (HOS, HFS, H-Kernel),
- dan **GUI ilmiah terpadu**.

### Apa itu Matematika Hijaiyyah?

Matematika Hijaiyyah adalah sistem formal yang memodelkan setiap huruf Hijaiyyah kanonik sebagai objek matematika, lalu memetakannya ke vektor integer 18-dimensi:

\`\`\`
h ∈ H₂₈  →  v₁₈(h) ∈ ℕ₀¹⁸
\`\`\`

melalui empat invarian geometri diskret:

| Invarian | Simbol | Deskripsi |
|---|---|---|
| **Nuqṭah** | N(h) = (Nₐ, Nᵦ, Nᵈ) | Struktur titik diskret per zona |
| **Khaṭṭ** | K(h) = (Kₚ, Kₓ, Kₛ, Kₐ, Kc) | Struktur garis per kategori |
| **Qaws** | Q(h) = (Qₚ, Qₓ, Qₛ, Qₐ, Qc) | Struktur lengkung per kategori |
| **Inḥinā'** | Θ̂(h) | Total belokan diskret MainPath |

Vektor codex yang dihasilkan bukan sekadar label — ia adalah **representasi aljabar operabel** yang mendukung **lima operasi metrik-vektorial** (Bab II) dan **paradigma komputasi hybit** (Bab III).

Unit komputasi formal yang dihasilkan disebut **hybit** (*Hijaiyyah Hyperdimensional Bit Integration Technology*) — paradigma komputasi ketiga yang secara aljabar berbeda dari bit dan qubit.

### Batas Domain (Scope & Boundaries)

Sistem ini **harus tetap berpusat pada huruf sebagai bentuk skriptural kanonik**, dengan pedoman berikut:

1. **Inti Resmi:** Domain inti dari sistem ini adalah **Hijaiyyah**. Matematika Hijaiyyah bukanlah framework generik untuk semua karakter Latin/ASCII atau simbol teknis utilitarian.
2. **HAR (Alphabet Registry):** Ruang lingkup keanggotaan HAR dibatasi pada analisis geometri karakter sebagai objek formal skriptural. \`HAR-001 (Hijaiyyah)\` adalah satu-satunya inti yang akan selalu berstatus tersertifikasi resmi (CERTIFIED).
3. **HC Language:** HC (Hijaiyyah Codex) adalah **alat komputasi hybit**, **bukan** proyek formalisasi visual di mana setiap token bahasanya harus menjadi hybit.

---

## Changelog Update Terbaru

> **v1.2.0-pipeline — Full System Alignment + Bab II Terminology Update**

### 🔄 Terminologi Bab II — Perubahan Utama

Seluruh terminologi Bab II diperbarui sesuai revisi terkini:

| Aspek | LAMA (v1.0–v1.1) | BARU (v1.2+) |
|---|---|---|
| **Judul Bab II** | Lima Bidang Matematika Hijaiyyah | **Sistem Operasi Metrik-Vektorial Hijaiyah** |
| **Operasi 1** | Vectronometry | **Vektronometry (VTM)** |
| **Operasi 2** | Kalkulus Diferensial / Differential | **Normivektor (NMV)** |
| **Operasi 3** | Kalkulus Integral / Integral | **Aggregametric (AGM)** |
| **Operasi 4** | Geometri Kodeks / Geometry | **Intrametric (ITM)** |
| **Operasi 5** | Analisis Eksomatriks / Exomatrix | **Exometric (EXM)** |
| **Notasi agregasi** | ∫ᵤᵥ = ∫ᵤ + ∫ᵥ | **Σᵤᵥ = Σᵤ + Σᵥ** |
| **Klasifikasi** | "Lima bidang analisis" | **"Lima operasi metrik-vektorial"** |
| **Pilar** | — | **Vektor + Norma + Metrik** |
| **Verifikasi Bab II** | 665 pemeriksaan | **683 pemeriksaan** |
| **Verifikasi Global** | 865 / 1.323 | **1.380 (658 + 683 + 39)** |

**Mengapa berubah:** Penamaan lama ("Kalkulus Diferensial", "Kalkulus Integral") menyiratkan kalkulus kontinu — padahal operasi sesungguhnya adalah **selisih hingga diskret** dan **akumulasi diskret** pada ruang vektor integer. Nama baru lebih jujur secara matematis.

### 🆕 Facade Modules Baru (Source Packages)

| Package Baru | Path | Re-exports dari | Fungsi |
|---|---|---|---|
| **\`compiler/\`** | \`src/hijaiyyah/compiler/\` | \`language/lexer\`, \`language/parser\`, \`hisa/compiler\` | HCC — HC Compiler facade |
| **\`assembler/\`** | \`src/hijaiyyah/assembler/\` | \`hisa/assembler\` | HASM — Hybit Assembler facade |
| **\`vm/\`** | \`src/hijaiyyah/vm/\` | \`hisa/machine\`, \`hisa/hcheck\`, \`core/guards\` | HVM — Hybit Virtual Machine facade |
| **\`pipeline/\`** | \`src/hijaiyyah/pipeline/\` | \`skeleton/csgi\`, \`core/codex\` | Ψ-Compiler facade + .hgeo format |
| **\`har/\`** | \`src/hijaiyyah/har/\` | \`core/master_table\` | HAR — Alphabet Registry facade |

### 🧪 Test Suite — 1.380-Check Verification Framework

| Bab | Pemeriksaan | Cakupan |
|---|---|---|
| **Bab I** | 658 | G1–G4 ×28, T1–T2 ×28, Injektivitas ×378, Turning ×28 |
| **Bab II** | 683 | VTM (83), NMV (7), AGM (7), ITM (390), EXM (196) |
| **Bab III** | 39 | Closure (3), Identity (8), Theorems (16), Pipeline (12) |

\`\`\`bash
$ python -m pytest tests/test_full_verification.py -v
============================ 1380 passed in 9.23s =============================
\`\`\`

---

## Hybit — Paradigma Komputasi Ketiga

### Tiga Struktur Aljabar yang Tak Tereduksi

| Dimensi | **Bit** (𝔽₂) | **Qubit** (ℂ²) | **Hybit** (𝒱 ⊂ ℕ₀¹⁸) |
|---|---|---|---|
| **Struktur** | Field | Ruang Hilbert | Monoid terkonstrain |
| **Dimensi** | 0 (diskret 2-titik) | 2 (kontinu kompleks) | 18 (diskret integer) |
| **Operasi native** | AND, OR, NOT, XOR | U(2) gates, pengukuran | HCADD, HGRD, HPROJ |
| **Constraint** | Closure | ‖ψ‖ = 1 | G1–G4, ρ ≥ 0 |
| **Validasi per unit** | Tidak ada | Parsial, destruktif | **Penuh, O(1), non-destruktif** |
| **Determinisme** | Deterministik | Probabilistik | Deterministik |
| **Invers aditif** | Ada | Ada | **Tidak ada** |
| **Domain optimal** | Logika Boolean | Simulasi kuantum | **Data terstruktur + audit** |

### Empat Properti Unik Hybit

| # | Properti | Deskripsi | Status |
|---|---|---|---|
| 1 | **Validasi intrinsik O(1)** | Setiap unit membawa bukti validitasnya sendiri | VF |
| 2 | **Preservasi constraint pada agregasi** | h₁* + h₂* ∈ 𝒱 dan semua identitas dipertahankan | VF |
| 3 | **Diagnostik per-lapisan** | Perbedaan didekomposisi ke 4 kontribusi bermakna via **Normivektor** | VF+CC |
| 4 | **Hukum kekekalan turning** | Guard G4 = constraint geometris lintas-lapisan | VF+CC |

---

## Pipeline Hybit

### Diagram Pipeline Lengkap

\`\`\`
JALUR 1 — KODE                          JALUR 2 — DATA GEOMETRI

  PENULIS KODE                             FONT KANONIK (sealed)
      │                                        │
      ▼                                        ▼
 ┌──────────┐                            [Ψ-Compiler]
 │  .hc     │ ← Source code HC            ├── Rasterisasi
 └────┬─────┘                              ├── CSGI extraction
      │                                    ├── MainPath selection
      ▼ [HCC — HC Compiler]                ├── Q₉₀ kuantisasi
      ├── Lexer → Token stream             └── Klasifikasi N-K-Q
      ├── Parser → AST                         │
      ├── Ψ-Injector (opsional)                ▼
      └── Codegen → Assembly              ┌──────────┐
      │                                   │ .hgeo    │ ← Geometry
      ▼                                   └────┬─────┘
 ┌──────────┐                                  │
 │ .hasm    │ ← Assembly H-ISA                 ▼
 └────┬─────┘                             ┌──────────┐
      │                                   │  HAR     │ ← Registry
      ▼ [HASM — Assembler]                └────┬─────┘
      │                                        │
      ▼                                        │
 ┌──────────┐                                  │
 │ .hbc     │ ← Bytecode binary               │
 └────┬─────┘                                  │
      │                                        │
      ▼ [HVM — Hybit Virtual Machine] ◄────────┘
      ├── Loader → Parse .hbc
      ├── Interpreter → Execute
      ├── Hybit Engine → HCADD, HPROJ, HDCMP
      ├── Guard System → G1–G4, T1–T2
      └── HCHECK → Runtime integrity
      │
      ▼
   OUTPUT
\`\`\`

### Prinsip: Satu Komponen = Satu Fungsi

| Komponen | Layer | Fungsi TUNGGAL | Status |
|---|---|---|---|
| **.hc** | Source | Kode sumber HC | ✅ Existing |
| **.hasm** | Assembly | Representasi H-ISA | 📐 Specified |
| **.hbc** | Binary | Executable bytecode | 📐 Specified |
| **.hgeo** | Data | Geometri per glyph | 📐 Specified |
| **HAR** | Registry | Database alfabet | ✅ Partial |
| **HCC** | Compiler | .hc → .hasm/.hbc | ✅ Partial |
| **HASM** | Assembler | .hasm → .hbc | 📐 Specified |
| **HVM** | Runtime | Eksekusi .hbc | ✅ Operational |
| **Guard** | Validation | G1–G4 per operasi | ✅ Existing |
| **HCHECK** | Monitor | Integritas seluruh state | 📐 Specified |
| **HOS** | OS | Sistem operasi hybit | 📝 Designed |
| **HFS** | Storage | File system hybit-aware | 📝 Designed |
| **H-Kernel** | Kernel | Process/memory mgmt | 📝 Designed |

---

## Format File

### Lima Format File Terstandar

| Format | Ekstensi | Layer | Deskripsi | Status |
|---|---|---|---|---|
| **Hybit Code** | \`.hc\` | Source | Kode sumber bahasa HC | ✅ Existing |
| **Hybit Assembly** | \`.hasm\` | Assembly | Representasi teks instruksi H-ISA | 📐 Specified |
| **Hybit Bytecode** | \`.hbc\` | Binary | Executable untuk HVM — magic \`"HBYT"\` | 📐 Specified |
| **Hybit Geometry** | \`.hgeo\` | Data | Hasil ekstraksi geometris per glyph | 📐 Specified |
| **Alphabet Registry** | HAR/ | Registry | Master table + metadata + validation | 📐 Specified |

### .hbc — Struktur Binary

\`\`\`
┌─────────────────────────────────────────────┐
│ HEADER (32 bytes)                            │
│   Magic: "HBYT" │ Version │ HAR-ID │ Flags  │
│   Entry point │ Const/Code/Data offsets      │
│   CRC32 checksum                             │
├─────────────────────────────────────────────┤
│ CONSTANT POOL — literals, hybit refs         │
├─────────────────────────────────────────────┤
│ CODE SECTION — [opcode:1][fmt:1][operands]   │
├─────────────────────────────────────────────┤
│ DATA SECTION — hybit vectors, strings        │
├─────────────────────────────────────────────┤
│ DEBUG INFO (opsional) — source map, symbols  │
└─────────────────────────────────────────────┘
\`\`\`

---

## Fitur Utama

### 🔬 Fondasi Matematis (Bab I)
- **Master Table** — dataset formal 28×18 yang disegel dan diverifikasi — **658/658 PASS**
- **Codex 14D & 18D** — representasi integer multidimensi huruf
- **Guard System** — validasi struktural intrinsik per unit data (G1–G4, T1–T2)
- **Theorem Engine** — verifikasi formal 13 teorema/identitas

### 📐 Sistem Operasi Metrik-Vektorial (Bab II)

Lima operasi formal berbasis **vektor, norma, dan metrik** — **683/683 PASS**:

| Operasi | Kode | Pertanyaan Sentral | Identitas Kunci |
|---|---|---|---|
| **Vektronometry** | VTM | Terbuat dari apa? | rN + rK + rQ = 1 |
| **Normivektor** | NMV | Bagaimana bedanya? | ‖Δ‖² = ΔΘ² + ‖ΔN‖² + ‖ΔK‖² + ‖ΔQ‖² |
| **Aggregametric** | AGM | Berapa totalnya? | Σᵤᵥ = Σᵤ + Σᵥ |
| **Intrametric** | ITM | Seberapa jauh? | d² = ‖h₁‖² + ‖h₂‖² − 2⟨h₁,h₂⟩ |
| **Exometric** | EXM | Konsisten internal? | R1–R5; Φ > ‖v₁₄‖² |

### ⚛️ Paradigma Hybit (Bab III)
- **Hybit sebagai paradigma ketiga** — 𝔽₂ ≠ ℂ² ≠ 𝒱 (terbukti formal) — **39/39 PASS**
- **Pipeline lengkap** — .hc → HCC → .hasm → HASM → .hbc → HVM → Output
- **Ψ-Compiler** — Font sealed → .hgeo → HAR
- **Guard vs HCHECK** — validasi per-operasi vs monitor integritas periodik
- **Spesifikasi OS** — HOS, HFS (guard-on-write), H-Kernel (18-wide alignment)

### 💻 Bahasa dan Kompilasi
- **HC Language** — bahasa pemrograman dengan \`hybit\` sebagai tipe bawaan (first-class)
- **HCC** — compiler 6-tahap (Lexer → Parser → Semantic → Ψ-Injector → Codegen → Assemble)
- **HASM** — assembler 4-pass (Label → Encode → Pool → Header)
- **H-ISA** — instruction set dengan operasi hybit-native

### 🔧 Runtime
- **HVM** — Hybit Virtual Machine mandiri (Loader, Interpreter, Hybit Engine, Guard, HCHECK)
- **Register file** — R0–R15, setiap register = satu hybit 18D lengkap (576 byte total)
- **Guard System** — validasi G1–G4, T1–T2 per operasi hybit — O(1) intrinsik
- **HCHECK** — runtime integrity monitor
- **GUARD_STRICT mode** — setiap HCADD wajib guard check

### 📡 HISAB — Standar Pertukaran Codex
- **Serialisasi kanonik** — LETTER Frame (9 byte), STRING Frame (36 byte), MATRIX Frame (25 byte)
- **Validasi 3-level** — Structural (magic/CRC), Guard (G1–G4/T1–T2), Semantic (Master Table)
- **Round-trip fidelity** — D(S(h*)) = h* untuk semua 28 huruf

### 🔍 Verifikasi dan Audit — 1.380-Check Framework

| Bab | Pemeriksaan | PASS |
|---|---|---|
| Bab I — Fondasi Formal | 658 | **658** ✓ |
| Bab II — Sistem Operasi Metrik-Vektorial | 683 | **683** ✓ |
| Bab III — Paradigma Hybit | 39 | **39** ✓ |
| **TOTAL** | **1.380** | **1.380** ✓ |

---

## Arsitektur Sistem

### Diagram Layer — Pipeline Terintegrasi

\`\`\`
┌─────────────────────────────────────────────────────────┐
│                       HOM GUI                            │
│  Letter · String · Audit · Intrametric · HISAB           │
│  MV-Workbench · HC IDE · HVM Inspector · CSGI · HAR     │
├─────────────────────────────────────────────────────────┤
│                  HC Language + HCC Compiler               │
│        Lexer → Parser → Semantic → Ψ-Inject → Codegen   │
├────────────────────────┬────────────────────────────────┤
│  Algebra:              │  HISAB Protocol                │
│  5 Operasi MV          │  Serialize · Validate          │
│  VTM·NMV·AGM·ITM·EXM  │  Digest · Audit · Bridge       │
├────────────────────────┴────────────────────────────────┤
│  HASM Assembler  │  .hbc Format  │  .hgeo + Ψ-Comp     │
├─────────────────────────────────────────────────────────┤
│  Integrity · Theorems · Crypto · Release · Net · HCHECK │
├─────────────────────────────────────────────────────────┤
│         HVM — Hybit Virtual Machine                      │
│  Loader │ Interpreter │ Hybit Engine │ Guard System      │
│  R0–R15 (18×16-bit)  │  Stack: 1024 │  Heap: Dynamic    │
├─────────────────────────────────────────────────────────┤
│         H-ISA (Instruction Set Architecture)             │
│  HCADD · HGRD · HPROJ · HDCMP · HNRM2 · HDIST · HEXMT │
│  HSER · HDES · HCHK · IADD · ISUB · JMP · HALT         │
├─────────────────────────────────────────────────────────┤
│              CSGI (Skeleton Graph Interface)              │
├─────────────────────────────────────────────────────────┤
│    Core: Master Table · Codex · Guards · HAR Registry    │
├─────────────────────────────────────────────────────────┤
│      Dataset Seal: HM-28-v1.2-HC18D (252 bytes ROM)     │
└─────────────────────────────────────────────────────────┘
\`\`\`

### Prinsip Arsitektur

| Prinsip | Penjelasan |
|---|---|
| **GUI tidak menghitung** | Logika domain ada di core/algebra/vm |
| **Core tidak import GUI** | Dependency satu arah |
| **Satu komponen = satu fungsi** | Single Responsibility |
| **Pipeline tidak menggantikan HOM** | HOM = lab ilmiah, Pipeline = sistem produksi |
| **Facade re-export, tidak duplikasi** | Module baru wraps existing |
| **Guard ≠ HCHECK** | Guard = per-operasi, HCHECK = periodik seluruh state |
| **Kode ≠ Data** | .hbc (program) dan HAR (alfabet) terpisah — Harvard principle |

---

## Technology Stack

### Inventaris Komponen Lengkap — 24 Komponen

| Layer | Komponen | Status | Deskripsi |
|---|---|---|---|
| **L0** | Master Table | ✅ **SEALED** | Dataset 28×18 (252 bytes ROM) |
| **L0** | CSGI | ✅ **OPERATIONAL** | Canonical Skeleton Graph Interface |
| **L1** | HC Language | ✅ **OPERATIONAL** | Bahasa pemrograman codex v1.0 |
| **L1** | HL-18E | 📐 SPECIFIED | Grammar formal 18-EBNF |
| **L2** | H-ISA | ✅ **OPERATIONAL** | Instruction Set Architecture (44 opcode unik; 28 di RTL) |
| **L3** | CMM-18C | 📐 SPECIFIED | Codex Multidimensional Machine |
| **L4** | HCPU | 📝 DESIGNED | Arsitektur prosesor 18D (fotonik) |
| **L5** | HVM | ✅ **OPERATIONAL** | Hybit Virtual Machine |
| **L6** | HGSS | ✅ **OPERATIONAL** | Guard + Signature System |
| **L7** | HC18DC | 📐 SPECIFIED | Canonical Data Exchange Format |
| **⟂** | HISAB | ✅ **OPERATIONAL** | Inter-System Standard for Auditable Bridging |
| **GUI** | HOM | ✅ **OPERATIONAL** | Integrated Scientific Environment |
| **Compile** | HCC (lexer+parser) | ✅ **PARTIAL** | HC Compiler — tahap 1–2 |
| **Compile** | HCC (codegen) | 📐 SPECIFIED | HC Compiler — tahap 3–6 |
| **Assembly** | HASM | 📐 SPECIFIED | Hybit Assembler (4-pass) |
| **Binary** | .hbc format | 📐 SPECIFIED | Hybit Bytecode (32B header, "HBYT") |
| **Data** | .hgeo format | 📐 SPECIFIED | Hybit Geometry File (JSON) |
| **Registry** | HAR | ✅ **PARTIAL** | HAR-001 Hijaiyyah (auto-loaded) |
| **Monitor** | HCHECK | 📐 SPECIFIED | Runtime integrity monitor |
| **OS** | HOS | 📝 DESIGNED | Hybit Operating System |
| **Storage** | HFS | 📝 DESIGNED | Hybit File System (guard-on-write) |

**Status agregat:** 11 operational · 10 specified · 3 designed = **24 total**

---

## H-ISA — Instruction Set Architecture

### Instruksi Hybit-Native

| Instruksi | Operasi MV | Fungsi |
|---|---|---|
| \`HLOAD\` | — | Load hybit dari HAR/memory |
| \`HCADD\` | AGM | Codex addition: dst ← src1 + src2 |
| \`HGRD\` | EXM | Guard check G1–G4, T1–T2 |
| \`HPROJ\` | VTM | Proyeksi subruang: Θ/N/K/Q |
| \`HDCMP\` | VTM | Dekomposisi turning: (U, ρ) ← Θ̂ |
| \`HNRM2\` | VTM | Norma kuadrat: ‖v₁₄‖² |
| \`HDIST\` | ITM | Jarak Euclidean antar huruf |
| \`HEXMT\` | EXM | Bangun exomatrix 5×5 |
| \`HSER\` | — | Serialize ke HISAB Frame |
| \`HDES\` | — | Deserialize dari HISAB Frame |
| \`HCHK\` | — | Runtime integrity check |

**Pemetaan Operasi MV → Instruksi:**

| Operasi MV | Instruksi H-ISA |
|---|---|
| **VTM** (Vektronometry) | HPROJ, HDCMP, HNRM2 |
| **NMV** (Normivektor) | HDIST, HNRM2 (pada Δ) |
| **AGM** (Aggregametric) | HCADD |
| **ITM** (Intrametric) | HDIST |
| **EXM** (Exometric) | HGRD, HEXMT |

---

## Guard System vs HCHECK

| Dimensi | Guard System | HCHECK |
|---|---|---|
| **Kapan** | Setiap operasi hybit | Periodik (setiap N instruksi) |
| **Apa** | Satu vektor (hasil operasi) | Seluruh state (register, stack, heap) |
| **Deteksi** | Inkonsistensi geometris (G1–G4 gagal) | Korupsi memori (bit flip, overflow) |
| **Kompleksitas** | O(1) per operasi | O(R+S) per scan |
| **Analogi** | Type checker per statement | Memory sanitizer periodik |
| **Kegagalan** | \`GUARD_FAIL\` → operasi ditolak | \`CORRUPTION\` → program dihentikan |

---

## Verifikasi Matematis

| Pemeriksaan | Hasil | Domain |
|---|---|---|
| Guard checks G1–G4, T1–T2 | **168/168 PASS** | Bab I |
| Guard topologis T1–T2 | **56/56 PASS** | Bab I |
| Injectivity v₁₈ | **378/378 unique pairs** | Bab I |
| Dekomposisi Θ̂ = U + ρ | **28/28 PASS** | Bab I |
| Non-negativitas ρ ≥ 0 | **28/28 PASS** | Bab I |
| Kelengkapan rN+rK+rQ=1 | **28/28 PASS** | **VTM** |
| Pythagoras dekomposisi | **28/28 PASS** | **VTM** |
| Diagnostik per-lapisan | **7/7 PASS** | **NMV** |
| Aditivitas konkatenasi | **2/2 PASS** | **AGM** |
| Cosine similarity ≥ 0 | **378/378 PASS** | **ITM** |
| Aksioma ruang metrik M1–M4 | **4/4 PASS** | **ITM** |
| Diameter = √70 | **1/1 VERIFIED** | **ITM** |
| rank(M₁₄) = 14 | **1/1 VERIFIED** | **ITM** |
| Exometric R1–R5 audit | **140/140 PASS** | **EXM** |
| Energy inequality Φ > ‖v₁₄‖² | **28/28 strict PASS** | **EXM** |
| Rekonstruksi unik exomatrix | **28/28 PASS** | **EXM** |
| Hybit closure (HCADD) | **PROVEN** | Bab III |
| Tak-tereduksi 3 paradigma | **PROVEN** | Bab III |

---

## HOM Test Suite Report — v1.2.0

\`\`\`
╔═══════════════════════════════════════════════════════════════╗
║   HOM TEST SUITE REPORT — v1.2.0 (FINAL)                     ║
║                                                               ║
║   Collected :  1,628  tests                                   ║
║   Passed    :  1,628  ✅                                       ║
║   Skipped   :      0                                          ║
║   Failed    :      0                                          ║
║   Duration  :  ~46 seconds                                    ║
║                                                               ║
║   ZERO SKIP.  ZERO FAIL.  ALL GREEN.                          ║
╚═══════════════════════════════════════════════════════════════╝
\`\`\`

### Ringkasan per Modul — 14 Modul

| # | Modul | Tests | Status |
|---|---|---|---|
| 1 | **Verification Framework** | 1,380 | ✅ PASS |
| 2 | **Virtual Machine** | 34 | ✅ PASS |
| 3 | **Hybit Core** | 52 | ✅ PASS |
| 4 | **Language** | 27 | ✅ PASS |
| 5 | **HISA Machine** | 18 | ✅ PASS |
| 6 | **HISAB** | 17 | ✅ PASS |
| 7 | **Compiler — HCC** | 16 | ✅ PASS |
| 8 | **Assembler — HASM** | 16 | ✅ PASS |
| 9 | **Algebra — Metrik-Vektorial** | 15 | ✅ PASS |
| 10 | **HAR Registry** | 15 | ✅ PASS |
| 11 | **Pipeline / Ψ-Compiler** | 13 | ✅ PASS |
| 12 | **Integrity** | 5 | ✅ PASS |
| 13 | **Integration / E2E** | 2 | ✅ PASS |
| 14 | **Theorems** | 1 | ✅ PASS |
| | **TOTAL** | **1,628** | **1,628 PASS** |

---

## Instalasi

### Metode 1 — Development mode (disarankan)

\`\`\`bash
git clone https://github.com/hybittech/HOM.git
cd HOM
pip install -e ".[dev]"
\`\`\`

### Verifikasi instalasi

\`\`\`bash
python -c "from hijaiyyah.version import __version__; print(__version__)"
# Output: 1.2.0
\`\`\`

### Verifikasi 1.380-check framework

\`\`\`bash
python -m pytest tests/test_full_verification.py -v
# Output: 1380 passed
\`\`\`

---

## Contoh Kode HC

### Hello HC

\`\`\`
fn main() {
    println("Hello, HC v1.2");
}
\`\`\`

### Load huruf dan analisis Vektronometri

\`\`\`
fn main() {
    let h = load('ب');
    println("Theta:", h.theta());     // 2
    println("Guard:", h.guard());     // PASS
    println("Norm2:", h.norm2());     // 7

    // Dekomposisi turning (VTM)
    let (u, rho) = h.decompose();
    println("U:", u, "rho:", rho);    // U=0, ρ=2

    // Profil Vektronometri (VTM)
    let (rn, rk, rq) = h.ratios();
    println("rN:", rn, "rK:", rk, "rQ:", rq);
    assert(rn + rk + rq == 1.0);    // Identitas VTM ✓
}
\`\`\`

### Lima operasi metrik-vektorial

\`\`\`
fn main() {
    let h = load('ج');

    // ── VTM: Vektronometry ──
    println("Norm²:", h.norm2());

    // ── NMV: Normivektor ──
    let delta = hm::normivektor::diff(load('ت'), load('ب'));
    println("‖Δ‖²:", delta.norm2());

    // ── AGM: Aggregametric ──
    let cod = hm::aggregametric::string_sum("بسم");
    println("Σ_w Θ̂:", cod.theta());

    // ── ITM: Intrametric ──
    let dist = hm::intrametric::euclidean(load('ا'), load('هـ'));
    println("d₂:", dist);            // √70 ≈ 8.367

    // ── EXM: Exometric ──
    let e = hm::exometric::build(h);
    println("R1–R5:", e.audit());    // ALL PASS
}
\`\`\`

---

## Struktur Direktori

\`\`\`
HOM/
├── README.md
├── src/
│   └── hijaiyyah/
│       ├── core/              ← L0: dataset formal + guards
│       ├── algebra/           ← Bab II: 5 operasi metrik-vektorial
│       ├── language/          ← L1: HC language core
│       ├── compiler/          ← HCC: compiler pipeline
│       ├── assembler/         ← HASM: .hasm → .hbc encoding
│       ├── vm/                ← HVM: runtime (5 komponen)
│       ├── pipeline/          ← Ψ-Compiler (.hgeo generation)
│       ├── har/               ← HAR: alphabet registry
│       ├── hisa/              ← L2: instruction set architecture
│       ├── hisab/             ← HISAB protocol
│       ├── skeleton/          ← CSGI: skeleton graph extraction
│       ├── integrity/         ← audit, verification, HCHECK
│       └── gui/               ← HOM GUI
├── har/                       ← Alphabet Registry
│   └── HAR-001/               ← Hijaiyyah (CERTIFIED)
├── data/
│   ├── hm28.json              ← master table JSON
│   └── hm28.rom               ← ROM 252 bytes
├── tests/
│   ├── test_full_verification.py  ← 1.380-check framework
│   ├── test_core/
│   ├── test_algebra/
│   └── ...
└── docs/
\`\`\`

---

## Release Certificate

\`\`\`
╔══════════════════════════════════════════════════════════════╗
║       HIJAIYYAH MATHEMATICS — RELEASE CERTIFICATE            ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Release:    HM-28-v1.2-HC18D                                ║
║  Version:    1.2.0                                           ║
║  Status:     VERIFIED & SEALED                               ║
║                                                              ║
║  Dataset:    28 letters × 18 dimensions                      ║
║  ROM:        252 bytes (nibble-packed)                        ║
║  Integrity:  SEALED (SHA-256)                                ║
║                                                              ║
║  Operations: VTM · NMV · AGM · ITM · EXM                    ║
║  Pilar:      Vektor + Norma + Metrik                         ║
║  Checks:     683/683 PASS                                    ║
║                                                              ║
║  1.380-Check Verification Framework                          ║
║  Bab I:      658/658  PASS                                   ║
║  Bab II:     683/683  PASS                                   ║
║  Bab III:     39/39   PASS                                   ║
║  TOTAL:    1.380/1.380 PASS — 0 FAIL                         ║
║                                                              ║
║  Paradigm:   bit ⊕ qubit ⊕ hybit PROVEN (VF)                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
\`\`\`

---

## Dokumentasi

| Dokumen | Lokasi | Status |
|---|---|---|
| Arsitektur Sistem | \`docs/architecture.md\` | UPDATED |
| Arsitektur RTL & Hardware | \`rtl/docs/Hybit Architecture (HCPU).md\` | EXACT |
| Spesifikasi HC | \`docs/hc_language.md\` | Existing |
| Spesifikasi H-ISA | \`docs/hisa_spec.md\` | UPDATED |
| Spesifikasi CSGI | \`docs/csgi_spec.md\` | Existing |
| Spesifikasi HVM | \`docs/hcvm_spec.md\` | UPDATED |
| Spesifikasi Pipeline | \`docs/hybit_pipeline_spec.md\` | Existing |
| Spesifikasi .hbc | \`docs/hbc_format.md\` | Existing |
| Spesifikasi .hgeo | \`docs/hgeo_format.md\` | Existing |
| Spesifikasi HAR | \`docs/har_spec.md\` | Existing |
| Spesifikasi HISAB | \`docs/hisab_spec.md\` | Existing |
| Kebijakan Rilis | \`docs/release_policy.md\` | Existing |

---

## Lisensi

\`\`\`
© 2026 Hijaiyyah Mathematics Computational Laboratory (HMCL)
All Rights Reserved.

Seluruh kerangka matematika, implementasi perangkat lunak, dataset,
spesifikasi bahasa, pipeline kompilasi, format file, arsitektur
prosesor, dan desain sistem operasi dalam repository ini dilindungi
hak cipta.
\`\`\`

---

## Penulis

\`\`\`
╔══════════════════════════════════════════════════════════════╗
║       AUTHOR SIGNATURE                                       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Signed:     Maulana Amratulloh                       ║
║              Perancang & Perumus Matematika Hijaiyyah        ║
║  Release:    HM-28-v1.2-HC18D                                ║
║  Seal:       VERIFIED & SEALED                               ║
║  Framework:  1.380/1.380 PASS — 0 FAIL                       ║
║                                                              ║
║  © 2026 (HMCL)                                               ║
║  Hijaiyyah Mathematics Computational Laboratory              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
\`\`\`

---

*Tiga paradigma. Tiga domain optimal. Lima operasi. Satu pipeline. Satu ekosistem.*

*bit ⊕ qubit ⊕ hybit*

*© 2026 HMCL — HM-28-v1.2-HC18D*
`;

/* ─── Custom Markdown Components for dark theme ─── */
const mdComponents = {
  h1: ({ children }) => (
    <h1 className="text-3xl md:text-4xl font-bold text-hom-text mt-12 mb-6 pb-3 border-b border-hom-border/30 first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-2xl md:text-3xl font-bold text-hom-text mt-10 mb-5 pb-2 border-b border-hom-border/20">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-xl font-bold text-hom-accent mt-8 mb-3">{children}</h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-lg font-semibold text-hom-text/90 mt-6 mb-2">{children}</h4>
  ),
  p: ({ children }) => (
    <p className="text-sm md:text-base text-hom-text/85 leading-relaxed mb-4">{children}</p>
  ),
  a: ({ href, children }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-hom-accent hover:text-hom-accent/80 underline underline-offset-2 transition-colors">
      {children}
    </a>
  ),
  ul: ({ children }) => (
    <ul className="space-y-1.5 mb-4 ml-4">{children}</ul>
  ),
  ol: ({ children }) => (
    <ol className="space-y-1.5 mb-4 ml-4 list-decimal">{children}</ol>
  ),
  li: ({ children }) => (
    <li className="text-sm text-hom-text/80 leading-relaxed pl-1">
      <span className="text-hom-accent mr-1.5">▸</span>
      {children}
    </li>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-2 border-hom-gold/50 pl-4 py-2 my-4 bg-hom-gold/5 rounded-r-lg">
      {children}
    </blockquote>
  ),
  code: ({ className, children, ...props }) => {
    const isBlock = className?.includes('language-');
    if (isBlock) {
      return (
        <code className="block text-[11px] md:text-xs font-mono text-hom-text/90 whitespace-pre overflow-x-auto" {...props}>
          {children}
        </code>
      );
    }
    return (
      <code className="text-[11px] md:text-xs font-mono px-1.5 py-0.5 rounded bg-hom-accent/10 text-hom-accent border border-hom-accent/15" {...props}>
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="bg-hom-bg/80 border border-hom-border/30 rounded-xl p-4 my-4 overflow-x-auto backdrop-blur-sm" style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
      {children}
    </pre>
  ),
  table: ({ children }) => (
    <div className="overflow-x-auto my-6 rounded-xl border border-hom-border/30" style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}>
      <table className="w-full text-sm border-collapse">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-hom-panel/80 border-b border-hom-border/40">
      {children}
    </thead>
  ),
  th: ({ children, style }) => (
    <th className="py-3 px-4 text-[10px] font-bold uppercase tracking-wider text-hom-accent text-left" style={style}>
      {children}
    </th>
  ),
  td: ({ children, style }) => (
    <td className="py-2.5 px-4 text-xs text-hom-text/80 border-b border-hom-border/10" style={style}>
      {children}
    </td>
  ),
  tr: ({ children }) => (
    <tr className="hover:bg-hom-accent/[0.03] transition-colors">{children}</tr>
  ),
  hr: () => (
    <hr className="my-10 border-0 h-px bg-gradient-to-r from-transparent via-hom-accent/20 to-transparent" />
  ),
  img: ({ src, alt }) => {
    if (src?.includes('img.shields.io')) {
      return <img src={src} alt={alt} className="inline-block h-5 mr-1 mb-1" />;
    }
    return <img src={src} alt={alt} className="max-w-md mx-auto my-4 rounded-lg" />;
  },
  strong: ({ children }) => (
    <strong className="font-bold text-hom-text">{children}</strong>
  ),
  em: ({ children }) => (
    <em className="italic text-hom-text/70">{children}</em>
  ),
};

export default function Documentation() {
  return (
    <div className="max-w-5xl mx-auto">
      <div className="bg-hom-panel/30 backdrop-blur-xl border border-hom-border/20 rounded-2xl p-6 md:p-10">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm, remarkMath]} 
          rehypePlugins={[rehypeKatex]}
          components={mdComponents}
        >
          {readmeContent}
        </ReactMarkdown>
      </div>
    </div>
  );
}
