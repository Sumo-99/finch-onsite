import type { CaseReport } from '../api/case'

type CaseHeaderProps = {
  client: CaseReport['client']
  caseData: CaseReport['case']
}

function formatValue(value: string | number | null | undefined) {
  return value ?? '—'
}

function formatLiable(value: boolean | null | undefined) {
  if (value === null || value === undefined) {
    return '—'
  }

  return value ? 'Yes' : 'No'
}

function CaseHeader({ client, caseData }: CaseHeaderProps) {
  const incidentType = caseData.incident_type ?? '—'
  const incidentSummary = caseData.incident_summary ?? '—'

  return (
    <header className="w-full rounded bg-[#fcfbf8] p-6 shadow-[0_10px_30px_rgba(74,58,34,0.06)] ring-1 ring-[#e5ddd2]">
      <div className="mb-6 space-y-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#9a8f81]">
          Case Overview
        </p>
        <h2 className="text-[18px] font-semibold text-[#1f2933]">Client Details</h2>
      </div>

      <div className="grid gap-6 md:grid-cols-2 md:gap-6">
        <section className="space-y-3">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
              Name
            </p>
            <p className="mt-1 text-[15px] font-normal text-[#111111]">
              {formatValue(client.name)}
            </p>
          </div>

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
              Age
            </p>
            <p className="mt-1 text-[15px] font-normal text-[#111111]">
              {formatValue(client.age)}
            </p>
          </div>

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
              Email
            </p>
            <p className="mt-1 text-[15px] font-normal text-[#111111]">
              {formatValue(client.email)}
            </p>
          </div>

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
              Phone
            </p>
            <p className="mt-1 text-[15px] font-normal text-[#111111]">
              {formatValue(client.phone)}
            </p>
          </div>

          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
              Liable
            </p>
            <p className="mt-1 text-[15px] font-normal text-[#111111]">
              {formatLiable(client.liable)}
            </p>
          </div>

          {client.liable_reason !== null ? (
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
                Liability Justification
              </p>
              <p className="mt-1 text-[15px] leading-[1.6] text-[#111111]">
                {client.liable_reason}
              </p>
            </div>
          ) : null}
        </section>

        <section className="space-y-3 md:border-l md:border-[#e5ddd2] md:pl-6">
          <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
            {incidentType}
          </p>
          <p className="text-[15px] leading-[1.6] text-[#333333]">{incidentSummary}</p>
        </section>
      </div>
    </header>
  )
}

export default CaseHeader
