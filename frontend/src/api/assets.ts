import type { Asset } from '../types/asset'

const API_BASE = '/api'

export type AssetListFilters = {
  collectionId?: number
  collectionItemId?: number
  serialNumber?: string
  status?: string
}

export async function listAssets(
  filters: AssetListFilters = {},
): Promise<Asset[]> {
  const params = new URLSearchParams()

  if (filters.collectionId !== undefined) {
    params.set('collection_id', String(filters.collectionId))
  }

  if (filters.collectionItemId !== undefined) {
    params.set(
      'collection_item_id',
      String(filters.collectionItemId),
    )
  }

  if (filters.serialNumber !== undefined) {
    params.set('serial_number', filters.serialNumber)
  }

  if (filters.status !== undefined) {
    params.set('status_filter', filters.status)
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