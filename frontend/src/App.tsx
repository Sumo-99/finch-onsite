import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [status, setStatus] = useState('Checking backend...')
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await axios.get('/api/health/')
        setStatus(JSON.stringify(response.data))
        setConnected(response.data.status === 'ok')
      } catch {
        setStatus('Unable to reach backend')
        setConnected(false)
      }
    }

    void fetchHealth()
  }, [])

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-6 py-12 text-slate-50">
      <section className="w-full max-w-2xl rounded-3xl border border-emerald-500/30 bg-slate-900/80 p-8 shadow-2xl shadow-emerald-950/30 backdrop-blur">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-emerald-400">
          Finch Onsite
        </p>
        <h1 className="mt-4 text-4xl font-bold tracking-tight sm:text-5xl">
          Full stack boilerplate
        </h1>
        <p className="mt-4 max-w-xl text-base leading-7 text-slate-300">
          This frontend calls the Django health endpoint on load so you can
          verify the monorepo is wired up end to end.
        </p>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/70 p-6">
          <p className="text-sm text-slate-400">GET /api/health/</p>
          <p
            className={`mt-3 text-lg font-medium ${
              connected ? 'text-emerald-400' : 'text-amber-300'
            }`}
          >
            {connected ? 'Backend reachable' : 'Waiting for backend'}
          </p>
          <pre className="mt-4 overflow-x-auto rounded-xl bg-slate-900 p-4 text-sm text-slate-100">
            {status}
          </pre>
        </div>
      </section>
    </main>
  )
}

export default App
