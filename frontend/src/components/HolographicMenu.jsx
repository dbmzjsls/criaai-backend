import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

export default function HolographicMenu({
  show = false,
  items = [],
  position = { x: 0, y: 0 },
}) {
  return (
    <AnimatePresence>
      {show && (
        <motion.div
          className="absolute z-50 py-2 px-2 rounded-2xl"
          style={{
            background: 'rgba(18, 18, 26, 0.9)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            border: '1px solid rgba(217, 70, 239, 0.25)',
            boxShadow: '0 0 30px rgba(217, 70, 239, 0.15), 0 8px 32px rgba(0,0,0,0.5)',
            left: position.x,
            top: position.y,
          }}
          initial={{ opacity: 0, scale: 0.9, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 10 }}
          transition={{ duration: 0.2 }}
        >
          {items.map((item) => (
            <motion.button
              key={item.key}
              onClick={item.onClick}
              className="flex items-center gap-2 w-full px-3 py-2 rounded-xl text-sm text-white/70 hover:text-white hover:bg-white/5 transition-all duration-200 whitespace-nowrap"
              whileHover={{ x: 4 }}
            >
              {item.icon && <item.icon size={16} className="text-neon-magenta/60" />}
              {item.label}
            </motion.button>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  )
}
