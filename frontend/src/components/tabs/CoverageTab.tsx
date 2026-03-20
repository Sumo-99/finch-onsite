import type { CaseReport } from '../../api/case'

type CoverageTabProps = {
  coverage: CaseReport['coverage']
}

function formatText(value: string | number | null | undefined) {
  return value ?? '—'
}

function CoverageTab({ coverage }: CoverageTabProps) {
  if (coverage === null) {
    return (
      <section className="text-base leading-7 text-neutral-700">
        No coverage information available.
      </section>
    )
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Coverage Type
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(coverage.type)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Insurer Name
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(coverage.insurer_name)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Policy Limit
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(coverage.policy_limit)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Deductible
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(coverage.deductible)}
        </p>
      </div>
    </section>
  )
}

export default CoverageTab
