import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { Article, Sparkle, Copy, Check } from '@phosphor-icons/react'
import NeonGlowCard from '../components/NeonGlowCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import NeonInput from '../components/NeonInput.jsx'
import PillSelector from '../components/PillSelector.jsx'
import axiosInstance from '../api/axios.js'

const container = { hidden: {}, visible: { transition: { staggerChildren: 0.08 } } }
const item = { hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0, transition: { duration: 0.4 } } }

export default function CopywritingPage() {
  const [keyword, setKeyword] = useState('')
  const [lang, setLang] = useState('zh')
  const [copyType, setCopyType] = useState('grass')
  const [tone, setTone] = useState('warm')
  const [length, setLength] = useState('medium')
  const [result, setResult] = useState('')
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [isError, setIsError] = useState(false)

  const generate = async () => {
    if (!keyword.trim()) return
    setLoading(true); setResult('')
    try {
      const res = await axiosInstance.post('/v1/copywriting/generate', { keyword, language: lang }, { timeout: 120000 })
      const content = res.data.content || res.data.result
      if (!content) throw new Error('No content returned')
      if (content.includes('<html') || content.includes('<!DOCTYPE')) throw new Error('Server returned error page')
      setResult(content)
      setIsError(false)
    } catch (e) {
      let msg
      // 提取 detail，兼容 object 和 string 两种格式
      const detail = e.response?.data?.detail
      const detailMsg = (typeof detail === 'object' && detail) ? detail.message : detail

      if (e.code === 'ECONNABORTED') {
        msg = '生成超时，请重试（服务器处理超过 120 秒）'
      } else if (e.response?.status === 400) {
        msg = detailMsg || '请求参数有误，请检查输入内容'
      } else if (e.response?.status === 504) {
        msg = '服务器超时（504），请稍后重试'
      } else if (e.response?.status === 500) {
        msg = '服务器内部错误（500），AI 服务可能暂时不可用，请稍后重试'
      } else if (e.response?.status === 502) {
        msg = '网关错误（502），服务器可能正在重启'
      } else if (!e.response && e.message === 'Network Error') {
        msg = '网络连接失败，请检查后端服务是否运行'
      } else {
        msg = detailMsg || ('生成失败: ' + e.message)
      }
      setResult(msg)
      setIsError(true)
    } finally { setLoading(false) }
  }

  const copy = () => {
    navigator.clipboard.writeText(result)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <motion.div variants={container} initial="hidden" animate="visible" className="space-y-6 pb-8">
      <PageHeader title="AI 文案生成" subtitle="基于关键词生成多语言营销文案" />

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Settings Panel */}
        <motion.div variants={item}>
          <NeonGlowCard color="magenta" className="p-6 space-y-5">
            <h3 className="text-white/70 font-heading font-semibold text-sm">生成设置</h3>

            <NeonInput
              value={keyword}
              onChange={e => setKeyword(e.target.value)}
              placeholder="例如：高端护肤品、抗衰老精华..."
              multiline rows={3}
            />

            <div>
              <label className="block text-xs text-white/40 mb-2">文案类型</label>
              <PillSelector
                options={[
                  { key: 'grass', label: '种草文案' },
                  { key: 'brand', label: '品牌故事' },
                  { key: 'promo', label: '促销文案' },
                  { key: 'desc', label: '产品描述' },
                  { key: 'social', label: '社交媒体' },
                  { key: 'live', label: '直播脚本' },
                ]}
                selected={copyType}
                onChange={setCopyType}
                multi={false}
              />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">语气风格</label>
              <PillSelector
                options={[
                  { key: 'pro', label: '专业' },
                  { key: 'warm', label: '温馨' },
                  { key: 'fun', label: '活泼' },
                  { key: 'luxury', label: '奢华' },
                ]}
                selected={tone}
                onChange={setTone}
                multi={false}
              />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">篇幅长度</label>
              <PillSelector
                options={[
                  { key: 'short', label: '短篇 (50字)' },
                  { key: 'medium', label: '中篇 (150字)' },
                  { key: 'long', label: '长篇 (300字)' },
                ]}
                selected={length}
                onChange={setLength}
                multi={false}
              />
            </div>

            <div>
              <label className="block text-xs text-white/40 mb-2">语言</label>
              <PillSelector
                options={[
                  { key: 'zh', label: '中文' },
                  { key: 'en', label: 'English' },
                  { key: 'pt', label: 'Português' },
                  { key: 'es', label: 'Español' },
                ]}
                selected={lang}
                onChange={setLang}
                multi={false}
              />
            </div>

            <button
              onClick={generate}
              disabled={loading || !keyword.trim()}
              className="btn-neon w-full py-3 text-white font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed pulse-neon"
            >
              <Sparkle size={16} weight="fill" />
              {loading ? '生成中...' : '生成文案'}
            </button>
          </NeonGlowCard>
        </motion.div>

        {/* Result Panel */}
        <motion.div variants={item}>
          <NeonGlowCard color="purple" className="p-6 h-full">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-white/70 font-heading font-semibold text-sm flex items-center gap-2">
                <Article size={16} className="text-neon-magenta" />
                生成结果
              </h3>
              {result && !isError && (
                <button onClick={copy} className="flex items-center gap-1 text-xs text-neon-magenta/70 hover:text-neon-magenta transition-colors">
                  {copied ? <Check size={14} className="text-neon-green" /> : <Copy size={14} />}
                  {copied ? '已复制' : '复制'}
                </button>
              )}
            </div>
            <div className="min-h-[300px] bg-space-800/50 rounded-xl p-4 border border-white/5">
              {loading ? (
                <div className="flex items-center gap-2 text-neon-magenta/70 text-sm">
                  <div className="w-4 h-4 border-2 border-neon-magenta/30 border-t-neon-magenta rounded-full animate-spin" />
                  AI 正在撰写...
                </div>
              ) : result ? (
                <p className={`text-sm leading-relaxed whitespace-pre-wrap ${isError ? 'text-red-400' : 'text-white/80'}`}>
                  {result}
                </p>
              ) : (
                <p className="text-white/15 text-sm">生成的文案将显示在这里...</p>
              )}
            </div>
          </NeonGlowCard>
        </motion.div>
      </div>
    </motion.div>
  )
}
