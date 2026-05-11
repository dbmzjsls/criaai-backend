import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkle, Article, Image, VideoCamera } from '@phosphor-icons/react'

const actions = [
  { to: '/app/copywriting', icon: Article, label: 'AI 文案', color: '#d946ef' },
  { to: '/app/images', icon: Image, label: '生成图片', color: '#7c3aed' },
  { to: '/app/videos', icon: VideoCamera, label: '生成视频', color: '#22d3ee' },
]

export default function FloatingActionButton() {
  const [open, setOpen] = useState(false)
  const navigate = useNavigate()

  return (
    <div className="fixed bottom-8 right-8 z-50 flex flex-col items-end gap-3">
      <AnimatePresence>
        {open && actions.map(({ to, icon: Icon, label, color }, i) => (
          <motion.button
            key={to}
            initial={{ opacity: 0, x: 20, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 20, scale: 0.8 }}
            transition={{ delay: i * 0.05 }}
            onClick={() => { navigate(to); setOpen(false) }}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-white text-sm font-medium transition-all"
            style={{
              background: `rgba(18,18,26,0.8)`,
              backdropFilter: 'blur(20px)',
              border: `1px solid ${color}40`,
              boxShadow: `0 4px 16px ${color}20`,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = `${color}80`
              e.currentTarget.style.boxShadow = `0 0 20px ${color}30, 0 4px 16px ${color}10`
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = `${color}40`
              e.currentTarget.style.boxShadow = `0 4px 16px ${color}20`
            }}
          >
            <Icon size={16} weight="duotone" />
            {label}
          </motion.button>
        ))}
      </AnimatePresence>

      <motion.button
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setOpen(!open)}
        className="w-14 h-14 rounded-full bg-gradient-to-br from-cyan-400 to-cyan-600 text-white flex items-center justify-center relative"
        style={{ boxShadow: '0 0 30px rgba(34,211,238,0.4), 0 4px 16px rgba(34,211,238,0.2)' }}
      >
        <motion.div
          animate={{ rotate: open ? 45 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <Sparkle size={24} weight="fill" />
        </motion.div>
        {/* Pulse rings */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-cyan-400/30"
          animate={{ scale: [1, 1.6], opacity: [0.6, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeOut' }}
        />
      </motion.button>
    </div>
  )
}
