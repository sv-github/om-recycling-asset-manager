export type AssetProcessing = {
  id: number
  asset_id: number

  processing_type: string
  grade: string | null

  refurbishment_status: string

  processor: string | null

  processing_date: string

  condition_summary: string | null
  repairs_performed: string | null
  parts_replaced: string | null
  testing_notes: string | null

  processing_reference: string | null

  cost: string | null

  notes: string | null

  created_at: string
  updated_at: string
}