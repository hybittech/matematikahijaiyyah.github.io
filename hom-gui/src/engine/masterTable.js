// Complete Master Table: 28 letters × 18 components
// Canonical 18D ordering, identical to data/hm28.csv and core/master_table.py:
//   v18 = [Θ̂, Na,Nb,Nd, Kp,Kx,Ks,Ka,Kc, Qp,Qx,Qs,Qa,Qc, AN,AK,AQ, H*]
//         index  0   1  2  3   4  5  6  7  8   9 10 11 12 13   14 15 16   17
// U and ρ are derived (U = Qx+Qs+Qa+4·Qc, ρ = Θ̂−U), not stored.
// Source of truth: Master Table HM-28-v.1.0-HC18D.

const raw = [
  { char: 'ا', name: 'Alif',    v18: [0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0] },
  { char: 'ب', name: 'Ba',      v18: [2,0,0,1,0,1,0,0,0,1,0,0,0,0,1,1,1,0] },
  { char: 'ت', name: 'Ta',      v18: [2,2,0,0,0,1,0,0,0,1,0,0,0,0,2,1,1,0] },
  { char: 'ث', name: 'Tha',     v18: [2,3,0,0,0,1,0,0,0,1,0,0,0,0,3,1,1,0] },
  { char: 'ج', name: 'Jim',     v18: [3,0,1,0,0,1,0,0,0,1,0,0,0,0,1,1,1,0] },
  { char: 'ح', name: 'Ha',      v18: [3,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,1,0] },
  { char: 'خ', name: 'Kha',     v18: [3,1,0,0,0,1,0,0,0,1,0,0,0,0,1,1,1,0] },
  { char: 'د', name: 'Dal',     v18: [1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0] },
  { char: 'ذ', name: 'Dhal',    v18: [1,1,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0] },
  { char: 'ر', name: 'Ra',      v18: [1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0] },
  { char: 'ز', name: 'Zay',     v18: [1,1,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0] },
  { char: 'س', name: 'Sin',     v18: [4,0,0,0,0,0,0,0,0,1,2,0,0,0,0,0,3,0] },
  { char: 'ش', name: 'Shin',    v18: [4,3,0,0,0,0,0,0,0,1,2,0,0,0,3,0,3,0] },
  { char: 'ص', name: 'Sad',     v18: [6,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,2,0] },
  { char: 'ض', name: 'Dad',     v18: [6,1,0,0,0,0,0,0,0,1,0,0,0,1,1,0,2,0] },
  { char: 'ط', name: 'Tta',     v18: [4,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,1,0] },
  { char: 'ظ', name: 'Ththa',   v18: [4,1,0,0,0,0,1,0,0,0,0,0,0,1,1,1,1,0] },
  { char: 'ع', name: 'Ayn',     v18: [3,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,2,0] },
  { char: 'غ', name: 'Ghayn',   v18: [3,1,0,0,0,0,0,0,0,1,1,0,0,0,1,0,2,0] },
  { char: 'ف', name: 'Fa',      v18: [5,1,0,0,0,1,0,0,0,1,0,0,0,1,1,1,2,0] },
  { char: 'ق', name: 'Qaf',     v18: [6,2,0,0,0,0,0,0,0,1,0,0,0,1,2,0,2,0] },
  { char: 'ك', name: 'Kaf',     v18: [2,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,1] },
  { char: 'ل', name: 'Lam',     v18: [1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,1,0] },
  { char: 'م', name: 'Mim',     v18: [4,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,1,0] },
  { char: 'ن', name: 'Nun',     v18: [2,1,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,0] },
  { char: 'و', name: 'Waw',     v18: [5,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,2,0] },
  { char: 'هـ', name: 'Ha2',    v18: [8,0,0,0,0,0,0,0,1,0,0,0,0,2,0,1,2,0] },
  { char: 'ي', name: 'Ya',      v18: [3,0,0,2,0,0,0,0,0,1,1,0,0,0,2,0,2,0] },
];

export const MASTER_TABLE = raw.map((entry, idx) => ({
  ...entry,
  id: idx + 1,
  v14: entry.v18.slice(0, 14),
}));

export function getLetterByChar(char) {
  return MASTER_TABLE.find((l) => l.char === char) || null;
}

export function getAllLetters() {
  return MASTER_TABLE;
}
