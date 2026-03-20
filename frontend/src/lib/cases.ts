import axios from 'axios'

import {
  mapCaseResponse,
  type CaseApiResponse,
  type CaseRecord,
  type CreateCasePayload,
} from '../types/cases'

export async function listCases(status?: 'active' | 'closed'): Promise<CaseRecord[]> {
  const response = await axios.get<CaseApiResponse[]>('/api/cases/', {
    params: status ? { status } : undefined,
  })

  return response.data.map(mapCaseResponse)
}

export async function createCase(payload: CreateCasePayload): Promise<CaseRecord> {
  const response = await axios.post<CaseApiResponse>('/api/cases/', {
    client_name: payload.clientName.trim(),
    client_email: payload.clientEmail.trim(),
    incident_date: payload.incidentDate,
    incident_type: payload.incidentType.trim(),
    insurance_company_name: payload.insuranceCompanyName.trim(),
  })

  return mapCaseResponse(response.data)
}

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail

    if (typeof detail === 'string' && detail) {
      return detail
    }

    const values = error.response?.data
    if (values && typeof values === 'object') {
      const firstMessage = Object.values(values)
        .flatMap((value) =>
          Array.isArray(value) ? value : typeof value === 'string' ? [value] : [],
        )
        .find((value) => typeof value === 'string' && value.length > 0)

      if (firstMessage) {
        return firstMessage
      }
    }
  }

  return error instanceof Error
    ? error.message
    : 'Something went wrong while communicating with the case service.'
}
