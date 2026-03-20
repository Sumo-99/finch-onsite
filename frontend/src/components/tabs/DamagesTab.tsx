import type { CaseReport } from '../../api/case'

type DamagesTabProps = {
  damages: CaseReport['damages']
}

function formatText(value: string | number | null | undefined) {
  return value ?? '—'
}

function formatBoolean(value: boolean | null | undefined) {
  if (value === null || value === undefined) {
    return '—'
  }

  return value ? 'Yes' : 'No'
}

function DamagesTab({ damages }: DamagesTabProps) {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Treatment Received
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatBoolean(damages.treatment_received)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Treatment Type
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(damages.treatment_type)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Description
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(damages.description)}
        </p>
      </div>

      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Treatment Cost
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatText(damages.treatment_cost)}
        </p>
      </div>
    </section>
  )
}

export default DamagesTab
