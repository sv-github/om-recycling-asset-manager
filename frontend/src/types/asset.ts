export type Asset = {
  id: number
  asset_code: string
  serial_number: string | null

  collection_id: number
  collection_item_id: number | null

  asset_category: string
  manufacturer: string | null
  model: string | null
  description: string | null

  status: string

  received_at: string
  received_by: string | null
  receiving_notes: string | null

  data_wipe_status: string
  data_wipe_method: string | null
  data_wipe_date: string | null
  data_wipe_reference: string | null

  final_disposition: string | null
  notes: string | null

  created_at: string
  updated_at: string
}