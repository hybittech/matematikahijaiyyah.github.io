// banking.hc — integrity without a stored checksum.
// Companion to docs/HC_LANGUAGE_SPEC.md §7 and Bab III §1.3.
//
// A conventional ledger validates with a checksum: a value stored alongside
// the data, which says nothing about whether the data is meaningful. The
// codex validates with geometry. The guards are relations the data must
// satisfy in itself, so there is nothing separate to forge.

fn describe(label, h) {
    println(label, "-> theta", h.theta(), "| rho", h.rho(), "| guard", h.guard());
    return h.guard();
}

println("=== Individual entries ===");
let a = describe("Account A", 'ب');
let b = describe("Account B", 'س');
let c = describe("Account C", 'م');

// The valid set is closed under addition: adding two valid entries always
// yields a valid entry. That is what makes the codex a monoid, and it is why
// a ledger can be summed without losing its ability to self-validate.
println("=== Aggregated ledger ===");
let ledger = hm::integral::string_integral("بسم");
println("Total cod18:", ledger.cod18);
println("Entries:    ", ledger.length);

// The three sum-checks survive aggregation because each is linear.
let theta = ledger.cod18[0];
let a_n   = ledger.cod18[14];
let a_k   = ledger.cod18[15];
let a_q   = ledger.cod18[16];
println("Theta:", theta, "| A_N:", a_n, "| A_K:", a_k, "| A_Q:", a_q);

// Recomputing the point sum from its components must reproduce A_N. If a
// single component were altered in transit, this equality would break —
// and it would say which layer was damaged, not merely that something was.
let recomputed = ledger.cod18[1] + ledger.cod18[2] + ledger.cod18[3];
println("A_N recomputed:", recomputed);
assert(recomputed == a_n, "G1 violated: point sum does not match A_N");
println("G1 holds on the aggregate.");
