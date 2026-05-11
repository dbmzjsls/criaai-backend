import React, { useState } from 'react'

export default function NeonInput({
  value,
  onChange,
  placeholder = '',
  className = '',
  type = 'text',
  multiline = false,
  rows = 3,
  icon: Icon,
  ...props
}) {
  const [focused, setFocused] = useState(false)

  const baseClasses =
    'w-full transition-all duration-300 outline-none bg-space-800/70 text-white/90 placeholder-white/20 font-body border rounded-full'

  const focusClasses = focused
    ? 'border-neon-magenta/50 shadow-[0_0_0_3px_rgba(217,70,239,0.08),0_0_20px_rgba(217,70,239,0.1)]'
    : 'border-white/8 hover:border-white/12'

  if (multiline) {
    return (
      <div className="relative">
        <textarea
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          rows={rows}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          className={`${baseClasses} ${focusClasses} rounded-2xl px-5 py-3 resize-none ${className}`}
          {...props}
        />
        {Icon && (
          <Icon size={16} className="absolute top-3 right-4 text-white/15" />
        )}
      </div>
    )
  }

  return (
    <div className="relative">
      {Icon && (
        <Icon
          size={16}
          className={`absolute left-4 top-1/2 -translate-y-1/2 transition-colors duration-300 ${
            focused ? 'text-neon-magenta/60' : 'text-white/15'
          }`}
        />
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        className={`${baseClasses} ${focusClasses} ${Icon ? 'pl-11 pr-5' : 'px-5'} py-3 ${className}`}
        {...props}
      />
      {/* Glowing cursor line when focused */}
      {focused && (
        <div className="absolute bottom-0 left-6 right-6 h-px bg-gradient-to-r from-transparent via-neon-magenta/40 to-transparent" />
      )}
    </div>
  )
}
