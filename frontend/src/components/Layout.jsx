import React, { useState, Suspense } from 'react'
import { Outlet, NavLink } from 'react-router-dom'
import {
  HomeIcon, DocumentTextIcon, PhotoIcon, VideoCameraIcon,
  FolderIcon, FilmIcon, CubeIcon, Bars3Icon, XMarkIcon, BoltIcon, BanknotesIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline'
import FloatingActionButton from './FloatingActionButton'
import RechargeModal from './RechargeModal'
import logoUrl from '../assets/logo.svg'

const ParticleBackground = React.lazy(() => import('./ParticleBackground'))

const navItems = [
  { to: '/app/dashboard', icon: HomeIcon, label: '工作台' },
  { to: '/app/pipeline', icon: BoltIcon, label: '一条龙' },
  { to: '/app/products', icon: CubeIcon, label: '产品管理' },
  { to: '/app/copywriting', icon: DocumentTextIcon, label: 'AI 文案' },
  { to: '/app/images', icon: PhotoIcon, label: '图片生成' },
  { to: '/app/videos', icon: VideoCameraIcon, label: '视频生成' },
  { to: '/app/assets', icon: FolderIcon, label: '素材库' },
  { to: '/app/media', icon: FilmIcon, label: '媒体库' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [showRecharge, setShowRecharge] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden relative grid-bg"
      style={{ background: 'var(--space-bg)' }}>

      {/* Particle background (lazy loaded) */}
      <Suspense fallback={null}>
        <ParticleBackground />
      </Suspense>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/70 z-20 lg:hidden backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-30
        w-64 flex flex-col
        transform transition-transform duration-300 ease-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}
        style={{
          background: 'rgba(10,10,15,0.9)',
          backdropFilter: 'blur(30px)',
          WebkitBackdropFilter: 'blur(30px)',
          borderRight: '1px solid rgba(217,70,239,0.1)',
          boxShadow: '2px 0 40px rgba(0,0,0,0.3)',
        }}
      >
        {/* Logo */}
        <div className="px-6 py-6 flex items-center gap-3" style={{ borderBottom: '1px solid rgba(217,70,239,0.08)' }}>
          <img src={logoUrl} alt="千绘智能" className="w-10 h-10"
            style={{ filter: 'drop-shadow(0 0 10px rgba(217,70,239,0.4))' }} />
          <div>
            <h1 className="font-display text-lg font-bold"
              style={{ background: 'linear-gradient(135deg, #f0abfc, #d946ef, #7c3aed)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              千绘智能
            </h1>
            <p className="text-[10px] text-neon-cyan/40 tracking-wider">千绘智能 · 工作室</p>
          </div>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden ml-auto text-white/40 hover:text-white/70">
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-5 space-y-1 overflow-y-auto">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) => `
                flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium
                transition-all duration-200 relative
                ${isActive
                  ? 'text-white font-semibold sidebar-link-active'
                  : 'sidebar-link-inactive'
                }
              `}
            >
              {({ isActive }) => (
                <>
                  {isActive && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full"
                      style={{ background: 'linear-gradient(180deg, #d946ef, #7c3aed)', boxShadow: '0 0 8px rgba(217,70,239,0.5)' }} />
                  )}
                  <Icon className="w-[18px] h-[18px] shrink-0" style={{ opacity: isActive ? 1 : 0.5 }} />
                  {label}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Bottom user area */}
        <div className="px-4 py-4 space-y-2" style={{ borderTop: '1px solid rgba(217,70,239,0.08)' }}>
          {/* 充值入口 — 磨砂金属质感 */}
          <button
            onClick={() => setShowRecharge(true)}
            className="relative w-full py-2 rounded-[12px] text-xs font-semibold select-none overflow-hidden
              transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"
            style={{
              background: `
                linear-gradient(145deg, #4e4680 0%, #352d62 55%, #261f4a 100%)
              `,
              border: '1px solid rgba(167,139,250,0.2)',
              color: 'rgba(255,255,255,0.88)',
              boxShadow: `
                2px 3px 8px rgba(99,80,200,0.2),
                inset -2px -2px 5px rgba(200,180,255,0.04),
                inset 2px 2px 6px rgba(0,0,0,0.25)
              `,
            }}
          >
            {/* 噪声纹理 */}
            <span
              className="absolute inset-0 pointer-events-none"
              style={{
                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.08'/%3E%3C/svg%3E")`,
                mixBlendMode: 'soft-light',
                opacity: 0.35,
              }}
            />
            {/* 左上高光线 */}
            <span
              className="absolute top-[3px] left-[8%] right-[8%] h-px rounded-full pointer-events-none"
              style={{
                background: 'linear-gradient(90deg, transparent, rgba(200,180,255,0.15), transparent)',
              }}
            />
            <span className="relative flex items-center justify-center gap-1.5">
              <BanknotesIcon className="w-3.5 h-3.5" />
              账户充值
            </span>
          </button>

          <div className="flex items-center gap-3 px-2 py-2 rounded-xl hover:bg-white/[0.04] transition-colors cursor-pointer">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-fuchsia-500 to-purple-600 flex items-center justify-center"
              style={{ boxShadow: '0 2px 12px rgba(217,70,239,0.3)' }}>
              <UserCircleIcon className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white/70 text-xs font-medium truncate">管理员</p>
              <p className="text-white/20 text-[10px] truncate">admin@criaai.com</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0 relative z-10">
        {/* Mobile header */}
        <header className="lg:hidden flex items-center justify-between px-4 py-3"
          style={{ background: 'rgba(10,10,15,0.85)', backdropFilter: 'blur(20px)', borderBottom: '1px solid rgba(217,70,239,0.08)' }}>
          <button onClick={() => setSidebarOpen(true)} className="text-white/50 hover:text-white/80">
            <Bars3Icon className="w-6 h-6" />
          </button>
          <div className="flex items-center gap-2">
            <img src={logoUrl} alt="千绘智能" className="w-7 h-7" />
            <h1 className="font-display text-base font-bold gradient-text">千绘智能</h1>
          </div>
          <div className="w-6" />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-6 relative">
          <Outlet />
        </main>
      </div>

      {/* Floating Action Button */}
      <FloatingActionButton />

      {/* 充值弹窗 */}
      <RechargeModal
        isOpen={showRecharge}
        onClose={() => setShowRecharge(false)}
        onSuccess={(amount) => console.log('充值成功: ¥' + amount)}
      />
    </div>
  )
}
