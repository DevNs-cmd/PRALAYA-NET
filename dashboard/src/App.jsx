import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CommandCenter from './components/CommandCenter'
import EnhancedCommandCenter from './components/EnhancedCommandCenterFixed'
import ReliableCommandCenter from './components/ReliableCommandCenter'
import DemoCommandCenter from './components/DemoCommandCenter'
import DroneView from './components/DroneView'
import ErrorBoundary from './components/ErrorBoundary'
import './index.css'

// Navigation component with enhanced styling
const Navigation = () => {
  const location = useLocation()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [backendStatus, setBackendStatus] = useState('checking')

  // Check backend status
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch('/api/health')
        setBackendStatus(response.ok ? 'online' : 'offline')
      } catch {
        setBackendStatus('offline')
      }
    }
    
    checkBackend()
    const interval = setInterval(checkBackend, 10000)
    return () => clearInterval(interval)
  }, [])

  const navLinks = [
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/command-center', label: 'Command Center', icon: '🎛️' },
    { path: '/enhanced-command-center', label: 'Enhanced CC', icon: '⚡' },
    { path: '/demo-command-center', label: 'Demo CC', icon: '🎯' },
    { path: '/drone-view', label: 'Drone View', icon: '🚁', highlight: true }
  ]

  const isActive = (path) => location.pathname === path

  const getStatusColor = () => {
    if (backendStatus === 'checking') return '#d4a574'
    if (backendStatus === 'online') return '#5a8a5a'
    return '#c45a5a'
  }

  return (
    <nav style={{
      background: 'linear-gradient(180deg, #1a1d29 0%, #151720 100%)',
      borderBottom: '1px solid #3a3d4a',
      position: 'sticky',
      top: 0,
      zIndex: 1000,
      boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)'
    }}>
      <div style={{
        maxWidth: '1600px',
        margin: '0 auto',
        padding: '0 24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '72px'
        }}>
          {/* Logo Section */}
          <Link to="/" style={{
            display: 'flex',
            alignItems: 'center',
            gap: '14px',
            textDecoration: 'none',
            color: '#e8e9ea'
          }}>
            <div style={{
              width: '42px',
              height: '42px',
              background: 'linear-gradient(135deg, #4a90e2 0%, #c45a5a 100%)',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              boxShadow: '0 4px 12px rgba(74, 144, 226, 0.3)'
            }}>
              🌪️
            </div>
            <div>
              <div style={{
                fontSize: '18px',
                fontWeight: '800',
                letterSpacing: '0.5px',
                background: 'linear-gradient(90deg, #ffffff, #b4b6ba)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                PRALAYA-NET
              </div>
              <div style={{
                fontSize: '9px',
                color: '#6b7280',
                textTransform: 'uppercase',
                letterSpacing: '2px',
                fontWeight: '600'
              }}>
                Autonomous Command System
              </div>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(0, 0, 0, 0.3)',
            padding: '6px 12px',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.08)'
          }}>
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: link.highlight 
                    ? '10px 18px' 
                    : '10px 14px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontSize: '13px',
                  fontWeight: '600',
                  color: isActive(link.path) ? '#ffffff' : '#9ca3af',
                  background: isActive(link.path) 
                    ? (link.highlight 
                        ? 'linear-gradient(90deg, #4a90e2, #3b82f6)' 
                        : 'rgba(74, 144, 226, 0.15)')
                    : 'transparent',
                  border: isActive(link.path) 
                    ? (link.highlight ? 'none' : '1px solid rgba(74, 144, 226, 0.3)')
                    : '1px solid transparent',
                  transition: 'all 0.2s ease',
                  boxShadow: isActive(link.path) && link.highlight 
                    ? '0 4px 15px rgba(59, 130, 246, 0.4)' 
                    : 'none'
                }}
              >
                <span style={{
                  filter: isActive(link.path) ? 'none' : 'grayscale(50%)'
                }}>{link.icon}</span>
                <span className="nav-label">{link.label}</span>
              </Link>
            ))}
          </div>

          {/* Status & Actions */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '16px'
          }}>
            {/* Backend Status */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              padding: '8px 16px',
              background: 'rgba(0, 0, 0, 0.3)',
              borderRadius: '25px',
              border: '1px solid rgba(255, 255, 255, 0.08)'
            }}>
              <span style={{
                width: '10px',
                height: '10px',
                borderRadius: '50%',
                background: getStatusColor(),
                animation: backendStatus === 'online' ? 'pulse 2s infinite' : 'none',
                boxShadow: backendStatus === 'online' ? '0 0 10px rgba(90, 138, 90, 0.5)' : 'none'
              }}></span>
              <span style={{ 
                fontSize: '12px', 
                fontWeight: '600',
                color: backendStatus === 'online' ? '#5a8a5a' : 
                       backendStatus === 'checking' ? '#d4a574' : '#c45a5a'
              }}>
                {backendStatus === 'online' ? 'SYSTEM ONLINE' : 
                 backendStatus === 'checking' ? 'CHECKING...' : 'OFFLINE'}
              </span>
            </div>

            {/* Mode Indicator */}
            <div style={{
              padding: '8px 16px',
              background: 'linear-gradient(90deg, rgba(74, 144, 226, 0.15), rgba(196, 90, 90, 0.15))',
              borderRadius: '25px',
              border: '1px solid rgba(74, 144, 226, 0.2)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{ fontSize: '12px' }}>🎯</span>
              <span style={{ 
                fontSize: '12px', 
                fontWeight: '700',
                background: 'linear-gradient(90deg, #4a90e2, #c45a5a)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent'
              }}>
                LIVE MODE
              </span>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              style={{
                display: 'none',
                flexDirection: 'column',
                gap: '5px',
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '10px',
                color: '#e8e9ea'
              }}
              className="mobile-menu-btn"
            >
              <span style={{
                width: '22px',
                height: '2px',
                background: 'currentColor',
                borderRadius: '2px',
                transition: 'all 0.3s ease'
              }}></span>
              <span style={{
                width: '22px',
                height: '2px',
                background: 'currentColor',
                borderRadius: '2px',
                transition: 'all 0.3s ease'
              }}></span>
              <span style={{
                width: '22px',
                height: '2px',
                background: 'currentColor',
                borderRadius: '2px',
                transition: 'all 0.3s ease'
              }}></span>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            padding: '20px 0',
            borderTop: '1px solid #3a3d4a'
          }}>
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setMobileMenuOpen(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '14px',
                  padding: '14px 16px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  fontSize: '15px',
                  fontWeight: '600',
                  color: isActive(link.path) ? '#ffffff' : '#9ca3af',
                  background: isActive(link.path) 
                    ? 'rgba(74, 144, 226, 0.15)' 
                    : 'transparent',
                  marginBottom: '4px'
                }}
              >
                <span style={{ fontSize: '18px' }}>{link.icon}</span>
                <span>{link.label}</span>
              </Link>
            ))}
          </div>
        )}
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.1); }
        }
        @keyframes blink {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
        @media (max-width: 1024px) {
          .mobile-menu-btn { display: flex !important; }
          .nav-label { display: none !important; }
        }
        @media (min-width: 1025px) {
          .mobile-menu-btn { display: none !important; }
        }
      `}</style>
    </nav>
  )
}

function App() {
  return (
    <Router>
      <ErrorBoundary>
        <div style={{
          minHeight: '100vh',
          background: '#0f1219',
          fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        }}>
          <Navigation />
          
          <main style={{
            flex: 1,
            background: 'linear-gradient(180deg, #0f1219 0%, #1a1d29 50%, #151720 100%)'
          }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/command-center" element={<CommandCenter />} />
              <Route path="/enhanced-command-center" element={<EnhancedCommandCenter />} />
              <Route path="/reliable-command-center" element={<ReliableCommandCenter />} />
              <Route path="/demo-command-center" element={<DemoCommandCenter />} />
              <Route path="/drone-view" element={<DroneView />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer style={{
            padding: '20px 24px',
            background: 'linear-gradient(180deg, #151720 0%, #0f1219 100%)',
            borderTop: '1px solid #2f3240',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '24px',
              fontSize: '12px',
              color: '#6b7280'
            }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ 
                  width: '8px', 
                  height: '8px', 
                  borderRadius: '50%', 
                  background: '#5a8a5a',
                  animation: 'pulse 2s infinite'
                }}></span>
                <span style={{ color: '#9ca3af', fontWeight: '600' }}>SYSTEM OPERATIONAL</span>
              </span>
              <span style={{ color: '#6b7280' }}>|</span>
              <span style={{ color: '#9ca3af' }}>NDMA Compatible</span>
              <span style={{ color: '#6b7280' }}>|</span>
              <span style={{ color: '#9ca3af' }}>ISRO Integrated</span>
            </div>
            <div style={{
              fontSize: '12px',
              color: '#6b7280',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span style={{
                padding: '4px 10px',
                background: 'rgba(74, 144, 226, 0.1)',
                borderRadius: '4px',
                fontSize: '10px',
                fontWeight: '600',
                color: '#4a90e2'
              }}>
                v1.0.0
              </span>
              <span>© 2024 PRALAYA-NET</span>
            </div>
          </footer>
        </div>
      </ErrorBoundary>
    </Router>
  )
}

export default App

