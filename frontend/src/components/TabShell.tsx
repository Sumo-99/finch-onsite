import { useState } from 'react'

import type { CaseReport } from '../api/case'
import CoverageTab from './tabs/CoverageTab'
import DamagesTab from './tabs/DamagesTab'
import LiabilityTab from './tabs/LiabilityTab'

type TabShellProps = {
  client: CaseReport['client']
  damages: CaseReport['damages']
  coverage: CaseReport['coverage']
}

type TabKey = 'damages' | 'liability' | 'coverage'

function TabShell({ client, damages, coverage }: TabShellProps) {
  const [activeTab, setActiveTab] = useState<TabKey>('damages')

  return (
    <section className="space-y-6 rounded bg-[#fcfbf8] p-6 shadow-[0_10px_30px_rgba(74,58,34,0.06)] ring-1 ring-[#e5ddd2]">
      <div className="space-y-2">
        <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#9a8f81]">
          Case Analysis
        </p>
        <h2 className="text-[18px] font-semibold text-[#1f2933]">Insights</h2>
      </div>

      <div className="flex flex-wrap gap-6 text-[14px]">
        <button
          type="button"
          className={
            activeTab === 'damages'
              ? 'border-b-2 border-[#1f2933] pb-1 font-medium text-[#1f2933]'
              : 'border-b-2 border-transparent pb-1 font-normal text-[#8a8175]'
          }
          onClick={() => setActiveTab('damages')}
        >
          Damages
        </button>
        <button
          type="button"
          className={
            activeTab === 'liability'
              ? 'border-b-2 border-[#1f2933] pb-1 font-medium text-[#1f2933]'
              : 'border-b-2 border-transparent pb-1 font-normal text-[#8a8175]'
          }
          onClick={() => setActiveTab('liability')}
        >
          Liability
        </button>
        <button
          type="button"
          className={
            activeTab === 'coverage'
              ? 'border-b-2 border-[#1f2933] pb-1 font-medium text-[#1f2933]'
              : 'border-b-2 border-transparent pb-1 font-normal text-[#8a8175]'
          }
          onClick={() => setActiveTab('coverage')}
        >
          Coverage
        </button>
      </div>

      <div>
        {activeTab === 'damages' && <DamagesTab damages={damages} />}
        {activeTab === 'liability' && <LiabilityTab client={client} />}
        {activeTab === 'coverage' && <CoverageTab coverage={coverage} />}
      </div>
    </section>
  )
}

export default TabShell
