export type Collection = {
  id: number
  collection_code: string
  customer_id: number
  location_id: number
  collection_date: string
  pickup_receipt_number: string | null
  source_type: string
  status: string
  expected_item_count: number | null
  transport_reference: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type Customer = {
  id: number
  customer_code: string
  company_name: string
  is_active: boolean
}

export type CustomerLocation = {
  id: number
  customer_id: number
  location_code: string
  location_name: string
  is_active: boolean
}

export type CollectionStatus = {
  id: number
  code: string
  name: string
  description: string | null
  is_active: boolean
  sort_order: number
}