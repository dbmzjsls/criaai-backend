import React, { Suspense } from 'react'
import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import {
  Article, PaintBucket, VideoCamera, Package, Folder, Sparkle
} from '@phosphor-icons/react'
import StatCard from '../components/StatCard.jsx'
import TrendChart from '../components/TrendChart.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonGlowCard from '../components/NeonGlowCard.jsx'

// Lazy-loaded 3D components
const RotatingSphere = React.lazy(() => import('../components/RotatingSphere'))
const ThreeDWaveChart = React.lazy(() => import('../components/ThreeDWaveChart'))

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i = 0) => ({
    opacity: 1, y: 0,
    transition: { duration: 0.5, delay: i * 0.1, ease: 'easeOut' }
  })
}

const statCards = [
  { label: '产品总数', icon: Package, color: 'magenta', trend: 12.5, value: 2846 },
  { label: '素材总数', icon: Folder, color: 'purple', trend: 8.3, value: 15720 },
  { label: '今日生成', icon: Sparkle, color: 'cyan', trend: 23.1, value: 847 },
]

const features = [
  { to: '/app/copywriting', icon: Article, title: 'AI 文案生成', desc: '多语言 · SEO 优化 · 营销文案', color: 'magenta', tags: ['多语言', 'SEO', '6种风格'] },
  { to: '/app/images', icon: PaintBucket, title: 'AI 图片生成', desc: '产品图 · 海报 · 广告创意', color: 'purple', tags: ['高清/超清', '6种风格', '4种比例'] },
  { to: '/app/videos', icon: VideoCamera, title: 'AI 视频生成', desc: '图生视频 · AI 产品短视频', color: 'cyan', tags: ['wan2.6', '5-10秒', '1080P'] },
]

export default function DashboardPage() {

  return (
    <div className="space-y-8 pb-24">
      {/* Page header */}
      <PageHeader
        title="千绘智能 · 工作台"
        subtitle="面向拉美电商的 AI 内容引擎 — 文案、视觉与视频，分钟级生成"
      />

      {/* === BENTO GRID LAYOUT === */}

      {/* Row 1: 3D Wave Chart (full width) */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={0}>
        <NeonGlowCard color="magenta" className="p-5 overflow-hidden relative">
          <div className="flex items-center justify-between mb-3 relative z-10">
            <div>
              <h3 className="font-heading font-semibold text-sm text-white/80">实时内容生成</h3>
              <p className="text-white/25 text-xs mt-0.5">销售转化趋势 · 紫橙渐变波形</p>
            </div>
            <div className="flex gap-1.5 bg-white/5 rounded-lg p-1">
              {['7D', '30D', '90D'].map(p => (
                <button key={p} className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${p === '7D' ? 'gradient-bg text-white shadow-[0_2px_8px_rgba(217,70,239,0.3)]' : 'text-white/40 hover:text-white/70'}`}>
                  {p}
                </button>
              ))}
            </div>
          </div>
          <Suspense fallback={
            <div className="h-[280px] flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
            </div>
          }>
            <ThreeDWaveChart />
          </Suspense>
        </NeonGlowCard>
      </motion.div>

      {/* Row 2: AI Engine Status (left 60%) + Stats (right 40%) */}
      <div className="grid lg:grid-cols-5 gap-6">
        {/* AI Engine Status with rotating sphere */}
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={1} className="lg:col-span-3">
          <NeonGlowCard color="purple" className="p-6 h-full">
            <h3 className="font-heading font-semibold text-sm text-white/80 mb-4">
              <span className="neon-text-purple">AI 引擎状态</span>
            </h3>
            <div className="grid grid-cols-3 gap-4 h-full">
              {/* 3D Sphere */}
              <div className="col-span-2">
                <Suspense fallback={
                  <div className="aspect-square min-h-[280px] flex items-center justify-center">
                    <div className="w-16 h-16 rounded-full border-4 border-neon-magenta/20 border-t-neon-magenta animate-spin" />
                  </div>
                }>
                  <RotatingSphere />
                </Suspense>
              </div>
              {/* Engine Metrics */}
              <div className="space-y-3 flex flex-col justify-center">
                <div className="space-y-1">
                  <p className="text-white/25 text-[10px] uppercase tracking-wider">GPU 负载</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-neon-green to-neon-cyan" style={{ width: '67%' }} />
                    </div>
                    <span className="font-mono text-xs text-neon-green">67%</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-white/25 text-[10px] uppercase tracking-wider">内存占用</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-neon-magenta to-neon-purple" style={{ width: '42%' }} />
                    </div>
                    <span className="font-mono text-xs text-neon-magenta">42%</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <p className="text-white/25 text-[10px] uppercase tracking-wider">任务队列</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 rounded-full bg-white/5 overflow-hidden">
                      <div className="h-full rounded-full bg-gradient-to-r from-neon-yellow to-neon-orange" style={{ width: '15%' }} />
                    </div>
                    <span className="font-mono text-xs text-neon-yellow">3 jobs</span>
                  </div>
                </div>
                <div className="pt-2 mt-2 border-t border-white/5">
                  <p className="text-white/20 text-[10px]">运行时长</p>
                  <p className="font-mono text-sm text-white/60">99.9%</p>
                </div>
              </div>
            </div>
          </NeonGlowCard>
        </motion.div>

        {/* Stats 2x2 */}
        <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={2} className="lg:col-span-2">
          <div className="grid grid-cols-2 gap-3 h-full">
            {statCards.map(({ label, icon, color, trend, value }) => (
              <StatCard
                key={label}
                label={label}
                value={value}
                icon={icon}
                color={color}
                trend={trend}
              />
            ))}
          </div>
        </motion.div>
      </div>

      {/* Row 3: Feature cards (3-column bento) */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={3}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {features.map(({ to, icon: Icon, title, desc, color, tags }) => (
            <Link to={to} key={to}>
              <NeonGlowCard hover color={color} className="p-5 h-full">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center"
                    style={{ boxShadow: color === 'magenta' ? '0 4px 16px rgba(217,70,239,0.3)' : color === 'purple' ? '0 4px 16px rgba(124,58,237,0.3)' : '0 4px 16px rgba(34,211,238,0.3)' }}>
                    <Icon size={20} weight="duotone" className="text-white" />
                  </div>
                  <div>
                    <h4 className="text-white/85 font-semibold text-sm">{title}</h4>
                    <p className="text-white/30 text-xs">{desc}</p>
                  </div>
                </div>
                <div className="flex gap-1.5 flex-wrap">
                  {tags.map(tag => (
                    <span key={tag} className="px-2 py-0.5 rounded-full bg-white/[0.03] text-white/30 text-[10px] border border-white/[0.06]">
                      {tag}
                    </span>
                  ))}
                </div>
              </NeonGlowCard>
            </Link>
          ))}
        </div>
      </motion.div>

      {/* Row 4: Trend chart (secondary) */}
      <motion.div variants={fadeUp} initial="hidden" animate="visible" custom={4}>
        <TrendChart />
      </motion.div>
    </div>
  )
}
