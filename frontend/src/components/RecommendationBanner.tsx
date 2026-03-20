type Recommendation = 'ACCEPT' | 'REJECT' | 'REVIEW'

type RecommendationBannerProps = {
  recommendation: Recommendation | null
  reason: string | null
}

const recommendationStyles: Record<
  Recommendation | 'PENDING',
  { backgroundColor: string; label: string }
> = {
  ACCEPT: {
    backgroundColor: '#16a34a',
    label: 'ACCEPT',
  },
  REJECT: {
    backgroundColor: '#dc2626',
    label: 'REJECT',
  },
  REVIEW: {
    backgroundColor: '#d97706',
    label: 'REVIEW',
  },
  PENDING: {
    backgroundColor: '#6b7280',
    label: 'Pending',
  },
}

function RecommendationBanner({ recommendation, reason }: RecommendationBannerProps) {
  const state = recommendation ?? 'PENDING'
  const { backgroundColor, label } = recommendationStyles[state]

  return (
    <div
      className="flex w-full flex-col items-start justify-center gap-2 rounded border border-white/30 px-6 py-5 text-left text-white shadow-[0_8px_20px_rgba(0,0,0,0.08)]"
      style={{ backgroundColor }}
    >
      <div className="space-y-1">
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-white/80">
          Intake Decision
        </p>
        <p className="text-[13px] font-medium text-white/90">
          Recommended next step for this client
        </p>
      </div>
      <span className="text-[14px] font-bold uppercase tracking-[0.1em]">{label}</span>
      {reason !== null ? (
        <p className="mt-2 max-w-[600px] self-center text-center text-[14px] font-normal text-white/85">
          {reason}
        </p>
      ) : null}
    </div>
  )
}

export default RecommendationBanner
