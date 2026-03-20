import { AnimatePresence, motion } from 'motion/react'
import { ArrowRight, CircleCheckBig, RefreshCcw } from 'lucide-react'
import { useMemo, useState } from 'react'
import type { FormEvent } from 'react'

import { Button } from './ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Label } from './ui/label'
import { Separator } from './ui/separator'

export type NewCaseFormValues = {
  clientName: string
  clientEmail: string
  incidentDate: string
  incidentType: string
  insuranceCompanyName: string
}

export interface NewCaseFormProps {
  onSubmit?: (values: NewCaseFormValues) => Promise<void> | void
  className?: string
  initialValues?: Partial<NewCaseFormValues>
  submitLabel?: string
  successTitle?: string
  successDescription?: string
}

type FieldErrors = Partial<Record<keyof NewCaseFormValues, string>>

const DEFAULT_VALUES: NewCaseFormValues = {
  clientName: '',
  clientEmail: '',
  incidentDate: '',
  incidentType: '',
  insuranceCompanyName: '',
}

function isValidEmail(value: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
}

function getTodayIsoDate() {
  return new Date().toISOString().slice(0, 10)
}

function buildInitialValues(
  initialValues?: Partial<NewCaseFormValues>,
): NewCaseFormValues {
  return {
    clientName: initialValues?.clientName?.trim() ?? '',
    clientEmail: initialValues?.clientEmail?.trim() ?? '',
    incidentDate: initialValues?.incidentDate?.trim() ?? '',
    incidentType: initialValues?.incidentType?.trim() ?? '',
    insuranceCompanyName: initialValues?.insuranceCompanyName?.trim() ?? '',
  }
}

function validateValues(values: NewCaseFormValues): FieldErrors {
  const errors: FieldErrors = {}
  const today = getTodayIsoDate()

  if (!values.clientName.trim()) {
    errors.clientName = 'Client name is required.'
  }

  if (!values.clientEmail.trim()) {
    errors.clientEmail = 'Client email is required.'
  } else if (!isValidEmail(values.clientEmail.trim())) {
    errors.clientEmail = 'Enter a valid email address.'
  }

  if (!values.incidentDate) {
    errors.incidentDate = 'Incident date is required.'
  } else if (values.incidentDate > today) {
    errors.incidentDate = 'Incident date cannot be in the future.'
  }

  if (!values.incidentType.trim()) {
    errors.incidentType = 'Incident type is required.'
  }

  if (!values.insuranceCompanyName.trim()) {
    errors.insuranceCompanyName = 'Insurance company name is required.'
  }

  return errors
}

function FieldError({ id, message }: { id: string; message?: string }) {
  if (!message) {
    return null
  }

  return (
    <p id={id} className="mt-2 text-sm leading-6 text-[color:var(--danger)]">
      {message}
    </p>
  )
}

function StatusBanner({
  tone,
  title,
  description,
}: {
  tone: 'error' | 'success'
  title: string
  description: string
}) {
  const styles =
    tone === 'error'
      ? 'border-[rgba(185,96,83,0.22)] bg-[#fff5f3] text-[#8a4b43]'
      : 'border-[#c8d7bd] bg-[#f2f8ef] text-[#51624a]'

  return (
    <div className={`rounded-2xl border px-4 py-3 ${styles}`} role="status">
      <p className="text-sm font-semibold uppercase tracking-[0.26em]">{title}</p>
      <p className="mt-1 text-sm leading-6 opacity-90">{description}</p>
    </div>
  )
}

export default function NewCaseForm({
  onSubmit,
  className,
  initialValues,
  submitLabel = 'Create case record',
  successTitle = 'Case record saved',
  successDescription = 'The intake information was captured and the matter is ready for review.',
}: NewCaseFormProps) {
  const startingValues = useMemo(
    () => ({ ...DEFAULT_VALUES, ...buildInitialValues(initialValues) }),
    [initialValues],
  )

  const [values, setValues] = useState<NewCaseFormValues>(startingValues)
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({})
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const statusTone = formError ? 'error' : 'success'

  const resetForm = () => {
    setValues(startingValues)
    setFieldErrors({})
    setFormError(null)
    setIsSubmitting(false)
    setIsSuccess(false)
  }

  const handleChange = <K extends keyof NewCaseFormValues>(
    field: K,
    nextValue: NewCaseFormValues[K],
  ) => {
    setValues((current) => ({ ...current, [field]: nextValue }))
    setFieldErrors((current) => {
      if (!current[field]) {
        return current
      }

      const nextErrors = { ...current }
      delete nextErrors[field]
      return nextErrors
    })
    setFormError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const nextErrors = validateValues(values)
    setFieldErrors(nextErrors)

    if (Object.keys(nextErrors).length > 0) {
      setFormError('Please correct the highlighted fields before continuing.')
      setIsSuccess(false)
      return
    }

    setIsSubmitting(true)
    setFormError(null)

    try {
      await Promise.resolve(onSubmit?.(values))
      setIsSuccess(true)
    } catch (error) {
      setIsSuccess(false)
      setFormError(
        error instanceof Error
          ? error.message
          : 'We could not save the case record. Please try again.',
      )
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSuccess) {
    return (
      <Card className={className}>
        <CardHeader className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[#edf5e9] text-[#5d7653]">
              <CircleCheckBig className="h-6 w-6" />
            </div>
            <div>
              <CardTitle>{successTitle}</CardTitle>
              <CardDescription>{successDescription}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <StatusBanner
            tone="success"
            title="Intake captured"
            description="The matter has been added to the register and is ready for the next review step."
          />

          <div className="mt-6 grid gap-4 rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface-soft)] p-5 text-sm text-[color:var(--muted-foreground)] sm:grid-cols-2">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[color:var(--muted-foreground)]">
              Client
            </p>
            <p className="mt-2 text-base font-medium text-[color:var(--foreground)]">
              {values.clientName}
            </p>
            <p className="mt-1 break-all">{values.clientEmail}</p>
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[color:var(--muted-foreground)]">
              Incident
            </p>
            <p className="mt-2 text-base font-medium text-[color:var(--foreground)]">
              {values.incidentType}
            </p>
            <p className="mt-1">{values.incidentDate}</p>
          </div>
          <div className="sm:col-span-2">
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-[color:var(--muted-foreground)]">
              Insurance carrier
            </p>
            <p className="mt-2 text-base font-medium text-[color:var(--foreground)]">
              {values.insuranceCompanyName}
            </p>
          </div>
        </div>

          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Button type="button" onClick={resetForm} variant="secondary">
              <RefreshCcw className="h-4 w-4" />
            File another case
            </Button>
            <Button asChild variant="outline">
              <a href="/cases">
                Review active register
                <ArrowRight className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <p className="eyebrow">Intake document</p>
        <CardTitle className="text-3xl">New case details</CardTitle>
        <CardDescription>
          Capture the client facts, incident timing, and carrier context in one calm pass.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <AnimatePresence initial={false}>
          {formError ? (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
            >
          <StatusBanner
            tone={statusTone}
            title={statusTone === 'error' ? 'Action required' : 'Saved'}
            description={formError}
          />
            </motion.div>
          ) : null}
        </AnimatePresence>

        <form className="space-y-5" onSubmit={handleSubmit} noValidate>
          <div className="grid gap-5 md:grid-cols-2">
            <div className="md:col-span-1">
              <Label htmlFor="clientName">Client name</Label>
              <Input
                id="clientName"
                name="clientName"
                type="text"
                autoComplete="name"
                value={values.clientName}
                onChange={(event) => handleChange('clientName', event.target.value)}
                disabled={isSubmitting}
                aria-invalid={Boolean(fieldErrors.clientName)}
                aria-describedby={
                  fieldErrors.clientName ? 'clientName-error' : undefined
                }
                className="mt-2"
                placeholder="Client full name"
              />
              <FieldError id="clientName-error" message={fieldErrors.clientName} />
            </div>

            <div className="md:col-span-1">
              <Label htmlFor="clientEmail">Client email</Label>
              <Input
                id="clientEmail"
                name="clientEmail"
                type="email"
                autoComplete="email"
                value={values.clientEmail}
                onChange={(event) => handleChange('clientEmail', event.target.value)}
                disabled={isSubmitting}
                aria-invalid={Boolean(fieldErrors.clientEmail)}
                aria-describedby={
                  fieldErrors.clientEmail ? 'clientEmail-error' : undefined
                }
                className="mt-2"
                placeholder="name@client.com"
              />
              <FieldError id="clientEmail-error" message={fieldErrors.clientEmail} />
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <p className="eyebrow">Matter facts</p>
            <p className="text-sm leading-6 text-[color:var(--muted-foreground)]">
              These fields determine how the case enters the active register.
            </p>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            <div className="md:col-span-1">
              <Label htmlFor="incidentDate">Incident date</Label>
              <Input
                id="incidentDate"
                name="incidentDate"
                type="date"
                max={getTodayIsoDate()}
                value={values.incidentDate}
                onChange={(event) => handleChange('incidentDate', event.target.value)}
                disabled={isSubmitting}
                aria-invalid={Boolean(fieldErrors.incidentDate)}
                aria-describedby={
                  fieldErrors.incidentDate ? 'incidentDate-error' : undefined
                }
                className="mt-2"
              />
              <FieldError id="incidentDate-error" message={fieldErrors.incidentDate} />
            </div>

            <div className="md:col-span-1">
              <Label htmlFor="incidentType">Incident type</Label>
              <Input
                id="incidentType"
                name="incidentType"
                type="text"
                value={values.incidentType}
                onChange={(event) => handleChange('incidentType', event.target.value)}
                disabled={isSubmitting}
                aria-invalid={Boolean(fieldErrors.incidentType)}
                aria-describedby={
                  fieldErrors.incidentType ? 'incidentType-error' : undefined
                }
                className="mt-2"
                placeholder="Auto accident, premises liability, workplace injury..."
              />
              <FieldError id="incidentType-error" message={fieldErrors.incidentType} />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="insuranceCompanyName">Insurance company name</Label>
              <Input
                id="insuranceCompanyName"
                name="insuranceCompanyName"
                type="text"
                autoComplete="organization"
                value={values.insuranceCompanyName}
                onChange={(event) =>
                  handleChange('insuranceCompanyName', event.target.value)
                }
                disabled={isSubmitting}
                aria-invalid={Boolean(fieldErrors.insuranceCompanyName)}
                aria-describedby={
                  fieldErrors.insuranceCompanyName ? 'insuranceCompanyName-error' : undefined
                }
                className="mt-2"
                placeholder="Insurance carrier"
              />
              <FieldError
                id="insuranceCompanyName-error"
                message={fieldErrors.insuranceCompanyName}
              />
            </div>
          </div>

          <div className="flex flex-col gap-3 border-t border-[color:var(--border)] pt-5 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm leading-6 text-[color:var(--muted-foreground)]">
              Required fields are validated before submission. The case will not
              save until every value is complete.
            </p>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving case…' : submitLabel}
              {!isSubmitting ? <ArrowRight className="h-4 w-4" /> : null}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
