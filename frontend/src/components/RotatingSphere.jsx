import React from 'react'
import { motion } from 'framer-motion'

export default function RotatingSphere({ className = '' }) {
  return (
    <div className={`relative w-full aspect-square min-h-[280px] flex items-center justify-center ${className}`}>
      {/* Outer glow */}
      <motion.div
        className="absolute w-48 h-48 rounded-full"
        style={{
          background: 'radial-gradient(circle, rgba(217,70,239,0.25) 0%, transparent 70%)',
          filter: 'blur(30px)',
        }}
        animate={{ scale: [1, 1.15, 1], opacity: [0.6, 0.9, 0.6] }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      />

      {/* Rotating ring 1 */}
      <motion.div
        className="absolute w-56 h-56 rounded-full"
        style={{
          border: '1.5px solid rgba(217,70,239,0.3)',
          boxShadow: '0 0 20px rgba(217,70,239,0.15), inset 0 0 20px rgba(217,70,239,0.05)',
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 12, repeat: Infinity, ease: 'linear' }}
      />

      {/* Rotating ring 2 (tilted) */}
      <motion.div
        className="absolute w-64 h-64 rounded-full"
        style={{
          border: '1px solid rgba(34,211,238,0.2)',
          transform: 'rotateX(60deg)',
          boxShadow: '0 0 15px rgba(34,211,238,0.1)',
        }}
        animate={{ rotate: 360 }}
        transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
      />

      {/* Rotating ring 3 */}
      <motion.div
        className="absolute w-44 h-44 rounded-full"
        style={{
          border: '1px dashed rgba(124,58,237,0.25)',
          transform: 'rotateY(45deg)',
        }}
        animate={{ rotate: -360 }}
        transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
      />

      {/* Core sphere */}
      <motion.div
        className="relative w-24 h-24 rounded-full"
        style={{
          background: 'radial-gradient(circle at 35% 35%, #f0abfc 0%, #d946ef 30%, #7c3aed 70%, #4c1d95 100%)',
          boxShadow: '0 0 40px rgba(217,70,239,0.5), 0 0 80px rgba(124,58,237,0.3), 0 0 120px rgba(217,70,239,0.15), inset 0 -4px 12px rgba(0,0,0,0.3)',
        }}
        animate={{
          boxShadow: [
            '0 0 40px rgba(217,70,239,0.5), 0 0 80px rgba(124,58,237,0.3), 0 0 120px rgba(217,70,239,0.15), inset 0 -4px 12px rgba(0,0,0,0.3)',
            '0 0 55px rgba(217,70,239,0.65), 0 0 100px rgba(124,58,237,0.4), 0 0 140px rgba(34,211,238,0.2), inset 0 -4px 12px rgba(0,0,0,0.3)',
            '0 0 40px rgba(217,70,239,0.5), 0 0 80px rgba(124,58,237,0.3), 0 0 120px rgba(217,70,239,0.15), inset 0 -4px 12px rgba(0,0,0,0.3)',
          ],
        }}
        transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
      >
        {/* Inner highlight */}
        <div
          className="absolute w-8 h-8 rounded-full"
          style={{
            background: 'radial-gradient(circle, rgba(255,255,255,0.6) 0%, transparent 70%)',
            top: '20%',
            left: '25%',
          }}
        />
      </motion.div>

      {/* Orbiting dots */}
      {[0, 1, 2].map(i => (
        <motion.div
          key={i}
          className="absolute w-2 h-2 rounded-full"
          style={{
            background: i === 0 ? '#d946ef' : i === 1 ? '#22d3ee' : '#7c3aed',
            boxShadow: `0 0 8px ${i === 0 ? '#d946ef' : i === 1 ? '#22d3ee' : '#7c3aed'}`,
          }}
          animate={{
            rotate: 360,
          }}
          transition={{
            duration: 4 + i * 2,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          <div
            className="absolute"
            style={{
              width: 2,
              height: 2,
              left: 60 + i * 15,
              top: -1,
              borderRadius: '50%',
            }}
          />
        </motion.div>
      ))}
    </div>
  )
}
