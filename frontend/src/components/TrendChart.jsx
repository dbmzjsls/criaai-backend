import React, { useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const data7D = [
  { day: 'Mon', value: 12 },
  { day: 'Tue', value: 18 },
  { day: 'Wed', value: 15 },
  { day: 'Thu', value: 24 },
  { day: 'Fri', value: 28 },
  { day: 'Sat', value: 22 },
  { day: 'Sun', value: 32 },
]

const data30D = [
  { day: 'W1', value: 85 }, { day: 'W2', value: 92 }, { day: 'W3', value: 78 }, { day: 'W4', value: 105 },
]

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div
        className="px-4 py-2.5 rounded-xl"
        style={{
          background: 'rgba(18,18,26,0.9)',
          backdropFilter: 'blur(20px)',
          border: '1px solid rgba(217,70,239,0.2)',
        }}
      >
        <p className="text-white/40 text-xs mb-0.5">{label}</p>
        <p className="text-neon-magenta font-bold text-sm">{payload[0].value} 条内容</p>
      </div>
    )
  }
  return null
}

export default function TrendChart({ title = '内容生成趋势' }) {
  const [period, setPeriod] = useState('7D')
  const data = period === '7D' ? data7D : data30D

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-heading font-semibold text-sm text-white/80">{title}</h3>
        <div className="flex gap-1.5 bg-white/5 rounded-lg p-1">
          {['7D', '30D'].map(p => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                p === period
                  ? 'gradient-bg text-white shadow-[0_2px_8px_rgba(217,70,239,0.3)]'
                  : 'text-white/40 hover:text-white/70'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#d946ef" stopOpacity={0.4} />
                <stop offset="50%" stopColor="#7c3aed" stopOpacity={0.15} />
                <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" vertical={false} />
            <XAxis
              dataKey="day"
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.25)' }}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fontSize: 11, fill: 'rgba(255,255,255,0.25)' }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#d946ef', strokeWidth: 1, strokeDasharray: '4 4' }} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#d946ef"
              strokeWidth={2.5}
              fill="url(#trendGradient)"
              dot={{ fill: '#d946ef', stroke: '#12121a', strokeWidth: 2, r: 4 }}
              activeDot={{ fill: '#d946ef', stroke: '#12121a', strokeWidth: 2, r: 6, style: { filter: 'drop-shadow(0 0 6px rgba(217,70,239,0.6))' } }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
