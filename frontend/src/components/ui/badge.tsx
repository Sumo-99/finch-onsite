import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '../../lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-3 py-1 text-[0.68rem] font-semibold uppercase tracking-[0.22em]',
  {
    variants: {
      variant: {
        neutral: 'border-[color:var(--border)] bg-[color:var(--surface-soft)] text-[color:var(--muted-foreground)]',
        accent: 'border-[color:var(--accent-border)] bg-[color:var(--accent-soft)] text-[color:var(--accent-foreground)]',
        success: 'border-[#b9d9bf] bg-[#f0faf2] text-[#48624c]',
        warning: 'border-[#e7d1b8] bg-[#fff8ef] text-[#8c684c]',
      },
    },
    defaultVariants: {
      variant: 'neutral',
    },
  },
)

function Badge({
  className,
  variant,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof badgeVariants>) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge }
