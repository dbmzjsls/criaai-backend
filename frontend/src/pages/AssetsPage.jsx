import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Folder } from '@phosphor-icons/react'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import axiosInstance from '../api/axios.js'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

const typeColors = { copywriting: 'cyan', image: 'magenta', video: 'purple' }

export default function AssetsPage() {
  const [assets, setAssets] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    axiosInstance.get('/v1/assets/')
      .then(res => {
        const data = res.data.assets || res.data.items || res.data || []
        setAssets(Array.isArray(data) ? data : [])
      })
      .catch(() => setAssets([]))
      .finally(() => setLoading(false))
  }, [])

  const filtered = Array.isArray(assets) ? assets.filter(a =>
    (a.name || a.filename || a.asset_type || '').toLowerCase().includes(search.toLowerCase())
  ) : []

  return (
    <motion.div variants={fadeUp} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader
        title="素材库"
        subtitle="管理所有生成的图片、文案与视频素材"
        action={
          <NeonInput
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="搜索素材..."
            className="!w-48 !py-2 !text-xs"
          />
        }
      />

      {loading ? (
        <div className="flex items-center justify-center h-40 text-white/30">
          <div className="w-6 h-6 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin mr-3" />
          加载中...
        </div>
      ) : filtered.length === 0 ? (
        <NeonGlowCard color="magenta" className="p-12 flex flex-col items-center gap-3">
          <Folder size={48} className="text-white/10" />
          <p className="text-white/30 text-sm">暂无素材</p>
        </NeonGlowCard>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map((asset, i) => {
            const c = typeColors[asset.asset_type] || 'magenta'
            return (
              <motion.div key={asset.id || i}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.04 }}>
                <NeonGlowCard hover color={c} className="p-3">
                  <div className="aspect-square bg-space-700/50 rounded-xl mb-2 overflow-hidden flex items-center justify-center border border-white/5">
                    {asset.url || asset.file_url ? (
                      <img src={asset.url || asset.file_url} alt={asset.name} className="w-full h-full object-cover rounded-xl" />
                    ) : (
                      <Folder size={32} className="text-white/10" />
                    )}
                  </div>
                  <p className="text-white/70 text-xs truncate">{asset.name || asset.filename || '未命名'}</p>
                  <p className="text-white/25 text-[10px] mt-0.5 capitalize">{asset.asset_type || asset.type || '素材'}</p>
                </NeonGlowCard>
              </motion.div>
            )
          })}
        </div>
      )}
    </motion.div>
  )
}
