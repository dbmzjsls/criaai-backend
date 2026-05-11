import React, { Suspense } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, Sparkle } from '@phosphor-icons/react'
import logoUrl from '../assets/logo.svg'

const ParticleBackground = React.lazy(() => import('../components/ParticleBackground'))

export default function LoginPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden"
      style={{ background: 'radial-gradient(ellipse at 50% 50%, #1a0a2e 0%, #0a0a0f 60%, #000000 100%)' }}>

      {/* Particle background */}
      <Suspense fallback={null}>
        <ParticleBackground />
      </Suspense>

      {/* Extra glow orbs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-[500px] h-[500px] rounded-full opacity-[0.15]"
          style={{ background: 'radial-gradient(circle, #d946ef 0%, transparent 70%)', filter: 'blur(80px)' }} />
        <div className="absolute bottom-1/4 right-1/4 w-[400px] h-[400px] rounded-full opacity-[0.12]"
          style={{ background: 'radial-gradient(circle, #7c3aed 0%, transparent 70%)', filter: 'blur(80px)' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full opacity-[0.08]"
          style={{ background: 'radial-gradient(circle, #22d3ee 0%, transparent 70%)', filter: 'blur(100px)' }} />
      </div>

      {/* Rotating geometric rings */}
      <div className="pointer-events-none absolute inset-0">
        <svg className="animate-spin-slow absolute -top-40 -left-40 w-[600px] h-[600px] opacity-[0.06]"
          viewBox="0 0 300 300" fill="none">
          <circle cx="150" cy="150" r="140" stroke="#d946ef" strokeWidth="0.5" fill="none"/>
          <circle cx="150" cy="150" r="110" stroke="#7c3aed" strokeWidth="0.4" fill="none"/>
          <circle cx="150" cy="150" r="80" stroke="#22d3ee" strokeWidth="0.3" fill="none"/>
          <circle cx="150" cy="150" r="50" stroke="#ec4899" strokeWidth="0.2" fill="none"/>
        </svg>
        <svg className="animate-spin-slow-reverse absolute -bottom-40 -right-40 w-[500px] h-[500px] opacity-[0.06]"
          viewBox="0 0 300 300" fill="none">
          <polygon points="150,10 290,280 10,280" stroke="#d946ef" strokeWidth="0.5" fill="none"/>
          <polygon points="150,40 260,250 40,250" stroke="#7c3aed" strokeWidth="0.4" fill="none"/>
          <polygon points="150,70 230,220 70,220" stroke="#22d3ee" strokeWidth="0.3" fill="none"/>
        </svg>
      </div>

      {/* Beam sweep line */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute top-1/3 left-0 w-full h-px opacity-30"
          style={{ background: 'linear-gradient(90deg, transparent, #d946ef, #22d3ee, transparent)', animation: 'beamSweep 4s linear infinite' }} />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: 'easeOut' }}
        className="relative z-10 flex flex-col items-center text-center px-8"
      >
        {/* Logo */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <img src={logoUrl} alt="千绘智能" className="w-32 h-32"
            style={{ filter: 'drop-shadow(0 0 30px rgba(217,70,239,0.4)) drop-shadow(0 0 60px rgba(124,58,237,0.2))' }} />
        </motion.div>

        {/* Title */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mb-4"
        >
          <h1 className="font-display text-6xl md:text-7xl font-bold mb-4"
            style={{
              background: 'linear-gradient(135deg, #f0abfc 0%, #d946ef 30%, #7c3aed 60%, #22d3ee 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
              filter: 'drop-shadow(0 2px 16px rgba(217,70,239,0.5)) drop-shadow(0 0 40px rgba(124,58,237,0.25))',
            }}>
            千绘智能
          </h1>
          <div className="flex items-center justify-center gap-3 text-white/40 text-sm tracking-wide">
            <Sparkle size={14} className="text-fuchsia-400" weight="fill" />
            <span className="font-heading">CriaA.I. — 拉美电商 · AI 内容工作室</span>
            <Sparkle size={14} className="text-cyan-400" weight="fill" />
          </div>
        </motion.div>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.6 }}
          className="text-white/20 text-base mb-12 max-w-sm leading-relaxed font-body"
        >
          智能文案 · 视觉创作 · 视频生成<br/>
          一站式 AI 营销内容解决方案
        </motion.p>

        {/* ENTER button */}
        <motion.button
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.8 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => navigate('/app/dashboard')}
          className="btn-neon group flex items-center gap-3 px-12 py-5 text-white font-bold text-xl tracking-widest"
        >
          <span className="font-display">进入平台</span>
          <ArrowRight size={22} className="transition-transform duration-300 group-hover:translate-x-1" />
        </motion.button>

        {/* Bottom dots */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 1.0 }}
          className="flex gap-3 mt-12"
        >
          {[0, 1, 2].map(i => (
            <motion.div
              key={i}
              className="w-2 h-2 rounded-full"
              style={{ background: i === 1 ? '#d946ef' : '#22d3ee', opacity: i === 1 ? 1 : 0.3 }}
              animate={i === 1 ? { scale: [1, 1.3, 1], opacity: [1, 0.7, 1] } : {}}
              transition={{ duration: 2, repeat: Infinity }}
            />
          ))}
        </motion.div>
      </motion.div>
    </div>
  )
}
