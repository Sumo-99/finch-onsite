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
    <header className="w-full">
      <div className="grid gap-6 md:grid-cols-2 md:gap-10">
        <section className="space-y-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
              Name
            </p>
            <p className="mt-1 text-base text-neutral-950">
              {formatValue(client.name)}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
              Age
            </p>
            <p className="mt-1 text-base text-neutral-950">
              {formatValue(client.age)}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
              Email
            </p>
            <p className="mt-1 text-base text-neutral-950">
              {formatValue(client.email)}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
              Phone
            </p>
            <p className="mt-1 text-base text-neutral-950">
              {formatValue(client.phone)}
            </p>
          </div>

          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
              Liable
            </p>
            <p className="mt-1 text-base text-neutral-950">
              {formatLiable(client.liable)}
            </p>
          </div>
        </section>

        <section className="space-y-3">
          <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
            {incidentType}
          </p>
          <p className="text-base leading-7 text-neutral-950">{incidentSummary}</p>
        </section>
      </div>
    </header>
  )
}

export default CaseHeader
