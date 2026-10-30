import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Search, Target, Moon, Sun } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const [darkMode, setDarkMode] = useState(() => {
    if (typeof window !== 'undefined') {
      return document.documentElement.classList.contains('dark')
    }
    return false
  })

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle('dark')
  }

  const navItems = [
    { path: '/', label: 'Analyze', icon: Search },
    { path: '/intervene', label: 'Intervention', icon: Target },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Header with gradient border */}
      <header className="sticky top-0 z-50 w-full border-b border-primary/20 bg-background/80 backdrop-blur-xl supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center">
          <div className="mr-6 flex items-center gap-8">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-primary/60 text-primary-foreground font-bold shadow-lg shadow-primary/20 group-hover:shadow-primary/40 transition-shadow">
                <span className="text-lg">🔍</span>
              </div>
              <span className="font-bold text-xl tracking-tight">
                Attention<span className="text-primary">Lens</span>
              </span>
            </Link>
            <nav className="flex items-center gap-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all',
                      isActive
                        ? 'bg-primary text-primary-foreground shadow-md shadow-primary/20'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                    )}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </Link>
                )
              })}
            </nav>
          </div>
          <div className="flex flex-1 items-center justify-end gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleDarkMode}
              aria-label="Toggle dark mode"
              className="gap-2"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              <span className="hidden sm:inline text-xs">
                {darkMode ? 'Light' : 'Dark'}
              </span>
            </Button>
          </div>
        </div>
      </header>

      <main className="container py-8">
        {children}
      </main>

      <footer className="border-t border-primary/10 py-8 mt-16">
        <div className="container flex flex-col items-center gap-3 text-center">
          <p className="text-sm font-medium text-foreground">
            AttentionLens — Interactive Explainability for Vision Models
          </p>
          <p className="text-xs text-muted-foreground max-w-md">
            Grad-CAM shows you a heatmap. AttentionLens tells you the model cheated — and
            shows you the proof.
          </p>
        </div>
      </footer>
    </div>
  )
}
