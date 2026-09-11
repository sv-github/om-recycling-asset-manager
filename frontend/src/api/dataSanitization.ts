import type { AssetSanitization } from '../types/assetSanitization'

const API_BASE = '/api'

export async function listAssetSanitization(
  assetId: number,
): Promise<AssetSanitization[]> {
  const response = await fetch(
    `${API_BASE}/assets/${assetId}/data-sanitization`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load sanitization history (${response.status})`,
    )
  }

  return response.json() as Promise<AssetSanitization[]>
}