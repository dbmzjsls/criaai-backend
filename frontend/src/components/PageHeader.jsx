import React from 'react'
import { motion } from 'framer-motion'

export default function PageHeader({ title, subtitle, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center justify-between flex-wrap gap-3 mb-6"
    >
      <div>
        <h2 className="font-display text-2xl lg:text-3xl font-bold text-white neon-text-magenta mb-1">
          {title}
        </h2>
        {subtitle && <p className="text-white/35 text-sm font-body">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </motion.div>
  )
}
