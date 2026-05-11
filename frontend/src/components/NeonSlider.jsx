import React from 'react'

export default function NeonSlider({
  value,
  onChange,
  min = 0,
  max = 100,
  step = 1,
  label = '',
  leftLabel = '',
  rightLabel = '',
  color = 'magenta',
}) {
  const colorVals = {
    magenta: { track: '#d946ef', glow: 'rgba(217,70,239,0.4)' },
    cyan: { track: '#22d3ee', glow: 'rgba(34,211,238,0.4)' },
    purple: { track: '#7c3aed', glow: 'rgba(124,58,237,0.4)' },
  }
  const c = colorVals[color] || colorVals.magenta

  const pct = ((value - min) / (max - min)) * 100

  return (
    <div className="w-full">
      {(label || leftLabel || rightLabel) && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-white/40">{label || leftLabel}</span>
          <span className="text-xs font-mono text-white/60 tabular-nums">{value}{rightLabel}</span>
        </div>
      )}
      <div className="relative h-8 flex items-center">
        {/* Track background */}
        <div className="absolute w-full h-0.5 rounded-full bg-white/5" />
        {/* Filled track */}
        <div
          className="absolute h-0.5 rounded-full transition-all duration-200"
          style={{
            width: `${pct}%`,
            background: `linear-gradient(90deg, ${c.track}, ${c.glow})`,
            boxShadow: `0 0 8px ${c.glow}`,
          }}
        />
        {/* Diamond handle */}
        <div
          className="absolute w-4 h-4 rounded-sm rotate-45 transition-all duration-200 cursor-pointer"
          style={{
            left: `calc(${pct}% - 8px)`,
            background: `linear-gradient(135deg, ${c.track}, ${c.glow})`,
            boxShadow: `0 0 12px ${c.glow}, 0 0 24px ${c.glow}`,
            border: '1px solid rgba(255,255,255,0.2)',
          }}
        />
        {/* Invisible range input overlay */}
        <input
          type="range"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          step={step}
          className="absolute w-full h-8 opacity-0 cursor-pointer z-10"
        />
      </div>
    </div>
  )
}
