// string_analysis.hc — comparing two words as codex vectors.
// Companion to docs/HC_LANGUAGE_SPEC.md §6.3 and Bab II-C.
//
// A string integrates to a single 18-component vector. Two strings can then
// be compared the way two letters are, which is what makes the codex useful
// beyond single characters.

let w1 = "بسم";
let w2 = "سبم";

println("=== Two words, same letters, different order ===");

let c1 = hm::integral::string_integral(w1);
let c2 = hm::integral::string_integral(w2);

println(w1, "->", c1.cod18);
println(w2, "->", c2.cod18);

// The string integral is a sum, and addition is commutative, so an anagram
// integrates to exactly the same codex. The integral captures composition,
// not sequence — a property worth knowing before relying on it as an
// identity.
let same = c1.cod18[0] == c2.cod18[0];
println("Same turning total:", same);
assert(same, "anagrams should share a turning total");

println("=== Layer breakdown ===");
println(w1, "layers:", hm::integral::layer_integrals(w1));

println("=== Centroid: the average letter of a word ===");
println("Centroid:", hm::integral::centroid(w1));

println("=== Cumulative trajectory ===");
// The partial sums, letter by letter — the path the word traces through
// codex space rather than only its endpoint.
let path = hm::integral::cumulative(w1);
println("Steps recorded:", len(path));

println("=== A longer phrase ===");
let phrase = hm::integral::string_integral("بسم الله");
println("Letters counted:", phrase.length);
println("Turning total:  ", phrase.cod18[0]);
