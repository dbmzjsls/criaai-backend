import React from 'react'
import { motion } from 'framer-motion'

export default function ThreeDWaveChart({ className = '' }) {
  return (
    <div className={`relative w-full overflow-hidden ${className}`} style={{ height: 280 }}>
      {/* Gradient background simulating deep space */}
      <div className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 50% 80%, rgba(217,70,239,0.06) 0%, transparent 60%), radial-gradient(ellipse at 30% 50%, rgba(124,58,237,0.04) 0%, transparent 50%), radial-gradient(ellipse at 70% 40%, rgba(249,115,22,0.03) 0%, transparent 50%)',
        }} />

      {/* Wave layers — simulating 3D wave surface from purple to orange */}
      <div className="absolute inset-0 flex items-end">
        <svg viewBox="0 0 1200 280" preserveAspectRatio="none" className="w-full h-full">
          <defs>
            <linearGradient id="waveGradTop" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#d946ef" stopOpacity="0.55" />
              <stop offset="35%" stopColor="#7c3aed" stopOpacity="0.35" />
              <stop offset="70%" stopColor="#f97316" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#f97316" stopOpacity="0.02" />
            </linearGradient>
            <linearGradient id="waveGradMid" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#d946ef" stopOpacity="0.3" />
              <stop offset="40%" stopColor="#7c3aed" stopOpacity="0.2" />
              <stop offset="100%" stopColor="#f97316" stopOpacity="0.04" />
            </linearGradient>
            <linearGradient id="waveGradBot" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#d946ef" stopOpacity="0.15" />
              <stop offset="50%" stopColor="#7c3aed" stopOpacity="0.08" />
              <stop offset="100%" stopColor="#f97316" stopOpacity="0.02" />
            </linearGradient>
          </defs>

          {/* Wave layer 1 (front, most visible) */}
          <motion.path
            d="M0,200 C150,150 300,240 450,180 C600,120 750,200 900,160 C1050,120 1150,170 1200,150 L1200,280 L0,280 Z"
            fill="url(#waveGradTop)"
            animate={{
              d: [
                'M0,200 C150,150 300,240 450,180 C600,120 750,200 900,160 C1050,120 1150,170 1200,150 L1200,280 L0,280 Z',
                'M0,180 C150,220 300,160 450,200 C600,240 750,170 900,190 C1050,210 1150,160 1200,180 L1200,280 L0,280 Z',
                'M0,200 C150,150 300,240 450,180 C600,120 750,200 900,160 C1050,120 1150,170 1200,150 L1200,280 L0,280 Z',
              ],
            }}
            transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
          />

          {/* Wave layer 2 (middle) */}
          <motion.path
            d="M0,220 C200,190 350,250 500,210 C650,170 800,230 950,200 C1050,180 1150,210 1200,195 L1200,280 L0,280 Z"
            fill="url(#waveGradMid)"
            animate={{
              d: [
                'M0,220 C200,190 350,250 500,210 C650,170 800,230 950,200 C1050,180 1150,210 1200,195 L1200,280 L0,280 Z',
                'M0,200 C200,235 350,185 500,220 C650,255 800,195 950,225 C1050,245 1150,200 1200,215 L1200,280 L0,280 Z',
                'M0,220 C200,190 350,250 500,210 C650,170 800,230 950,200 C1050,180 1150,210 1200,195 L1200,280 L0,280 Z',
              ],
            }}
            transition={{ duration: 11, repeat: Infinity, ease: 'easeInOut' }}
          />

          {/* Wave layer 3 (back, subtle) */}
          <motion.path
            d="M0,235 C250,210 400,255 550,230 C700,205 850,245 1000,225 C1100,215 1150,230 1200,225 L1200,280 L0,280 Z"
            fill="url(#waveGradBot)"
            animate={{
              d: [
                'M0,235 C250,210 400,255 550,230 C700,205 850,245 1000,225 C1100,215 1150,230 1200,225 L1200,280 L0,280 Z',
                'M0,225 C250,255 400,215 550,245 C700,275 850,220 1000,240 C1100,250 1150,225 1200,235 L1200,280 L0,280 Z',
                'M0,235 C250,210 400,255 550,230 C700,205 850,245 1000,225 C1100,215 1150,230 1200,225 L1200,280 L0,280 Z',
              ],
            }}
            transition={{ duration: 14, repeat: Infinity, ease: 'easeInOut' }}
          />
        </svg>
      </div>

      {/* Sparkle particles */}
      {Array.from({ length: 20 }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute w-0.5 h-0.5 rounded-full"
          style={{
            left: `${5 + Math.random() * 90}%`,
            top: `${30 + Math.random() * 60}%`,
            background: i % 3 === 0 ? '#d946ef' : i % 3 === 1 ? '#22d3ee' : '#f97316',
            boxShadow: i % 3 === 0
              ? '0 0 4px #d946ef, 0 0 8px rgba(217,70,239,0.5)'
              : i % 3 === 1
              ? '0 0 4px #22d3ee, 0 0 8px rgba(34,211,238,0.5)'
              : '0 0 4px #f97316, 0 0 8px rgba(249,115,22,0.5)',
          }}
          animate={{
            opacity: [0, 0.8, 0],
            y: [0, -15 - Math.random() * 25, 0],
          }}
          transition={{
            duration: 2 + Math.random() * 4,
            repeat: Infinity,
            delay: Math.random() * 5,
            ease: 'easeInOut',
          }}
        />
      ))}

      {/* Grid lines overlay */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03]"
        style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 40px, #d946ef 40px, #d946ef 41px), repeating-linear-gradient(90deg, transparent, transparent 60px, #7c3aed 60px, #7c3aed 61px)',
        }} />

      {/* Edge fade gradients */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-space-900/60 via-transparent to-transparent" />
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-r from-space-900/40 via-transparent to-space-900/40" />
    </div>
  )
}
