import type { Asset } from '../types/asset'

const API_BASE = '/api'

export type AssetListFilters = {
  collectionId?: number
  collectionItemId?: number
  serialNumber?: string
  status?: string
}

export type AssetCreateInput = {
  collection_id: number
  collection_item_id?: number | null
  serial_number?: string | null
  asset_category: string
  manufacturer?: string | null
  model?: string | null
  description?: string | null
  received_by?: string | null
  receiving_notes?: string | null
  notes?: string | null
}

export async function listAssets(
  filters: AssetListFilters = {},
): Promise<Asset[]> {
  const params = new URLSearchParams()

  if (filters.collectionId !== undefined) {
    params.set(
      'collection_id',
      String(filters.collectionId),
    )
  }

  if (filters.collectionItemId !== undefined) {
    params.set(
      'collection_item_id',
      String(filters.collectionItemId),
    )
  }

  if (filters.serialNumber !== undefined) {
    params.set(
      'serial_number',
      filters.serialNumber,
    )
  }

  if (filters.status !== undefined) {
    params.set(
      'status_filter',
      filters.status,
    )
  }

  const queryString = params.toString()

  const response = await fetch(
    `${API_BASE}/assets${queryString ? `?${queryString}` : ''}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load assets (${response.status})`,
    )
  }

  return response.json() as Promise<Asset[]>
}

export async function getAsset(
  assetId: number,
): Promise<Asset> {
  const response = await fetch(
    `${API_BASE}/assets/${assetId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load asset (${response.status})`,
    )
  }

  return response.json() as Promise<Asset>
}

export async function createAsset(
  input: AssetCreateInput,
): Promise<Asset> {
  const response = await fetch(
    `${API_BASE}/assets`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(input),
    },
  )

  if (!response.ok) {
    let message = `Failed to register asset (${response.status})`

    try {
      const data = await response.json()

      if (typeof data.detail === 'string') {
        message = data.detail
      } else if (
        Array.isArray(data.detail)
      ) {
        message = data.detail
          .map(
            (item: {
              msg?: string
            }) => item.msg,
          )
          .filter(Boolean)
          .join('; ')
      }
    } catch {
      // Keep the generic HTTP error message.
    }

    throw new Error(message)
  }

  return response.json() as Promise<Asset>
}