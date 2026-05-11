import React, { useEffect, useState } from 'react'
import { motion, useSpring, useTransform, animate } from 'framer-motion'

export default function ScrollingNumber({
  value = 0,
  duration = 1.2,
  prefix = '',
  suffix = '',
  className = '',
  decimals = 0,
}) {
  const [displayValue, setDisplayValue] = useState(0)

  useEffect(() => {
    const controls = animate(displayValue, value, {
      duration,
      ease: [0.25, 0.1, 0.25, 1],
      onUpdate: (latest) => {
        setDisplayValue(latest)
      },
    })
    return () => controls.stop()
  }, [value, duration])

  const formatted = decimals > 0
    ? displayValue.toFixed(decimals)
    : Math.round(displayValue).toLocaleString()

  return (
    <span className={`font-mono tabular-nums tracking-tight ${className}`}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  )
}
