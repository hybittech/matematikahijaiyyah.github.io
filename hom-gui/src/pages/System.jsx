/* ═══════════════════════════════════════════════════════════════
   KOMPONEN PIPELINE HYBIT — STATUS IMPLEMENTASI
   HOM v1.2.0 · Commit 8fa0c12
   ═══════════════════════════════════════════════════════════════ */

const STATUS = {
  OP:   { label: 'Operasional',    icon: '✅', color: '#00c853', bg: 'rgba(0,200,83,0.08)',  border: 'rgba(0,200,83,0.35)' },
  SPEC: { label: 'Terspesifikasi', icon: '📐', color: '#d4af37', bg: 'rgba(212,175,55,0.08)', border: 'rgba(212,175,55,0.35)' },
  DES:  { label: 'Terdesain',      icon: '📝', color: '#b388ff', bg: 'rgba(179,136,255,0.08)',border: 'rgba(179,136,255,0.35)' },
  ASP:  { label: 'Aspirasional',   icon: '🎯', color: '#ff5252', bg: 'rgba(255,82,82,0.08)',  border: 'rgba(255,82,82,0.35)' },
};

/* ─── Reusable Components ─── */

function SectionTitle({ children, sub }) {
  return (
    <div className="mb-6">
      <h2 className="text-xl md:text-2xl font-bold text-hom-text tracking-wide" style={{ fontFamily: "'Orbitron', sans-serif" }}>
        {children}
      </h2>
      {sub && <p className="text-xs text-hom-muted mt-1 font-mono">{sub}</p>}
    </div>
  );
}

function PipelineNode({ name, sub, status, tests, glow }) {
  const s = STATUS[status];
  return (
    <div
      className="relative rounded-xl border p-4 backdrop-blur-xl transition-all duration-500 hover:scale-[1.03] hover:-translate-y-0.5 group"
      style={{
        borderColor: s.border,
        backgroundColor: s.bg,
        boxShadow: glow
          ? `0 6px 24px rgba(0,0,0,0.4), 0 0 20px ${s.border}`
          : '0 6px 24px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.04)',
      }}
    >
      <div className="flex items-center gap-2 mb-1">
        <span className="text-base">{s.icon}</span>
        <span className="text-sm font-bold font-mono" style={{ color: s.color }}>{name}</span>
      </div>
      {sub && <div className="text-[10px] text-hom-muted leading-tight">{sub}</div>}
      {tests && (
        <div className="mt-2 text-[9px] font-mono px-2 py-0.5 rounded-full inline-block border"
          style={{ color: '#00c853', borderColor: 'rgba(0,200,83,0.3)', backgroundColor: 'rgba(0,200,83,0.08)' }}>
          {tests} tests
        </div>
      )}
    </div>
  );
}

function Arrow({ direction = 'down', length = 32, color = 'rgba(255,255,255,0.15)' }) {
  if (direction === 'right') {
    return (
      <div className="flex items-center justify-center px-1" style={{ minWidth: 28 }}>
        <svg width={length} height="14">
          <defs>
            <linearGradient id="arGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} />
            </linearGradient>
          </defs>
          <line x1="0" y1="7" x2={length - 6} y2="7" stroke="url(#arGrad)" strokeWidth="2" />
          <polygon points={`${length - 8},3 ${length},7 ${length - 8},11`} fill={color} />
        </svg>
      </div>
    );
  }
  return (
    <div className="flex justify-center" style={{ height: length }}>
      <svg width="14" height={length}>
        <defs>
          <linearGradient id="adGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} />
          </linearGradient>
        </defs>
        <line x1="7" y1="0" x2="7" y2={length - 6} stroke="url(#adGrad)" strokeWidth="2" />
        <polygon points={`3,${length - 8} 7,${length} 11,${length - 8}`} fill={color} />
      </svg>
    </div>
  );
}

function InstructionChip({ name, color = '#00d4ff' }) {
  return (
    <span
      className="inline-block text-[10px] font-mono font-bold px-2 py-1 rounded-lg border mr-1.5 mb-1.5 transition-all hover:scale-105"
      style={{ color, borderColor: `${color}50`, backgroundColor: `${color}10`, textShadow: `0 0 8px ${color}40` }}
    >
      {name}
    </span>
  );
}

function StatusBadge({ status }) {
  const s = STATUS[status];
  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full border"
      style={{ color: s.color, borderColor: s.border, backgroundColor: s.bg }}>
      {s.icon} {s.label}
    </span>
  );
}

/* ═══════════════════════════════════════════════════════════════ */

export default function System() {
  return (
    <div className="space-y-10 max-w-6xl mx-auto">

      {/* ─── HEADER ─── */}
      <div className="text-center py-6">
        <h1 className="text-3xl md:text-4xl font-black tracking-widest text-hom-accent mb-2" style={{ fontFamily: "'Orbitron', sans-serif", textShadow: '0 0 20px rgba(0,212,255,0.3)' }}>
          Hybit Computational Architecture
        </h1>
        <p className="text-sm text-hom-muted font-mono">STATUS IMPLEMENTASI · HOM v1.2.0 · Commit 8fa0c12</p>
        <div className="flex flex-wrap justify-center gap-3 mt-4">
          {Object.entries(STATUS).map(([k, s]) => (
            <span key={k} className="inline-flex items-center gap-1.5 text-[11px] font-mono px-3 py-1 rounded-full border"
              style={{ color: s.color, borderColor: s.border, backgroundColor: s.bg }}>
              {s.icon} {s.label}
            </span>
          ))}
        </div>
      </div>

      {/* ═══════════ JALUR KODE (Code Path) ═══════════ */}
      <section className="rounded-2xl border border-hom-border/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
        <SectionTitle sub="Code Path">JALUR KODE</SectionTitle>

        {/* Flow: HC → HCC → HASM → .hbc → HVM */}
        <div className="flex flex-col items-center gap-0">
          {/* Row 1: Source tools */}
          <div className="flex flex-col md:flex-row items-center gap-3 md:gap-0 w-full justify-center">
            <PipelineNode name="HC Language" sub="Bahasa pemrograman codex v1.0" status="OP" tests="27" glow />
            <Arrow direction="right" color="#00c853" length={40} />
            <PipelineNode name="HCC Compiler" sub="6-tahap: Lexer → Parser → Semantic → Ψ → Codegen → Assemble" status="OP" tests="16" glow />
            <Arrow direction="right" color="#d4af37" length={40} />
            <PipelineNode name="HASM Assembler" sub="4-pass: Label → Encode → Pool → Header" status="SPEC" tests="16" />
          </div>

          <Arrow color="rgba(255,255,255,0.15)" length={28} />

          {/* Row 2: File formats */}
          <div className="flex flex-col md:flex-row items-center gap-3 md:gap-0 w-full justify-center">
            <div className="rounded-lg border border-hom-accent/30 bg-hom-accent/5 px-5 py-2 text-center">
              <div className="text-sm font-mono font-bold text-hom-accent">.hc</div>
              <div className="text-[9px] text-hom-muted">UTF-8 source</div>
            </div>
            <Arrow direction="right" color="rgba(255,255,255,0.15)" length={60} />
            <div className="rounded-lg border border-hom-accent/30 bg-hom-accent/5 px-5 py-2 text-center">
              <div className="text-sm font-mono font-bold text-hom-accent">.hasm</div>
              <div className="text-[9px] text-hom-muted">Assembly H-ISA</div>
            </div>
            <Arrow direction="right" color="rgba(255,255,255,0.15)" length={60} />
            <div className="rounded-lg border border-hom-gold/30 bg-hom-gold/5 px-5 py-2 text-center">
              <div className="text-sm font-mono font-bold text-hom-gold">.hbc</div>
              <div className="text-[9px] text-hom-muted">Bytecode "HBYT"</div>
            </div>
          </div>

          <Arrow color="rgba(255,255,255,0.15)" length={28} />

          {/* Row 3: HVM */}
          <div className="w-full max-w-lg">
            <PipelineNode name="HVM — Hybit Virtual Machine" sub="Loader │ Interpreter │ Hybit Engine │ Guard System │ HCHECK" status="OP" tests="34" glow />
          </div>
        </div>
      </section>

      {/* ═══════════ JALUR DATA (Data Path) ═══════════ */}
      <section className="rounded-2xl border border-hom-border/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
        <SectionTitle sub="Data Path">JALUR DATA</SectionTitle>

        <div className="flex flex-col items-center gap-0">
          <div className="flex flex-col md:flex-row items-center gap-3 md:gap-0 w-full justify-center">
            <PipelineNode name="Font KFGQPC" sub="SHA-256 sealed · Kanonik" status="OP" glow />
            <Arrow direction="right" color="#00c853" length={40} />
            <PipelineNode name="Ψ-Compiler" sub="Rasterisasi → CSGI → MainPath → Q₉₀ → N-K-Q" status="OP" tests="13" glow />
            <Arrow direction="right" color="#d4af37" length={40} />
            <div className="rounded-lg border border-hom-gold/30 bg-hom-gold/5 px-5 py-2 text-center">
              <div className="text-sm font-mono font-bold text-hom-gold">.hgeo</div>
              <div className="text-[9px] text-hom-muted">Geometry JSON</div>
            </div>
            <Arrow direction="right" color="#00c853" length={40} />
            <PipelineNode name="HAR Registry" sub="HAR-001 Hijaiyyah (CERTIFIED)" status="OP" tests="15" glow />
          </div>

          <Arrow color="rgba(255,255,255,0.15)" length={28} />

          <div className="flex flex-col md:flex-row items-center gap-4 w-full justify-center">
            <PipelineNode name="CSGI" sub="Canonical Skeleton Graph Interface" status="OP" glow />
            <div className="text-center">
              <div className="text-[10px] text-hom-muted font-mono mb-1">feeds into</div>
              <Arrow direction="right" color="rgba(255,255,255,0.15)" length={40} />
            </div>
            <PipelineNode name="HAR-001 Hijaiyyah" sub="28 × 18 matrix · CERTIFIED · 252 bytes ROM" status="OP" glow />
          </div>
        </div>
      </section>

      {/* ═══════════ INSTRUKSI H-ISA ═══════════ */}
      <section className="rounded-2xl border border-hom-border/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
        <SectionTitle sub="44 opcode unik · 28 di RTL · 18 tests">INSTRUKSI H-ISA</SectionTitle>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[
            { cat: 'Aritmetika', color: '#00d4ff', ops: ['HCADD','HCSUB','HCMUL','HCDIV','HCMOD'] },
            { cat: 'Vektor', color: '#00c853', ops: ['HCPROJ','HCNRM','HCDST','HCCOS','HCDOT'] },
            { cat: 'Guard', color: '#ff5252', ops: ['HGRD','HGRDR','HGRDX'] },
            { cat: 'MV-Operasi', color: '#d4af37', ops: ['HVTM','HNMV','HAGM','HITM','HEXM'] },
            { cat: 'Kontrol', color: '#b388ff', ops: ['HLT','NOP','JMP','JZ','JNZ'] },
            { cat: 'Memori', color: '#448aff', ops: ['HLOAD','HSTR','HPUSH','HPOP'] },
            { cat: 'I/O', color: '#ff9800', ops: ['HPRINT','HREAD','HLOG'] },
            { cat: 'Khusus', color: '#e91e63', ops: ['HCHECK','HSEAL'] },
          ].map((group) => (
            <div key={group.cat} className="rounded-xl border p-4"
              style={{ borderColor: `${group.color}30`, backgroundColor: `${group.color}06` }}>
              <div className="text-xs font-bold uppercase tracking-widest mb-3"
                style={{ color: group.color, fontFamily: "'Orbitron', sans-serif", textShadow: `0 0 10px ${group.color}40` }}>
                {group.cat}
              </div>
              <div className="flex flex-wrap">
                {group.ops.map((op) => (
                  <InstructionChip key={op} name={op} color={group.color} />
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════ VALIDASI & INTEGRITAS ═══════════ */}
      <section className="rounded-2xl border border-hom-border/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
        <SectionTitle sub="Multi-layer verification">VALIDASI & INTEGRITAS</SectionTitle>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: 'Guard System', sub: 'G1–G4, T1–T2 · 25 ops O(1)', tests: '168/168', status: 'OP' },
            { name: 'HCHECK', sub: 'Periodik full-scan runtime', tests: '7', status: 'OP' },
            { name: 'HISAB Protocol', sub: 'Pertukaran codex · 3-level validation', tests: '17', status: 'OP' },
            { name: 'SHA-256 Seal', sub: 'Integritas dataset · immutable', tests: '3', status: 'OP' },
            { name: 'Injectivity', sub: '378 pasangan unik v₁₈', tests: '2', status: 'OP' },
            { name: 'Exometric R1–R5', sub: 'Audit 140 checks · cascading', tests: '140/140', status: 'OP' },
          ].map((item) => (
            <div key={item.name} className="rounded-xl border border-hom-green/30 bg-hom-green/5 p-4 hover:scale-[1.02] transition-all"
              style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.2)' }}>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm">✅</span>
                <span className="text-sm font-bold text-hom-green font-mono">{item.name}</span>
              </div>
              <div className="text-[10px] text-hom-muted mb-2">{item.sub}</div>
              <span className="text-[9px] font-mono px-2 py-0.5 rounded-full border border-hom-green/30 bg-hom-green/10 text-hom-green">
                {item.tests} PASS
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════ LEVEL SISTEM (Designed) ═══════════ */}
      <section className="rounded-2xl border border-hom-border/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03)' }}>
        <SectionTitle sub="Designed · Blueprint phase">LEVEL SISTEM</SectionTitle>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[
            { name: 'HOS', sub: 'Hybit Operating System · 7-layer · Shell + Services + HAR Manager + Guard Monitor', desc: 'Sistem operasi native untuk ekosistem hybit' },
            { name: 'HFS', sub: 'Hybit File System · guard-on-write · Metadata-aware', desc: 'File system dengan validasi guard otomatis pada setiap write' },
            { name: 'H-Kernel', sub: 'Process / Memory / IO / Guard Daemon', desc: 'Kernel dengan 18-wide alignment dan pengelolaan proses hybit' },
          ].map((item) => (
            <div key={item.name} className="rounded-xl border border-hom-purple/30 bg-hom-purple/5 p-5 hover:scale-[1.02] transition-all"
              style={{ boxShadow: '0 4px 16px rgba(0,0,0,0.2)' }}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm">📝</span>
                <span className="text-lg font-bold text-hom-purple font-mono">{item.name}</span>
              </div>
              <div className="text-[11px] text-hom-text/80 mb-2">{item.sub}</div>
              <div className="text-[10px] text-hom-muted italic">{item.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ═══════════ REALISASI FISIK ═══════════ */}
      <section className="rounded-2xl border border-hom-green/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 30px rgba(0,200,83,0.05)' }}>
        <SectionTitle sub="Silicon RTL (Operasional) & Photonic (Aspirational)">REALISASI FISIK: HCPU</SectionTitle>

        {/* Silicon Phase 2.0 Block */}
        <div className="rounded-xl border border-hom-green/30 bg-hom-green/5 p-6 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">✅</span>
            <span className="text-xl font-bold text-hom-green font-mono">HCPU Phase 2.0</span>
            <span className="text-xs text-hom-muted ml-2">— Silicon RTL Architecture</span>
            <span className="ml-auto text-[9px] font-mono px-2 py-0.5 rounded-full border border-hom-green/30 bg-hom-green/10 text-hom-green">
              SYNTHESIS-READY
            </span>
          </div>
          
          <div className="mt-4 space-y-6">
            {/* Row 1: Pipeline & Memory */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl border border-hom-green/20 bg-hom-panel/40">
                <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-3 font-bold border-b border-hom-green/10 pb-2">
                  5-Stage Pipeline Arsitektur
                </div>
                <div className="space-y-2 text-xs font-mono">
                  <div className="flex gap-2"><span className="text-hom-accent w-6">IF</span><span className="text-hom-text/80">Instruction Fetch (BRAM sync, 2-phase)</span></div>
                  <div className="flex gap-2"><span className="text-hom-gold w-6">ID</span><span className="text-hom-text/80">Decode, GPR Read, Hazard Detection</span></div>
                  <div className="flex gap-2"><span className="text-hom-green w-6">EX</span><span className="text-hom-text/80">18-wide Vector ALU, HISAB, Branch Eval</span></div>
                  <div className="flex gap-2"><span className="text-hom-purple w-6">MEM</span><span className="text-hom-text/80">Data Memory Access (Combinational)</span></div>
                  <div className="flex gap-2"><span className="text-hom-red w-6">WB</span><span className="text-hom-text/80">GPR Write-back (Synchronous)</span></div>
                </div>
              </div>
              
              <div className="p-4 rounded-xl border border-hom-green/20 bg-hom-panel/40">
                <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-3 font-bold border-b border-hom-green/10 pb-2">
                  Memory & Hazard Resolution
                </div>
                <div className="space-y-2 text-xs text-hom-text/80 leading-relaxed">
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">Load-Use Hazard</strong>: Deteksi di ID stage, memicu 1-cycle stall + memori bypass otomatis.</span></div>
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">Store-Load Interlock</strong>: Mencegah bacaan invalid pada alamat memori yang sama.</span></div>
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">Data Forwarding</strong>: Rute EX→ID dan MEM→ID meminimalisasi pipeline bubbles.</span></div>
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">BRAM Sync</strong>: Pengawalan <code className="text-[10px] text-hom-accent px-1 bg-hom-panel rounded">imem_ce</code> untuk anti-loss instruksi saat ter-stall.</span></div>
                </div>
              </div>
            </div>

            {/* Row 2: Target Fabrikasi & Hisab */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl border border-hom-green/20 bg-hom-panel/40">
                <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-3 font-bold border-b border-hom-green/10 pb-2">
                  Target Integrasi MPW & FPGA
                </div>
                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between"><span className="text-hom-muted">Status Validasi</span><span className="text-hom-green font-mono font-bold">204/204 PASS (Zero Bug)</span></div>
                  <div className="flex justify-between"><span className="text-hom-muted">Chip Fabrikasi</span><span className="text-hom-accent font-mono">SkyWater SKY130 (Caravel)</span></div>
                  <div className="flex justify-between"><span className="text-hom-muted">Protokol Akses</span><span className="text-hom-text/80 font-mono">Wishbone B4 Slave (8-register maps)</span></div>
                  <div className="flex justify-between"><span className="text-hom-muted">Target FPGA</span><span className="text-hom-gold font-mono">Xilinx Arty A7-35T (100MHz)</span></div>
                  <div className="flex justify-between"><span className="text-hom-muted">Sintesis Logic</span><span className="text-hom-text/80 font-mono">Single Clock Domain (0 CDC)</span></div>
                  <div className="flex justify-between"><span className="text-hom-muted">Estimasi Resource</span><span className="text-hom-text/80 font-mono">LUT &lt; 85%, DSP48E1 &lt; 50%</span></div>
                </div>
              </div>
              
              <div className="p-4 rounded-xl border border-hom-green/20 bg-hom-panel/40">
                <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-3 font-bold border-b border-hom-green/10 pb-2">
                  HISAB & EXM In-Silico Subsystem
                </div>
                <div className="space-y-2 text-xs text-hom-text/80 leading-relaxed">
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">Nibble-Pack Serializer</strong>: <code className="text-[10px] text-hom-accent px-1 bg-hom-panel rounded">HPACK</code> mentransformasi vektor 18D menjadi standarisasi byte di hardware.</span></div>
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">IEEE 802.3 CRC32</strong>: Hardware digest generator kombinasional O(1) untuk lapis integritas frame HISAB.</span></div>
                  <div className="flex items-start gap-2"><span className="text-hom-green mt-0.5">▸</span><span><strong className="text-hom-text">Guard Checker</strong>: Aturan geometri mutlak (EXM R1-R5) diproses mandiri di <code className="text-[10px] px-1 bg-hom-panel rounded">hcpu_guard.v</code>.</span></div>
                </div>
              </div>
            </div>

            {/* Row 3: ASCII Block Diagram */}
            <div className="mt-6 p-5 rounded-xl border border-hom-green/20 bg-[#0a0a0f] overflow-x-auto shadow-inner hide-scrollbar">
              <div className="text-[10px] uppercase tracking-widest text-hom-green/80 flex items-center gap-2 mb-4 font-bold border-b border-hom-green/10 pb-2">
                <span className="w-1.5 h-1.5 rounded-full bg-hom-green animate-pulse"></span>
                RTL Topology Schematic
              </div>
              <pre className="text-[10px] sm:text-xs text-hom-green font-mono leading-tight whitespace-pre">
{`                    ┌──────────────────────────────────────────────────────┐
                    │                    HCPU Top-Level                    │
  ┌──────────┐      │  ┌───────┐  ┌───────┐  ┌─────────┐  ┌───────┐        │
  │   Code   │◄─────┤  │ FETCH │─►│DECODE │─►│ EXECUTE │─►│MEMORY │──►WB   │
  │   ROM    │      │  └───┬───┘  └───┬───┘  └────┬────┘  └───┬───┘        │
  └──────────┘      │      │          │    ┌──────┤            │           │
                    │      │    ┌─────┴──┐│┌─────┴────┐ ┌─────┴─────┐      │
                    │      │    │RegFile ││├ ScalarALU│ │  DataRAM  │      │
                    │      │    │18 GPR  │││ (32-bit) │ │  (16 KB)  │      │
                    │      │    │16 H-Reg│││ MOV/ADD/ │ │  LOAD/    │      │
                    │      │    │ FLAGS  │││ SUB/MUL/ │ │  STORE    │      │
                    │      │    └────────┘││ CMP      │ ├───────────┤      │
                    │      │              │├──────────┤ │  Stack    │      │
                    │      │              ││ CodexALU │ │ (256×32)  │      │
                    │ ┌────┴────┐         ││ HCADD    │ │ PUSH/POP  │      │
                    │ │  Ctrl   │         ││ HNRM2    │ └───────────┘      │
                    │ │ pc_stall│         ││ HDIST    │                    │
                    │ │ id_flush│         │├──────────┤  ┌──────────────┐  │
                    │ │ if_flush│         ││  Guard   │  │  UART TX     │  │
                    │ │ ex_stall│         ││ G1–G4    │  │  8N1 115200  │─┼──► TXD
                    │ └────┬────┘         ││ T1–T2    │  └──────────────┘  │
                    │      │       ┌──────┤└──────────┘                    │
                    │      │       │ FWD  │ ┌──────────┐                   │
                    │      └───────┤EX→ID │ │Master ROM│                   │
                    │              │MEM→ID│─┤28×144-bit│                   │
                    │              └──────┘ └──────────┘                   │
                    └──────────────────────────────────────────────────────┘`}
              </pre>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-hom-red/20 bg-hom-red/5 p-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🎯</span>
            <span className="text-xl font-bold text-hom-red font-mono">HCPU</span>
            <span className="text-xs text-hom-muted ml-2">— Arsitektur Prosesor Fotonik</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            <div>
              <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-2 font-bold">Pemetaan DoF Foton</div>
              <div className="space-y-1.5">
                {[
                  { dof: 'Fase (Phase)', map: 'Θ̂ — Inḥinā\'', color: '#d4af37' },
                  { dof: 'WDM (Wavelength)', map: 'N — Nuqṭah', color: '#ff5252' },
                  { dof: 'TDM (Time-slot)', map: 'K — Khaṭṭ', color: '#00c853' },
                  { dof: 'OAM (Orbital)', map: 'Q — Qaws', color: '#b388ff' },
                  { dof: 'Polarisasi', map: 'H* — Identitas huruf', color: '#00d4ff' },
                ].map((item) => (
                  <div key={item.dof} className="flex items-center gap-2 text-xs">
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                    <span className="text-hom-text/80 font-mono">{item.dof}</span>
                    <span className="text-hom-muted">→</span>
                    <span style={{ color: item.color }} className="font-mono">{item.map}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <div className="text-[10px] uppercase tracking-widest text-hom-muted mb-2 font-bold">Spesifikasi</div>
              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between">
                  <span className="text-hom-muted">Margin keamanan</span>
                  <span className="text-hom-green font-mono font-bold">22.5× (EH)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-hom-muted">Material</span>
                  <span className="text-hom-text/80 font-mono">Nd:YAG, Ce:YIG, YSZ, Er:YSO</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-hom-muted">Dimensi register</span>
                  <span className="text-hom-accent font-mono">18-wide (576 byte/reg)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-hom-muted">DoF tersedia</span>
                  <span className="text-hom-gold font-mono">20–32× (foton tunggal)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══════════ RINGKASAN STATUS ═══════════ */}
      <section className="rounded-2xl border border-hom-accent/30 bg-hom-panel/30 backdrop-blur-xl p-6 md:p-8"
        style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3), 0 0 25px rgba(0,212,255,0.08)' }}>
        <SectionTitle sub="Aggregate overview">RINGKASAN STATUS</SectionTitle>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { status: 'OP', count: 16 },
            { status: 'SPEC', count: 6 },
            { status: 'DES', count: 3 },
            { status: 'ASP', count: 1 },
          ].map((item) => {
            const s = STATUS[item.status];
            return (
              <div key={item.status} className="rounded-xl border p-5 text-center transition-all hover:scale-[1.03]"
                style={{ borderColor: s.border, backgroundColor: s.bg, boxShadow: `0 4px 16px rgba(0,0,0,0.2), 0 0 15px ${s.border}` }}>
                <div className="text-3xl font-bold font-mono" style={{ color: s.color }}>{item.count}</div>
                <div className="flex items-center justify-center gap-1.5 mt-2">
                  <span className="text-sm">{s.icon}</span>
                  <span className="text-[10px] font-mono" style={{ color: s.color }}>{s.label}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Detailed component table */}
        <div className="overflow-x-auto rounded-xl border border-hom-border/20">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-hom-panel/60 border-b border-hom-border/30">
                <th className="text-left py-3 px-4 text-[10px] uppercase tracking-wider text-hom-accent font-bold">Status</th>
                <th className="text-left py-3 px-4 text-[10px] uppercase tracking-wider text-hom-accent font-bold">Komponen</th>
              </tr>
            </thead>
            <tbody>
              {[
                { status: 'OP', components: 'HCPU RTL, HC, HCC, HVM, CSGI, H-ISA, Guard, HCHECK, HISAB, HAR, Ψ-Compiler, MasterTable, ROM, SHA-256, Injectivity, .hc' },
                { status: 'SPEC', components: 'HASM, .hbc, .hgeo, HCC codegen, HCHECK full, HAR extended' },
                { status: 'DES', components: 'HOS, HFS, H-Kernel' },
                { status: 'ASP', components: 'HCPU (fotonik)' },
              ].map((row) => {
                const s = STATUS[row.status];
                return (
                  <tr key={row.status} className="border-b border-hom-border/10 hover:bg-hom-accent/[0.03] transition-colors">
                    <td className="py-3 px-4">
                      <StatusBadge status={row.status} />
                    </td>
                    <td className="py-3 px-4 text-xs text-hom-text/80 font-mono">{row.components}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Total bar */}
        <div className="mt-6 rounded-xl border border-hom-accent/30 bg-hom-accent/5 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono text-hom-accent font-bold">TOTAL KOMPONEN</span>
            <span className="text-lg font-bold font-mono text-hom-accent">26</span>
          </div>
          <div className="h-3 bg-hom-bg/50 rounded-full overflow-hidden flex">
            <div className="h-full bg-[#00c853] transition-all" style={{ width: '61%' }} title="16 Operasional" />
            <div className="h-full bg-[#d4af37] transition-all" style={{ width: '23%' }} title="6 Terspesifikasi" />
            <div className="h-full bg-[#b388ff] transition-all" style={{ width: '12%' }} title="3 Terdesain" />
            <div className="h-full bg-[#ff5252] transition-all" style={{ width: '4%' }} title="1 Aspirasional" />
          </div>
          <div className="flex justify-between mt-1.5 text-[9px] font-mono text-hom-muted">
            <span className="text-[#00c853]">61% Operasional</span>
            <span className="text-[#d4af37]">23% Spesifikasi</span>
            <span className="text-[#b388ff]">12% Desain</span>
            <span className="text-[#ff5252]">4% Aspirasi</span>
          </div>
        </div>
      </section>

      {/* Footer */}
      <div className="text-center py-4 text-[10px] text-hom-muted font-mono">
        PIPELINE HYBIT · HOM v1.2.0 · HM-28-v1.2-HC18D · © 2026 HMCL
      </div>
    </div>
  );
}
