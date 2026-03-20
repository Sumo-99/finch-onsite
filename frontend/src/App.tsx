import { motion, useReducedMotion } from 'motion/react'
import { FileText, LayoutList, Sparkles } from 'lucide-react'
import { NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom'

import { Badge } from './components/ui/badge'
import { Button } from './components/ui/button'
import CaseListPage from './pages/CaseListPage'
import NewCasePage from './pages/NewCasePage'

function App() {
  const location = useLocation()
  const shouldReduceMotion = useReducedMotion()

  const tabClassName = ({ isActive }: { isActive: boolean }) =>
    [
      'rounded-full px-4 py-2 text-sm font-medium transition-colors',
      isActive
        ? 'bg-[color:var(--card)] text-[color:var(--foreground)] shadow-[0_10px_24px_rgba(94,72,55,0.08)]'
        : 'text-[color:var(--muted-foreground)] hover:bg-[color:var(--surface)] hover:text-[color:var(--foreground)]',
    ].join(' ')

  return (
    <div className="app-shell">
      <div className="app-shell__wash app-shell__wash--left" />
      <div className="app-shell__wash app-shell__wash--right" />
      <div className="app-shell__mesh" />

      <div className="mx-auto flex min-h-screen w-full max-w-[88rem] flex-col px-4 py-5 sm:px-6 lg:px-8">
        <header className="surface-shell sticky top-4 z-20">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
            <div className="flex items-start gap-5">
              <div className="brand-mark">
                <Sparkles className="h-5 w-5" />
              </div>
              <div>
                <p className="eyebrow">
                  Finch Onsite
                </p>
                <h1 className="font-display mt-2 text-3xl font-semibold tracking-tight text-[color:var(--foreground)] sm:text-4xl">
                  Warm concierge case workspace
                </h1>
                <p className="mt-3 max-w-3xl text-sm leading-7 text-[color:var(--muted-foreground)] sm:text-base">
                  A calm intake desk for opening matters, reviewing the active docket,
                  and moving staff through the next best action without visual friction.
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Badge variant="accent">Light-only experience</Badge>
              <Badge variant="neutral">Staff-guided intake</Badge>
              <Button asChild variant="outline" size="sm">
                <NavLink to="/cases/new">
                  <FileText className="h-4 w-4" />
                  Open matter
                </NavLink>
              </Button>
            </div>
          </div>

          <nav className="mt-6 flex gap-2 overflow-x-auto rounded-full border border-[color:var(--border)] bg-[color:var(--surface-strong)] p-1">
            <NavLink to="/cases" end className={tabClassName}>
              <LayoutList className="mr-2 inline h-4 w-4" />
              Cases
            </NavLink>
            <NavLink to="/cases/new" className={tabClassName}>
              <FileText className="mr-2 inline h-4 w-4" />
              New case
            </NavLink>
          </nav>
        </header>

        <main className="flex-1 py-6 sm:py-8">
          <motion.div
            key={location.pathname}
            initial={shouldReduceMotion ? undefined : { opacity: 0, y: 10 }}
            animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
            transition={{ duration: 0.24, ease: 'easeOut' }}
          >
            <Routes location={location}>
              <Route path="/" element={<Navigate to="/cases" replace />} />
              <Route path="/cases" element={<CaseListPage />} />
              <Route path="/cases/new" element={<NewCasePage />} />
              <Route path="*" element={<Navigate to="/cases" replace />} />
            </Routes>
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default App
