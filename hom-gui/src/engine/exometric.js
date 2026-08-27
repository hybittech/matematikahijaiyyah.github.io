// EXM — Exometric: constrained matrix, energy, audit

export function buildExomatrix(v18) {
  const theta = v18[0];
  const Na = v18[1], Nb = v18[2], Nd = v18[3];
  const Kp = v18[4], Kx = v18[5], Ks = v18[6], Ka = v18[7], Kc = v18[8];
  const Qp = v18[9], Qx2 = v18[10], Qs = v18[11], Qa = v18[12], Qc = v18[13];
  const AN = v18[14], AK = v18[15], AQ = v18[16];
  const Hstar = v18[17];

  const U = Qx2 + Qs + Qa + 4 * Qc;
  const rho = theta - U;

  return [
    [theta, U, rho, 0, 0],
    [Na, Nb, Nd, 0, AN],
    [Kp, Kx, Ks, Ka, Kc],
    [Qp, Qx2, Qs, Qa, Qc],
    [Hstar, 0, 0, AK, AQ],
  ];
}

export function computePhi(matrix) {
  let sum = 0;
  for (let r = 0; r < 5; r++) {
    for (let c = 0; c < 5; c++) {
      sum += matrix[r][c] ** 2;
    }
  }
  return sum;
}

export function auditR1R5(v18) {
  const theta = v18[0];
  const Na = v18[1], Nb = v18[2], Nd = v18[3];
  const Kp = v18[4], Kx = v18[5], Ks = v18[6], Ka = v18[7], Kc = v18[8];
  const Qp = v18[9], Qx2 = v18[10], Qs = v18[11], Qa = v18[12], Qc = v18[13];
  const AN = v18[14], AK = v18[15], AQ = v18[16];

  const U = Qx2 + Qs + Qa + 4 * Qc;
  const rho = theta - U;

  return [
    { id: 'R1', pass: theta === U + rho, formula: `Θ̂=${theta} = U(${U}) + ρ(${rho})` },
    { id: 'R2', pass: AN === Na + Nb + Nd, formula: `A_N=${AN} = ${Na}+${Nb}+${Nd}` },
    { id: 'R3', pass: AK === Kp + Kx + Ks + Ka + Kc, formula: `A_K=${AK} = Σ K_j` },
    { id: 'R4', pass: AQ === Qp + Qx2 + Qs + Qa + Qc, formula: `A_Q=${AQ} = Σ Q_j` },
    { id: 'R5', pass: U === Qx2 + Qs + Qa + 4 * Qc, formula: `U=${U} = ${Qx2}+${Qs}+${Qa}+4·${Qc}` },
  ];
}
