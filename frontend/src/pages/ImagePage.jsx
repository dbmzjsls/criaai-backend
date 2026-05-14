import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Image as ImageIcon, Sparkle, DownloadSimple } from '@phosphor-icons/react'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import PillSelector from '../components/PillSelector.jsx'
import NeonSlider from '../components/NeonSlider.jsx'
import ScanningLine from '../components/ScanningLine.jsx'
import axiosInstance from '../api/axios.js'
import { resolveMediaUrl } from '../utils/resolveMediaUrl.js'

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } }

export default function ImagePage() {
  const [prompt, setPrompt] = useState('')
  const [style, setStyle] = useState('luxury')
  const [ratio, setRatio] = useState('1:1')
  const [quality, setQuality] = useState('hd')
  const [lighting, setLighting] = useState('natural')
  const [composition, setComposition] = useState('center')
  const [loading, setLoading] = useState(false)
  const [imageUrl, setImageUrl] = useState(null)
  const [error, setError] = useState('')

  const generate = async () => {
    if (!prompt.trim()) return
    setLoading(true); setError(''); setImageUrl(null)
    try {
      const res = await axiosInstance.post('/v1/images/generate', { prompt, style }, { timeout: 180000 })
      const url = res.data.image_url || res.data.url
      if (!url) throw new Error('No image URL returned')
      if (url.includes('<html') || url.includes('<!DOCTYPE')) throw new Error('Server error')
      setImageUrl(resolveMediaUrl(url))
    } catch (e) {
      const detail = e.response?.data?.detail
      const detailMsg = (typeof detail === 'object' && detail) ? detail.message : detail
      if (e.code === 'ECONNABORTED') setError('生成超时，图片生成通常需要1-3分钟')
      else if (e.response?.status === 504) setError('服务器超时')
      else if (e.response?.status >= 500) setError('服务器错误')
      else setError(detailMsg || ('生成失败：' + e.message))
    } finally { setLoading(false) }
  }

  const downloadImage = async () => {
    if (!imageUrl) return
    try {
      if (imageUrl.includes('<html') || imageUrl.includes('<!DOCTYPE')) { setError('无效的图片链接'); return }
      const response = await fetch(imageUrl)
      const contentType = response.headers.get('content-type')
      if (!contentType || !contentType.startsWith('image/')) { setError('非图片文件'); return }
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `generated-image-${Date.now()}.png`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e) { setError('下载失败：' + e.message) }
  }

  return (
    <motion.div variants={container} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader title="AI 图片生成" subtitle="AI 驱动的产品图、海报与广告创意" />

      {/* Left-right split layout */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* LEFT: Control Panel (38%) */}
        <motion.div variants={item} className="lg:w-[38%] shrink-0">
          <div className="space-y-5 p-6 rounded-2xl"
            style={{
              background: 'rgba(18,18,26,0.6)',
              backdropFilter: 'blur(24px)',
              WebkitBackdropFilter: 'blur(24px)',
              border: '1px solid rgba(217,70,239,0.12)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            }}>
            <h3 className="text-white/70 font-heading font-semibold text-sm">控制面板</h3>

            {/* Prompt */}
            <NeonInput
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="例如：高端护肤品、白色背景、奢华风格..."
              multiline rows={3}
            />

            {/* Style pills */}
            <div>
              <label className="block text-xs text-white/40 mb-2">风格</label>
              <PillSelector multi={false} selected={style} onChange={setStyle}
                options={[
                  { key: 'luxury', label: '奢华' },
                  { key: 'minimal', label: '极简' },
                  { key: 'vibrant', label: '鲜艳' },
                  { key: 'dark', label: '暗黑' },
                  { key: 'vintage', label: '复古' },
                  { key: 'modern', label: '现代' },
                ]} />
            </div>

            {/* Aspect Ratio */}
            <div>
              <label className="block text-xs text-white/40 mb-2">宽高比例</label>
              <PillSelector multi={false} selected={ratio} onChange={setRatio}
                options={[
                  { key: '1:1', label: '1:1 正方形' },
                  { key: '4:3', label: '4:3' },
                  { key: '16:9', label: '16:9' },
                  { key: '9:16', label: '9:16 故事' },
                ]} />
            </div>

            {/* Quality slider */}
            <NeonSlider
              value={{ standard: 0, hd: 50, ultra: 100 }[quality] || 50}
              onChange={(v) => setQuality(v < 33 ? 'standard' : v < 80 ? 'hd' : 'ultra')}
              label="画质"
              rightLabel={quality === 'standard' ? '标准' : quality === 'hd' ? '高清' : '超清'}
              color="magenta"
              step={1}
            />

            {/* Lighting pills */}
            <div>
              <label className="block text-xs text-white/40 mb-2">光照</label>
              <PillSelector multi={false} selected={lighting} onChange={setLighting}
                options={[
                  { key: 'natural', label: '自然光' },
                  { key: 'studio', label: '影棚光' },
                  { key: 'backlight', label: '逆光' },
                  { key: 'soft', label: '柔光' },
                ]} />
            </div>

            {/* Composition pills */}
            <div>
              <label className="block text-xs text-white/40 mb-2">构图</label>
              <PillSelector multi={false} selected={composition} onChange={setComposition}
                options={[
                  { key: 'center', label: '居中' },
                  { key: 'rule3', label: '三分法' },
                  { key: 'closeup', label: '特写' },
                  { key: 'wide', label: '广角' },
                ]} />
            </div>

            {/* Generate button */}
            <button
              onClick={generate}
              disabled={loading || !prompt.trim()}
              className="btn-neon w-full py-3.5 text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              <Sparkle size={16} weight="fill" />
              {loading ? '生成中...' : '生成图片'}
            </button>
          </div>
        </motion.div>

        {/* RIGHT: Preview Canvas (62%) */}
        <motion.div variants={item} className="flex-1">
          <div className="h-full rounded-2xl p-6 flex flex-col"
            style={{
              background: 'radial-gradient(ellipse at center, #1a1a2e 0%, #0a0a0f 60%, #000 100%)',
              border: '1px solid rgba(124,58,237,0.1)',
              boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
            }}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white/70 font-heading font-semibold text-sm flex items-center gap-2">
                <ImageIcon size={16} className="text-neon-magenta" /> 预览画布
              </h3>
              {imageUrl && (
                <button onClick={downloadImage} className="flex items-center gap-1 text-xs text-neon-cyan/70 hover:text-neon-cyan transition-colors">
                  <DownloadSimple size={14} /> 下载
                </button>
              )}
            </div>

            {/* Canvas area */}
            <div className="flex-1 flex items-center justify-center relative">
              {loading ? (
                <div className="flex flex-col items-center gap-4 text-neon-magenta/70">
                  <div className="w-12 h-12 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
                  <span className="text-sm">AI 正在渲染...</span>
                  {/* Scanning line during generation */}
                  <div className="w-64 h-1 bg-gradient-to-r from-transparent via-neon-cyan/40 to-transparent animate-pulse rounded-full" />
                </div>
              ) : imageUrl ? (
                <div className="relative w-full max-w-lg">
                  {/* Image with reflection */}
                  <ScanningLine active>
                    <div className="relative rounded-2xl overflow-hidden">
                      <img src={imageUrl} alt="Generated" className="w-full rounded-2xl shadow-2xl" />
                    </div>
                  </ScanningLine>
                  {/* Floor reflection */}
                  <div className="mt-1">
                    <div className="w-full h-24 rounded-b-2xl overflow-hidden opacity-25"
                      style={{
                        background: `url(${imageUrl}) center/cover`,
                        transform: 'scaleY(-1)',
                        maskImage: 'linear-gradient(to top, rgba(0,0,0,0.4), transparent)',
                        WebkitMaskImage: 'linear-gradient(to top, rgba(0,0,0,0.4), transparent)',
                        filter: 'blur(2px)',
                      }} />
                  </div>
                  {/* Shadow below reflection */}
                  <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-3/4 h-4 rounded-full bg-neon-magenta/5 blur-xl" />
                </div>
              ) : error ? (
                <p className="text-red-400 text-sm px-8 text-center">{error}</p>
              ) : (
                <div className="flex flex-col items-center gap-3 text-white/8">
                  <ImageIcon size={64} />
                  <span className="text-sm text-white/15">生成的图片将显示在这里</span>
                  <p className="text-[10px] text-white/8">带有逼真地面倒影效果</p>
                </div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
