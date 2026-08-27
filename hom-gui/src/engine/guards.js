// Guard System G1–G4 (structural) + T1–T2 (topological)
//
// Canonical v18 ordering — identical to data/hm28.csv and core/master_table.py:
//   [Θ̂, Na,Nb,Nd, Kp,Kx,Ks,Ka,Kc, Qp,Qx,Qs,Qa,Qc, AN,AK,AQ, H*]
//     0   1  2  3   4  5  6  7  8   9 10 11 12 13   14 15 16   17

export function guardG1(v18) {
  // AN = Na + Nb + Nd
  const [, Na, Nb, Nd] = v18;
  const AN = v18[14];
  return { id: 'G1', pass: AN === Na + Nb + Nd, formula: `A_N=${AN} = ${Na}+${Nb}+${Nd}` };
}

export function guardG2(v18) {
  // AK = Kp + Kx + Ks + Ka + Kc
  const Kp = v18[4], Kx = v18[5], Ks = v18[6], Ka = v18[7], Kc = v18[8];
  const AK = v18[15];
  const sum = Kp + Kx + Ks + Ka + Kc;
  return { id: 'G2', pass: AK === sum, formula: `A_K=${AK} = ${Kp}+${Kx}+${Ks}+${Ka}+${Kc}` };
}

export function guardG3(v18) {
  // AQ = Qp + Qx + Qs + Qa + Qc
  const Qp = v18[9], Qx = v18[10], Qs = v18[11], Qa = v18[12], Qc = v18[13];
  const AQ = v18[16];
  const sum = Qp + Qx + Qs + Qa + Qc;
  return { id: 'G3', pass: AQ === sum, formula: `A_Q=${AQ} = ${Qp}+${Qx}+${Qs}+${Qa}+${Qc}` };
}

export function guardG4(v18) {
  // ρ = Θ̂ − U ≥ 0
  const theta = v18[0];
  const Qx = v18[10], Qs = v18[11], Qa = v18[12], Qc = v18[13];
  const U = Qx + Qs + Qa + 4 * Qc;
  const rho = theta - U;
  return { id: 'G4', pass: rho >= 0, formula: `ρ=${rho} = ${theta}−${U} ≥ 0` };
}

export function guardT1(v18) {
  // Ks > 0 ⇒ Qc ≥ 1
  const Ks = v18[6], Qc = v18[13];
  return { id: 'T1', pass: Ks === 0 || Qc >= 1, formula: `Ks=${Ks} > 0 ⇒ Qc=${Qc} ≥ 1` };
}

export function guardT2(v18) {
  // Kc > 0 ⇒ Qc ≥ 1
  const Kc = v18[8], Qc = v18[13];
  return { id: 'T2', pass: Kc === 0 || Qc >= 1, formula: `Kc=${Kc} > 0 ⇒ Qc=${Qc} ≥ 1` };
}

export function checkAllGuards(v18) {
  return [guardG1(v18), guardG2(v18), guardG3(v18), guardG4(v18), guardT1(v18), guardT2(v18)];
}

export function allGuardsPass(v18) {
  return checkAllGuards(v18).every((g) => g.pass);
}
