import React from 'react'
import { motion } from 'framer-motion'
import ScrollingNumber from './ScrollingNumber'

const colorMap = {
  magenta: {
    iconBg: 'from-fuchsia-500 to-purple-600',
    iconGlow: 'rgba(217,70,239,0.3)',
    border: 'rgba(217, 70, 239, 0.15)',
    label: 'text-white/40',
    cardBg: 'rgba(18,18,26,0.5)',
  },
  purple: {
    iconBg: 'from-purple-500 to-violet-600',
    iconGlow: 'rgba(124,58,237,0.3)',
    border: 'rgba(124, 58, 237, 0.15)',
    label: 'text-white/40',
    cardBg: 'rgba(18,18,26,0.5)',
  },
  cyan: {
    iconBg: 'from-cyan-500 to-teal-500',
    iconGlow: 'rgba(34,211,238,0.3)',
    border: 'rgba(34, 211, 238, 0.15)',
    label: 'text-white/40',
    cardBg: 'rgba(18,18,26,0.5)',
  },
  pink: {
    iconBg: 'from-pink-500 to-rose-500',
    iconGlow: 'rgba(236,72,153,0.3)',
    border: 'rgba(236, 72, 153, 0.15)',
    label: 'text-white/40',
    cardBg: 'rgba(18,18,26,0.5)',
  },
}

export default function StatCard({ label, value, icon: Icon, trend, color = 'magenta', loading = false }) {
  const c = colorMap[color] || colorMap.magenta

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-2xl relative overflow-hidden"
      style={{
        background: c.cardBg,
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: `1px solid ${c.border}`,
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <span className={`text-xs font-medium ${c.label}`}>{label}</span>
        {Icon && (
          <motion.div
            className={`w-9 h-9 rounded-xl bg-gradient-to-br ${c.iconBg} flex items-center justify-center`}
            style={{ boxShadow: `0 4px 16px ${c.iconGlow}` }}
          >
            <Icon size={18} weight="duotone" className="text-white" />
          </motion.div>
        )}
      </div>
      {loading ? (
        <div className="h-8 w-20 rounded-lg bg-white/5 animate-pulse" />
      ) : (
        <p className="text-2xl font-bold text-white font-mono tracking-tight">
          <ScrollingNumber value={typeof value === 'number' ? value : 0} duration={0.8} />
          {typeof value !== 'number' && <span>{value ?? '—'}</span>}
        </p>
      )}
      {trend !== undefined && (
        <div className="flex items-center gap-1 mt-1.5">
          <span className={`text-xs font-mono font-medium ${trend >= 0 ? 'text-neon-green neon-text-green' : 'text-red-400'}`}>
            {trend >= 0 ? '▲ +' : '▼ '}{Math.abs(trend)}%
          </span>
          <span className="text-white/20 text-[10px]">较上周</span>
        </div>
      )}
    </motion.div>
  )
}
