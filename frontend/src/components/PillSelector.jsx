import React from 'react'
import { motion } from 'framer-motion'

export default function PillSelector({
  options = [],
  selected = [],
  onChange,
  multi = true,
  className = '',
}) {
  const isSelected = (key) => (multi ? selected.includes(key) : selected === key)

  const handleClick = (key) => {
    if (multi) {
      if (selected.includes(key)) {
        onChange(selected.filter((s) => s !== key))
      } else {
        onChange([...selected, key])
      }
    } else {
      onChange(key)
    }
  }

  return (
    <div className={`flex flex-wrap gap-2 ${className}`}>
      {options.map(({ key, label, icon: Icon }) => {
        const active = isSelected(key)
        return (
          <motion.button
            key={key}
            onClick={() => handleClick(key)}
            whileTap={{ scale: 0.96 }}
            whileHover={{ scale: 1.03 }}
            className={`relative flex items-center gap-1.5 px-4 py-1.5 rounded-full text-xs font-medium transition-all duration-300 ${
              active
                ? 'pill-tag-active'
                : 'pill-tag'
            }`}
          >
            {Icon && <Icon size={14} />}
            {label}
            {/* Flowing light effect when active */}
            {active && (
              <motion.div
                className="absolute inset-0 rounded-full opacity-0"
                style={{
                  background:
                    'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                  backgroundSize: '200% 100%',
                }}
                animate={{ opacity: [0, 1, 0], backgroundPosition: ['200% 0', '-200% 0'] }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              />
            )}
          </motion.button>
        )
      })}
    </div>
  )
}
