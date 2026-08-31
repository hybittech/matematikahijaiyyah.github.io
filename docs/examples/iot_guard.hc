// iot_guard.hc — validating a stream of readings on arrival.
// Companion to docs/HC_LANGUAGE_SPEC.md §5 (control flow).
//
// The case the codex is built for: a device receives values it did not
// produce and must decide, cheaply, whether each one is structurally sound.
// Validation is a fixed number of integer operations per unit — no table
// lookup, no stored checksum, no allocation.
//
// Two notes on style, both current limits of the language rather than
// choices: HC has no assignment statement yet, so a loop cannot carry a
// running total — checks are written as assertions inside the loop instead
// of a counter compared afterwards. And an argument list cannot span
// lines, so calls are kept on one line however long they run.

println("=== Sweeping all 28 letters ===");

for i in 0..28 {
    let h = load_id(i);

    // Every canonical letter passes every guard. A rejection here would mean
    // the reading is not a canonical letter — corruption, not a false alarm.
    if h.guard() {
        println("  index", i, "accepted");
    } else {
        println("  index", i, "REJECTED");
    }

    assert(h.guard(), "a canonical letter failed its guards");
}

println("=== Localising a fault, not merely detecting one ===");

// Beyond pass/fail, the guards say where the trouble is. rho is the turning
// left over after the curve budget U is spent; a negative rho would mean the
// letter claims more curvature than its turning can support. A checksum can
// only report that something changed, never which layer.
for i in 0..6 {
    let h = load_id(i);
    println("  index", i, "| theta", h.theta(), "| rho", h.rho(), "| norm2", h.norm2());
    assert(h.rho() >= 0, "G4 violated: negative rho");
}

println("=== Per-relation detail for one reading ===");

// guard_detail() returns the five audit relations separately, so a caller
// can report which invariant broke rather than a single failed bit.
let sample = load_id(21);
println("Detail:", sample.guard_detail());

println("All readings validated.");
