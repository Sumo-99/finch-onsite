import { useEffect, useState } from 'react'

import { fetchCaseReport, type CaseReport } from '../api/case'
import CaseHeader from '../components/CaseHeader'
import RecommendationBanner from '../components/RecommendationBanner'
import TabShell from '../components/TabShell'

const CASE_ID = 3

function getCaseIdFromUrl() {
  const searchParams = new URLSearchParams(window.location.search)
  const queryCaseId = searchParams.get('caseId')

  if (queryCaseId !== null) {
    const parsedQueryCaseId = Number.parseInt(queryCaseId, 10)

    if (Number.isInteger(parsedQueryCaseId) && parsedQueryCaseId > 0) {
      return parsedQueryCaseId
    }
  }

  const pathSegments = window.location.pathname
    .split('/')
    .filter(Boolean)
    .reverse()

  for (const segment of pathSegments) {
    const parsedSegmentCaseId = Number.parseInt(segment, 10)

    if (Number.isInteger(parsedSegmentCaseId) && parsedSegmentCaseId > 0) {
      return parsedSegmentCaseId
    }
  }

  return CASE_ID
}

function CaseReportPage() {
  const [caseReport, setCaseReport] = useState<CaseReport | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  useEffect(() => {
    let ignore = false

    const loadCaseReport = async () => {
      try {
        const report = await fetchCaseReport(getCaseIdFromUrl())

        if (!ignore) {
          setCaseReport(report)
        }
      } catch {
        if (!ignore) {
          setHasError(true)
        }
      } finally {
        if (!ignore) {
          setIsLoading(false)
        }
      }
    }

    void loadCaseReport()

    return () => {
      ignore = true
    }
  }, [])

  if (isLoading) {
    return <div className="min-h-screen bg-[#f2eee8] px-6 py-12 text-[#1f2933]">Loading...</div>
  }

  if (hasError || caseReport === null) {
    return (
      <div className="min-h-screen bg-[#f2eee8] px-6 py-12 text-[#1f2933]">
        Error loading case.
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#f2eee8] text-[#1f2933]">
      <header className="w-full border-b border-[#d8d0c4] bg-[#fcfbf8] px-4 py-5 text-lg font-semibold text-[#1f2933]">
        Finch Legal
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-6 py-6 pb-12">
        <RecommendationBanner recommendation={caseReport.case.recommendation} />
        <CaseHeader client={caseReport.client} caseData={caseReport.case} />
        <TabShell
          client={caseReport.client}
          damages={caseReport.damages}
          coverage={caseReport.coverage}
        />
      </main>
    </div>
  )
}

export default CaseReportPage
