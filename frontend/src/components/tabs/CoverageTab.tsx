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
      <section className="text-[15px] leading-[1.6] text-[#111111]">
        No coverage information available.
      </section>
    )
  }

  const insurerLabel = coverage.insurer_inferred
    ? 'POTENTIAL INSURANCE PROVIDER'
    : 'INSURER'
  const showPendingVerificationNote =
    coverage.insurer_inferred &&
    coverage.policy_limit === null &&
    coverage.deductible === null &&
    coverage.type === null

  return (
    <section className="space-y-4">
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
          Coverage Type
        </p>
        <p className="mt-1 text-[15px] font-normal text-[#111111]">
          {formatText(coverage.type)}
        </p>
      </div>

      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
          {insurerLabel}
        </p>
        <p className="mt-1 text-[15px] font-normal text-[#111111]">
          {formatText(coverage.insurer_name)}
        </p>
        {showPendingVerificationNote ? (
          <p className="mt-1 text-[12px] text-[#888888]">
            Coverage details pending verification
          </p>
        ) : null}
      </div>

      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
          Policy Limit
        </p>
        <p className="mt-1 text-[15px] font-normal text-[#111111]">
          {formatText(coverage.policy_limit)}
        </p>
      </div>

      <div>
        <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
          Deductible
        </p>
        <p className="mt-1 text-[15px] font-normal text-[#111111]">
          {formatText(coverage.deductible)}
        </p>
      </div>
    </section>
  )
}

export default CoverageTab
