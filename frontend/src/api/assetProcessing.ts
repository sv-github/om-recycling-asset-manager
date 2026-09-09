import type { AssetProcessing } from '../types/assetProcessing'

const API_BASE = '/api'

export async function listAssetProcessing(
  assetId: number,
): Promise<AssetProcessing[]> {
  const response = await fetch(
    `${API_BASE}/asset-processing/asset/${assetId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load processing history (${response.status})`,
    )
  }

  return response.json() as Promise<
    AssetProcessing[]
  >
}