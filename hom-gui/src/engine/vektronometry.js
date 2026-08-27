// VTM — Vektronometry: composition metrics

export function computeVektronometry(v18) {
  const AN = v18[14], AK = v18[15], AQ = v18[16];
  const Atotal = AN + AK + AQ;

  const rN = Atotal > 0 ? AN / Atotal : 0;
  const rK = Atotal > 0 ? AK / Atotal : 0;
  const rQ = Atotal > 0 ? AQ / Atotal : 0;

  const theta = v18[0];
  const Qx = v18[10], Qs = v18[11], Qa = v18[12], Qc = v18[13];
  const U = Qx + Qs + Qa + 4 * Qc;
  const rho = theta - U;

  const rU = theta > 0 ? U / theta : 0;
  const rRho = theta > 0 ? rho / theta : 0;
  const rLoop = theta > 0 ? (4 * Qc) / theta : 0;

  // Norm² of v14
  const v14 = v18.slice(0, 14);
  const norm2 = v14.reduce((s, x) => s + x * x, 0);

  // Subruang norms
  const normTheta = v18[0] ** 2;
  const normN = v18[1] ** 2 + v18[2] ** 2 + v18[3] ** 2;
  const normK = v18.slice(4, 9).reduce((s, x) => s + x * x, 0);
  const normQ = v18.slice(9, 14).reduce((s, x) => s + x * x, 0);
  const pythagoras = normTheta + normN + normK + normQ === norm2;

  // Angle α
  const alpha = AK === 0 && AQ === 0 ? 0 : AK === 0 ? 90 : (Math.atan2(AQ, AK) * 180) / Math.PI;

  return {
    AN, AK, AQ, Atotal,
    rN, rK, rQ,
    theta, U, rho, rU, rRho, rLoop,
    norm2, normTheta, normN, normK, normQ,
    pythagoras, alpha,
    type: getType(rN, rK, rQ),
  };
}

function getType(rN, rK, rQ) {
  if (rK === 1) return 'Garis murni';
  if (rQ === 1) return 'Kurva murni';
  if (Math.abs(rN - 1 / 3) < 0.01 && Math.abs(rK - 1 / 3) < 0.01) return 'Seimbang N-K-Q';
  if (rN > 0.5) return 'Dominasi titik';
  if (rQ > 0.5) return 'Dominasi kurva';
  return 'Campuran';
}
