import type { AssetDisposition } from '../types/assetDisposition'

const API_BASE = '/api'

export async function listAssetDispositions(
  assetId: number,
): Promise<AssetDisposition[]> {
  const response = await fetch(
    `${API_BASE}/asset-dispositions/asset/${assetId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load disposition history (${response.status})`,
    )
  }

  return response.json() as Promise<
    AssetDisposition[]
  >
}