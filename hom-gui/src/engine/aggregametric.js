// AGM — Aggregametric: structured accumulation on strings

export function aggregateString(text, masterTable) {
  const chars = [...text].filter((c) => c.trim());
  const found = [];
  const notFound = [];

  const sum = new Array(18).fill(0);

  chars.forEach((ch) => {
    const entry = masterTable.find((l) => l.char === ch);
    if (entry) {
      found.push(entry);
      entry.v18.forEach((val, i) => {
        sum[i] += val;
      });
    } else {
      notFound.push(ch);
    }
  });

  // Verify identity preservation
  const theta = sum[0];
  const Qx = sum[10], Qs = sum[11], Qa = sum[12], Qc = sum[13];
  const U = Qx + Qs + Qa + 4 * Qc;
  const rho = theta - U;

  const AN = sum[14];
  const sumN = sum[1] + sum[2] + sum[3];
  const AK = sum[15];
  const sumK = sum[4] + sum[5] + sum[6] + sum[7] + sum[8];
  const AQ = sum[16];
  const sumQ = sum[9] + sum[10] + sum[11] + sum[12] + sum[13];

  return {
    text,
    letterCount: found.length,
    unknownChars: notFound,
    codex: sum,
    theta,
    U,
    rho,
    identityPreserved: theta === U + rho && rho >= 0,
    g1: AN === sumN,
    g2: AK === sumK,
    g3: AQ === sumQ,
    allPreserved: AN === sumN && AK === sumK && AQ === sumQ && theta === U + rho && rho >= 0,
  };
}
