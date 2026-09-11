export type AssetSanitization = {
  id: number
  asset_id: number
  data_wipe_status: string
  data_wipe_method: string | null
  data_wipe_date: string | null
  data_wipe_reference: string | null
  created_at: string
  updated_at: string
}