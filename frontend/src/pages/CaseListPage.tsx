import { motion, useReducedMotion } from 'motion/react'
import {
  ArrowRight,
  Clock3,
  Filter,
  FolderKanban,
  RefreshCw,
  Search,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'

import CaseTable from '../components/CaseTable'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Separator } from '../components/ui/separator'
import { Tabs, TabsList, TabsTrigger } from '../components/ui/tabs'
import { getApiErrorMessage, listCases } from '../lib/cases'
import type { CaseRecord } from '../types/cases'

type CaseListFilter = 'active' | 'all'

export function CaseListPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [cases, setCases] = useState<CaseRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchValue, setSearchValue] = useState('')
  const shouldReduceMotion = useReducedMotion()

  const filter = searchParams.get('status') === 'all' ? 'all' : 'active'
  const refreshKey = searchParams.get('refresh')
  const activeCases = cases.filter((caseRecord) => caseRecord.status === 'active')
  const baseCases = filter === 'active' ? activeCases : cases
  const searchQuery = searchValue.trim().toLowerCase()
  const visibleCases = useMemo(
    () =>
      baseCases.filter((caseRecord) =>
        searchQuery
          ? [
              caseRecord.clientName,
              caseRecord.incidentType,
              caseRecord.insuranceCompanyName,
              caseRecord.stage,
            ]
              .join(' ')
              .toLowerCase()
              .includes(searchQuery)
          : true,
      ),
    [baseCases, searchQuery],
  )
  const stats = [
    { label: 'Loaded cases', value: cases.length.toLocaleString(), icon: FolderKanban },
    { label: 'Active cases', value: activeCases.length.toLocaleString(), icon: Clock3 },
    { label: 'Visible now', value: visibleCases.length.toLocaleString(), icon: Filter },
  ]

  useEffect(() => {
    if (!searchParams.get('status')) {
      const nextParams = new URLSearchParams(searchParams)
      nextParams.set('status', 'active')
      setSearchParams(nextParams, { replace: true })
    }
  }, [searchParams, setSearchParams])

  useEffect(() => {
    let isCancelled = false

    const loadCases = async () => {
      setIsLoading(true)
      setError(null)

      try {
        const nextCases = await listCases(filter === 'active' ? 'active' : undefined)

        if (!isCancelled) {
          setCases(nextCases)
        }
      } catch (nextError) {
        if (!isCancelled) {
          setError(getApiErrorMessage(nextError))
        }
      } finally {
        if (!isCancelled) {
          setIsLoading(false)
        }
      }
    }

    void loadCases()

    return () => {
      isCancelled = true
    }
  }, [filter, refreshKey])

  const updateFilter = (nextFilter: CaseListFilter) => {
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('status', nextFilter)
    setSearchParams(nextParams)
  }

  const reloadCases = () => {
    const nextParams = new URLSearchParams(searchParams)
    nextParams.set('refresh', String(Date.now()))
    setSearchParams(nextParams)
  }

  return (
      <section className="flex flex-col gap-6">
        <motion.header
          initial={shouldReduceMotion ? undefined : { opacity: 0, y: 12 }}
          animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.32, ease: 'easeOut' }}
          className="page-frame overflow-hidden p-6 sm:p-8"
        >
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-3xl">
                <Badge variant="accent">Active desk workflow</Badge>
                <h1 className="font-display mt-4 text-4xl font-semibold tracking-tight text-[color:var(--foreground)] sm:text-5xl">
                  Case register
                </h1>
                <p className="mt-3 max-w-2xl text-sm leading-7 text-[color:var(--muted-foreground)] sm:text-base">
                  Review active matters first, keep archived work one tap away, and move into intake without leaving the register mindset.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <Button variant="outline" size="sm" onClick={reloadCases}>
                  <RefreshCw className="h-4 w-4" />
                  Refresh
                </Button>
                <Button asChild size="sm">
                  <Link to="/cases/new">
                  Create new case
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </Button>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-[1.2fr_0.8fr]">
              <div className="soft-ring rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface)] p-4 sm:p-5">
                <div className="flex items-center gap-3 rounded-full border border-[color:var(--border)] bg-[color:var(--surface-soft)] px-4 py-3">
                  <Search className="h-4 w-4 text-[color:var(--muted-foreground)]" />
                  <Input
                    value={searchValue}
                    onChange={(event) => setSearchValue(event.target.value)}
                    placeholder="Search by client, stage, carrier, or incident type"
                    className="h-auto border-0 bg-transparent p-0 shadow-none focus-visible:ring-0"
                  />
                </div>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="eyebrow">Viewing</p>
                    <p className="mt-2 text-sm leading-6 text-[color:var(--muted-foreground)]">
                      {filter === 'active'
                        ? 'Only active matters are shown by default to keep the desk focused.'
                        : 'All matters are visible, including closed work for reference.'}
                    </p>
                  </div>
                  <Tabs value={filter} onValueChange={(value) => updateFilter(value as CaseListFilter)}>
                    <TabsList>
                      <TabsTrigger value="active">Active cases</TabsTrigger>
                      <TabsTrigger value="all">All cases</TabsTrigger>
                    </TabsList>
                  </Tabs>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-1">
                {stats.map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={shouldReduceMotion ? undefined : { opacity: 0, y: 10 }}
                    animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
                    transition={{ duration: 0.28, delay: shouldReduceMotion ? 0 : 0.05 * index }}
                    className="soft-ring rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface)] px-5 py-4"
                  >
                    <div className="flex items-center justify-between">
                      <p className="eyebrow">{stat.label}</p>
                      <stat.icon className="h-4 w-4 text-[color:var(--primary)]" />
                    </div>
                    <p className="mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
                      {stat.value}
                    </p>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </motion.header>

        <motion.section
          initial={shouldReduceMotion ? undefined : { opacity: 0, y: 12 }}
          animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.34, delay: shouldReduceMotion ? 0 : 0.06, ease: 'easeOut' }}
          className="space-y-6"
        >
          <Card>
            <CardHeader className="pb-4">
              <CardTitle className="text-2xl">Live docket</CardTitle>
            </CardHeader>
            <CardContent>
              <Separator className="mb-6" />
              {isLoading ? (
                <LoadingState />
              ) : error ? (
                <ErrorState message={error} onRetry={reloadCases} />
              ) : visibleCases.length === 0 ? (
                <EmptyState hasActiveFilter={filter === 'active'} />
              ) : (
                <CaseTable
                  data={visibleCases}
                  getRowId={(caseRecord) => String(caseRecord.caseId)}
                  globalFilter={searchQuery}
                  caption={`${filter === 'active' ? 'Active' : 'All'} cases`}
                />
              )}
            </CardContent>
          </Card>
        </motion.section>
      </section>
  )
}

function LoadingState() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <div
          key={index}
          className="soft-ring rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface)] p-5"
        >
          <div className="h-3 w-24 animate-pulse rounded-full bg-[color:var(--surface-strong)]" />
          <div className="mt-5 h-8 w-40 animate-pulse rounded-full bg-[color:var(--surface-strong)]" />
          <div className="mt-4 h-3 w-full animate-pulse rounded-full bg-[color:var(--surface-strong)]" />
          <div className="mt-2 h-3 w-3/4 animate-pulse rounded-full bg-[color:var(--surface-strong)]" />
        </div>
      ))}
    </div>
  )
}

function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div
      role="alert"
      className="soft-ring rounded-[1.5rem] border border-[rgba(185,96,83,0.22)] bg-[#fff6f4] px-6 py-8"
    >
      <p className="eyebrow text-[color:var(--danger)]">
        Unable to load cases
      </p>
      <h2 className="font-display mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
        Something interrupted the desk view
      </h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-[color:var(--muted-foreground)]">
        {message}
      </p>
      {onRetry ? (
        <Button type="button" onClick={onRetry} variant="secondary" className="mt-6">
          <RefreshCw className="h-4 w-4" />
          Try again
        </Button>
      ) : null}
    </div>
  )
}

function EmptyState({ hasActiveFilter }: { hasActiveFilter: boolean }) {
  return (
    <div className="soft-ring rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface)] px-6 py-12 text-center">
      <p className="eyebrow">No records</p>
      <h2 className="font-display mt-3 text-3xl font-semibold tracking-tight text-[color:var(--foreground)]">
        {hasActiveFilter
          ? 'No active matters match the current view'
          : 'There are no matters in the register yet'}
      </h2>
      <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-[color:var(--muted-foreground)]">
        {hasActiveFilter
          ? 'Switch to the full docket to review archived work, or open a new matter if intake is ready.'
          : 'Once case records are created, they will appear here in a balanced and searchable register.'}
      </p>
      <Button asChild variant="outline" className="mt-6">
        <Link to="/cases/new">
          Create new case
          <ArrowRight className="h-4 w-4" />
        </Link>
      </Button>
    </div>
  )
}
export default CaseListPage
