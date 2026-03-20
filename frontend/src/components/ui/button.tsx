import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'

import { cn } from '../../lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-full text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[color:var(--ring)] focus-visible:ring-offset-2 focus-visible:ring-offset-[color:var(--background)] disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary:
          'bg-[color:var(--primary)] text-[color:var(--primary-foreground)] shadow-[0_14px_32px_rgba(158,107,74,0.18)] hover:-translate-y-0.5 hover:bg-[color:var(--primary-strong)]',
        secondary:
          'bg-[color:var(--surface-strong)] text-[color:var(--foreground)] shadow-[0_10px_20px_rgba(64,46,36,0.06)] hover:bg-[color:var(--surface)]',
        outline:
          'border border-[color:var(--border)] bg-[color:var(--surface)] text-[color:var(--foreground)] hover:border-[color:var(--accent-border)] hover:bg-[color:var(--surface-soft)]',
        ghost:
          'text-[color:var(--muted-foreground)] hover:bg-[color:var(--surface-soft)] hover:text-[color:var(--foreground)]',
      },
      size: {
        default: 'h-11 px-5',
        sm: 'h-9 px-4 text-xs uppercase tracking-[0.18em]',
        lg: 'h-12 px-6',
        icon: 'h-10 w-10 rounded-full',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'default',
    },
  },
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  },
)
Button.displayName = 'Button'

export { Button }
