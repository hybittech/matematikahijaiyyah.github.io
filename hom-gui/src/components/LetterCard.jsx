import { Link } from 'react-router-dom';

export default function LetterCard({ entry }) {
  const theta = entry.v18[0];
  const AN = entry.v18[14], AK = entry.v18[15], AQ = entry.v18[16];

  return (
    <Link
      to={`/explorer/${encodeURIComponent(entry.char)}`}
      className="glass p-4 hover:shadow-glow hover:border-hom-accent/40 transition-all duration-300 group cursor-pointer"
    >
      <div className="text-center">
        <div className="arabic-letter text-4xl mb-2 group-hover:neon-text transition-all">
          {entry.char}
        </div>
        <div className="text-xs text-hom-muted mb-2">{entry.name}</div>
        <div className="flex justify-center gap-2 text-[10px] font-mono">
          <span className="px-1.5 py-0.5 rounded bg-hom-accent/10 text-hom-accent">Θ̂={theta}</span>
          <span className="px-1.5 py-0.5 rounded bg-hom-gold/10 text-hom-gold">N={AN}</span>
          <span className="px-1.5 py-0.5 rounded bg-hom-green/10 text-hom-green">K={AK}</span>
          <span className="px-1.5 py-0.5 rounded bg-hom-purple/10 text-hom-purple">Q={AQ}</span>
        </div>
      </div>
    </Link>
  );
}
