import React, { useCallback, useEffect, useState } from 'react'
import Particles from 'react-tsparticles'
import { loadFull } from 'tsparticles'

export default function ParticleBackground({ reduced = false }) {
  const [mounted, setMounted] = useState(false)
  useEffect(() => { setMounted(true) }, [])

  const particlesInit = useCallback(async (engine) => {
    await loadFull(engine)
  }, [])

  if (!mounted) return null

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
      options={{
        fullScreen: false,
        fpsLimit: 30,
        detectRetina: false,
        particles: {
          number: {
            value: reduced ? 20 : 50,
            density: { enable: true, area: 800 }
          },
          color: {
            value: ['#d946ef', '#7c3aed', '#22d3ee', '#a78bfa']
          },
          shape: { type: 'circle' },
          opacity: {
            value: { min: 0.05, max: 0.25 },
            animation: { enable: true, speed: 0.5, sync: false }
          },
          size: {
            value: { min: 1, max: 3 },
            animation: { enable: true, speed: 1, sync: false }
          },
          move: {
            enable: true,
            speed: { min: 0.1, max: 0.5 },
            direction: 'none',
            random: true,
            straight: false,
            outModes: { default: 'out' }
          },
          links: {
            enable: true,
            color: 'rgba(217, 70, 239, 0.06)',
            distance: 150,
            opacity: 0.3,
            width: 0.5
          }
        },
        interactivity: {
          events: {
            onHover: { enable: true, mode: 'grab' },
          },
          modes: {
            grab: {
              distance: 140,
              links: { opacity: 0.5, color: '#d946ef' }
            }
          }
        }
      }}
    />
  )
}
