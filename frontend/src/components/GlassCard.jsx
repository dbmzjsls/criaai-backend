import React from 'react'

const colorMap = {
  magenta: {
    border: 'rgba(217, 70, 239, 0.12)',
    borderHover: 'rgba(217, 70, 239, 0.35)',
    glow: '0 0 20px rgba(217,70,239,0.2), 0 0 60px rgba(217,70,239,0.06)',
  },
  purple: {
    border: 'rgba(124, 58, 237, 0.12)',
    borderHover: 'rgba(124, 58, 237, 0.35)',
    glow: '0 0 20px rgba(124,58,237,0.2), 0 0 60px rgba(124,58,237,0.06)',
  },
  cyan: {
    border: 'rgba(34, 211, 238, 0.12)',
    borderHover: 'rgba(34, 211, 238, 0.35)',
    glow: '0 0 20px rgba(34,211,238,0.15), 0 0 60px rgba(34,211,238,0.04)',
  },
  pink: {
    border: 'rgba(236, 72, 153, 0.12)',
    borderHover: 'rgba(236, 72, 153, 0.35)',
    glow: '0 0 20px rgba(236,72,153,0.15)',
  },
  green: {
    border: 'rgba(34, 197, 94, 0.12)',
    borderHover: 'rgba(34, 197, 94, 0.35)',
    glow: '0 0 16px rgba(34,197,94,0.12)',
  },
}

export default function GlassCard({ children, className = '', hover = false, onClick, color = 'magenta' }) {
  const c = colorMap[color] || colorMap.magenta

  return (
    <div
      onClick={onClick}
      className={`
        glass-card
        ${hover ? 'cursor-pointer' : ''}
        ${className}
      `}
      style={{
        borderColor: c.border,
      }}
      onMouseEnter={e => {
        if (hover) {
          e.currentTarget.style.borderColor = c.borderHover
          e.currentTarget.style.boxShadow = `${c.glow}, 0 8px 32px rgba(0,0,0,0.3)`
          e.currentTarget.style.transform = 'scale(1.02)'
        }
      }}
      onMouseLeave={e => {
        if (hover) {
          e.currentTarget.style.borderColor = c.border
          e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)'
          e.currentTarget.style.transform = 'scale(1)'
        }
      }}
    >
      {children}
    </div>
  )
}
