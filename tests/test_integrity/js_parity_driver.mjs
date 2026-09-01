// Dumps everything hom-gui/src/engine computes, as JSON on stdout, so
// test_js_engine_parity.py can diff it against the Python implementation.
//
// The JS engine is a hand-written re-implementation of src/hijaiyyah/algebra
// and src/hijaiyyah/core/guards.py. Nothing else forces the two to agree, so
// this driver exists purely to make divergence a test failure.

import { readFileSync } from 'node:fs';

import { MASTER_TABLE } from '../../hom-gui/src/engine/masterTable.js';
import { checkAllGuards } from '../../hom-gui/src/engine/guards.js';
import { computeVektronometry } from '../../hom-gui/src/engine/vektronometry.js';
import { computeIntrametric, computeDiameter } from '../../hom-gui/src/engine/intrametric.js';
import { buildExomatrix, computePhi, auditR1R5 } from '../../hom-gui/src/engine/exometric.js';
import { computeNormivektor } from '../../hom-gui/src/engine/normivektor.js';
import { aggregateString } from '../../hom-gui/src/engine/aggregametric.js';

const letters = MASTER_TABLE.map((e) => ({
  char: e.char,
  v18: e.v18,
  guards: Object.fromEntries(checkAllGuards(e.v18).map((g) => [g.id, g.pass])),
  vtm: (() => {
    const r = computeVektronometry(e.v18);
    return {
      norm2: r.norm2, theta: r.theta, U: r.U, rho: r.rho,
      AN: r.AN, AK: r.AK, AQ: r.AQ,
      rN: r.rN, rK: r.rK, rQ: r.rQ,
      normTheta: r.normTheta, normN: r.normN, normK: r.normK, normQ: r.normQ,
      pythagoras: r.pythagoras, alpha: r.alpha,
    };
  })(),
  exo: buildExomatrix(e.v18),
  phi: computePhi(buildExomatrix(e.v18)),
  audit: Object.fromEntries(auditR1R5(e.v18).map((r) => [r.id, r.pass])),
}));

// All 378 unordered pairs.
const pairs = [];
for (let i = 0; i < MASTER_TABLE.length; i++) {
  for (let j = i + 1; j < MASTER_TABLE.length; j++) {
    const a = MASTER_TABLE[i], b = MASTER_TABLE[j];
    const itm = computeIntrametric(a.v18, b.v18);
    const nmv = computeNormivektor(a.v18, b.v18);
    pairs.push({
      a: a.char, b: b.char,
      d2sq: itm.d2sq, d1: itm.d1, dH: itm.dH, inner: itm.inner,
      polarization: itm.polarization,
      deltaTheta2: nmv.deltaTheta2, deltaN2: nmv.deltaN2,
      deltaK2: nmv.deltaK2, deltaQ2: nmv.deltaQ2,
      totalNorm2: nmv.totalNorm2, decompValid: nmv.decompValid,
    });
  }
}

const STRINGS = ['بسم', 'الله', 'سبم', 'محمد', 'ا'];
const strings = STRINGS.map((text) => {
  const r = aggregateString(text, MASTER_TABLE);
  return {
    text, codex: r.codex, letterCount: r.letterCount,
    theta: r.theta, U: r.U, rho: r.rho, allPreserved: r.allPreserved,
  };
});

const { diameter, pair } = computeDiameter(MASTER_TABLE);

// Every canonical letter passes every guard, so the 28 rows above cannot tell
// a correct guard apart from one hardwired to `true`. The Python side feeds in
// synthetic vectors that violate each guard on purpose; these are scored here.
const probeInput = readFileSync(0, 'utf8').trim();
const probes = probeInput
  ? JSON.parse(probeInput).map((v18) => ({
      v18,
      guards: Object.fromEntries(checkAllGuards(v18).map((g) => [g.id, g.pass])),
      audit: Object.fromEntries(auditR1R5(v18).map((r) => [r.id, r.pass])),
      U: computeVektronometry(v18).U,
      rho: computeVektronometry(v18).rho,
      norm2: computeVektronometry(v18).norm2,
      exo: buildExomatrix(v18),
      phi: computePhi(buildExomatrix(v18)),
    }))
  : [];

process.stdout.write(
  JSON.stringify({ letters, pairs, strings, diameter, diameterPair: pair, probes })
);
