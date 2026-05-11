import React from 'react'
import { motion } from 'framer-motion'

export default function RingProgress({
  progress = 0,
  size = 80,
  strokeWidth = 4,
  color = 'magenta',
  label = '',
  showPct = true,
}) {
  const colorMap = {
    magenta: { stroke: '#d946ef', glow: 'rgba(217,70,239,0.4)', bg: 'rgba(217,70,239,0.08)' },
    cyan: { stroke: '#22d3ee', glow: 'rgba(34,211,238,0.4)', bg: 'rgba(34,211,238,0.08)' },
    purple: { stroke: '#7c3aed', glow: 'rgba(124,58,237,0.4)', bg: 'rgba(124,58,237,0.08)' },
    green: { stroke: '#22c55e', glow: 'rgba(34,197,94,0.4)', bg: 'rgba(34,197,94,0.08)' },
    yellow: { stroke: '#eab308', glow: 'rgba(234,179,8,0.4)', bg: 'rgba(234,179,8,0.08)' },
  }
  const c = colorMap[color] || colorMap.magenta

  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (progress / 100) * circumference

  return (
    <div className="flex flex-col items-center gap-1.5" style={{ width: size }}>
      <motion.div
        className="relative flex items-center justify-center"
        style={{ width: size, height: size }}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        {/* Glow filter */}
        <svg width="0" height="0">
          <defs>
            <filter id={`glow-${color}`}>
              <feGaussianBlur stdDeviation="2" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
        </svg>

        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={c.bg}
            strokeWidth={strokeWidth}
          />
          {/* Progress circle */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={c.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.2, ease: [0.25, 0.1, 0.25, 1] }}
            style={{
              filter: `url(#glow-${color})`,
              boxShadow: `0 0 12px ${c.glow}`,
            }}
          />
        </svg>

        {/* Center text */}
        {showPct && (
          <span className="absolute text-xs font-mono text-white/80 tabular-nums">
            {Math.round(progress)}%
          </span>
        )}
      </motion.div>
      {label && <span className="text-[10px] text-white/35 text-center">{label}</span>}
    </div>
  )
}
