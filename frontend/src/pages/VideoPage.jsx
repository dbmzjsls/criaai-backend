import React, { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { VideoCamera, Sparkle, Play, DownloadSimple, UploadSimple } from '@phosphor-icons/react'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import PillSelector from '../components/PillSelector.jsx'
import ScanningLine from '../components/ScanningLine.jsx'
import EnergyBar from '../components/EnergyBar.jsx'
import axiosInstance from '../api/axios.js'

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } }

export default function VideoPage() {
  const [prompt, setPrompt] = useState('')
  const [duration, setDuration] = useState('5')
  const [shotType, setShotType] = useState('single')
  const [resolution, setResolution] = useState('720P')
  const [videoStyle, setVideoStyle] = useState('realistic')
  const [imgMode, setImgMode] = useState('upload')
  const [imgUrl, setImgUrl] = useState('')
  const [uploadedImgUrl, setUploadedImgUrl] = useState('')
  const [imgPreview, setImgPreview] = useState(null)
  const [uploading, setUploading] = useState(false)
  const fileRef = useRef(null)
  const [loading, setLoading] = useState(false)
  const [videoUrl, setVideoUrl] = useState(null)
  const [error, setError] = useState('')

  const activeImgUrl = imgMode === 'upload' ? uploadedImgUrl : imgUrl

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImgPreview(URL.createObjectURL(file))
    setUploadedImgUrl('')
    setError('')
    setUploading(true)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await axiosInstance.post('/v1/videos/upload-image', form, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadedImgUrl(res.data.img_url)
    } catch (e) {
      const detail = e.response?.data?.detail
      setError('上传失败：' + ((typeof detail === 'object' && detail) ? detail.message : (detail || e.message)))
      setImgPreview(null)
    } finally { setUploading(false) }
  }

  const generate = async () => {
    if (!prompt.trim()) return
    if (!activeImgUrl) { setError('请提供一张参考图片'); return }
    setLoading(true); setError(''); setVideoUrl(null)
    try {
      const res = await axiosInstance.post('/v1/videos/generate', {
        prompt, img_url: activeImgUrl, duration: parseInt(duration),
        shot_type: shotType, resolution,
      }, { timeout: 600000 })
      const url = res.data.video_url || res.data.url
      if (!url) throw new Error('No video URL returned')
      setVideoUrl(url)
    } catch (e) {
      const detail = e.response?.data?.detail
      const detailMsg = (typeof detail === 'object' && detail) ? detail.message : detail
      if (e.code === 'ECONNABORTED') setError('生成超时，视频生成通常需要3-5分钟')
      else if (e.response?.status === 504) setError('服务器超时')
      else if (e.response?.status >= 500) setError('服务器错误')
      else setError(detailMsg || ('生成失败：' + e.message))
    } finally { setLoading(false) }
  }

  const downloadVideo = async () => {
    if (!videoUrl) return
    try {
      const response = await fetch(videoUrl)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url; a.download = `generated-video-${Date.now()}.mp4`
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (e) { setError('下载失败：' + e.message) }
  }

  return (
    <motion.div variants={container} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader title="AI 视频生成" subtitle="wan2.6-i2v · 图生视频 · AI 产品短视频" />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Settings Panel */}
        <motion.div variants={item}>
          <NeonGlowCard color="magenta" className="p-6 space-y-5">
            <h3 className="text-white/70 font-heading font-semibold text-sm">生成设置</h3>

            {/* Reference Image */}
            <div>
              <label className="block text-xs text-white/40 mb-2">参考图片（必填）</label>
              <PillSelector
                options={[
                  { key: 'upload', label: '本地上传' },
                  { key: 'url', label: '图片链接' },
                ]}
                selected={imgMode}
                onChange={setImgMode}
                multi={false}
              />
              <div className="mt-2">
                {imgMode === 'upload' ? (
                  <div onClick={() => fileRef.current?.click()}
                    className="relative cursor-pointer rounded-2xl border-2 border-dashed border-neon-magenta/20 bg-space-800/40 hover:border-neon-magenta/40 transition-all overflow-hidden"
                    style={{ minHeight: 96 }}>
                    <input ref={fileRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
                    {imgPreview ? (
                      <img src={imgPreview} alt="preview" className="w-full h-32 object-cover rounded-2xl" />
                    ) : (
                      <div className="flex flex-col items-center justify-center h-24 gap-1 text-white/15">
                        <UploadSimple size={24} />
                        <span className="text-xs">{uploading ? '上传中...' : '点击上传图片'}</span>
                      </div>
                    )}
                    {uploading && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-2xl">
                        <div className="w-5 h-5 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
                      </div>
                    )}
                    {uploadedImgUrl && !uploading && (
                      <div className="absolute top-2 right-2 px-2 py-1 rounded-full bg-neon-green/20 text-neon-green text-[10px] border border-neon-green/30">已上传</div>
                    )}
                  </div>
                ) : (
                  <NeonInput value={imgUrl} onChange={e => setImgUrl(e.target.value)}
                    placeholder="粘贴图片链接 或 /static/outputs/xxx.png" className="!text-xs" />
                )}
              </div>
            </div>

            <NeonInput
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="例如：产品展示、奢华风格、慢动作..."
              multiline rows={3}
            />

            <div>
              <label className="block text-xs text-white/40 mb-2">时长</label>
              <PillSelector multi={false} selected={duration} onChange={setDuration}
                options={[{ key: '5', label: '5s' }, { key: '10', label: '10s' }]} />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">镜头类型</label>
              <PillSelector multi={false} selected={shotType} onChange={setShotType}
                options={[{ key: 'single', label: '单镜头' }, { key: 'multi', label: '多镜头' }]} />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">分辨率</label>
              <PillSelector multi={false} selected={resolution} onChange={setResolution}
                options={[{ key: '720P', label: '720P' }, { key: '1080P', label: '1080P' }]} />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">风格</label>
              <PillSelector multi={false} selected={videoStyle} onChange={setVideoStyle}
                options={[
                  { key: 'realistic', label: '写实' },
                  { key: 'cinematic', label: '电影感' },
                  { key: 'dynamic', label: '动感' },
                ]} />
            </div>

            <button
              onClick={generate}
              disabled={loading || !prompt.trim() || !activeImgUrl || uploading}
              className="btn-neon w-full py-3 text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
              <Sparkle size={16} weight="fill" />
              {loading ? '生成中...' : '生成视频'}
            </button>
          </NeonGlowCard>
        </motion.div>

        {/* Preview Panel */}
        <motion.div variants={item}>
          <NeonGlowCard color="purple" className="p-6">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white/70 font-heading font-semibold text-sm flex items-center gap-2">
                <VideoCamera size={16} className="text-neon-magenta" /> 预览
              </h3>
              {videoUrl && (
                <button onClick={downloadVideo} className="flex items-center gap-1 text-xs text-neon-magenta/70 hover:text-neon-magenta transition-colors">
                  <DownloadSimple size={14} /> 下载
                </button>
              )}
            </div>

            <ScanningLine active={loading}>
              <div className="min-h-[180px] bg-space-800 rounded-2xl flex items-center justify-center overflow-hidden">
                {loading ? (
                  <div className="flex flex-col items-center gap-4 text-neon-magenta/70 p-8 w-full">
                    <div className="w-8 h-8 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
                    <span className="text-sm">AI 正在生成视频（3-5分钟）...</span>
                    <EnergyBar value={45} max={100} color="magenta" className="w-full max-w-xs" />
                  </div>
                ) : videoUrl ? (
                  <video src={videoUrl} controls className="w-full rounded-2xl" />
                ) : error ? (
                  <p className="text-red-400 text-sm px-4 text-center">{error}</p>
                ) : (
                  <div className="flex flex-col items-center gap-2 text-white/10">
                    <Play size={48} />
                    <span className="text-sm text-white/15">视频预览</span>
                  </div>
                )}
              </div>
            </ScanningLine>

            {/* Timeline indicator */}
            <div className="mt-3 bg-space-800/50 rounded-xl p-3 border border-white/5">
              <div className="flex items-center gap-2 mb-2">
                <EnergyBar value={0} max={parseInt(duration)} color="magenta" height="h-1.5" showValue={false} />
                <span className="text-white/30 text-[10px] font-mono">0:{duration.padStart(2, '0')}</span>
              </div>
              <div className="grid grid-cols-6 gap-1">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className={`h-8 rounded-lg border transition-all ${i === 0 ? 'bg-neon-magenta/10 border-neon-magenta/20' : 'bg-white/[0.02] border-white/[0.04]'}`} />
                ))}
              </div>
            </div>
          </NeonGlowCard>
        </motion.div>
      </div>
    </motion.div>
  )
}
