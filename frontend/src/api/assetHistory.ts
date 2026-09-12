import type { AssetHistoryResponse } from '../types/assetHistory'

const API_BASE = '/api'

export async function getAssetHistory(
  assetId: number,
): Promise<AssetHistoryResponse> {
  const response = await fetch(
    `${API_BASE}/assets/${assetId}/history`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load asset history (${response.status})`,
    )
  }

  return response.json() as Promise<AssetHistoryResponse>
}