export type DispositionType =
  | 'resale'
  | 'reuse'
  | 'internal_use'
  | 'recycling'
  | 'scrap'
  | 'returned'
  | 'donated'
  | 'other'

export type DispositionStatus =
  | 'pending'
  | 'approved'
  | 'completed'
  | 'cancelled'

export type AssetDisposition = {
  id: number
  asset_id: number
  disposition_type: DispositionType
  disposition_status: DispositionStatus
  disposition_date: string
  processed_by: string | null
  disposition_reference: string | null
  recipient_name: string | null
  recipient_reference: string | null
  amount: string | null
  currency: string | null
  notes: string | null
  created_at: string
  updated_at: string
}