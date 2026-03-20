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
        <p className="text-[10px] font-semibold uppercase tracking-[0.08em] text-[#888888]">
          Liable
        </p>
        <p className="mt-1 text-[15px] font-normal text-[#111111]">
          {formatLiable(client.liable)}
        </p>
      </div>

      <p className="text-[15px] leading-[1.6] text-[#111111]">
        {getLiabilityNote(client.liable)}
      </p>

      {client.liable_reason !== null ? (
        <p className="text-[15px] leading-[1.6] text-[#111111]">
          {client.liable_reason}
        </p>
      ) : null}
    </section>
  )
}

export default LiabilityTab
