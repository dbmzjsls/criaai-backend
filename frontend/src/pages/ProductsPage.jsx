import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Package, Plus, Pencil, Trash, MagnifyingGlass, Microphone } from '@phosphor-icons/react'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import HolographicMenu from '../components/HolographicMenu.jsx'
import axiosInstance from '../api/axios.js'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

export default function ProductsPage() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ name: '', description: '', category: '' })
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState('')
  const [hoveredId, setHoveredId] = useState(null)
  const [menuPos, setMenuPos] = useState({ x: 0, y: 0 })

  useEffect(() => {
    axiosInstance.get('/v1/products/')
      .then(res => setProducts(res.data.items || res.data || []))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false))
  }, [])

  const save = async (e) => {
    e.preventDefault()
    setSaving(true)
    try {
      const res = await axiosInstance.post('/v1/products/', form)
      setProducts(prev => [res.data, ...prev])
      setShowForm(false)
      setForm({ name: '', description: '', category: '' })
    } catch (e) { console.error(e) }
    finally { setSaving(false) }
  }

  const filtered = products.filter(p =>
    (p.name || p.product_name || '').toLowerCase().includes(search.toLowerCase())
  )

  const handleCardHover = (id, e) => {
    setHoveredId(id)
    const rect = e.currentTarget.getBoundingClientRect()
    setMenuPos({ x: rect.right - 160, y: rect.top - 10 })
  }

  return (
    <motion.div variants={fadeUp} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader
        title="产品管理"
        subtitle="管理用于 AI 内容生成的产品档案"
        action={
          <button onClick={() => setShowForm(!showForm)} className="btn-magenta flex items-center gap-2 !rounded-full">
            <Plus size={16} />
            添加产品
          </button>
        }
      />

      {/* Glowing search bar */}
      <div className="max-w-xl mx-auto">
        <NeonInput
          value={search}
          onChange={e => setSearch(e.target.value)}
          placeholder="搜索产品..."
          icon={MagnifyingGlass}
          className="!py-3.5 !text-base !rounded-full"
        />
        {/* AI voice ripple */}
        <div className="flex justify-center mt-3">
          <motion.div className="w-8 h-8 rounded-full bg-neon-magenta/10 border border-neon-magenta/20 flex items-center justify-center cursor-pointer"
            animate={{ boxShadow: ['0 0 0 0 rgba(217,70,239,0.2)', '0 0 0 12px rgba(217,70,239,0)', '0 0 0 0 rgba(217,70,239,0.2)'] }}
            transition={{ duration: 2, repeat: Infinity }}>
            <Microphone size={14} className="text-neon-magenta/60" />
          </motion.div>
        </div>
      </div>

      {/* Add form */}
      {showForm && (
        <NeonGlowCard color="purple" className="p-6 max-w-2xl mx-auto">
          <h3 className="text-white/70 font-heading font-semibold text-sm mb-4">新建产品</h3>
          <form onSubmit={save} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <NeonInput
                value={form.name}
                onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
                placeholder="产品名称"
                required
              />
              <NeonInput
                value={form.category}
                onChange={e => setForm(p => ({ ...p, category: e.target.value }))}
                placeholder="例如：护肤品"
              />
            </div>
            <NeonInput
              value={form.description}
              onChange={e => setForm(p => ({ ...p, description: e.target.value }))}
              placeholder="产品特点、卖点描述..."
              multiline rows={3}
            />
            <div className="flex gap-3">
              <button type="submit" disabled={saving} className="btn-magenta">
                {saving ? '保存中...' : '保存产品'}
              </button>
              <button type="button" onClick={() => setShowForm(false)}
                className="px-6 py-2 rounded-full bg-white/5 text-white/50 text-sm border border-white/8 hover:bg-white/10 transition-all">
                取消
              </button>
            </div>
          </form>
        </NeonGlowCard>
      )}

      {/* Product waterfall cards */}
      {loading ? (
        <div className="flex items-center justify-center h-40 text-white/30">
          <div className="w-6 h-6 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin mr-3" />
          加载中...
        </div>
      ) : filtered.length === 0 ? (
        <NeonGlowCard className="p-12 flex flex-col items-center gap-3">
          <Package size={48} className="text-white/10" />
          <p className="text-white/30 text-sm">暂无产品，添加第一个产品吧</p>
        </NeonGlowCard>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((p, i) => (
            <div key={p.product_id || p.id || i} className="relative"
              onMouseEnter={e => handleCardHover(p.product_id || p.id || i, e)}
              onMouseLeave={() => setHoveredId(null)}>
              <NeonGlowCard hover color={i % 3 === 0 ? 'magenta' : i % 3 === 1 ? 'purple' : 'cyan'} className="p-0 overflow-hidden">
                {/* Product image placeholder */}
                <div className="h-36 bg-gradient-to-br from-space-700 via-space-800 to-space-900 flex items-center justify-center relative">
                  <Package size={40} className="text-white/8" />
                  <div className="absolute inset-0 bg-gradient-to-t from-space-800/80 to-transparent" />
                </div>

                {/* Data overlay */}
                <div className="p-4 relative">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="text-white/85 font-semibold text-sm truncate pr-2">{p.name || p.product_name}</h4>
                    {/* Status capsule */}
                    <span className="status-ready shrink-0">就绪</span>
                  </div>
                  <p className="text-white/25 text-xs line-clamp-2 mb-2">{p.description || '暂无描述'}</p>
                  {(p.category) && (
                    <span className="pill-tag text-[10px]">{p.category}</span>
                  )}
                </div>
              </NeonGlowCard>

              {/* Holographic quick edit menu */}
              <HolographicMenu
                show={hoveredId === (p.product_id || p.id || i)}
                position={menuPos}
                items={[
                  { key: 'edit', label: '快速编辑', icon: Pencil },
                  { key: 'delete', label: '删除', icon: Trash },
                ]}
              />
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}
