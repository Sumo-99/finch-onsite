import {
  type ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  useReactTable,
  type ColumnDef,
} from '@tanstack/react-table'

import { Badge } from './ui/badge'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './ui/table'

export interface CaseTableRow {
  caseId: number
  status: string
  stage: string
  startDate: string | Date
  incidentType: string
  insuranceCompanyName: string
  clientName: string
}

export interface CaseTableProps<TData extends CaseTableRow> {
  data: TData[]
  columns?: Array<ColumnDef<TData>>
  getRowId?: (row: TData, index: number) => string
  globalFilter?: string
  className?: string
  caption?: string
}

const defaultColumns: Array<ColumnDef<CaseTableRow>> = [
  {
    accessorKey: 'stage',
    header: 'Stage',
    cell: ({ row, getValue }) => (
      <StageBadge status={row.original.status} value={String(getValue())} />
    ),
  },
  {
    accessorKey: 'startDate',
    header: 'Start date',
    cell: ({ getValue }) => <span>{formatCaseDate(getValue() as string | Date)}</span>,
  },
  {
    accessorKey: 'incidentType',
    header: 'Incident type',
    cell: ({ getValue }) => getValue() as string,
  },
  {
    accessorKey: 'insuranceCompanyName',
    header: 'Insurance company',
    cell: ({ getValue }) => getValue() as string,
  },
  {
    accessorKey: 'clientName',
    header: 'Client name',
    cell: ({ getValue }) => getValue() as string,
  },
]

function formatCaseDate(value: string | Date): string {
  const date = value instanceof Date ? value : new Date(value)

  if (Number.isNaN(date.getTime())) {
    return String(value)
  }

  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(date)
}

export function CaseTable<TData extends CaseTableRow>({
  data,
  columns = defaultColumns as Array<ColumnDef<TData>>,
  getRowId,
  globalFilter = '',
  className,
  caption = 'Case register',
}: CaseTableProps<TData>) {
  const columnFilters: ColumnFiltersState = globalFilter
    ? [{ id: 'clientName', value: globalFilter }]
    : []

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getRowId: (row, index) => getRowId?.(row, index) ?? String(row.caseId),
    state: {
      columnFilters,
    },
  })

  return (
      <div
        className={[
          'page-frame overflow-hidden p-2 sm:p-3',
          className,
        ]
          .filter(Boolean)
          .join(' ')}
      >
        <Table>
          <TableCaption className="sr-only">{caption}</TableCaption>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="hover:bg-transparent">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length > 0 ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="text-[color:var(--foreground)]">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center text-sm text-[color:var(--muted-foreground)]"
                >
                  No cases match the current view.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
  )
}

function StageBadge({ status, value }: { status: string; value: string }) {
  const tone = resolveStageTone(status)

  return (
    <Badge variant={tone}>
      {formatStageLabel(value)}
    </Badge>
  )
}

function resolveStageTone(status: string) {
  const normalized = status.toLowerCase()

  if (normalized === 'active') {
    return 'accent'
  }

  if (normalized === 'closed') {
    return 'success'
  }

  return 'warning'
}

function formatStageLabel(value: string) {
  if (value === 'LOR') {
    return value
  }

  if (value === 'MMI_reached') {
    return 'MMI reached'
  }

  return value
    .replaceAll('_', ' ')
    .split(' ')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ')
}

export default CaseTable
