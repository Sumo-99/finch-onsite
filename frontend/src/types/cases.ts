export type CaseApiResponse = {
  case_id: number
  start_date: string
  intake_date: string
  incident_type: string
  insurance_company_name: string
  status: string
  stage: string
  client: number
  client_name: string
  user: number
  user_email: string
}

export type CaseRecord = {
  caseId: number
  startDate: string
  intakeDate: string
  incidentType: string
  insuranceCompanyName: string
  status: string
  stage: string
  clientId: number
  clientName: string
  userId: number
  userEmail: string
}

export type CreateCasePayload = {
  clientName: string
  clientEmail: string
  incidentDate: string
  incidentType: string
  insuranceCompanyName: string
}

export function mapCaseResponse(caseRecord: CaseApiResponse): CaseRecord {
  return {
    caseId: caseRecord.case_id,
    startDate: caseRecord.start_date,
    intakeDate: caseRecord.intake_date,
    incidentType: caseRecord.incident_type,
    insuranceCompanyName: caseRecord.insurance_company_name,
    status: caseRecord.status,
    stage: caseRecord.stage,
    clientId: caseRecord.client,
    clientName: caseRecord.client_name,
    userId: caseRecord.user,
    userEmail: caseRecord.user_email,
  }
}
