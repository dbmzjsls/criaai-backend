import React from 'react'
import { motion } from 'framer-motion'

export default function ConveyorCard({
  children,
  index = 0,
  active = false,
  className = '',
}) {
  const rotate = (index - 1) * 2
  const translateY = (index - 1) * -8

  return (
    <motion.div
      className={`relative p-4 rounded-2xl transition-all duration-500 ${className}`}
      style={{
        background: active
          ? 'rgba(18, 18, 26, 0.8)'
          : 'rgba(18, 18, 26, 0.4)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        border: active
          ? '1px solid rgba(217, 70, 239, 0.3)'
          : '1px solid rgba(255, 255, 255, 0.05)',
        transform: `perspective(600px) rotateX(${rotate}deg) translateY(${translateY}px)`,
        zIndex: active ? 10 : 5 - index,
        marginTop: index > 0 ? '-12px' : '0',
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.5 }}
      whileHover={
        active
          ? { scale: 1.02, borderColor: 'rgba(217, 70, 239, 0.5)' }
          : {}
      }
    >
      {children}
    </motion.div>
  )
}
