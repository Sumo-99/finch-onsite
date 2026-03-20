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
      className="flex w-full items-center justify-center px-6 py-4 text-center font-black uppercase tracking-[0.25em] text-white"
      style={{ backgroundColor }}
    >
      <span className="text-2xl sm:text-3xl">{label}</span>
    </div>
  )
}

export default RecommendationBanner
