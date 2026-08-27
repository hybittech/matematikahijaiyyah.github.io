import { Link } from 'react-router-dom';
import HijaiyyahScene from '../components/HijaiyyahScene';
import FormulaBlock from '../components/FormulaBlock';
import GlassPanel from '../components/GlassPanel';
import { useLocale } from '../store/useLocale';
import { Languages, Layers, ShieldCheck, Cpu } from 'lucide-react';

/* ──────────── tiny helpers ──────────── */
const colors = {
  accent: '#00d4ff',
  gold: '#d4af37',
  green: '#00c853',
  purple: '#b388ff',
  red: '#ff5252',
  blue: '#448aff',
  muted: '#6b6b80',
  text: '#e0e0e8',
  bg: '#0a0a0f',
  panel: '#12121a',
  border: '#1e1e2e',
};

/* ──────────── Connector SVG ──────────── */
function ArrowDown({ height = 28, color = 'currentColor' }) {
  return (
    <svg width="12" height={height} className="mx-auto block" style={{ color }}>
      <line x1="6" y1="0" x2="6" y2={height - 6} stroke="currentColor" strokeWidth="1.5" />
      <polygon points={`2,${height - 6} 10,${height - 6} 6,${height}`} fill="currentColor" />
    </svg>
  );
}

/* ──────────── Node Box ──────────── */
function NodeBox({ label, sub, formula, color, borderColor, bgColor, small, className = '', glow }) {
  return (
    <div
      className={`framework-node rounded-lg border text-center transition-all ${className} ${glow ? 'shadow-lg' : ''}`}
      style={{
        borderColor,
        backgroundColor: bgColor,
        boxShadow: glow ? `0 0 20px ${borderColor}40` : undefined,
      }}
    >
      <div
        className={`font-bold font-mono ${small ? 'text-[10px] px-2 py-1' : 'text-xs px-3 py-2'}`}
        style={{ color }}
      >
        {label}
      </div>
      {sub && (
        <div className="text-[9px] text-hom-muted px-2 pb-1.5 -mt-0.5">{sub}</div>
      )}
      {formula && (
        <div className="text-[9px] px-2 pb-2 opacity-80">
          <FormulaBlock tex={formula} />
        </div>
      )}
    </div>
  );
}


const stats = [
  { label: 'Letters', value: '28', sub: 'Canonical Hijaiyyah', icon: Languages, color: 'text-hom-accent' },
  { label: 'Dimensions', value: '18', sub: 'Integer Vector Space', icon: Layers, color: 'text-hom-gold' },
  { label: 'Tests', value: '1,628', sub: 'All PASS · 0 FAIL', icon: ShieldCheck, color: 'text-hom-green' },
  { label: 'ROM', value: '252', sub: 'Bytes (nibble-packed)', icon: Cpu, color: 'text-hom-purple' },
];

const operations = [
  {
    code: 'VTM',
    name: 'Vektronometry',
    tagline: 'Composition Metrics',
    color: 'hom-accent',
    borderColor: 'border-hom-accent/30',
    bgColor: 'bg-hom-accent/5',
    textColor: 'text-hom-accent',
    glowColor: 'shadow-glow',
    question: 'What is a letter made of?',
    identity: 'r_N + r_K + r_Q = 1',
    description:
      'Vektronometry measures the internal composition of each letter — what proportion is dots (N), lines (K), and curves (Q). It decomposes every letter vector into four orthogonal subspaces (Θ, N, K, Q) and verifies the Pythagorean decomposition theorem. The compositional profile uniquely characterizes each letter\'s geometric DNA.',
    capabilities: [
      'Primitive ratio analysis: rN, rK, rQ per letter',
      'Turning ratio decomposition: rU + rρ = 1',
      'Pythagorean norm decomposition across 4 subspaces',
      'Compositional angle α = arctan(AQ / AK)',
      'Loop ratio measurement for closed-path letters',
      'Cosine similarity between any two letters (always ≥ 0)',
    ],
    example: 'Letter ب: rN=0.333, rK=0.333, rQ=0.333 → Balanced (equal parts dot, line, curve)',
  },
  {
    code: 'NMV',
    name: 'Normivektor',
    tagline: 'Norm-Difference Diagnostics',
    color: 'hom-gold',
    borderColor: 'border-hom-gold/30',
    bgColor: 'bg-hom-gold/5',
    textColor: 'text-hom-gold',
    glowColor: 'shadow-glow-gold',
    question: 'How do two letters differ?',
    identity: '‖Δ‖² = ΔΘ² + ‖ΔN‖² + ‖ΔK‖² + ‖ΔQ‖²',
    description:
      'Normivektor computes the structured difference between any two letters — not just "how much" they differ (scalar distance), but precisely "where" the difference lies (which geometric layer). The norm of the difference vector decomposes into four orthogonal contributions, enabling layer-by-layer diagnostics. This is discrete finite difference, not continuous calculus.',
    capabilities: [
      'Total difference operator Δ(h₁, h₂) ∈ ℤ¹⁴',
      'Per-layer decomposition: Θ, N, K, Q contributions',
      'Nuqṭah gradient ∇N: tracks dot-change patterns',
      'Discovery: 8/9 dot-variants differ only in ascender zone (Na)',
      'Second-order difference Δ² (acceleration detection)',
      'Turning budget gradient ∇Q U = (0, 1, 1, 1, 4) — constant',
    ],
    example: 'ح → خ: 100% difference in N-layer (one dot added above). Zero leakage to K or Q layers.',
  },
  {
    code: 'AGM',
    name: 'Aggregametric',
    tagline: 'Structured String Accumulation',
    color: 'hom-green',
    borderColor: 'border-hom-green/30',
    bgColor: 'bg-hom-green/5',
    textColor: 'text-hom-green',
    glowColor: 'shadow-glow-green',
    question: 'What is the total codex of a word?',
    identity: 'Σ_uv = Σ_u + Σ_v',
    description:
      'Aggregametric accumulates codex vectors across strings (words, sentences) with a critical guarantee: all algebraic identities from Chapter I are preserved at the string level. Guards G1–G4, turning decomposition, and non-negativity of ρ survive aggregation. This is discrete accumulation, not continuous integration — the notation uses Σ, not ∫.',
    capabilities: [
      'Fundamental Additivity Theorem: Σ(uv) = Σ(u) + Σ(v)',
      'Anagram Invariance: permutations yield identical codex',
      'Full identity preservation: Θ̂ = U + ρ on strings',
      'Cumulative trajectory S_k(w) encodes letter ordering',
      'String centroid v̄(w) = (1/n)·Σ_w — "average letter"',
      'Energy bound: Σ_w Φ ≥ 2n (minimum energy per letter)',
    ],
    example: '"بسم": Σ_w Θ̂=10, Σ_w U=6, Σ_w ρ=4 → 10=6+4 ✓ (identity preserved)',
  },
  {
    code: 'ITM',
    name: 'Intrametric',
    tagline: 'Internal Distance Geometry',
    color: 'hom-purple',
    borderColor: 'border-hom-purple/30',
    bgColor: 'bg-hom-purple/5',
    textColor: 'text-hom-purple',
    glowColor: '',
    question: 'How far apart are two letters?',
    identity: 'd² = ‖h₁‖² + ‖h₂‖² − 2⟨h₁,h₂⟩',
    description:
      'Intrametric establishes a formal metric space (ℋ₂₈, d₂) on the alphabet — with rigorously verified axioms (identity requires injectivity from Chapter I), diameter, centroid, and nearest neighbors all explicitly characterized. The metric captures visual similarity: the closest letter pairs (d₂=1) are exactly the dot-variant pairs that look most alike.',
    capabilities: [
      'Three metrics: Euclidean d₂, Manhattan d₁, Hamming dH',
      'Full metric space axioms M1–M4 verified (M1 needs injectivity!)',
      'Gram Matrix G = M₁₄·M₁₄ᵀ ∈ ℕ₀²⁸ˣ²⁸, rank = 14',
      'Diameter = √70 ≈ 8.367, uniquely achieved by (ا, هـ)',
      'All 6 nearest-neighbor pairs at d₂=1 are dot-variants',
      'Alif (ا) is orthogonal to all 27 other letters',
    ],
    example: 'ا ⊥ all others (support disjoint). Nearest pairs: ح↔خ, ص↔ض, ط↔ظ (all d₂=1)',
  },
  {
    code: 'EXM',
    name: 'Exometric',
    tagline: 'External Consistency Audit',
    color: 'hom-red',
    borderColor: 'border-hom-red/30',
    bgColor: 'bg-hom-red/5',
    textColor: 'text-hom-red',
    glowColor: '',
    question: 'Is the data internally consistent?',
    identity: 'R1–R5 ; Φ(h) > ‖v₁₄(h)‖²',
    description:
      'Exometric builds a 5×5 constrained matrix (Letter Exomatrix) for each letter and validates it against five interlocking audit relations R1–R5. A single data corruption triggers an average of 2.3 cascading failures — providing redundant detection with location information. The Frobenius Energy Index Φ(h) is strictly greater than the codex norm for all 28 letters.',
    capabilities: [
      'Letter Exomatrix ℰ(h): 5×5 matrix with 15 degrees of freedom',
      'Five audit relations R1–R5 (140 total checks: 28×5)',
      'Cascading failure analysis: 1 corruption → ~2.3 failures',
      'Frobenius Energy Φ(h) = ‖ℰ(h)‖²F',
      'Strict Energy-Norm Inequality: Φ > ‖v₁₄‖² for all 28 letters',
      'Unique reconstruction: ℰ(h₁) = ℰ(h₂) ⟹ h₁ = h₂',
    ],
    example: 'Corrupt Qc(هـ) from 2→3: R1 FAIL + R4 FAIL + R5 FAIL (3 cascading failures detected)',
  },
];

export default function Landing() {
  const { t } = useLocale();

  return (
    <div className="space-y-16">
      {/* ═══════════════ HERO ═══════════════ */}
      <section className="relative min-h-[70vh] flex flex-col items-center pt-8 pb-20">
        <div className="absolute inset-0 -z-10">
          <HijaiyyahScene />
        </div>

        {/* CENTRED QUOTE */}
        <div className="relative z-10 w-full max-w-4xl mx-auto px-4 md:px-8 text-center mb-12">
           <p className="text-hom-green font-bold text-xs md:text-sm tracking-wide leading-relaxed glass inline-block px-6 py-3.5 rounded-2xl border border-hom-green/30 shadow-[0_0_15px_rgba(0,255,128,0.15)] uppercase">
             {t('landing.hero.quote')}
           </p>
        </div>

        <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-8 md:gap-12 px-4 md:px-8">
          {/* ─── Left: Text Content ─── */}
          <div className="flex-1 min-w-0">
            <div className="mb-10">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-[10px] font-mono px-2 py-1 rounded-full bg-hom-accent/10 text-hom-accent border border-hom-accent/20">
                  HM-28-v1.2-HC18D
                </span>
                <span className="text-[10px] font-mono px-2 py-1 rounded-full bg-hom-green/10 text-hom-green border border-hom-green/20">
                  1,628 PASS · 0 FAIL
                </span>
              </div>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-4">
              <span className="neon-text">{t('Hijaiyyah')}</span>
              <br />
              <span className="text-hom-text">{t('Mathematics')}</span>
            </h1>

            <p className="text-hom-muted text-sm md:text-base leading-relaxed mb-4 max-w-lg">
              {t('A formal mathematical system mapping 28 canonical Hijaiyyah letters to 18-dimensional integer vectors through four discrete geometric invariants — establishing ')}
              <span className="text-hom-green font-semibold">hybit</span>
              {t(' as the third computational paradigm.')}
            </p>

            <FormulaBlock
              tex="h \in \mathcal{H}_{28} \xrightarrow{\text{Measure}} \mathbf{H}(h) \xrightarrow{\text{Map}} v_{18}(h) \in \mathbb{N}_0^{18} \xrightarrow{\text{Name}} h^*"
              display
              align="left"
              className="!mx-0"
            />

            <div className="flex flex-wrap gap-3 mt-6">
              <Link
                to="/explorer"
                className="px-5 py-2.5 rounded-lg bg-hom-accent text-black font-semibold text-sm hover:shadow-glow transition-all"
              >
                {t('Start Exploring →')}
              </Link>
              <Link
                to="/lab"
                className="px-5 py-2.5 rounded-lg border border-hom-border text-hom-text text-sm hover:border-hom-accent/50 transition-all"
              >
                {t('Open Lab')}
              </Link>
              <a
                href="https://github.com/hybittech/HOM"
                target="_blank"
                rel="noopener noreferrer"
                className="px-5 py-2.5 rounded-lg border border-hom-border text-hom-muted text-sm hover:border-hom-gold/50 hover:text-hom-gold transition-all flex items-center gap-2"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                {t('GitHub')}
              </a>
            </div>
          </div>

          {/* ─── Right: Arabic Calligraphy Logo ─── */}
          <div className="flex-shrink-0 flex items-center justify-center md:justify-end w-full md:w-auto translate-x-3 md:translate-x-8 lg:translate-x-16">
            <video
              src={import.meta.env.BASE_URL + 'hybit_vid_02.mp4'}
              autoPlay
              loop
              muted
              playsInline
              className="h-64 md:h-96 lg:h-[32rem] w-auto select-none pointer-events-none"
            />
          </div>
        </div>
      </section>

      {/* ═══════════════ EXTENDED DEFINITION BLOCK - TRUE EDGE-TO-EDGE ═══════════════ */}
      <section className="w-full py-20 border-t border-b border-hom-border/10 bg-hom-panel/10">
        <div className="w-full px-4 md:px-8 max-w-7xl mx-auto">
          <p className="text-hom-text/90 text-sm md:text-lg leading-relaxed mb-8 text-justify">
            {t('landing.hero.intro.part1')}
          </p>

          <div className="mb-8 w-full overflow-x-auto rounded-2xl bg-black/40 border border-hom-border/40 p-5 md:p-8 flex items-center justify-center shadow-[inset_0_4px_20px_rgba(0,0,0,0.5)] scrollbar-thin scrollbar-thumb-hom-border scrollbar-track-transparent">
            <FormulaBlock
              tex={t('landing.hero.intro.tex')}
              display
              className="!m-0 text-[10px] sm:text-xs md:text-sm lg:text-base w-max mx-auto text-hom-green drop-shadow-[0_0_8px_rgba(0,255,128,0.25)]"
            />
          </div>

          <p className="text-hom-text/90 text-sm md:text-lg leading-relaxed mb-16 text-justify">
            {t('landing.hero.intro.part2a')}
            <span className="inline-flex items-center mx-2 translate-y-0 text-hom-accent font-semibold tracking-wide">
              Σ-MV(<span className="font-serif italic font-bold">ℋ</span><sub className="text-[0.6em]">28</sub>)
            </span>
            {t('landing.hero.intro.part2b')}
          </p>
        </div>

        <div className="w-full px-4 md:px-0"> {/* Minimal padding for mobile, zero for desktop edge-to-edge */}

          {/* 5 Formal Operations Grid */}
          {(() => {
            const opColors = [
              { border: 'border-hom-accent/50', glow: 'rgba(0,212,255,0.25)', num: 'bg-hom-accent/20 text-hom-accent border-hom-accent/40', title: 'text-hom-accent', shadow: '0 0 20px rgba(0,212,255,0.15)' },
              { border: 'border-hom-gold/50', glow: 'rgba(212,175,55,0.25)', num: 'bg-hom-gold/20 text-hom-gold border-hom-gold/40', title: 'text-hom-gold', shadow: '0 0 20px rgba(212,175,55,0.15)' },
              { border: 'border-hom-green/50', glow: 'rgba(0,200,83,0.25)', num: 'bg-hom-green/20 text-hom-green border-hom-green/40', title: 'text-hom-green', shadow: '0 0 20px rgba(0,200,83,0.15)' },
              { border: 'border-hom-purple/50', glow: 'rgba(179,136,255,0.25)', num: 'bg-hom-purple/20 text-hom-purple border-hom-purple/40', title: 'text-hom-purple', shadow: '0 0 20px rgba(179,136,255,0.15)' },
              { border: 'border-hom-red/50', glow: 'rgba(255,82,82,0.25)', num: 'bg-hom-red/20 text-hom-red border-hom-red/40', title: 'text-hom-red', shadow: '0 0 20px rgba(255,82,82,0.15)' },
            ];
            return (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4 mb-16 px-4 md:px-0">
                {[1, 2, 3, 4, 5].map((num) => {
                  const c = opColors[num - 1];
                  return (
                    <div
                      key={num}
                      className={`relative p-6 rounded-2xl border ${c.border} bg-hom-panel/60 backdrop-blur-xl transition-all duration-500 group flex flex-col items-center text-center overflow-hidden cursor-default hover:scale-[1.04] hover:-translate-y-1`}
                      style={{ boxShadow: `0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05), ${c.shadow}` }}
                      onMouseEnter={(e) => e.currentTarget.style.boxShadow = `0 12px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.08), 0 0 35px ${c.glow}`}
                      onMouseLeave={(e) => e.currentTarget.style.boxShadow = `0 8px 32px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05), ${c.shadow}`}
                    >
                      {/* Number Badge */}
                      <span className={`flex items-center justify-center w-10 h-10 rounded-xl ${c.num} border text-sm font-bold font-mono mb-4 shadow-lg`}>
                        {num}
                      </span>
                      {/* Title */}
                      <h3 className={`text-sm md:text-base font-bold uppercase tracking-widest ${c.title} mb-3`} style={{ fontFamily: "'Orbitron', sans-serif", textShadow: `0 0 12px ${c.glow}` }}>
                        {t(`landing.hero.op${num}_title`)}
                      </h3>
                      {/* Divider */}
                      <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent mb-4" />
                      {/* Description */}
                      <p className="text-xs md:text-sm text-hom-text/80 leading-relaxed">
                        {t(`landing.hero.op${num}_desc`)}
                      </p>
                    </div>
                  );
                })}
              </div>
            );
          })()}

          <div className="space-y-10 px-4 md:px-0">
            <p className="text-hom-text/80 text-sm md:text-lg leading-relaxed text-justify">
              {t('landing.hero.mid')}
            </p>

            <div className="relative pt-12">
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-hom-gold/40 to-transparent" />
              <p className="text-hom-gold/90 font-medium text-sm md:text-xl leading-relaxed text-justify italic">
                {t('landing.hero.conclusion')}
              </p>
            </div>
          </div>
        </div>
      </section>

      <div className="max-w-7xl mx-auto space-y-16 px-4 md:px-0">

      {/* ═══════════════ STATS ═══════════════ */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s) => (
          <GlassPanel key={s.label} glow className="relative overflow-hidden group">
            <div className="absolute top-3 right-3 opacity-10 group-hover:opacity-30 transition-opacity">
              <s.icon size={48} className={s.color} />
            </div>
            <div className="flex items-center gap-3 mb-2">
              <s.icon size={20} className={s.color} />
              <div className="text-3xl font-bold neon-text font-mono">
                {s.value}
              </div>
            </div>
            <div className="text-sm text-hom-text mt-1">{t(s.label)}</div>
            <div className="text-[10px] text-hom-muted mt-0.5">{t(s.sub)}</div>
          </GlassPanel>
        ))}
      </section>

      {/* ═══════════════ PARADIGM ═══════════════ */}
      <section>
        <GlassPanel
          title={t('Three Computational Paradigms')}
          badge={t('Proven VF — Birkhoff Variety Analysis')}
          glow="gold"
        >
          <FormulaBlock
            tex="\color{white}{\text{bit} \;\oplus\; \text{qubit} \;\oplus\; \text{hybit} \;=\; \text{three fundamental paradigms}}"
            display
          />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
            {[
              {
                name: 'Bit',
                struct: '\\mathbb{F}_2',
                desc: 'Field (2 elements)',
                domain: 'Boolean logic, switching',
                validation: 'None',
                color: 'text-hom-gold',
              },
              {
                name: 'Qubit',
                struct: '\\mathbb{C}^2',
                desc: 'Hilbert Space (continuous)',
                domain: 'Quantum simulation',
                validation: 'Partial, destructive',
                color: 'text-hom-purple',
              },
              {
                name: 'Hybit',
                struct: '\\mathcal{V} \\subset \\mathbb{N}_0^{18}',
                desc: 'Constrained Monoid (discrete)',
                domain: 'Structured data + audit',
                validation: 'Full, O(1), non-destructive',
                color: 'text-hom-green',
              },
            ].map((p) => (
              <div
                key={p.name}
                className="text-center p-5 rounded-xl bg-hom-bg/50 border border-hom-border/30"
              >
                <div className={`text-xl font-bold ${p.color}`}>{t(p.name)}</div>
                <div className="my-2">
                  <FormulaBlock tex={p.struct} />
                </div>
                <div className="text-xs text-hom-text">{t(p.desc)}</div>
                <div className="text-[10px] text-hom-muted mt-2">
                  {t('Domain: ')}{t(p.domain)}
                </div>
                <div className="text-[10px] text-hom-muted">
                  {t('Validation: ')}{t(p.validation)}
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center text-[10px] text-hom-muted">
            {t('Mutually irreducible: ')}<span className="text-hom-green">Hybit</span> ↛ <span className="text-hom-gold">Bit</span>, <span className="text-hom-green">Hybit</span> ↛ Qubit, <span className="text-hom-gold">Bit</span> ↛ <span className="text-hom-green">Hybit</span>
            {t('(Theorems 3.8.1–3.8.3)')}
          </div>
        </GlassPanel>
      </section>

      {/* ═══════════════ KEY IDENTITIES & THEOREMS ═══════════════ */}
      <section>
        <GlassPanel
          title={t('Key Identities & Theorems')}
          badge={t('12 Proven Results')}
          glow
        >
          <p className="text-sm text-hom-muted mb-6">
            {t('The complete set of identities and theorems that form the mathematical backbone of Hijaiyyah Mathematics. Each result is rigorously verified across all 28 letters.')}
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-hom-border/40">
                  <th className="text-left py-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-hom-muted w-8">#</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-hom-muted">{t('Result')}</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-hom-muted">{t('Formula')}</th>
                  <th className="text-center py-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-hom-muted w-16">{t('Label')}</th>
                  <th className="text-left py-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-hom-muted w-28">{t('Source')}</th>
                </tr>
              </thead>
              <tbody>
                {[
                  {
                    id: 1,
                    result: 'Turning Decomposition',
                    tex: '\\hat{\\Theta}(h) = U(h) + \\rho(h)',
                    label: 'DP',
                    labelColor: 'text-hom-accent',
                    labelBg: 'bg-hom-accent/10 border-hom-accent/20',
                    source: '',
                  },
                  {
                    id: 2,
                    result: 'Non-Negativity of Residue',
                    tex: '\\rho(h) \\geq 0 \\;\\; \\text{for 28/28 letters}',
                    label: 'CC',
                    labelColor: 'text-hom-green',
                    labelBg: 'bg-hom-green/10 border-hom-green/20',
                    source: '',
                  },
                  {
                    id: 3,
                    result: 'Mod-4 Theorem',
                    tex: '\\text{MainPath closed} \\;\\Rightarrow\\; \\hat{\\Theta} \\equiv 0 \\pmod{4}',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                  {
                    id: 4,
                    result: 'MainPath Uniqueness',
                    tex: '\\exists!\\; \\gamma_h \\;\\text{for each}\\; h \\in \\mathcal{H}_{28}',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                  {
                    id: 5,
                    result: 'Codex Injectivity',
                    tex: 'v_{18}(h_1) = v_{18}(h_2) \\;\\Rightarrow\\; h_1 = h_2 \\;\\text{on}\\; \\mathcal{H}_{28}',
                    label: 'CC',
                    labelColor: 'text-hom-green',
                    labelBg: 'bg-hom-green/10 border-hom-green/20',
                    source: 'Claim',
                  },
                  {
                    id: 6,
                    result: 'Vektronometry Identity',
                    tex: 'r_N(h) + r_K(h) + r_Q(h) = 1 \\;\\text{for 28/28}',
                    label: 'DP+CC',
                    labelColor: 'text-hom-accent',
                    labelBg: 'bg-hom-accent/10 border-hom-accent/20',
                    source: '',
                  },
                  {
                    id: 7,
                    result: 'Vektronometry Pythagorean',
                    tex: '\\|h\\|^2 = \\|\\Pi_\\Theta\\|^2 + \\|\\Pi_N\\|^2 + \\|\\Pi_K\\|^2 + \\|\\Pi_Q\\|^2',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                  {
                    id: 8,
                    result: 'Normivektor Identity',
                    tex: '\\|\\Delta\\|^2 = \\Delta_\\Theta^2 + \\|\\Delta_N\\|^2 + \\|\\Delta_K\\|^2 + \\|\\Delta_Q\\|^2',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                  {
                    id: 9,
                    result: 'Aggregametric Additivity',
                    tex: '\\Sigma_{uv}\\vec{h} = \\Sigma_u\\vec{h} + \\Sigma_v\\vec{h}',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                  {
                    id: 10,
                    result: 'Intrametric Polarization Identity',
                    tex: 'd^2 = \\|h_1\\|^2 + \\|h_2\\|^2 - 2\\langle h_1, h_2 \\rangle',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: 'Prop. 2.38.1',
                  },
                  {
                    id: 11,
                    result: 'Energy-Norm Inequality',
                    tex: '\\Phi(h) > \\|v_{14}(h)\\|^2 \\;\\text{strict for 28/28}',
                    label: 'VF+CC',
                    labelColor: 'text-hom-purple',
                    labelBg: 'bg-hom-purple/10 border-hom-purple/20',
                    source: '',
                  },
                  {
                    id: 12,
                    result: 'Mutual Irreducibility',
                    tex: '\\color{#d4af37}{\\mathbb{F}_2} \\neq \\color{#00c853}{\\mathcal{V}} \\neq \\mathbb{C}^2 \\;\\text{(three distinct algebraic varieties)}',
                    label: 'VF',
                    labelColor: 'text-hom-gold',
                    labelBg: 'bg-hom-gold/10 border-hom-gold/20',
                    source: '',
                  },
                ].map((row, i) => (
                  <tr
                    key={row.id}
                    className={`border-b border-hom-border/10 hover:bg-hom-accent/[0.03] transition-colors ${
                      i % 2 === 0 ? 'bg-hom-bg/30' : ''
                    }`}
                  >
                    <td className="py-3 px-3 font-mono text-xs text-hom-muted">{row.id}</td>
                    <td className="py-3 px-3 text-xs text-hom-text font-medium whitespace-nowrap">{t(row.result)}</td>
                    <td className="py-3 px-3">
                      <FormulaBlock tex={row.tex} />
                    </td>
                    <td className="py-3 px-3 text-center">
                      <span className={`text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full border ${row.labelBg} ${row.labelColor}`}>
                        {row.label}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-[10px] text-hom-muted font-mono">{t(row.source)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-hom-accent/5 border border-hom-accent/15 text-center">
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-hom-accent/10 border border-hom-accent/20 text-hom-accent">DP</span>
              <div className="text-[10px] text-hom-muted mt-2">{t('Decomposition Property')}</div>
              <div className="text-[10px] text-hom-text/60">{t('Structural splitting of invariants')}</div>
            </div>
            <div className="p-3 rounded-lg bg-hom-green/5 border border-hom-green/15 text-center">
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-hom-green/10 border border-hom-green/20 text-hom-green">CC</span>
              <div className="text-[10px] text-hom-muted mt-2">{t('Computational Check')}</div>
              <div className="text-[10px] text-hom-text/60">{t('Verified exhaustively on all 28 letters')}</div>
            </div>
            <div className="p-3 rounded-lg bg-hom-gold/5 border border-hom-gold/15 text-center">
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-hom-gold/10 border border-hom-gold/20 text-hom-gold">VF</span>
              <div className="text-[10px] text-hom-muted mt-2">{t('Verified Formal')}</div>
              <div className="text-[10px] text-hom-text/60">{t('Proven theorem with formal proof')}</div>
            </div>
          </div>
        </GlassPanel>
      </section>

      {/* ═══════════════ FIVE OPERATIONS — DETAILED ═══════════════ */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">
            {t('Metrik-Vektorial Operations System')}
          </h2>
          <p className="text-sm text-hom-muted mt-1">
            {t('Five formal operations built on three pillars: ')}
            <span className="text-hom-accent">{t('Vector')}</span> +{' '}
            <span className="text-hom-gold">{t('Norm')}</span> +{' '}
            <span className="text-hom-green">{t('Metric')}</span>
            {t(' — each answering a fundamentally different question about letter structure.')}
          </p>
        </div>

        <div className="space-y-6">
          {operations.map((op, idx) => (
            <GlassPanel
              key={op.code}
              className={`border-l-2 ${op.borderColor}`}
            >
              <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
                {/* Left: Identity Card */}
                <div className={`p-4 rounded-xl ${op.bgColor} space-y-3`}>
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-2xl font-mono font-bold ${op.textColor}`}
                    >
                      {op.code}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-hom-panel border border-hom-border/30 text-hom-muted">
                      II-{String.fromCharCode(65 + idx)}
                    </span>
                  </div>
                  <div className="text-lg font-semibold text-hom-text">
                    {t(op.name)}
                  </div>
                  <div className={`text-xs font-medium ${op.textColor}`}>
                    {t(op.tagline)}
                  </div>
                  <div className="glow-line" />
                  <div className="text-[11px] text-hom-muted italic">
                    "{t(op.question)}"
                  </div>
                  <div className="mt-2">
                    <div className="text-[10px] text-hom-muted mb-1">
                      Key Identity:
                    </div>
                    <code
                      className={`text-xs font-mono ${op.textColor} block p-2 rounded bg-hom-bg/50`}
                    >
                      {op.identity}
                    </code>
                  </div>
                </div>

                {/* Right: Description + Capabilities */}
                <div className="space-y-4">
                  <p className="text-sm text-hom-text/90 leading-relaxed">
                    {t(op.description)}
                  </p>

                  <div>
                    <div className="text-[10px] text-hom-muted font-semibold uppercase tracking-wider mb-2">
                      {t('Capabilities')}
                    </div>
                    <ul className="space-y-1.5">
                      {op.capabilities.map((cap, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-2 text-xs text-hom-text/80"
                        >
                          <span className={`mt-0.5 ${op.textColor}`}>▸</span>
                          <span>{t(cap)}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div
                    className={`text-[11px] font-mono p-3 rounded-lg ${op.bgColor} border ${op.borderColor}`}
                  >
                    <span className="text-hom-muted">{t('Example: ')}</span>
                    <span className="text-hom-text/80">{t(op.example)}</span>
                  </div>
                </div>
              </div>
            </GlassPanel>
          ))}
        </div>

        {/* Operations Flow Diagram (Hybit Framework) */}
        <div className="w-full overflow-x-auto mt-8 border-t border-hom-border/30 pt-12">
          <div className="min-w-[700px] max-w-4xl mx-auto py-6 px-4 space-y-1">

            {/* ═══════════ TITLE ═══════════ */}
            <div className="text-center mb-6">
              <h2 className="text-3xl md:text-4xl font-black tracking-wider" style={{ color: colors.green }}>
                HYBIT
              </h2>
              <div className="text-2xl md:text-4xl text-hom-text mt-2 mb-4 font-mono leading-relaxed" dir="rtl">
                ا، ب، ت، ث، ج، ح، خ، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ع، غ، ف، ق، ك، ل، م، ن، و، هـ، ي
              </div>
              <div className="text-sm font-semibold mt-1" style={{ color: colors.gold }}>
                <FormulaBlock tex="\mathcal{H}_{28}" /> — Hijaiyyah Mathematics
              </div>
            </div>

            {/* ═══════════ ROW 1: CSGI + Euklides ═══════════ */}
            <div className="flex items-center justify-center gap-6 mb-1">
              <NodeBox
                label={t('C S G I')}
                sub={t('Skeletonizer')}
                color={colors.text}
                borderColor={colors.border}
                bgColor={`${colors.panel}`}
              />
              <svg width="40" height="2"><line x1="0" y1="1" x2="40" y2="1" stroke={colors.muted} strokeWidth="1" strokeDasharray="4 3" /><polygon points="36,0 40,1 36,2" fill={colors.muted} /></svg>
              <NodeBox
                label="Euklides ℝ²"
                color={colors.blue}
                borderColor={`${colors.blue}50`}
                bgColor={`${colors.blue}10`}
              />
            </div>

            <ArrowDown color={colors.muted} />

            {/* ═══════════ ROW 2: Four Geometric Invariants ═══════════ */}
            <div className="grid grid-cols-4 gap-3">
              <NodeBox
                label="Nuqṭah نُقْطَة"
                sub="N(h) ∈ ℕ₀³"
                formula="N(h) = (N_a, N_b, N_d)"
                color={colors.red}
                borderColor={`${colors.red}40`}
                bgColor={`${colors.red}08`}
              />
              <NodeBox
                label="Khaṭṭ خَطّ"
                sub="K(h) ∈ ℕ₀⁵"
                formula="K(h) = (K_p, K_z, K_s, K_a, K_c)"
                color={colors.green}
                borderColor={`${colors.green}40`}
                bgColor={`${colors.green}08`}
              />
              <NodeBox
                label="Qaws قَوْس"
                sub="Q(h) ∈ ℕ₀⁵"
                formula="Q(h) = (Q_h, Q_z, Q_s, Q_a, Q_c)"
                color={colors.purple}
                borderColor={`${colors.purple}40`}
                bgColor={`${colors.purple}08`}
              />
              <NodeBox
                label="Inḥinā' إنْحِنَاء"
                sub="Θ̂(h) ∈ ℕ₀"
                formula="\hat{\Theta}(h) = Q_{90}(|\Theta^*(h)|) \in \mathbb{N}_0"
                color={colors.gold}
                borderColor={`${colors.gold}40`}
                bgColor={`${colors.gold}08`}
              />
            </div>

            {/* Arrows from 4 invariants down */}
            <div className="grid grid-cols-4 gap-3">
              {[0, 1, 2, 3].map(i => (
                <ArrowDown key={i} height={20} color={colors.muted} />
              ))}
            </div>

            {/* ═══════════ ROW 3: Core Invariant + Vektor 14 + MainPath ═══════════ */}
            <div className="grid grid-cols-[1fr_1.2fr_1fr] gap-3 items-start">
              {/* Core Invariant */}
              <div className="space-y-1">
                <NodeBox
                  label={t('Core Invariant')}
                  formula="h = [\hat{\Theta} \mid \mathbf{N} \mid \mathbf{K} \mid \mathbf{Q}]"
                  color={colors.accent}
                  borderColor={`${colors.accent}40`}
                  bgColor={`${colors.accent}08`}
                  glow
                />
              </div>

              {/* Vektor 14 (center) */}
              <div className="space-y-1">
                <NodeBox
                  label={t('Vektor 14')}
                  formula="v_{14}(h) = [\hat{\Theta} \mid \mathbf{N} \mid \mathbf{K} \mid \mathbf{Q}] \in \mathbb{N}_0^{14}"
                  color={colors.accent}
                  borderColor={`${colors.accent}50`}
                  bgColor={`${colors.accent}0a`}
                  glow
                />
              </div>

              {/* MainPath */}
              <div className="space-y-1">
                <NodeBox
                  label={t('MainPath')}
                  formula="\gamma_h : [0, L_h] \to \mathbb{R}^2"
                  color={colors.gold}
                  borderColor={`${colors.gold}40`}
                  bgColor={`${colors.gold}08`}
                />
                <ArrowDown height={16} color={colors.muted} />
                <NodeBox
                  label={t('Turning & Residu')}
                  formula="\hat{\Theta}(h) = U(h) + \rho(h)"
                  color={colors.gold}
                  borderColor={`${colors.gold}30`}
                  bgColor={`${colors.gold}06`}
                  small
                />
                <ArrowDown height={16} color={colors.muted} />
                <NodeBox
                  label={t('Mod-4')}
                  formula="\hat{\Theta}(h) \equiv 0 \pmod{4}"
                  color={colors.gold}
                  borderColor={`${colors.gold}20`}
                  bgColor={`${colors.gold}05`}
                  small
                />
              </div>
            </div>

            {/* Connection line from Core Invariant and right side into center */}
            <ArrowDown color={colors.muted} />

            {/* ═══════════ ROW 4: tag + Anāṣir + Algebra ═══════════ */}
            <div className="grid grid-cols-[1fr_1.5fr_1fr] gap-3 items-center">
              <NodeBox
                label="tag(ε) = H*"
                color={colors.purple}
                borderColor={`${colors.purple}30`}
                bgColor={`${colors.purple}06`}
                small
              />
              <div className="text-center space-y-1">
                <NodeBox
                  label="Anāṣir العَنَاصِرُ"
                  formula="\mathbf{A}(h) = (A_N(h),\; A_K(h),\; A_Q(h)) \in \mathbb{N}_0^3"
                  color={colors.green}
                  borderColor={`${colors.green}40`}
                  bgColor={`${colors.green}08`}
                />
              </div>
              <NodeBox
                label="Algebra"
                formula="\sum_{i=1}^{m} v_{18}(x_i) + \sum_{j=1}^{n} v_{18}(y_j)"
                color={colors.blue}
                borderColor={`${colors.blue}30`}
                bgColor={`${colors.blue}06`}
                small
              />
            </div>

            <ArrowDown color={colors.muted} />

            {/* ═══════════ ROW 5: Injective → Vektor 18D ═══════════ */}
            <div className="grid grid-cols-[1fr_2fr_1fr] gap-3 items-center">
              <NodeBox
                label={t('Injective')}
                color={colors.accent}
                borderColor={`${colors.accent}30`}
                bgColor={`${colors.accent}06`}
                small
              />
              <NodeBox
                label={t('Vektor 18D')}
                formula="v_{18}(h) = [\hat{\Theta} \mid \mathbf{N} \mid \mathbf{K} \mid \mathbf{Q} \mid A_N, A_K, A_Q \mid H^*(h)] \in \mathbb{N}_0^{18}"
                color={colors.accent}
                borderColor={`${colors.accent}60`}
                bgColor={`${colors.accent}0c`}
                glow
              />
              <div />
            </div>

            {/* Arrows to foundations */}
            <ArrowDown color={colors.muted} />

            {/* ═══════════ ROW 6: Audit Collision + Formal Foundation + Guards ═══════════ */}
            <div className="grid grid-cols-3 gap-3">
              <NodeBox
                label={t('Audit Collision')}
                color={colors.red}
                borderColor={`${colors.red}30`}
                bgColor={`${colors.red}06`}
              />
              <NodeBox
                label={t('Formal Foundation')}
                color={colors.text}
                borderColor={`${colors.border}`}
                bgColor={colors.panel}
                glow
              />
              <NodeBox
                label="G1-G2-G3-G4"
                color={colors.green}
                borderColor={`${colors.green}30`}
                bgColor={`${colors.green}06`}
              />
            </div>

            <ArrowDown color={colors.muted} />

            {/* ═══════════ ROW 7: Mathematical Operating System ═══════════ */}
            <div className="text-center">
              <div
                className="framework-node inline-block rounded-xl border-2 px-8 py-3 mx-auto"
                style={{
                  borderColor: `${colors.gold}60`,
                  backgroundColor: `${colors.gold}0a`,
                  boxShadow: `0 0 30px ${colors.gold}20`,
                }}
              >
                <div className="text-base font-bold" style={{ color: colors.gold }}>
                  {t('Mathematical Operating System')}
                </div>
              </div>
            </div>

            {/* ═══════════ ROW 8: 5 Metrik-Vektorial Operations ═══════════ */}
            <div className="grid grid-cols-5 gap-2 mt-1">
              {/* connecting lines */}
              <div className="col-span-5 flex justify-around px-8">
                {[colors.red, colors.accent, colors.gold, colors.purple, colors.green].map((c, i) => (
                  <ArrowDown key={i} height={20} color={c} />
                ))}
              </div>
            </div>

            <div className="grid grid-cols-5 gap-2">
              <NodeBox
                label={t('Normivektor')}
                color={colors.red}
                borderColor={`${colors.red}50`}
                bgColor={`${colors.red}0a`}
                glow
              />
              <NodeBox
                label={t('Vectronometry')}
                color={colors.accent}
                borderColor={`${colors.accent}50`}
                bgColor={`${colors.accent}0a`}
                glow
              />
              <NodeBox
                label={t('Intrametric')}
                color={colors.gold}
                borderColor={`${colors.gold}50`}
                bgColor={`${colors.gold}0a`}
                glow
              />
              <NodeBox
                label={t('Exometric')}
                color={colors.purple}
                borderColor={`${colors.purple}50`}
                bgColor={`${colors.purple}0a`}
                glow
              />
              <NodeBox
                label={t('Aggregametric')}
                color={colors.green}
                borderColor={`${colors.green}50`}
                bgColor={`${colors.green}0a`}
                glow
              />
            </div>

            {/* ═══════════ Converge to Hybit ═══════════ */}
            <div className="flex justify-center">
              <svg width="500" height="30" className="block mx-auto">
                {/* Lines from each of 5 columns converging to center */}
                {[50, 150, 250, 350, 450].map((x, i) => (
                  <line key={i} x1={x} y1="0" x2={250} y2="26" stroke={[colors.red, colors.accent, colors.gold, colors.purple, colors.green][i]} strokeWidth="1" opacity="0.5" />
                ))}
                <polygon points="247,26 253,26 250,30" fill={colors.gold} />
              </svg>
            </div>

            {/* ═══════════ HYBIT CORE ═══════════ */}
            <div className="text-center">
              <div
                className="framework-node inline-block rounded-2xl border-2 px-12 py-4 mx-auto"
                style={{
                  borderColor: `${colors.gold}80`,
                  backgroundColor: `${colors.gold}0c`,
                  boxShadow: `0 0 40px ${colors.gold}30, 0 0 80px ${colors.gold}10`,
                }}
              >
                <div className="text-2xl font-black tracking-widest" style={{ color: colors.green }}>
                  Hybit
                </div>
                <div className="text-[10px] text-hom-muted mt-1">
                  {t('Hijaiyyah Hyperdimensional Bit Integration Technology')}
                </div>
              </div>
            </div>

            <ArrowDown color={colors.gold} height={24} />

            {/* ═══════════ ROW 9: Pipeline Components - Row 1 ═══════════ */}
            <div className="grid grid-cols-5 gap-2">
              {[
                { label: 'HCC', color: colors.accent },
                { label: 'HASM', color: colors.green },
                { label: 'HOM', color: colors.gold },
                { label: 'H-Kernel', color: colors.purple },
                { label: 'HGEO', color: colors.blue },
              ].map((item) => (
                <NodeBox
                  key={item.label}
                  label={item.label}
                  color={item.color}
                  borderColor={`${item.color}40`}
                  bgColor={`${item.color}08`}
                  small
                />
              ))}
            </div>

            {/* Pipeline Row 2 */}
            <div className="grid grid-cols-4 gap-2 mt-1">
              {[
                { label: 'H-ISA', color: colors.accent },
                { label: 'HC18DC', color: colors.green },
                { label: 'HISAB', color: colors.gold },
                { label: 'CMM-18C', color: colors.purple },
              ].map((item) => (
                <NodeBox
                  key={item.label}
                  label={item.label}
                  color={item.color}
                  borderColor={`${item.color}35`}
                  bgColor={`${item.color}06`}
                  small
                />
              ))}
            </div>

            {/* Pipeline Row 3 */}
            <div className="grid grid-cols-5 gap-2 mt-1">
              {[
                { label: 'HGGS', color: colors.red },
                { label: 'HL-18E', color: colors.accent },
                { label: 'HOS', color: colors.gold },
                { label: 'HCVM', color: colors.green },
                { label: 'HCPU', color: colors.purple },
              ].map((item) => (
                <NodeBox
                  key={item.label}
                  label={item.label}
                  color={item.color}
                  borderColor={`${item.color}30`}
                  bgColor={`${item.color}05`}
                  small
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════════ VERIFICATION ═══════════════ */}
      <section>
        <GlassPanel
          title={t('1,380-Check Verification Framework')}
          badge={t('ALL PASS')}
          glow="green"
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            {[
              { bab: 'Bab I', checks: 658, label: 'Foundation', sub: 'Guards · Injectivity · Mod-4' },
              { bab: 'Bab II', checks: 683, label: 'Metrik-Vektorial', sub: 'VTM · NMV · AGM · ITM · EXM' },
              { bab: 'Bab III', checks: 39, label: 'Hybit Pipeline', sub: 'Closure · Theorems · Pipeline' },
            ].map((b) => (
              <div
                key={b.bab}
                className="p-5 rounded-xl bg-hom-bg/50 border border-hom-green/10"
              >
                <div className="text-3xl font-bold text-hom-green font-mono">
                  {b.checks}
                </div>
                <div className="text-sm text-hom-text mt-1">{t(b.bab)}</div>
                <div className="text-xs text-hom-muted">{t(b.label)}</div>
                <div className="text-[10px] text-hom-muted/60 mt-1">{t(b.sub)}</div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center">
            <span className="font-mono text-sm text-hom-green">
              {t('1,380 PASS · 0 FAIL · 0 SKIP')}
            </span>
          </div>
          <div className="mt-2 text-center text-[10px] text-hom-muted">
            {t('Full test suite: 1,628 passed · 0 skipped · 0 failed in ~0.7s')}
          </div>
        </GlassPanel>
      </section>

      {/* ═══════════════ DOWNLOAD & RUN ═══════════════ */}
      <section>
        <div className="mb-6">
          <h2 className="text-2xl font-bold">{t('Download & Run')}</h2>
          <p className="text-sm text-hom-muted mt-1">
            {t('HOM is open for audit. Clone the repository, install, and run locally.')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Repository Card */}
          <GlassPanel glow>
            <div className="flex items-center gap-3 mb-4">
              <svg
                className="w-8 h-8 text-hom-text"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              <div>
                <div className="text-sm font-semibold">{t('GitHub Repository')}</div>
                <div className="text-[10px] text-hom-muted">
                  {t('Full source code, tests, documentation')}
                </div>
              </div>
            </div>
            <a
              href="https://github.com/hybittech/HOM"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full text-center px-4 py-3 rounded-lg bg-hom-accent/10 border border-hom-accent/30 text-hom-accent font-mono text-sm hover:bg-hom-accent/20 transition-all"
            >
              github.com/hybittech/HOM
            </a>
            <div className="mt-4 space-y-2 text-xs text-hom-muted">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-hom-green" />
                {t('Python 3.11+ backend — 1,628 tests')}
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-hom-accent" />
                {t('React + Three.js frontend — this GUI')}
              </div>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-hom-gold" />
                {t('24 pipeline components defined')}
              </div>
            </div>
          </GlassPanel>

          {/* Quick Start Card */}
          <GlassPanel>
            <div className="text-sm font-semibold mb-4">
              {t('Quick Start — Run Locally')}
            </div>

            <div className="space-y-4">
              {/* Step 1 */}
              <div>
                <div className="text-[10px] text-hom-accent font-semibold uppercase tracking-wider mb-1">
                  Step 1 — Clone
                </div>
                <code className="block p-3 rounded-lg bg-hom-bg border border-hom-border/30 font-mono text-xs text-hom-text">
                  git clone https://github.com/hybittech/HOM.git
                </code>
              </div>

              {/* Step 2 */}
              <div>
                <div className="text-[10px] text-hom-gold font-semibold uppercase tracking-wider mb-1">
                  Step 2 — Install & Run (Python Backend)
                </div>
                <code className="block p-3 rounded-lg bg-hom-bg border border-hom-border/30 font-mono text-xs text-hom-text whitespace-pre">
{`cd HOM
pip install -e ".[dev]"
pytest tests/test_full_verification.py -v
# → 1,380 passed`}
                </code>
              </div>

              {/* Step 3 */}
              <div>
                <div className="text-[10px] text-hom-green font-semibold uppercase tracking-wider mb-1">
                  Step 3 — Run GUI (Frontend)
                </div>
                <code className="block p-3 rounded-lg bg-hom-bg border border-hom-border/30 font-mono text-xs text-hom-text whitespace-pre">
{`npm install
npm run dev
# → Open http://localhost:5173/HOM/`}
                </code>
              </div>

              {/* Step 4 */}
              <div>
                <div className="text-[10px] text-hom-purple font-semibold uppercase tracking-wider mb-1">
                  Step 4 — Run Full HOM Application
                </div>
                <code className="block p-3 rounded-lg bg-hom-bg border border-hom-border/30 font-mono text-xs text-hom-text whitespace-pre">
{`python -m hijaiyyah
# → Opens HOM GUI (Tkinter-based scientific environment)`}
                </code>
              </div>
            </div>
          </GlassPanel>
        </div>

        {/* Prerequisites */}
        <GlassPanel className="mt-4" title={t('Prerequisites')}>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { name: 'Python', version: '3.11+', check: 'python --version' },
              { name: 'Node.js', version: '18+', check: 'node --version' },
              { name: 'pip', version: '22+', check: 'pip --version' },
              { name: 'npm', version: '9+', check: 'npm --version' },
            ].map((req) => (
              <div
                key={req.name}
                className="p-3 rounded-lg bg-hom-bg/50 border border-hom-border/20 text-center"
              >
                <div className="text-sm font-semibold text-hom-text">
                  {req.name}
                </div>
                <div className="text-hom-accent text-xs font-mono">
                  {req.version}
                </div>
                <div className="text-[9px] text-hom-muted mt-1 font-mono">
                  {req.check}
                </div>
              </div>
            ))}
          </div>
        </GlassPanel>

        {/* Alternative Access */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <a
            href="https://github.com/hybittech/HOM/archive/refs/heads/main.zip"
            target="_blank"
            rel="noopener noreferrer"
            className="glass p-4 text-center hover:border-hom-accent/40 transition-all"
          >
            <div className="text-lg mb-1">📦</div>
            <div className="text-xs font-semibold">{t('Download ZIP')}</div>
            <div className="text-[10px] text-hom-muted">
              {t('No Git required')}
            </div>
          </a>
          <a
            href="https://codespaces.new/hybittech/HOM"
            target="_blank"
            rel="noopener noreferrer"
            className="glass p-4 text-center hover:border-hom-green/40 transition-all"
          >
            <div className="text-lg mb-1">☁️</div>
            <div className="text-xs font-semibold">{t('GitHub Codespaces')}</div>
            <div className="text-[10px] text-hom-muted">
              {t('Run in browser — no local install')}
            </div>
          </a>
          <a
            href="https://hybittech.github.io/#/"
            target="_blank"
            rel="noopener noreferrer"
            className="glass p-4 text-center hover:border-hom-gold/40 transition-all"
          >
            <div className="text-lg mb-1">🌐</div>
            <div className="text-xs font-semibold">{t('Live Demo')}</div>
            <div className="text-[10px] text-hom-muted">
              {t('This page — already running')}
            </div>
          </a>
        </div>
      </section>

      {/* ═══════════════ FOOTER CTA ═══════════════ */}
      <section className="text-center py-8">
        <div className="glow-line mb-8" />
        <FormulaBlock
          tex="\boxed{\color{white}{\text{bit} \;\oplus\; \text{qubit} \;\oplus\; \text{hybit}}}"
          display
        />
        <p className="text-sm text-hom-muted mt-4 max-w-md mx-auto">
          {t('Three paradigms. Three optimal domains. Five metrik-vektorial operations. One pipeline. One ecosystem.')}
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <Link
            to="/explorer"
            className="px-6 py-2.5 rounded-lg bg-hom-accent text-black font-semibold text-sm hover:shadow-glow transition-all"
          >
            {t('Start Exploring →')}
          </Link>
          <a
            href="https://github.com/hybittech/HOM"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 rounded-lg border border-hom-border text-hom-muted text-sm hover:text-hom-gold hover:border-hom-gold/50 transition-all"
          >
            {t('View Source on GitHub')}
          </a>
        </div>
        <div className="mt-12 max-w-4xl mx-auto flex flex-col items-center gap-8 px-4">
          <div className="text-[10px] md:text-xs text-white leading-relaxed text-justify space-y-4 p-8 rounded-xl border border-hom-border/20 bg-hom-panel w-full shadow-lg shadow-black/20">
            <p className="font-semibold text-white text-center mb-6 text-sm">
              {t('© 2026 Hijaiyyah Mathematics Computational Laboratory (HMCL). All rights reserved.')}
            </p>
            <p>
              {t('The content, technology, and materials available within this platform—including but not limited to mathematical frameworks, computational models, software implementations, datasets, language specifications, compilation pipelines, file formats, processor architectures, and operating system designs—are proprietary to HMCL and are protected by applicable intellectual property laws.')}
            </p>
            <p>
              {t('No part of this platform may be copied, modified, distributed, transmitted, displayed, published, or otherwise used for commercial or non-commercial purposes without prior written authorization from HMCL.')}
            </p>
            <p>
              {t('HMCL, Hijaiyyah Mathematics, and all related names, logos, product names, and design marks are trademarks or registered trademarks of Hijaiyyah Mathematics Computational Laboratory.')}
            </p>
            <p className="font-semibold text-hom-red/90 text-center py-2 bg-hom-red/5 rounded-lg border border-hom-red/10">
              {t('Unauthorized use, reproduction, or distribution may result in civil and/or criminal penalties under applicable laws.')}
              <br />
              <span className="text-white/60 text-[9px] tracking-[0.3em] font-bold mt-2 block">
                PT PURI PERTIWI INTERNATIONAL
              </span>
            </p>
            
            <div className="mt-8 pt-6 border-t border-hom-border/20 flex flex-row items-center justify-center gap-8 md:gap-16">
              {/* Left Icon (Web) */}
              <img src={import.meta.env.BASE_URL + 'icon-web.png'} alt="web icon" className="h-16 md:h-24 w-auto object-contain opacity-100 hover:scale-110 transition-transform duration-300 drop-shadow-lg" />
              
              {/* Center Signature Details */}
              <div className="flex flex-col items-center text-center space-y-2">
                <span className="text-hom-gold font-bold tracking-wide text-sm">Maulana Amratulloh</span>
                <span className="text-hom-muted">{t('Founder & Principal Architect')}</span>
                
                <div className="flex flex-col items-center mt-4">
                  <span className="text-hom-muted text-[10px] uppercase tracking-[0.2em] font-bold mb-1 opacity-70">{t('Contact')}</span>
                  <a href="mailto:admin@hybit.tech" className="text-hom-accent font-mono text-xs hover:underline hover:text-hom-accent/80 transition-all">admin@hybit.tech</a>
                </div>

                <div className="flex flex-wrap justify-center gap-4 mt-6 font-mono text-[10px]">
                  <span className="px-3 py-1.5 rounded-full bg-hom-accent/10 border border-hom-accent/20 text-hom-accent">{t('Release: HM-28-v1.2-HC18D')}</span>
                  <span className="px-3 py-1.5 rounded-full bg-hom-green/10 border border-hom-green/20 text-hom-green">
                    {t('Status: Verified & Sealed')}
                  </span>
                </div>
              </div>

              {/* Right Icon (PT) */}
              <img src={import.meta.env.BASE_URL + 'icon-PT.png'} alt="PT icon" className="h-16 md:h-24 w-auto object-contain opacity-100 hover:scale-110 transition-transform duration-300 drop-shadow-lg" />
            </div>
          </div>


        </div>
      </section>
    </div>
  </div>
);
}
