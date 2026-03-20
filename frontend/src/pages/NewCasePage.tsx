import { motion, useReducedMotion } from 'motion/react'
import { ArrowLeft, ConciergeBell, HeartHandshake, ShieldCheck } from 'lucide-react'
import { Link } from 'react-router-dom'

import NewCaseForm, { type NewCaseFormValues } from '../components/NewCaseForm'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Card, CardContent } from '../components/ui/card'
import { Separator } from '../components/ui/separator'
import { createCase, getApiErrorMessage } from '../lib/cases'

export interface NewCasePageProps {
  onSubmit?: (values: NewCaseFormValues) => Promise<void> | void
  title?: string
  subtitle?: string
  className?: string
}

const submitCase = async (values: NewCaseFormValues) => {
  try {
    await createCase(values)
  } catch (error) {
    throw new Error(getApiErrorMessage(error))
  }
}

export default function NewCasePage({
  onSubmit,
  title = 'Open a new matter',
  subtitle = 'A disciplined intake screen for client facts, incident timing, and carrier details.',
  className,
}: NewCasePageProps) {
  const handleSubmit = onSubmit ?? submitCase
  const shouldReduceMotion = useReducedMotion()

  return (
    <section className={className}>
      <div className="grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
        <motion.section
          initial={shouldReduceMotion ? undefined : { opacity: 0, y: 12 }}
          animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
          className="page-frame p-8 sm:p-10"
        >
          <div className="space-y-6">
            <Badge variant="accent">Warm concierge intake</Badge>
            <div className="space-y-4">
              <p className="eyebrow text-[color:var(--primary)]">
              Case intake
              </p>
              <h1 className="font-display text-5xl leading-none text-[color:var(--foreground)] sm:text-6xl">
                {title}
              </h1>
              <p className="max-w-2xl text-base leading-8 text-[color:var(--muted-foreground)] sm:text-lg">
                {subtitle}
              </p>
            </div>
            <Button asChild variant="outline">
              <Link to="/cases">
                <ArrowLeft className="h-4 w-4" />
                Return to case register
              </Link>
            </Button>
          </div>

          <Separator className="my-8" />

          <div className="grid gap-4">
            {[
              {
                icon: ConciergeBell,
                title: 'Gentle intake rhythm',
                description: 'The form groups client identity and matter facts so staff never feel like they are dropping data into a void.',
              },
              {
                icon: HeartHandshake,
                title: 'Human guidance',
                description: 'Validation copy stays plain and supportive, with surfaces that feel warm rather than clinical or dark.',
              },
              {
                icon: ShieldCheck,
                title: 'Trustworthy handoff',
                description: 'The confirmation state should reassure the user and make the next action obvious: return to the live register or open another case.',
              },
            ].map((item, index) => (
              <motion.div
                key={item.title}
                initial={shouldReduceMotion ? undefined : { opacity: 0, x: -8 }}
                animate={shouldReduceMotion ? undefined : { opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: shouldReduceMotion ? 0 : index * 0.08 }}
                className="soft-ring rounded-[1.5rem] border border-[color:var(--border)] bg-[color:var(--surface)] p-5"
              >
                <item.icon className="h-5 w-5 text-[color:var(--primary)]" />
                <h2 className="mt-3 text-lg font-semibold text-[color:var(--foreground)]">
                  {item.title}
                </h2>
                <p className="mt-2 text-sm leading-6 text-[color:var(--muted-foreground)]">
                  {item.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        <motion.div
          initial={shouldReduceMotion ? undefined : { opacity: 0, y: 12 }}
          animate={shouldReduceMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.35, delay: shouldReduceMotion ? 0 : 0.08, ease: 'easeOut' }}
          className="self-start"
        >
          <NewCaseForm
            onSubmit={handleSubmit}
            submitLabel="Save matter to active register"
            successTitle="Matter intake complete"
            successDescription="Client facts are recorded, the carrier is attached, and the case is ready for staff review."
          />
          <Card className="mt-5">
            <CardContent className="grid gap-3 p-5 text-sm leading-6 text-[color:var(--muted-foreground)]">
              <p className="eyebrow">After submission</p>
              <p>
                The case enters the active register immediately, so the intake coordinator can pivot
                back to review without losing context.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </section>
  )
}
