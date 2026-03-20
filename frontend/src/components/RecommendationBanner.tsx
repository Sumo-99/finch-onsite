type Recommendation = 'ACCEPT' | 'REJECT' | 'REVIEW'

type RecommendationBannerProps = {
  recommendation: Recommendation | null
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

function RecommendationBanner({ recommendation }: RecommendationBannerProps) {
  const state = recommendation ?? 'PENDING'
  const { backgroundColor, label } = recommendationStyles[state]

  return (
    <div
      className="flex h-12 w-full items-center justify-center rounded border border-white/30 px-6 text-center text-[14px] font-bold uppercase tracking-[0.1em] text-white shadow-[0_8px_20px_rgba(0,0,0,0.08)]"
      style={{ backgroundColor }}
    >
      <span>{label}</span>
    </div>
  )
}

export default RecommendationBanner
