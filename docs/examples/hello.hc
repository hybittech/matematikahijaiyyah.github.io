// hello.hc — the smallest complete HC program.
// Companion to docs/HC_LANGUAGE_SPEC.md §1–§3.

// A letter literal is written in single quotes. Only the 28 canonical
// Hijaiyyah letters lex as a letter literal; anything else is a lex error,
// so an invalid letter can never reach the guards.
let jim = 'ج';

println("=== hello.hc ===");
println("Letter:", jim);

// Every letter answers questions about its own geometry. theta() is the
// turning number, the first slot of v18.
println("Theta:", jim.theta());

// norm2() is the squared norm over v14 — the 14 independent components.
println("Norm2:", jim.norm2());

// guard() runs all six constraints (G1-G4, T1-T2) and returns one verdict.
// Every canonical letter passes; this is what makes validation intrinsic
// rather than a stored checksum.
println("Guard:", jim.guard());

// guard_detail() returns the individual audit relations instead of a verdict.
println("Detail:", jim.guard_detail());

// Letters can also be fetched by index, 0-27, in canonical order.
let first = load_id(0);
println("Letter 0:", first, "theta =", first.theta());
