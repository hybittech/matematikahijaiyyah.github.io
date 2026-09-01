<div align="center">

# **HC Language Specification**
## Hijaiyyah Codex Programming Language — Version 1.0

### Formal Language Specification for Hijaiyyah Mathematics

**HM-28-v1.0-HC18D · 2026**

</div>

---

## Daftar Isi

- [1. Pendahuluan](#1-pendahuluan)
- [2. Desain dan Filosofi Bahasa](#2-desain-dan-filosofi-bahasa)
- [3. Leksikal](#3-leksikal)
- [4. Tipe Data](#4-tipe-data)
- [5. Variabel dan Konstanta](#5-variabel-dan-konstanta)
- [6. Operator](#6-operator)
- [7. Ekspresi](#7-ekspresi)
- [8. Struktur Kontrol](#8-struktur-kontrol)
- [9. Fungsi](#9-fungsi)
- [10. Modul dan Import](#10-modul-dan-import)
- [11. Metode Hybit](#11-metode-hybit)
- [12. Standard Library](#12-standard-library)
- [13. Built-in Functions](#13-built-in-functions)
- [14. Error Handling](#14-error-handling)
- [15. Grammar Formal (EBNF)](#15-grammar-formal-ebnf)
- [16. Contoh Program](#16-contoh-program)
- [17. Konvensi dan Gaya](#17-konvensi-dan-gaya)
- [18. Eksekusi dan Tooling](#18-eksekusi-dan-tooling)
- [19. Batasan dan Rencana Pengembangan](#19-batasan-dan-rencana-pengembangan)
- [20. Referensi](#20-referensi)

---

## 1. Pendahuluan

### 1.1 Apa itu HC?

**HC (Hijaiyyah Codex)** adalah bahasa pemrograman formal yang dirancang
khusus untuk **Matematika Hijaiyyah**. HC menjadikan **hybit** — vektor
integer 18-dimensi yang merepresentasikan struktur bentuk huruf
Hijaiyyah — sebagai **tipe data bawaan (first-class type)**.

HC memungkinkan pengguna untuk:
- memuat dan menginspeksi codex huruf,
- melakukan operasi aljabar, diferensial, integral, geometri, dan exomatrix,
- memverifikasi guard dan audit formal,
- membangun program komputasi berbasis codex,
- dan mengembangkan aplikasi yang memanfaatkan struktur hybit.

### 1.2 Mengapa HC?

Bahasa pemrograman umum (Python, Rust, C++) **dapat** memproses
vektor integer. Namun mereka tidak:
- memahami codex sebagai tipe bawaan,
- menerapkan guard secara otomatis,
- menyediakan modul matematika Hijaiyyah secara native,
- atau menghubungkan operasi codex langsung ke mesin H-ISA.

HC diciptakan untuk mengisi kekosongan itu.

### 1.3 Posisi HC dalam Ekosistem

```
Pengguna
   │
   ├── menulis program HC (.hc)
   │
   ▼
HC Lexer → Parser → AST → Evaluator
   │
   ├── standard library (hm::*)
   ├── H-ISA compiler (opsional)
   ├── HCVM runtime
   │
   ▼
Hasil: codex, analisis, audit, output
```

### 1.4 Catatan Status

HC v1.0 adalah **spesifikasi rilis pertama**. Beberapa fitur
yang disebutkan dalam dokumen ini mungkin masih pada tahap
implementasi awal. Fitur yang belum sepenuhnya tersedia
ditandai dengan label **[PLANNED]**.

---

## 2. Desain dan Filosofi Bahasa

### 2.1 Prinsip Desain

| Prinsip | Penjelasan |
|---|---|
| **Familiar** | sintaks mirip Rust/Python, mudah dipelajari |
| **Codex-native** | hybit sebagai tipe bawaan |
| **Auditable** | guard dan audit terintegrasi |
| **Deterministic** | komputasi integer, tidak ada floating-point ambiguity |
| **Composable** | modul standard library yang saling melengkapi |
| **Readable** | kode yang mudah dibaca dan didokumentasikan |

### 2.2 Perbandingan Gaya Sintaks

```
HC:     let h = load('ب');
Python: h = load('ب')
Rust:   let h = load('ب');
```

```
HC:     fn add(a: int, b: int) -> int { return a + b; }
Python: def add(a: int, b: int) -> int: return a + b
Rust:   fn add(a: i32, b: i32) -> i32 { a + b }
```

HC mengambil:
- **deklarasi** ala Rust (`let`, `let mut`, `const`, `fn`),
- **keterbacaan** ala Python (nama jelas, minim simbol eksotik),
- **tipe data** yang spesifik untuk domain Hijaiyyah.

### 2.3 Apa yang HC Bukan

HC **bukan**:
- bahasa general-purpose (belum ada I/O file, threading, dll.),
- bahasa untuk memproses bahasa natural Arab,
- bahasa untuk tafsir atau analisis teks keagamaan,
- ekstensi dari Python atau Rust.

HC **adalah**:
- bahasa domain-specific untuk komputasi codex Hijaiyyah,
- dengan potensi pengembangan ke domain yang lebih luas.

---

## 3. Leksikal

### 3.1 Encoding

| Aturan | Nilai |
|---|---|
| Encoding file | UTF-8 |
| Normalisasi | NFC diterapkan sebelum tokenisasi |
| Character set | ASCII + Unicode Hijaiyyah canonical |

### 3.2 Whitespace

Spasi, tab, carriage return, dan newline diperlakukan sebagai
pemisah token. HC tidak sensitif terhadap indentasi.

### 3.3 Komentar

#### Komentar satu baris

```hc
// ini komentar satu baris
let x = 10; // komentar di akhir baris
```

#### Komentar blok

```hc
/* ini komentar blok
   bisa multi-baris */
let y = 20;
```

### 3.4 Kata Kunci

Kata kunci berikut **tidak boleh** digunakan sebagai identifier:

```
let      mut      const    fn       return
if       else     match    while    for
in       use      struct   enum     true
false    none     try      catch
```

### 3.5 Literal

#### Integer

```hc
42
0
1000
```

#### Float

```hc
3.14
0.5
100.0
```

#### Boolean

```hc
true
false
```

#### String

```hc
"Hello, HC"
"بسم الله"
"line\nnewline"
"tab\there"
"quote\"inside"
"backslash\\"
```

Escape sequences yang didukung:

| Escape | Karakter |
|---|---|
| `\n` | newline |
| `\t` | tab |
| `\r` | carriage return |
| `\"` | kutip ganda |
| `\\` | backslash |

#### Hijaiyyah Literal

Huruf Hijaiyyah kanonik ditulis dalam tanda kutip tunggal:

```hc
'ب'
'ج'
'هـ'
'ا'
```

Aturan:
- harus tepat satu karakter Hijaiyyah kanonik,
- `'ه'` secara otomatis dinormalisasi menjadi `'هـ'`,
- literal yang bukan anggota $\mathcal{H}_{28}$ menghasilkan error.

#### None

```hc
none
```

#### Array

```hc
[1, 2, 3, 4]
['ب', 'ت', 'ث']
```

### 3.6 Identifier

Identifier dimulai dengan huruf ASCII atau underscore,
diikuti oleh huruf, digit, atau underscore:

```
[a-zA-Z_][a-zA-Z0-9_]*
```

Contoh valid:
```
x
total
my_function
_private
h28
codex_entry
```

### 3.7 Operator dan Delimiter

#### Operator satu karakter

```
+  -  *  /  %  !  <  >  =  .
```

#### Operator dua karakter

```
==  !=  <=  >=  &&  ||  ->  =>  ::  ..
```

#### Operator tiga karakter

```
..=
```

#### Delimiter

```
(  )  {  }  [  ]  ,  :  ;
```

---

## 4. Tipe Data

### 4.1 Tipe Primitif

| Tipe | Deskripsi | Contoh |
|---|---|---|
| `int` | Bilangan bulat | `42`, `-7`, `0` |
| `float` | Bilangan pecahan | `3.14`, `0.5` |
| `bool` | Boolean | `true`, `false` |
| `char` | Karakter Unicode | `'ب'` |
| `string` | Rangkaian karakter | `"بسم الله"` |
| `none` | Nilai kosong | `none` |

### 4.2 Tipe Codex (Domain-Specific)

| Tipe | Dimensi | Deskripsi |
|---|---|---|
| `hybit` | 18 | Vektor codex 18D (tipe utama) |
| `codex14` | 14 | Vektor codex inti 14D |
| `nuqtah3` | 3 | Vektor titik $(N_a, N_b, N_d)$ |
| `khatt5` | 5 | Vektor garis $(K_p, K_x, K_s, K_a, K_c)$ |
| `qaws5` | 5 | Vektor lengkung $(Q_p, Q_x, Q_s, Q_a, Q_c)$ |
| `exomatrix` | 5×5 | Matriks audit Exomatrix |

### 4.3 Tipe Koleksi

| Tipe | Deskripsi | Contoh |
|---|---|---|
| `array` | Array dinamis | `[1, 2, 3]` |
| `range` | Rentang integer | `0..10`, `1..=28` |

### 4.4 Tipe Keamanan **[PLANNED]**

| Tipe | Deskripsi |
|---|---|
| `seal` | Identitas dataset-seal |
| `signature` | Tanda tangan digital |
| `bytes` | Data biner mentah |

### 4.5 Tipe Error Handling **[PLANNED]**

| Tipe | Deskripsi |
|---|---|
| `result<T, E>` | Nilai berhasil atau error |
| `option<T>` | Nilai ada atau kosong |

### 4.6 Konversi Tipe

HC melakukan konversi implisit secara terbatas:

| Dari | Ke | Konversi |
|---|---|---|
| `int` | `float` | otomatis dalam ekspresi campuran |
| `char` (Hijaiyyah) | `hybit` | melalui `load()` |
| `hybit` | `codex14` | melalui `load14()` atau slicing |
| `hybit` | `exomatrix` | melalui `.exomatrix()` atau `hm::exomatrix::build()` |

Konversi lain harus dilakukan secara eksplisit.

---

## 5. Variabel dan Konstanta

### 5.1 Deklarasi Variabel

#### Immutable (default)

```hc
let x: int = 10;
let name: string = "Hijaiyyah";
let h = load('ب');
```

#### Mutable

```hc
let mut total: hybit = zero();
let mut count: int = 0;
```

### 5.2 Deklarasi Konstanta

```hc
const PI: float = 3.14159;
const MAX_LETTERS: int = 28;
const RELEASE: string = "HM-28-v1.0-HC18D";
```

### 5.3 Inferensi Tipe

Anotasi tipe bersifat **opsional** jika tipe dapat diinferensi:

```hc
let x = 42;           // int
let h = load('ب');    // hybit (CodexEntry)
let s = "hello";      // string
let flag = true;       // bool
```

### 5.4 Shadowing

```hc
let x = 10;
let x = x + 5;  // x sekarang 15
```

---

## 6. Operator

### 6.1 Operator Aritmetika

| Operator | Fungsi | Contoh |
|---|---|---|
| `+` | penjumlahan | `a + b` |
| `-` | pengurangan | `a - b` |
| `*` | perkalian | `a * b` |
| `/` | pembagian | `a / b` |
| `%` | modulo | `a % b` |

#### Penjumlahan Codex

Operator `+` pada dua hybit/codex menghasilkan
**penjumlahan vektor komponen per komponen**:

```hc
let h1 = load('ب');
let h2 = load('س');
let total = h1 + h2;  // vektor 18D: [h1[i] + h2[i]]
```

#### Pengurangan Codex

Operator `-` pada dua codex menghasilkan
**delta vektor 14D** (dalam $\mathbb{Z}^{14}$):

```hc
let delta = load('ت') - load('ب');  // delta 14D
```

### 6.2 Operator Perbandingan

| Operator | Fungsi |
|---|---|
| `==` | sama dengan |
| `!=` | tidak sama |
| `<` | kurang dari |
| `>` | lebih dari |
| `<=` | kurang dari atau sama |
| `>=` | lebih dari atau sama |

### 6.3 Operator Logika

| Operator | Fungsi |
|---|---|
| `&&` | AND logika |
| `\|\|` | OR logika |
| `!` | NOT logika |

### 6.4 Operator Range

| Operator | Fungsi | Contoh |
|---|---|---|
| `..` | range eksklusif | `0..10` (0 sampai 9) |
| `..=` | range inklusif | `1..=28` (1 sampai 28) |

### 6.5 Operator Akses

| Operator | Fungsi | Contoh |
|---|---|---|
| `.` | akses method/properti | `h.theta()` |
| `::` | akses modul | `hm::geometry::euclidean()` |

### 6.6 Precedence (Prioritas)

Dari **tertinggi** ke **terendah**:

| Level | Operator |
|---|---|
| 1 | `!`, `-` (unary) |
| 2 | `*`, `/`, `%` |
| 3 | `+`, `-` |
| 4 | `..`, `..=` |
| 5 | `<`, `>`, `<=`, `>=` |
| 6 | `==`, `!=` |
| 7 | `&&` |
| 8 | `\|\|` |

Tanda kurung `( )` dapat digunakan untuk mengubah prioritas.

---

## 7. Ekspresi

### 7.1 Literal

```hc
42
3.14
"hello"
'ب'
true
none
[1, 2, 3]
```

### 7.2 Referensi Variabel

```hc
x
total
my_variable
```

### 7.3 Binary Expression

```hc
a + b
x * 2
h1.dist2(h2)
```

### 7.4 Unary Expression

```hc
-x
!flag
```

### 7.5 Call Expression

```hc
load('ب')
println("Hello")
hm::geometry::euclidean(h1, h2)
```

### 7.6 Method Call

```hc
h.theta()
h.guard()
h.norm2()
h.dist2(other)
```

### 7.7 Module Access

```hc
hm::vectronometry::norm2(h)
hm::integral::string_integral("بسم")
```

### 7.8 Array Literal

```hc
[1, 2, 3, 4, 5]
['ب', 'ت', 'ث']
```

### 7.9 Range Expression

```hc
0..10
1..=28
```

---

## 8. Struktur Kontrol

### 8.1 If / Else

```hc
if condition {
    // ...
}

if condition {
    // ...
} else {
    // ...
}

if condition1 {
    // ...
} else if condition2 {
    // ...
} else {
    // ...
}
```

#### Contoh

```hc
if h.guard() {
    println("Codex valid");
} else {
    println("Codex invalid!");
}
```

### 8.2 Match

```hc
match value {
    pattern1 => expression1,
    pattern2 => expression2,
    _ => default_expression
}
```

#### Contoh

```hc
match h.theta() {
    0 => println("No turning"),
    1 => println("Quarter turn"),
    2 => println("Half turn"),
    3 => println("Three-quarter turn"),
    4 => println("Full turn"),
    _ => println("Multi-turn")
}
```

#### Match dengan block

```hc
match category {
    "line" => {
        println("Pure line form");
        println("alpha = 0");
    },
    "curve" => {
        println("Pure curve form");
        println("alpha = 90");
    },
    _ => println("Mixed")
}
```

### 8.3 While

```hc
while condition {
    // ...
}
```

#### Contoh

```hc
let mut i = 0;
while i < 28 {
    println(i);
    i = i + 1;
}
```

### 8.4 For

```hc
for variable in iterable {
    // ...
}
```

#### Contoh

```hc
for ch in "بسم" {
    println(ch);
}

for i in 1..=28 {
    println(i);
}

for i in 1..=28 {
    let h = load_id(i);
    println(h.theta());
}
```

---

## 9. Fungsi

### 9.1 Deklarasi

```hc
fn name(param1: type1, param2: type2) -> return_type {
    // body
    return value;
}
```

### 9.2 Tanpa Return Type

```hc
fn greet(name: string) {
    println("Hello,", name);
}
```

### 9.3 Contoh Lengkap

```hc
fn kodeks_kata(teks: string) -> hybit {
    let mut total = zero();
    for ch in teks {
        if ch != ' ' {
            total = total + load(ch);
        }
    }
    return total;
}

fn jarak(a: char, b: char) -> float {
    let h1 = load(a);
    let h2 = load(b);
    return hm::geometry::euclidean(h1, h2);
}

fn is_open_path(h) -> bool {
    return h.theta() % 4 != 0;
}
```

### 9.4 Fungsi sebagai First-Class **[PLANNED]**

```hc
// belum didukung di v1.0
let f = fn(x: int) -> int { return x * 2; };
```

---

## 10. Modul dan Import

### 10.1 Use Statement

```hc
use hm::vectronometry;
use hm::geometry;
```

### 10.2 Wildcard Import

```hc
use hm::vectronometry::*;
```

### 10.3 Named Import

```hc
use hm::geometry::{euclidean, manhattan, nearest};
```

### 10.4 Module Path

```hc
hm::vectronometry::norm2(h)
hm::differential::diff(h1, h2)
hm::integral::string_integral("بسم")
hm::geometry::diameter()
hm::exomatrix::build(h)
```

### 10.5 Modul yang Tersedia

| Path | Bidang |
|---|---|
| `hm::vectronometry` | Bab II-A |
| `hm::differential` | Bab II-B |
| `hm::integral` | Bab II-C |
| `hm::geometry` | Bab II-D |
| `hm::exomatrix` | Bab II-E |

---

## 11. Metode Hybit

Setiap objek hybit/CodexEntry memiliki metode bawaan
yang dapat dipanggil dengan sintaks dot-notation.

### 11.1 Akses Komponen

| Method | Return | Deskripsi |
|---|---|---|
| `.theta()` | `int` | $\hat{\Theta}(h)$ |
| `.Na()` | `int` | Nuqṭah ascender |
| `.Nb()` | `int` | Nuqṭah body |
| `.Nd()` | `int` | Nuqṭah descender |
| `.Kp()` | `int` | Khaṭṭ primer |
| `.Kx()` | `int` | Khaṭṭ auxiliary |
| `.Ks()` | `int` | Khaṭṭ straight vertical |
| `.Ka()` | `int` | Khaṭṭ angular |
| `.Kc()` | `int` | Khaṭṭ closed-loop |
| `.Qp()` | `int` | Qaws primer |
| `.Qx()` | `int` | Qaws auxiliary |
| `.Qs()` | `int` | Qaws smooth |
| `.Qa()` | `int` | Qaws angular |
| `.Qc()` | `int` | Qaws closed loop |
| `.AN()` | `int` | Total Nuqṭah |
| `.AK()` | `int` | Total Khaṭṭ |
| `.AQ()` | `int` | Total Qaws |
| `.Hstar()` | `int` | Marker Hamzah |

### 11.2 Metode Struktural

| Method | Return | Deskripsi |
|---|---|---|
| `.U()` | `int` | Budget turning: $Q_x + Q_s + Q_a + 4Q_c$ |
| `.rho()` | `int` | Residu turning: $\hat{\Theta} - U$ |
| `.guard()` | `bool` | Validasi guard G1–G4 |
| `.guard_detail()` | `dict` | Detail guard per relasi |
| `.total()` | `tuple` | $(A_N, A_K, A_Q)$ |
| `.array()` | `list` | Vektor 18D sebagai list |

### 11.3 Metode Aljabar

| Method | Return | Deskripsi |
|---|---|---|
| `.norm2()` | `int` | $\|v_{14}\|^2$ |
| `.norm()` | `float` | $\|v_{14}\|$ |
| `.dot(other)` | `int` | $\langle h_1, h_2 \rangle$ |
| `.cosine(other)` | `float` | Cosine similarity |
| `.dist2(other)` | `int` | $d_2^2(h_1, h_2)$ |
| `.dist(other)` | `float` | $d_2(h_1, h_2)$ |
| `.manhattan(other)` | `int` | $d_1(h_1, h_2)$ |
| `.hamming(other)` | `int` | $d_H(h_1, h_2)$ |

### 11.4 Metode Proyeksi

| Method | Return | Deskripsi |
|---|---|---|
| `.proj_theta()` | `list` | Proyeksi layer $\Theta$ |
| `.proj_N()` | `list` | Proyeksi layer N |
| `.proj_K()` | `list` | Proyeksi layer K |
| `.proj_Q()` | `list` | Proyeksi layer Q |

### 11.5 Metode Rasio

| Method | Return | Deskripsi |
|---|---|---|
| `.r_N()` | `float` | Rasio Nuqṭah |
| `.r_K()` | `float` | Rasio Khaṭṭ |
| `.r_Q()` | `float` | Rasio Qaws |
| `.r_U()` | `float` | Rasio turning non-primer |
| `.r_rho()` | `float` | Rasio turning primer |
| `.r_loop()` | `float` | Rasio loop |

### 11.6 Metode Exomatrix

| Method | Return | Deskripsi |
|---|---|---|
| `.exomatrix()` | `list[list]` | Exomatrix 5×5 |
| `.phi()` | `int` | Frobenius energy $\Phi$ |

---

## 12. Standard Library

### 12.1 `hm::vectronometry`

**Referensi:** Bab II-A (Vectronometry)

| Fungsi | Return | Deskripsi |
|---|---|---|
| `project(h)` | `dict` | Proyeksi ke 4 subruang |
| `primitive_ratios(h)` | `dict` | $r_N, r_K, r_Q$ |
| `turning_ratios(h)` | `dict` | $r_U, r_\rho, r_{loop}$ |
| `comp_angle(h)` | `float` | Sudut komposisional $\alpha(h)$ |
| `norm2(h)` | `int` | $\|v_{14}\|^2$ |
| `norm(h)` | `float` | $\|v_{14}\|$ |
| `inner(h1, h2)` | `int` | Inner product |
| `cosine(h1, h2)` | `float` | Cosine similarity |
| `pythagorean_check(h)` | `dict` | Verifikasi Pythagorean |
| `full_table()` | `list` | Tabel 28 huruf lengkap |

### 12.2 `hm::differential`

**Referensi:** Bab II-B (Differential Vector Calculus)

| Fungsi | Return | Deskripsi |
|---|---|---|
| `diff(h1, h2)` | `list[int]` | $\Delta(h_1, h_2) \in \mathbb{Z}^{14}$ |
| `diff_theta(h1, h2)` | `int` | $\Delta_\Theta$ |
| `diff_N(h1, h2)` | `list[int]` | $\Delta_N$ |
| `diff_K(h1, h2)` | `list[int]` | $\Delta_K$ |
| `diff_Q(h1, h2)` | `list[int]` | $\Delta_Q$ |
| `norm_decomposition(h1, h2)` | `dict` | Dekomposisi $\|\Delta\|^2$ |
| `dot_gradient(h1, h2)` | `list[int]` | Gradien Nuqṭah |
| `u_gradient()` | `list[int]` | $\nabla_Q U = (0,1,1,1,4)$ |
| `second_diff(h1, h2, h3)` | `list[int]` | $\Delta^2$ |
| `all_dot_variants()` | `list` | Semua pasangan dot-variant |
| `distance_table()` | `list` | Tabel jarak dot-variant |

### 12.3 `hm::integral`

**Referensi:** Bab II-C (Integral Vector Calculus)

| Fungsi | Return | Deskripsi |
|---|---|---|
| `string_integral(text)` | `dict` | $\int_w \vec{h}$ |
| `add_codex(cod1, cod2)` | `dict` | $\int_{uv} = \int_u + \int_v$ |
| `layer_integrals(text)` | `dict` | Integral per layer |
| `centroid(text)` | `list[float]` | $\bar{v}(w)$ |
| `cumulative(text)` | `list` | $S_0, S_1, \ldots, S_n$ |
| `energy_integral(text)` | `int` | $\int_w \Phi$ |
| `mean_theta(text)` | `float` | Rata-rata $\hat{\Theta}$ |

### 12.4 `hm::geometry`

**Referensi:** Bab II-D (Codex Geometry)

| Fungsi | Return | Deskripsi |
|---|---|---|
| `euclidean(h1, h2)` | `float` | $d_2$ |
| `euclidean_sq(h1, h2)` | `int` | $d_2^2$ |
| `manhattan(h1, h2)` | `int` | $d_1$ |
| `hamming(h1, h2)` | `int` | $d_H$ |
| `distance_decomposition(h1, h2)` | `dict` | Per-layer decomposition |
| `nearest(h)` | `tuple` | Huruf terdekat + jarak |
| `k_nearest(h, k)` | `list` | $k$ huruf terdekat |
| `is_orthogonal(h1, h2)` | `bool` | Support orthogonality |
| `gram_matrix()` | `list[list]` | Gram matrix $28 \times 28$ |
| `diameter_sq()` | `int` | $\text{diam}^2(\mathcal{H}_{28})$ |
| `diameter()` | `float` | $\text{diam}(\mathcal{H}_{28})$ |
| `alphabet_centroid()` | `list[float]` | Centroid $v_{14}$ |
| `polarization_check(h1, h2)` | `dict` | Identitas polarisasi |

### 12.5 `hm::exomatrix`

**Referensi:** Bab II-E (Exomatrix Analysis)

| Fungsi | Return | Deskripsi |
|---|---|---|
| `build(h)` | `list[list]` | Exomatrix $\mathcal{E}(h)$ |
| `audit(E)` | `dict` | R1–R5 audit |
| `row_sums(E)` | `list[int]` | $\sigma_1, \ldots, \sigma_5$ |
| `grand_sum(E)` | `int` | $\sum_{r,c} E_{r,c}$ |
| `phi(E)` | `int` | $\Phi(h) = \|\mathcal{E}\|_F^2$ |
| `phi_decomposition(E)` | `dict` | Per-layer energy |
| `string_exomatrix(text)` | `list[list]` | $\mathcal{E}(w)$ |
| `energy_table()` | `list` | 28 huruf diurutkan $\Phi$ |
| `reconstruct(E)` | `list[int]` | $v_{18}$ dari $\mathcal{E}$ |
| `rank_M14()` | `int` | $\text{rank}(M_{14})$ |
| `rank_M()` | `int` | $\text{rank}(M)$ |

---

## 13. Built-in Functions

### 13.1 Codex Operations

| Fungsi | Deskripsi |
|---|---|
| `load(ch)` | Muat codex huruf dari $\mathcal{H}_{28}$ |
| `load_id(idx)` | Muat codex berdasarkan index huruf, 1–28 |
| `zero()` | Vektor nol 18D |
| `identify(vec)` | Identifikasi huruf dari vektor |
| `is_hijaiyyah(ch)` | Cek apakah karakter termasuk $\mathcal{H}_{28}$ |

> `load14`, `zero14`, dan `hybit` pernah tercantum di sini tetapi tidak
> pernah diimplementasi. Keduanya dihapus agar daftar ini menggambarkan
> fungsi yang benar-benar dapat dipanggil;
> `tests/test_language/test_docs_builtins.py` menjaganya tetap begitu.

### 13.2 Output

| Fungsi | Deskripsi |
|---|---|
| `print(...)` | Cetak tanpa newline |
| `println(...)` | Cetak dengan newline |

### 13.3 Assertion

| Fungsi | Deskripsi |
|---|---|
| `assert(cond, msg)` | Gagal jika `cond` false |
| `assert_approx(a, b, eps)` | Gagal jika $|a-b| > \epsilon$ |

### 13.4 Utility

| Fungsi | Deskripsi |
|---|---|
| `len(x)` | Panjang string atau array |
| `abs(x)` | Nilai mutlak |
| `sqrt(x)` | Akar kuadrat (float) |
| `now()` | Timestamp saat ini (placeholder) |

---

## 14. Error Handling

### 14.1 Status Saat Ini

HC v1.0 menggunakan mekanisme error sederhana:

- runtime error menghasilkan pesan di console,
- `assert()` menghentikan eksekusi jika gagal,
- evaluator menangkap exception dan menampilkan pesan.

### 14.2 Rencana **[PLANNED]**

```hc
// belum didukung di v1.0
let result = try {
    load('x')  // karakter invalid
} catch err {
    println("Error:", err);
    zero()
};
```

---

## 15. Grammar Formal (EBNF)

```ebnf
program         = { statement } ;

statement       = use_stmt | let_stmt | const_stmt | fn_decl
                | return_stmt | while_stmt | for_stmt | expr_stmt ;

use_stmt        = "use" , path ,
                  [ "::" , "*" | "::" , "{" , ident , { "," , ident } , "}" ] ,
                  [ ";" ] ;

let_stmt        = "let" , [ "mut" ] , ident , [ ":" , type_expr ] ,
                  "=" , expr , [ ";" ] ;

const_stmt      = "const" , ident , [ ":" , type_expr ] ,
                  "=" , expr , [ ";" ] ;

fn_decl         = "fn" , ident , "(" , [ param_list ] , ")" ,
                  [ "->" , type_expr ] , block ;

param_list      = param , { "," , param } ;
param           = ident , [ ":" , type_expr ] ;

return_stmt     = "return" , [ expr ] , [ ";" ] ;
while_stmt      = "while" , expr , block ;
for_stmt        = "for" , ident , "in" , expr , block ;
expr_stmt       = expr , [ ";" ] ;

block           = "{" , { statement } , "}" ;

expr            = if_expr | match_expr | logic_or ;
if_expr         = "if" , expr , block , [ "else" , ( block | if_expr ) ] ;
match_expr      = "match" , expr , "{" , match_arm , { "," , match_arm } ,
                  [ "," ] , "}" ;
match_arm       = expr , "=>" , ( expr | block ) ;

logic_or        = logic_and , { "||" , logic_and } ;
logic_and       = equality , { "&&" , equality } ;
equality        = comparison , { ( "==" | "!=" ) , comparison } ;
comparison      = range_expr , { ( "<" | "<" | "<=" | ">=" ) , range_expr } ;
range_expr      = additive , [ ( ".." | "..=" ) , additive ] ;
additive        = multiplicative , { ( "+" | "-" ) , multiplicative } ;
multiplicative  = unary , { ( "*" | "/" | "%" ) , unary } ;
unary           = [ "!" | "-" ] , postfix ;

postfix         = primary ,
                  { "." , ident , [ "(" , [ arg_list ] , ")" ]
                  | "(" , [ arg_list ] , ")" } ;

arg_list        = expr , { "," , expr } ;

primary         = integer | float | string | hijaiyyah | ident | path
                | array | "(" , expr , ")" | "true" | "false" | "none" ;

array           = "[" , [ expr , { "," , expr } ] , "]" ;
path            = ident , "::" , ident , { "::" , ident } ;
type_expr       = ident | path ;
```

---

## 16. Contoh Program

### 16.1 Hello HC

```hc
fn main() {
    println("Hello, HC v1.0");
    println("Matematika Hijaiyyah — Formal Computational Framework");
}
```

### 16.2 Analisis Huruf

```hc
fn main() {
    let h = load('ج');
    println("Letter: Jim");
    println("Theta:", h.theta(), "=", h.theta() * 90, "degrees");
    println("N:", h.Na(), h.Nb(), h.Nd());
    println("K:", h.Kp(), h.Kx(), h.Ks(), h.Ka(), h.Kc());
    println("Q:", h.Qp(), h.Qx(), h.Qs(), h.Qa(), h.Qc());
    println("U:", h.U());
    println("Rho:", h.rho());
    println("Guard:", h.guard());
    println("Norm2:", h.norm2());
}
```

### 16.3 String Integral

```hc
fn kodeks_kata(teks: string) -> hybit {
    let mut total = zero();
    for ch in teks {
        if ch != ' ' {
            total = total + load(ch);
        }
    }
    return total;
}

fn main() {
    let bsm = kodeks_kata("بسم");
    let allah = kodeks_kata("الله");

    println("Codex(بسم):", bsm);
    println("Codex(الله):", allah);

    let bsm_layers = hm::integral::layer_integrals("بسم");
    println("Theta:", bsm_layers);
}
```

### 16.4 Five Fields Demo

```hc
fn main() {
    let h = load('ف');
    let h2 = load('ب');

    // Field 1: Vectronometry
    println("=== Vectronometry ===");
    println("Norm2:", h.norm2());
    let ratios = hm::vectronometry::primitive_ratios(h);
    println("Ratios:", ratios);

    // Field 2: Differential
    println("=== Differential ===");
    let delta = hm::differential::diff(h, h2);
    println("Delta:", delta);

    // Field 3: Integral
    println("=== Integral ===");
    let cod = hm::integral::string_integral("بسم");
    println("Integral:", cod);

    // Field 4: Geometry
    println("=== Geometry ===");
    let dist = hm::geometry::euclidean(load('ا'), load('هـ'));
    println("Distance:", dist);
    println("Diameter:", hm::geometry::diameter());

    // Field 5: Exomatrix
    println("=== Exomatrix ===");
    let e = hm::exomatrix::build(h);
    println("E(h):", e);
    let audit = hm::exomatrix::audit(e);
    println("Audit:", audit);
    println("Phi:", hm::exomatrix::phi(e));
}
```

### 16.5 Guard Validation

```hc
fn validate_all() {
    for i in 1..=28 {
        let h = load_id(i);
        if h.guard() {
            println("PASS:", i);
        } else {
            println("FAIL:", i);
        }
    }
}

fn main() {
    validate_all();
    println("All 28 letters validated.");
}
```

### 16.6 Geometry Explorer

```hc
fn main() {
    let a = load('ا');
    let h = load('هـ');

    println("d2(Alif, Haa):", hm::geometry::euclidean(a, h));
    println("d2^2:", hm::geometry::euclidean_sq(a, h));
    println("d1:", hm::geometry::manhattan(a, h));
    println("dH:", hm::geometry::hamming(a, h));

    let nearest = hm::geometry::nearest(a);
    println("Nearest to Alif:", nearest);

    let orth = hm::geometry::is_orthogonal(a, load('ب'));
    println("Alif perp Ba:", orth);

    println("Diameter:", hm::geometry::diameter());
}
```

---

## 17. Konvensi dan Gaya

### 17.1 Penamaan

| Objek | Konvensi | Contoh |
|---|---|---|
| Variabel | `snake_case` | `total_theta` |
| Fungsi | `snake_case` | `kodeks_kata()` |
| Konstanta | `UPPER_SNAKE` | `MAX_LETTERS` |
| Tipe | `PascalCase` | `CodexEntry` |

### 17.2 File

| Konvensi | Nilai |
|---|---|
| Ekstensi | `.hc` |
| Encoding | UTF-8 |
| Indentasi | 4 spasi |
| Max baris | 100 karakter |

### 17.3 Dokumentasi Kode

```hc
// Hitung codex string dengan mengagregasikan v18 per huruf
fn kodeks_kata(teks: string) -> hybit {
    // ...
}
```

---

## 18. Eksekusi dan Tooling

### 18.1 Menjalankan Program

```bash
hc run program.hc       # jalankan
hc check program.hc     # parse saja, laporkan galat tanpa mengeksekusi
hc repl                 # sesi interaktif
hc lsp                  # language server, lewat stdin/stdout
```

`hc` terpasang bersama paketnya (`pip install -e .`).

`hc check` menerima banyak berkas sekaligus, sehingga cocok untuk pre-commit
hook atau CI:

```bash
hc check examples/*.hc docs/examples/*.hc
```

Program juga dapat dievaluasi dari Python bila diperlukan — misalnya untuk
menangkap keluaran alih-alih mencetaknya:

```python
from hijaiyyah.language.lexer import Lexer
from hijaiyyah.language.parser import Parser
from hijaiyyah.language.evaluator import HCEvaluator

lines = []
ast = Parser(Lexer(open("program.hc").read()).tokenize()).parse()
HCEvaluator(print_func=lambda *a: lines.append(" ".join(map(str, a)))).evaluate(ast)
```

### 18.2 Tooling yang Tersedia

| Tool | Fungsi |
|---|---|
| **`hc`** | CLI: run, check, repl, language server |
| **Ekstensi VS Code** | Pewarnaan sintaks + diagnostik langsung (`editors/vscode/`) |
| **HOM HC IDE** | Editor + evaluator + panel rujukan |
| **HCVM** | Virtual machine mandiri |
| **Bytecode Inspector** | Decoder H-ISA waktu nyata |
| **H-ISA Machine** | Penampil keadaan CPU |

Ekstensi VS Code dipasang dengan menautkannya ke direktori ekstensi:

```bash
ln -s "$(pwd)/editors/vscode" ~/.vscode/extensions/hc-hijaiyyah
```

Pewarnaan sintaks berjalan tanpa apa pun terpasang. Diagnostik langsung
menuntut `hc` ada di PATH; tanpa itu ekstensi memberi tahu sekali lalu tetap
mewarnai.

### 18.3 Diagnostik

Galat leksikal dan sintaksis dilaporkan dengan kutipan sumber dan penunjuk
kolom:

```
error: Unexpected token in expression (got SEMICOLON ';')
 --> program.hc:2:9
  |
2 | let b = ;
  |         ^
  help: declare it first with `let`
```

Galat semantik — variabel tak dikenal, fungsi stdlib salah eja — tidak membawa
posisi, sehingga ditampilkan tanpa kutipan sumber alih-alih menunjuk lokasi
yang belum tentu benar.

Language server melaporkan galat parse selagi diketik. Galat semantik baru
muncul saat program dijalankan, karena evaluator belum menyimpan posisi.

Selain itu tersedia `println()` untuk penelusuran, dan penampil AST di HOM GUI.

---

## 19. Batasan dan Rencana Pengembangan

### 19.1 Batasan HC v1.0

| Batasan | Penjelasan |
|---|---|
| Tidak ada file I/O | belum bisa baca/tulis file |
| Tidak ada network | belum bisa akses jaringan |
| Tidak ada threading | single-threaded |
| Tidak ada FFI | belum bisa panggil C/Python |
| Tidak ada struct/enum | belum didukung |
| Tidak ada generics | belum didukung |
| Tidak ada closure | belum didukung |
| Error handling minimal | belum ada try/catch |
| Tidak ada package manager | belum ada hcpm |
| Sandbox belum ketat | jangan jalankan kode tidak dipercaya |

### 19.2 Sudah Terkirim

Tiga butir berikut semula tercantum sebagai rencana v1.1 dan v2.0, dan kini
sudah tersedia:

```
☑ improved diagnostics      kutipan sumber + penunjuk kolom (§18.3)
☑ syntax highlighting       ekstensi VS Code (editors/vscode/)
☑ LSP                       hc lsp — diagnostik, hover, completion
```

Selain itu, tiga celah yang membuat program biasa tak dapat ditulis sudah
ditutup: pernyataan penugasan (`x = 2`, dengan `let mut`), pemutus baris di
dalam kurung, dan evaluasi literal array. Ketiganya sudah tercantum di grammar
formal sejak awal tetapi belum diimplementasi.

### 19.3 Rencana v1.1 **[PLANNED]**

```
□ try / catch error handling
□ struct dan enum
□ file I/O dasar
□ package manifest (hc.toml)
□ posisi pada galat semantik      agar dapat dilaporkan selagi diketik
```

### 19.4 Rencana v2.0 **[PLANNED]**

```
□ closures dan higher-order functions
□ generics
□ FFI ke Python/C
□ async primitives
□ network module
□ WebAssembly target
□ hcpm package manager
```

---

## 20. Referensi

| Referensi | Deskripsi |
|---|---|
| Bab I | Fondasi Formal Matematika Hijaiyyah |
| Bab II | Lima Bidang Matematika Hijaiyyah |
| Bab III | Hybit dan Arsitektur Fotonik |
| | Hijaiyyah Technology Stack v1.0 |
| Bab V | Hybit: Unit Komputasi dan Ekosistem |
| `docs/architecture.md` | Arsitektur HOM |
| `docs/hisa_spec.md` | Spesifikasi H-ISA |
| `README.md` | Dokumentasi utama |

---

<div align="center">

**HC — Hijaiyyah Codex Language**

*Version 1.0 · HM-28-v1.0-HC18D · 2026*

© 2026 Hijaiyyah Mathematics Computational Laboratory (HMCL)

</div>
