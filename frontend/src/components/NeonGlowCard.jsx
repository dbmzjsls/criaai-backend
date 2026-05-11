import React from 'react'
import { motion } from 'framer-motion'

const colorMap = {
  magenta: {
    border: 'rgba(217, 70, 239, 0.12)',
    borderHover: 'rgba(217, 70, 239, 0.4)',
    glow: '0 0 20px rgba(217, 70, 239, 0.2), 0 0 60px rgba(217, 70, 239, 0.06)',
    neonClass: 'neon-card-magenta',
  },
  purple: {
    border: 'rgba(124, 58, 237, 0.12)',
    borderHover: 'rgba(124, 58, 237, 0.4)',
    glow: '0 0 20px rgba(124, 58, 237, 0.2), 0 0 60px rgba(124, 58, 237, 0.06)',
    neonClass: 'neon-card-purple',
  },
  cyan: {
    border: 'rgba(34, 211, 238, 0.12)',
    borderHover: 'rgba(34, 211, 238, 0.4)',
    glow: '0 0 20px rgba(34, 211, 238, 0.15), 0 0 60px rgba(34, 211, 238, 0.04)',
    neonClass: 'neon-card-cyan',
  },
  green: {
    border: 'rgba(34, 197, 94, 0.12)',
    borderHover: 'rgba(34, 197, 94, 0.35)',
    glow: '0 0 16px rgba(34, 197, 94, 0.15)',
    neonClass: '',
  },
}

export default function NeonGlowCard({
  children,
  className = '',
  color = 'magenta',
  hover = false,
  onClick,
  style = {},
  as = 'div',
}) {
  const c = colorMap[color] || colorMap.magenta

  const combined = {
    background: 'var(--glass-bg)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: `1px solid ${c.border}`,
    borderRadius: '20px',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
    transition: 'all 0.35s cubic-bezier(0.4, 0, 0.2, 1)',
    ...style,
  }

  return (
    <motion.div
      className={`${c.neonClass} ${hover ? 'cursor-pointer' : ''} ${className}`}
      style={combined}
      onClick={onClick}
      whileHover={
        hover
          ? {
              borderColor: c.borderHover,
              boxShadow: `${c.glow}, 0 8px 32px rgba(0,0,0,0.3)`,
              scale: 1.01,
            }
          : {}
      }
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  )
}
