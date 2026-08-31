// five_fields.hc — one call into each of the five analytical fields.
// Companion to docs/HC_LANGUAGE_SPEC.md §6 (stdlib) and Bab II of the book.
//
// The five fields are reached through the hm:: namespace. Each answers a
// different question about the same letter.

let h = 'هـ';

println("=== Field 1 — Vectronometry: composition ===");
// How the letter divides between points, lines and curves.
println("Ratios:  ", hm::vectronometry::primitive_ratios(h));
// Squared norm over v14, and its layer-wise split. The two must agree —
// that is the Pythagorean identity of the codex.
println("Pythagoras:", hm::vectronometry::pythagorean_check(h));

println("=== Field 2 — Differential: change between letters ===");
// The component-wise difference between two letters.
println("Diff:    ", hm::differential::diff(h, 'م'));
// How the U functional weights each curve component: Qx, Qs, Qa, then Qc x4.
println("Gradient:", hm::differential::u_gradient());

println("=== Field 3 — Integral: accumulation over a string ===");
// A string integrates to a single 18-component codex.
let word = hm::integral::string_integral("بسم");
println("Cod18:   ", word.cod18);
println("Layers:  ", hm::integral::layer_integrals("بسم"));

println("=== Field 4 — Geometry: distance in letter space ===");
println("Distance:", hm::geometry::euclidean(h, 'م'));
// The widest separation anywhere in the 28-letter space.
println("Diameter:", hm::geometry::diameter());

println("=== Field 5 — Exomatrix: the 5x5 structured view ===");
let E = hm::exomatrix::build(h);
println("Phi:     ", hm::exomatrix::phi(E));
// R1-R5 restate the guards as relations over the matrix.
println("Audit:   ", hm::exomatrix::audit(E));
