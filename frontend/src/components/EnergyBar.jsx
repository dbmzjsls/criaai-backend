import React from 'react'
import { motion } from 'framer-motion'

export default function EnergyBar({
  value = 0,
  max = 100,
  label = '',
  showValue = true,
  color = 'magenta',
  height = 'h-2',
  className = '',
}) {
  const pct = Math.min(100, Math.max(0, (value / max) * 100))

  const gradients = {
    magenta: 'from-neon-cyan via-neon-magenta to-neon-purple',
    cyan: 'from-neon-cyan via-neon-cyan to-neon-magenta',
    fire: 'from-neon-yellow via-neon-orange to-neon-magenta',
  }
  const grad = gradients[color] || gradients.magenta

  return (
    <div className={`w-full ${className}`}>
      {(label || showValue) && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-xs text-white/40">{label}</span>
          {showValue && (
            <span className="text-xs font-mono text-white/60 tabular-nums">
              {value}/{max}
            </span>
          )}
        </div>
      )}
      <div className={`relative ${height} rounded-full overflow-hidden bg-white/5`}>
        <motion.div
          className={`absolute inset-y-0 left-0 rounded-full bg-gradient-to-r ${grad}`}
          style={{ backgroundSize: '200% 100%' }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1] }}
        />
        {/* Shine effect */}
        <motion.div
          className="absolute inset-y-0 w-20 bg-gradient-to-r from-transparent via-white/10 to-transparent"
          animate={{ left: ['-20%', '120%'] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear', repeatDelay: 1.5 }}
        />
      </div>
    </div>
  )
}
