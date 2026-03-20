import type { CaseReport } from '../../api/case'

type LiabilityTabProps = {
  client: CaseReport['client']
}

function formatLiable(value: boolean | null | undefined) {
  if (value === null || value === undefined) {
    return '—'
  }

  return value ? 'Yes' : 'No'
}

function getLiabilityNote(value: boolean | null | undefined) {
  if (value === true) {
    return 'Client bears fault. Exercise caution.'
  }

  if (value === false) {
    return 'Another party bears fault.'
  }

  return 'Liability undetermined.'
}

function LiabilityTab({ client }: LiabilityTabProps) {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-medium uppercase tracking-[0.24em] text-neutral-500">
          Liable
        </p>
        <p className="mt-1 text-base text-neutral-950">
          {formatLiable(client.liable)}
        </p>
      </div>

      <p className="text-base leading-7 text-neutral-700">
        {getLiabilityNote(client.liable)}
      </p>
    </section>
  )
}

export default LiabilityTab
