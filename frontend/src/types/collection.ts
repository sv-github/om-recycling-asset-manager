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
  legal_name: string | null
  gstin: string | null
  primary_contact_name: string | null
  primary_contact_email: string | null
  primary_contact_phone: string | null
  address: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type CustomerLocation = {
  id: number
  customer_id: number
  location_code: string
  location_name: string
  address: string | null
  contact_name: string | null
  contact_email: string | null
  contact_phone: string | null
  notes: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export type CollectionStatus = {
  id: number
  code: string
  name: string
  description: string | null
  is_active: boolean
  sort_order: number
}

export type CollectionItem = {
  id: number
  collection_id: number
  category: string
  manufacturer: string | null
  model: string | null
  description: string | null
  expected_quantity: number
  notes: string | null
  created_at: string
  updated_at: string
}

export type CollectionAsset = {
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