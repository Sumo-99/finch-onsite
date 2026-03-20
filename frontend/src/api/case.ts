import axios from 'axios'

export type CaseReport = {
  case: {
    id: number
    status: string
    incident_type: string | null
    incident_summary: string | null
    recommendation: 'ACCEPT' | 'REJECT' | 'REVIEW' | null
    created_at: string
  }
  client: {
    name: string | null
    age: number | null
    email: string | null
    phone: string | null
    liable: boolean | null
    liable_reason: string | null
  }
  damages: {
    treatment_received: boolean | null
    treatment_type: string | null
    description: string | null
    treatment_cost: string | null
  }
  coverage:
    | {
        type: string | null
        insurer_name: string | null
        policy_limit: string | null
        deductible: string | null
      }
    | null
}

export async function fetchCaseReport(caseId: number): Promise<CaseReport> {
  const response = await axios.get<CaseReport>(
    `http://localhost:8000/api/cases/${caseId}/report/`,
    {
      headers: {
        Authorization: 'Bearer 1a59206c30a42a62292e42bab7c0fbc043f42fa8',
      },
    }
  )

  return response.data
}
