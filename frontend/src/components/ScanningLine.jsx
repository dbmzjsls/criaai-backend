import React from 'react'

export default function ScanningLine({ children, active = true, className = '' }) {
  return (
    <div className={`scan-frame ${active ? '' : 'opacity-40'} ${className}`}>
      {children}
      {/* Corner accents */}
      {active && (
        <>
          <div className="absolute top-0 left-0 w-8 h-8 border-t border-l border-neon-cyan/40 rounded-tl-xl pointer-events-none z-10" />
          <div className="absolute top-0 right-0 w-8 h-8 border-t border-r border-neon-cyan/40 rounded-tr-xl pointer-events-none z-10" />
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b border-l border-neon-cyan/40 rounded-bl-xl pointer-events-none z-10" />
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b border-r border-neon-cyan/40 rounded-br-xl pointer-events-none z-10" />
          {/* Scanning dot */}
          <div
            className="absolute w-2 h-2 bg-neon-cyan rounded-full shadow-[0_0_8px_rgba(34,211,238,0.8)] pointer-events-none z-10"
            style={{
              animation: 'scanLine 3s linear infinite',
              left: 'calc(100% - 5px)',
            }}
          />
        </>
      )}
    </div>
  )
}
