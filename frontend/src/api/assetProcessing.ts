import type { Asset } from '../types/asset'
import type { AssetProcessing } from '../types/assetProcessing'

const API_BASE = '/api'

export type AssetProcessingCreateInput = {
  asset_id: number
  processing_type: string
  grade?: string | null
  refurbishment_status: string
  processor?: string | null
  processing_date: string
  condition_summary?: string | null
  repairs_performed?: string | null
  parts_replaced?: string | null
  testing_notes?: string | null
  processing_reference?: string | null
  cost?: string | null
  notes?: string | null
}

export type AssetProcessingUpdateInput = Partial<
  Omit<AssetProcessingCreateInput, 'asset_id'>
>

async function parseError(response: Response, fallback: string): Promise<Error> {
  try {
    const data = await response.json()
    if (typeof data.detail === 'string') return new Error(data.detail)
    if (Array.isArray(data.detail)) {
      const message = data.detail
        .map((item: { msg?: string }) => item.msg)
        .filter(Boolean)
        .join('; ')
      if (message) return new Error(message)
    }
  } catch {
    // Keep fallback.
  }
  return new Error(fallback)
}

export async function listAssetProcessing(assetId: number): Promise<AssetProcessing[]> {
  const response = await fetch(`${API_BASE}/asset-processing/asset/${assetId}`)
  if (!response.ok) {
    throw await parseError(response, `Failed to load processing history (${response.status})`)
  }
  return response.json() as Promise<AssetProcessing[]>
}

export async function createAssetProcessing(
  input: AssetProcessingCreateInput,
): Promise<AssetProcessing> {
  const response = await fetch(`${API_BASE}/asset-processing`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw await parseError(response, `Failed to create processing record (${response.status})`)
  }
  return response.json() as Promise<AssetProcessing>
}

export async function updateAssetProcessing(
  processingId: number,
  input: AssetProcessingUpdateInput,
): Promise<AssetProcessing> {
  const response = await fetch(`${API_BASE}/asset-processing/${processingId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) {
    throw await parseError(response, `Failed to update processing record (${response.status})`)
  }
  return response.json() as Promise<AssetProcessing>
}

export function findAssetByBarcode(assets: Asset[], barcode: string): Asset | undefined {
  const value = barcode.trim().toLowerCase()
  if (!value) return undefined

  return assets.find((asset) =>
    [asset.asset_code, asset.serial_number].some(
      (candidate) => candidate?.trim().toLowerCase() === value,
    ),
  )
}
