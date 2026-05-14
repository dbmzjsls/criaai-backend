import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Sparkle, Lightning, Article, Image as ImageIcon,
  VideoCamera, Check, X, Warning, DownloadSimple,
  ArrowRight, Play, Copy
} from '@phosphor-icons/react'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import PillSelector from '../components/PillSelector.jsx'
import ScanningLine from '../components/ScanningLine.jsx'
import EnergyBar from '../components/EnergyBar.jsx'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import { startPipeline, getTaskStatus } from '../api/pipeline.js'
import { resolveMediaUrl } from '../utils/resolveMediaUrl.js'

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.06 } } }
const item = { hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.35 } } }

const STEP_CONFIG = [
  { key: 'copywriting', label: 'AI 文案', icon: Article, color: 'magenta' },
  { key: 'image', label: '图片', icon: ImageIcon, color: 'cyan' },
  { key: 'video', label: '视频', icon: VideoCamera, color: 'purple' },
]

function StepIcon({ config, status, isActive }) {
  const { icon: Icon, color } = config
  const colorClass = `text-neon-${color}`

  if (status === 'done') {
    return (
      <div className={`w-12 h-12 rounded-full bg-neon-green/20 border-2 border-neon-green/40 flex items-center justify-center`}>
        <Check size={20} weight="bold" className="text-neon-green" />
      </div>
    )
  }
  if (status === 'failed') {
    return (
      <div className="w-12 h-12 rounded-full bg-red-500/20 border-2 border-red-500/40 flex items-center justify-center">
        <X size={20} weight="bold" className="text-red-400" />
      </div>
    )
  }
  if (status === 'running') {
    return (
      <div className="w-12 h-12 rounded-full bg-neon-magenta/20 border-2 border-neon-magenta/40 flex items-center justify-center pulse-neon">
        <div className="w-5 h-5 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
      </div>
    )
  }
  return (
    <div className={`w-12 h-12 rounded-full bg-${color === 'magenta' ? 'neon-magenta' : color === 'cyan' ? 'neon-cyan' : 'neon-purple'}/10 border-2 border-white/10 flex items-center justify-center ${isActive ? `border-neon-${color}/30` : ''}`}>
      <Icon size={20} className={isActive ? colorClass : 'text-white/20'} />
    </div>
  )
}

export default function PipelinePage() {
  const [settings, setSettings] = useState({
    keyword: '',
    language: 'zh',
    style: '专业',
    platform: 'Amazon',
    imageStyle: 'luxury',
    videoDuration: 5,
    videoShotType: 'single',
    videoResolution: '720P',
  })

  const [pipeline, setPipeline] = useState({
    taskId: null,
    status: 'idle', // idle | running | completed | failed
    activeStep: 0,
    steps: {
      copywriting: { status: 'pending', result: null },
      image: { status: 'pending', result: null },
      video: { status: 'pending', result: null },
    },
    error: null,
  })

  const pollingRef = useRef(null)
  const [copied, setCopied] = useState(false)
  const [downloadState, setDownloadState] = useState({})

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [])

  const startPolling = (taskId) => {
    if (pollingRef.current) clearInterval(pollingRef.current)
    pollingRef.current = setInterval(async () => {
      try {
        const res = await getTaskStatus(taskId)
        const data = res.data
        updateFromTask(data)
        if (data.status === 'completed' || data.status === 'failed') {
          clearInterval(pollingRef.current)
          pollingRef.current = null
        }
      } catch (e) {
        console.error('Poll error:', e)
      }
    }, 2000)
  }

  const updateFromTask = (data) => {
    setPipeline(prev => {
      const newSteps = { ...prev.steps }
      Object.keys(data.progress || {}).forEach(step => {
        if (newSteps[step]) {
          newSteps[step] = { ...newSteps[step], status: data.progress[step] }
        }
      })

      // Map results
      if (data.result?.copywriting && newSteps.copywriting) {
        newSteps.copywriting.result = data.result.copywriting
      }
      if (data.result?.image && newSteps.image) {
        newSteps.image.result = data.result.image
      }
      if (data.result?.video && newSteps.video) {
        newSteps.video.result = data.result.video
      }

      let activeStep = 0
      if (newSteps.copywriting.status === 'done') activeStep = 1
      if (newSteps.image.status === 'done') activeStep = 2
      if (newSteps.video.status === 'done') activeStep = 2

      return {
        ...prev,
        status: data.status,
        activeStep,
        steps: newSteps,
        error: data.error || null,
      }
    })
  }

  const handleGenerate = async () => {
    if (!settings.keyword.trim()) return

    setPipeline({
      taskId: null,
      status: 'running',
      activeStep: 0,
      steps: {
        copywriting: { status: 'pending', result: null },
        image: { status: 'pending', result: null },
        video: { status: 'pending', result: null },
      },
      error: null,
    })

    try {
      const res = await startPipeline(settings)
      const { task_id } = res.data
      setPipeline(prev => ({ ...prev, taskId: task_id }))
      startPolling(task_id)
    } catch (e) {
      const detail = e.response?.data?.detail
      const detailMsg = (typeof detail === 'object' && detail) ? detail.message : detail
      setPipeline(prev => ({
        ...prev,
        status: 'failed',
        error: detailMsg || ('启动流水线失败：' + e.message),
      }))
    }
  }

  const downloadFile = async (url, filename) => {
    setDownloadState(prev => ({ ...prev, [filename]: 'downloading' }))
    try {
      const response = await fetch(url)
      const blob = await response.blob()
      const objUrl = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = objUrl; a.download = filename
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      window.URL.revokeObjectURL(objUrl)
      setDownloadState(prev => ({ ...prev, [filename]: 'done' }))
    } catch (e) {
      setDownloadState(prev => ({ ...prev, [filename]: 'error' }))
    }
  }

  const copyText = () => {
    const text = pipeline.steps.copywriting.result?.content
    if (text) {
      navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const isGenerating = pipeline.status === 'running'
  const isComplete = pipeline.status === 'completed'
  const hasFailed = pipeline.status === 'failed'

  return (
    <motion.div variants={container} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader
        title="一条龙流水线"
        subtitle="一键完成：文案 → 图片 → 视频"
        icon={<Lightning size={20} weight="fill" className="text-neon-cyan" />}
      />

      {/* Settings + Generate */}
      <motion.div variants={item}>
        <NeonGlowCard color="magenta" className="p-6">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div className="md:col-span-2 lg:col-span-2">
              <NeonInput
                value={settings.keyword}
                onChange={e => setSettings(s => ({ ...s, keyword: e.target.value }))}
                placeholder="输入产品关键词，例如：高端护肤、无线耳机..."
                multiline
                rows={2}
                disabled={isGenerating}
              />
            </div>
            <div>
              <label className="block text-xs text-white/40 mb-1.5">语言</label>
              <PillSelector
                multi={false}
                selected={settings.language}
                onChange={v => setSettings(s => ({ ...s, language: v }))}
                disabled={isGenerating}
                options={[
                  { key: 'zh', label: '中文' },
                  { key: 'en', label: 'English' },
                  { key: 'pt', label: 'Português' },
                  { key: 'es', label: 'Español' },
                ]}
              />
            </div>
            <div>
              <label className="block text-xs text-white/40 mb-1.5">语气风格</label>
              <PillSelector
                multi={false}
                selected={settings.style}
                onChange={v => setSettings(s => ({ ...s, style: v }))}
                disabled={isGenerating}
                options={[
                  { key: '专业', label: '专业' },
                  { key: '温馨', label: '温馨' },
                  { key: '幽默', label: '幽默' },
                ]}
              />
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !settings.keyword.trim()}
              className="btn-neon px-8 py-3 text-white font-semibold text-sm flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed pulse-neon"
            >
              <Sparkle size={16} weight="fill" />
              {isGenerating ? '生成中...' : hasFailed ? '重试' : '开始生成'}
            </button>
            {isGenerating && (
              <span className="text-neon-magenta/60 text-xs animate-pulse">
                运行中... 每2秒轮询一次
              </span>
            )}
            {pipeline.taskId && (
              <span className="text-white/20 text-xs font-mono">
                任务：{pipeline.taskId.slice(0, 8)}...
              </span>
            )}
          </div>
        </NeonGlowCard>
      </motion.div>

      {/* Step Stepper */}
      <motion.div variants={item}>
        <div className="grid grid-cols-3 gap-4">
          {STEP_CONFIG.map((config, idx) => {
            const stepState = pipeline.steps[config.key]
            const isActive = pipeline.activeStep === idx
            const status = stepState.status
            const colorMap = { magenta: 'pink', cyan: 'cyan', purple: 'purple' }
            const neonColor = colorMap[config.color]

            return (
              <div key={config.key}>
                <NeonGlowCard color={neonColor} className="p-5 h-full">
                  <div className="flex items-center gap-3 mb-3">
                    <StepIcon config={config} status={status} isActive={isActive} />
                    <div>
                      <h4 className="text-white/80 font-heading text-sm">{config.label}</h4>
                      <span className="text-[10px] text-white/30">
                        第 {idx + 1} 步 · {status === 'running' ? '生成中...' : status === 'done' ? '已完成' : status === 'failed' ? '失败' : '等待中'}
                      </span>
                    </div>
                  </div>

                  {/* Progress indicator */}
                  <AnimatePresence mode="wait">
                    {status === 'running' && (
                      <motion.div
                        key="loading"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="space-y-3"
                      >
                        <ScanningLine active>
                          <div className="h-20 bg-space-800/80 rounded-xl flex items-center justify-center">
                            <div className="flex items-center gap-2 text-neon-magenta/60 text-xs">
                              <div className="w-3 h-3 border border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
                              AI 正在处理中...
                            </div>
                          </div>
                        </ScanningLine>
                        {config.key === 'video' && (
                          <EnergyBar value={60} max={100} color="purple" height="h-1" showValue={false} />
                        )}
                      </motion.div>
                    )}

                    {status === 'done' && stepState.result && (
                      <motion.div
                        key="result"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="space-y-2"
                      >
                        {config.key === 'copywriting' && (
                          <div>
                            <div className="bg-space-800/60 rounded-lg p-3 max-h-32 overflow-y-auto">
                              <p className="text-xs text-white/60 leading-relaxed line-clamp-4">
                                {stepState.result.content}
                              </p>
                            </div>
                            <button
                              onClick={copyText}
                              className="mt-2 flex items-center gap-1 text-[10px] text-neon-magenta/60 hover:text-neon-magenta transition-colors"
                            >
                              {copied ? <Check size={12} className="text-neon-green" /> : <Copy size={12} />}
                              {copied ? '已复制' : '复制文案'}
                            </button>
                          </div>
                        )}
                        {config.key === 'image' && (
                          <div className="relative rounded-lg overflow-hidden bg-space-800">
                            <img
                              src={resolveMediaUrl(stepState.result.image_url)}
                              alt="Generated"
                              className="w-full h-28 object-cover rounded-lg"
                            />
                            <button
                              onClick={() => downloadFile(resolveMediaUrl(stepState.result.image_url), `image-${Date.now()}.png`)}
                              className="absolute bottom-2 right-2 w-6 h-6 rounded-full bg-black/60 flex items-center justify-center hover:bg-black/80 transition-colors"
                            >
                              <DownloadSimple size={12} className="text-white" />
                            </button>
                          </div>
                        )}
                        {config.key === 'video' && (
                          <div className="relative rounded-lg overflow-hidden bg-space-800">
                            <video
                              src={resolveMediaUrl(stepState.result.video_url)}
                              controls
                              className="w-full h-28 object-cover rounded-lg"
                            />
                            <button
                              onClick={() => downloadFile(resolveMediaUrl(stepState.result.video_url), `video-${Date.now()}.mp4`)}
                              className="absolute bottom-2 right-2 w-6 h-6 rounded-full bg-black/60 flex items-center justify-center hover:bg-black/80 transition-colors"
                            >
                              <DownloadSimple size={12} className="text-white" />
                            </button>
                          </div>
                        )}
                      </motion.div>
                    )}

                    {status === 'failed' && (
                      <motion.div
                        key="error"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="bg-red-500/10 rounded-lg p-3 border border-red-500/20"
                      >
                        <div className="flex items-center gap-1.5 text-red-400 text-xs">
                          <Warning size={14} />
                          {pipeline.error || '生成失败'}
                        </div>
                      </motion.div>
                    )}

                    {status === 'pending' && !isGenerating && (
                      <div className="h-20 bg-space-800/40 rounded-xl flex items-center justify-center">
                        <span className="text-white/10 text-xs">等待开始...</span>
                      </div>
                    )}

                    {status === 'pending' && isGenerating && (
                      <div className="h-20 bg-space-800/40 rounded-xl flex items-center justify-center">
                        <span className="text-white/15 text-xs">排队中...</span>
                      </div>
                    )}
                  </AnimatePresence>
                </NeonGlowCard>
              </div>
            )
          })}
        </div>
      </motion.div>

      {/* Connector arrows between steps (visual) */}
      {isComplete && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <NeonGlowCard color="cyan" className="p-6 text-center">
            <div className="flex items-center justify-center gap-3 text-neon-green">
              <Check size={24} weight="bold" />
              <span className="text-lg font-heading font-semibold">
                流水线完成！
              </span>
            </div>
            <p className="text-white/40 text-sm mt-2">
              所有素材已生成完毕。可在此页面下载各步骤文件，或在素材库中统一管理。
            </p>
          </NeonGlowCard>
        </motion.div>
      )}
    </motion.div>
  )
}
