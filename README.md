<div align="center">

<img src="data/logo/matematika-hijaiyyah-logo.png" alt="Matematika Hijaiyyah" width="360">

# Matematika Hijaiyyah

**Formalisasi geometri diskret 28 huruf Hijaiyyah kanonik menjadi codex integer,
beserta aljabar, validasi intrinsik, dan arsitektur komputasinya.**

[![Rilis dataset](https://img.shields.io/badge/dataset-HM--28--v.1.0--HC18D-1B4F8F)](data/hm28.csv)
[![Segel](https://img.shields.io/badge/SHA--256-f82d3859…-8A6714)](#reproduksibilitas)
[![Test](https://img.shields.io/badge/test-1649%20passed-116B50)](docs/TEST_REPORT.md)
[![Kerangka verifikasi](https://img.shields.io/badge/verifikasi-1380%20checks-116B50)](#verifikasi)
[![RTL](https://img.shields.io/badge/RTL-204%20assertions-116B50)](rtl/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](pyproject.toml)
[![Lisensi](https://img.shields.io/badge/lisensi-proprietary-A0292A)](LICENSE)

[**Aplikasi Web**](https://hybit.tech) ·
[Instalasi](#instalasi) · [Verifikasi](#verifikasi) · [Arsitektur](#arsitektur) ·
[Status](#status-pengembangan) · [Sitasi](#sitasi)

</div>

---

## Ringkasan

Setiap sistem matematika formal beroperasi pada suatu domain. Geometri Euklides
beroperasi pada titik, garis, dan bidang; teori bilangan pada ℤ. Repositori ini
menetapkan **28 huruf Hijaiyyah bentuk isolated** sebagai domain semacam itu —
bukan sebagai simbol fonetik, melainkan sebagai objek geometri diskret yang dapat
diukur, dioperasikan, dan divalidasi.

Setiap huruf dipetakan secara deterministik ke **vektor integer 18 dimensi**
melalui empat invarian: total belokan MainPath (Inḥinā'), distribusi titik
(Nuqṭah), komponen garis (Khaṭṭ), dan komponen lengkung (Qaws). Pemetaan ini
injektif, terkendala oleh enam guard yang dapat diperiksa dalam O(1), dan
tertutup terhadap penjumlahan.

```
Font KFGQPC (tersegel)
  └─ CSGI ─────────► skeleton graph        8-neighborhood, nuqṭah dikecualikan
      └─ MainPath ─► lintasan dominan      skor leksikografis, tunggal
          └─ Q₉₀ ──► Inḥinā' Θ̂             kuantisasi kuadran 90°
              └─ N-K-Q klasifikasi
                  └─ codex v₁₈ ──► guard G1–G4, T1–T2 ──► hybit
```

Setiap angka dalam codex dapat ditelusuri mundur hingga koordinat Bézier pada
berkas font.

---

## Label epistemik

Setiap klaim dalam sistem ini membawa label yang menyatakan **status
pembuktiannya**, bukan tingkat keyakinan penulis. Label melekat pada klaim, di
dokumentasi maupun di kode.

| Label | Arti | Cara memverifikasi |
|:---|:---|:---|
| `VF` | Verified Formally — dibuktikan secara matematis | Baca buktinya |
| `CC` | Computationally Confirmed — diverifikasi menyeluruh atas domain hingga | Jalankan test-nya |
| `DP` | Design Property — konsekuensi definisi | Baca definisinya |
| `EH` | Engineering Hypothesis — kelayakan dengan bukti individual | Belum tuntas |
| `AT` | Aspirational Target — rancangan, belum diimplementasikan | Belum ada |

Pemisahan ini mengikat. Klaim berlabel `EH` tidak boleh dibaca sebagai `CC`,
dan tidak ada klaim yang naik label tanpa bukti baru.

---

## Hasil inti

Seluruh nilai di bawah dihitung ulang dari dataset, bukan disalin dari
dokumentasi. Kolom terakhir menunjukkan cara memeriksanya sendiri.

| Hasil | Nilai | Label | Verifikasi |
|:---|:---|:---:|:---|
| Injektivitas v₁₈ | 0 tabrakan dari 378 pasangan | `CC` | `pytest tests/test_integrity/` |
| Rank M₁₄ | 14 (rank penuh) | `CC` | eliminasi Gauss eksak atas ℚ |
| Diameter alfabet | √70 ≈ 8,3666 pada (ا, هـ) — tunggal | `CC` | 378 pasangan menyeluruh |
| Aksioma ruang metrik | M1–M4, 0 pelanggaran dari 19.656 triple | `VF+CC` | `tests/test_algebra/` |
| Identitas polarisasi | 378/378 | `VF` | `tests/test_algebra/` |
| Pythagoras VTM | 28/28 | `VF` | `tests/test_algebra/` |
| Guard G1–G4, T1–T2 | 168/168 (28 huruf × 6) | `CC` | `tests/test_core/test_guards.py` |
| Audit exomatrix R1–R5 | 140/140 | `CC` | `tests/test_algebra/test_exometric.py` |
| Ketaksamaan energi Φ > ‖v₁₄‖² | strict pada 28/28 | `VF+CC` | `tests/test_algebra/` |
| Closure monoid (𝒱, +) | tertutup | `VF` | bukti aljabar, linearitas U |
| Rekonstruksi exomatrix | bijektif, 28/28 | `VF` | roundtrip |

**Batas yang diketahui.** Cod₁₈ adalah fungsi multiset dan **tidak injektif pada
string**: ker Cod₁₈ berdimensi 14, dengan 32 kelas collision minimal dua-huruf
(mis. `ت+خ` ≡ `ث+ح`). Guard memvalidasi keterbentukan, bukan identitas isi;
substitusi di dalam kernel tidak terdeteksi. Untuk pembedaan string, gunakan
lintasan kumulatif Λ, yang injektif.

---

## Instalasi

**Prasyarat.** Python 3.11+ · Node 22+ (opsional, untuk GUI web) ·
Icarus Verilog (opsional, untuk RTL)

```bash
git clone https://github.com/hybittech/matematikahijaiyyah.github.io.git
cd matematikahijaiyyah.github.io

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Verifikasi instalasi:

```bash
python -c "import hijaiyyah; print(hijaiyyah.__version__, hijaiyyah.__dataset_release__)"
# 1.2.0 HM-28-v.1.0-HC18D
```

---

## Verifikasi

Sistem ini dirancang agar klaimnya dapat difalsifikasi. Berikut cara mengujinya.

```bash
# Seluruh suite
pytest -q
# 1649 passed

# Kerangka verifikasi formal — Bab I (658) + Bab II (683) + Bab III (39)
pytest tests/test_full_verification.py -q
# 1380 passed

# Konsistensi antar salinan dataset dan atribusi
pytest tests/test_integrity/ -q

# Lint
ruff check src/
```

**Perangkat keras** (perlu Icarus Verilog):

```bash
for tb in tb_guard tb_rom tb_codex_alu tb_hisab tb_hcpu_top; do
  iverilog -g2012 -I rtl -o /tmp/$tb.vvp rtl/tb/$tb.v rtl/*.v && vvp /tmp/$tb.vvp
done
# 204 assertions, 0 gagal
```

**Sintesis** (perlu Yosys):

```bash
cd rtl/mpw && yosys -s synth_hcpu.ys
# laporan: rtl/mpw/hcpu_synth_report.txt
```

### Reproduksibilitas

Master Table dikunci oleh segel SHA-256:

```
f82d385917ffe32ae2b5711409b1341e90934c52172ae9d0fa68888e3b9c51c8
```

Salinan yang segelnya berbeda bukan dataset kanonik. Konsistensi antara
`data/hm28.csv`, `data/hm28.json`, `core/master_table.py`, `rtl/hcpu_rom.v`,
`hm28.rom`, dan tabel GUI ditegakkan oleh
[`tests/test_integrity/test_dataset_consistency.py`](tests/test_integrity/test_dataset_consistency.py) —
build gagal bila salah satu menyimpang.

---

## Arsitektur

```
L0  CSGI            citra glyph → skeleton graph
L1  Codex           v₁₄ / v₁₈, guard G1–G4 + T1–T2
L2  Metrik-Vektorial VTM · NMV · AGM · ITM · EXM
L3  H-ISA           44 opcode unik (28 diimplementasikan di RTL)
L4  Toolchain       .hc → HCC → .hasm → HASM → .hbc
L5  Runtime         HVM (perangkat lunak) · HCPU (perangkat keras)
```

### Lima operasi metrik-vektorial

| Operasi | Pertanyaan | Identitas kunci |
|:---|:---|:---|
| **VTM** Vektronometry | Terbuat dari apa sebuah huruf? | rN + rK + rQ = 1 |
| **NMV** Normivektor | Apa yang membedakan dua huruf, di lapisan mana? | ‖Δ‖² = ΔΘ² + ‖ΔN‖² + ‖ΔK‖² + ‖ΔQ‖² |
| **AGM** Aggregametric | Berapa total codex sebuah string? | Σ_uv = Σ_u + Σ_v |
| **ITM** Intrametric | Seberapa jauh dua huruf? | d² = ‖h₁‖² + ‖h₂‖² − 2⟨h₁,h₂⟩ |
| **EXM** Exometric | Apakah konsisten secara internal? | R1–R5, Φ > ‖v₁₄‖² |

### Guard system

Enam kendala, diperiksa dalam 25 operasi integer — tanpa tabel, tanpa memori
tambahan, tanpa rujukan tersimpan.

```
G1  A_N = Na + Nb + Nd                    sum-check nuqṭah
G2  A_K = Kp + Kx + Ks + Ka + Kc          sum-check khaṭṭ
G3  A_Q = Qp + Qx + Qs + Qa + Qc          sum-check qaws
G4  ρ = Θ̂ − U ≥ 0,  U = Qx+Qs+Qa+4Qc      kekekalan turning
T1  Ks > 0 ⇒ Qc ≥ 1                       topologi loop-vertikal
T2  Kc > 0 ⇒ Qc ≥ 1                       topologi loop-pengiring
```

G4 menghubungkan dua pengukuran independen: Θ̂ dari kurvatur MainPath, U dari
klasifikasi Qaws. Konsistensinya bukan tautologi melainkan kendala geometris.

> **Guard bukan checksum, dan tidak menggantikannya.** Guard adalah predikat
> keabsahan bebas-rujukan; CRC adalah pendeteksi perubahan berbasis-rujukan.
> Keduanya menjawab pertanyaan berbeda dan saling melengkapi — lihat batas
> collision di [Hasil inti](#hasil-inti).

---

## Struktur repositori

```
data/            Master Table: hm28.csv, hm28.json, PDF kanonik, manifest
src/hijaiyyah/
  core/          codex, guard, exomatrix, master table, ROM
  algebra/       lima operasi metrik-vektorial
  language/      lexer, parser, evaluator HC
  hisa/          opcode, assembler, compiler, mesin H-ISA
  hisab/         protokol pertukaran codex (nibble-pack + CRC32)
  skeleton/      CSGI — ekstraksi skeleton
  gui/           aplikasi desktop HOM (Tkinter, 14 tab)
rtl/             HCPU — Verilog, testbench, target MPW/FPGA
hom-gui/         aplikasi web (React + Vite) → hybit.tech
tests/           1.649 test
docs/            spesifikasi format dan protokol
```

---

## Status pengembangan

Dinyatakan apa adanya, dengan label epistemik.

| Komponen | Status | Label |
|:---|:---|:---:|
| Fondasi formal (Bab I) | Terbukti dan terverifikasi menyeluruh | `VF+CC` |
| Metrik-vektorial (Bab II) | 683 pemeriksaan, 0 gagal | `VF+CC` |
| Struktur monoid terkendala | Closure dibuktikan secara aljabar | `VF` |
| HVM, HC, HCC, HASM | Operasional | `CC` |
| HCPU RTL | 204 assertion simulasi, 0 gagal | `CC` |
| HCPU sintesis | Berjalan; lihat catatan di bawah | `CC` |
| Target ASIC | Belum ada pemetaan sel standar | `EH` |
| Realisasi fotonik | DoF individual terdemonstrasi | `EH` |
| HOS, HFS, H-Kernel | Terancang | `AT` |

### Catatan sintesis

Sintesis generik terhadap gerbang menghasilkan **384.840 sel dan 143.112
flip-flop** — jauh di atas estimasi tangan terdahulu (~28.200 gerbang).
Penyebab dominan: `hcpu_dataram` menyumbang 270.568 sel karena 4096×32 bit
tersintesis sebagai flip-flop; alur gerbang generik tidak punya primitif
memori untuk memetakannya.

Angka itu turun dari 480.795 sel setelah `hcpu_dataram` dan stack `hcpu_memory`
diubah ke baca teregistrasi. Yang perlu dibaca adalah selisihnya: sel turun 20%
sementara flip-flop nyaris tak bergerak — pohon multiplexer baca yang hilang,
bukan penyimpanannya. Terhadap pustaka memori sungguhan efeknya terlihat penuh:
disintesis untuk Tang Nano 9K, desainnya memakai **3.053 LUT dari 8.640** dan
**1.646 flip-flop dari 6.480**, dengan array-nya di block RAM.

Karena itu klaim luas die dan kesiapan MPW **ditahan** sampai data RAM dipetakan
ke makro SRAM dan sintesis dijalankan ulang terhadap PDK sungguhan. Angka
lengkapnya di [`rtl/mpw/hcpu_synth_report.txt`](rtl/mpw/hcpu_synth_report.txt).

---

## Dokumentasi

| Berkas | Isi |
|:---|:---|
| [`docs/CSGI_SPEC.md`](docs/CSGI_SPEC.md) | Ekstraksi skeleton kanonik |
| [`docs/HC_LANGUAGE_SPEC.md`](docs/HC_LANGUAGE_SPEC.md) | Bahasa HC |
| [`docs/HISA_SPEC.md`](docs/HISA_SPEC.md) | Instruction set architecture |
| [`docs/hisab_spec.md`](docs/hisab_spec.md) | Protokol pertukaran codex |
| [`docs/HC18DC_FORMAT.md`](docs/HC18DC_FORMAT.md) | Format codex 18D |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Arsitektur sistem |
| [`docs/ORIGIN_PROTOCOL.md`](docs/ORIGIN_PROTOCOL.md) | Provenans domain |
| [`docs/TEST_REPORT.md`](docs/TEST_REPORT.md) | Laporan test lengkap per modul |
| [`rtl/docs/`](rtl/docs/) | Arsitektur HCPU |

---

## Sitasi

```bibtex
@book{amratulloh2026hijaiyyah,
  author    = {Maulana Amratulloh},
  title     = {Matematika Hijaiyyah: Fondasi Formal, Codex Teknologi,
               dan Arsitektur Hybit},
  publisher = {Hijaiyyah Mathematics Computational Laboratory},
  year      = {2026},
  note      = {Master Table HM-28-v.1.0-HC18D,
               SHA-256 f82d385917ffe32ae2b5711409b1341e90934c52172ae9d0fa68888e3b9c51c8}
}
```

---

## Lisensi dan atribusi

Perangkat lunak proprietary. Hak cipta © 2026 Hijaiyyah Mathematics
Computational Laboratory (HMCL). Seluruh hak dilindungi — lihat
[`LICENSE`](LICENSE) dan [`NOTICE`](NOTICE).

**Inventor & Chief Architect:** Maulana Amratulloh — lihat [`AUTHORS`](AUTHORS).

Sitasi kerangka matematis dalam publikasi akademik diizinkan dan dianjurkan,
dengan atribusi sebagaimana tercantum di atas.

<div align="center">

---

**Hijaiyyah Mathematics Computational Laboratory**
Fondasi Formal · Codex Teknologi · Arsitektur Hybit

</div>
