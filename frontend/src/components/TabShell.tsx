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
    <section className="space-y-6">
      <div className="flex flex-wrap gap-6 text-sm text-neutral-950">
        <button
          type="button"
          className={activeTab === 'damages' ? 'underline underline-offset-8' : ''}
          onClick={() => setActiveTab('damages')}
        >
          Damages
        </button>
        <button
          type="button"
          className={activeTab === 'liability' ? 'underline underline-offset-8' : ''}
          onClick={() => setActiveTab('liability')}
        >
          Liability
        </button>
        <button
          type="button"
          className={activeTab === 'coverage' ? 'underline underline-offset-8' : ''}
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
