export type AssetHistoryEventType =
  | 'inspection'
  | 'processing'
  | 'sanitization'
  | 'disposition'
  | 'return'

export type AssetHistoryEvent = {
  event_type: AssetHistoryEventType
  event_id: number
  event_date: string
  title: string
  status: string | null
  details: Record<string, unknown>
}

export type AssetHistoryResponse = {
  asset_id: number
  asset_code: string
  events: AssetHistoryEvent[]
}