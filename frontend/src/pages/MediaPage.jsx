import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { FilmStrip, UploadSimple } from '@phosphor-icons/react'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import axiosInstance from '../api/axios.js'
import { resolveMediaUrl } from '../utils/resolveMediaUrl.js'

const fadeUp = { hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }

export default function MediaPage() {
  const [media, setMedia] = useState([])
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    axiosInstance.get('/v1/media/')
      .then(res => setMedia(res.data.items || res.data || []))
      .catch(() => setMedia([]))
      .finally(() => setLoading(false))
  }, [])

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await axiosInstance.post('/v1/media/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setMedia(prev => [res.data, ...prev])
    } catch (e) {
      console.error(e)
    } finally { setUploading(false) }
  }

  const filtered = media.filter(m =>
    (m.filename || m.name || '').toLowerCase().includes(search.toLowerCase())
  )

  return (
    <motion.div variants={fadeUp} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader
        title="媒体库"
        subtitle="上传与管理原始媒体文件"
        action={
          <div className="flex gap-3">
            <NeonInput
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="搜索..."
              className="!w-40 !py-2 !text-xs"
            />
            <label className="btn-magenta flex items-center gap-2 cursor-pointer !rounded-full text-xs">
              <UploadSimple size={16} />
              {uploading ? '上传中...' : '上传文件'}
              <input type="file" className="hidden" onChange={handleUpload} accept="image/*,video/*" />
            </label>
          </div>
        }
      />

      {loading ? (
        <div className="flex items-center justify-center h-40 text-white/30">
          <div className="w-6 h-6 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin mr-3" />
          加载中...
        </div>
      ) : filtered.length === 0 ? (
        <NeonGlowCard color="magenta" className="p-12 flex flex-col items-center gap-3">
          <FilmStrip size={48} className="text-white/10" />
          <p className="text-white/30 text-sm">暂无媒体文件，上传文件即可开始</p>
        </NeonGlowCard>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {filtered.map((item, i) => (
            <NeonGlowCard key={item.id || i} hover color={i % 2 === 0 ? 'magenta' : 'purple'} className="p-3">
              <div className="aspect-square bg-space-700/50 rounded-xl mb-2 overflow-hidden flex items-center justify-center border border-white/5">
                {item.file_url || item.url ? (
                  item.media_type === 'video' ? (
                    <video src={resolveMediaUrl(item.file_url || item.url)} className="w-full h-full object-cover rounded-xl" />
                  ) : (
                    <img src={resolveMediaUrl(item.file_url || item.url)} alt={item.filename} className="w-full h-full object-cover rounded-xl" />
                  )
                ) : (
                  <FilmStrip size={32} className="text-white/10" />
                )}
              </div>
              <p className="text-white/70 text-xs truncate">{item.filename || item.name || '未命名'}</p>
              <p className="text-white/25 text-[10px] mt-0.5">{item.media_type || '媒体'}</p>
            </NeonGlowCard>
          ))}
        </div>
      )}
    </motion.div>
  )
}
