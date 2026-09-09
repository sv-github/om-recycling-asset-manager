export type AssetInspection = {
  id: number
  asset_id: number

  inspection_type: string
  inspection_date: string
  inspected_by: string | null

  working_status: string
  overall_condition: string

  display_condition: string
  body_condition: string
  keyboard_condition: string
  touchpad_condition: string
  hinge_condition: string
  ports_condition: string
  battery_condition: string
  charger_status: string

  ram_status: string
  storage_status: string
  cpu_status: string
  gpu_status: string

  accessories: string | null
  inspection_notes: string | null

  created_at: string
  updated_at: string
}