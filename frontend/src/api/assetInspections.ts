import type { AssetInspection } from '../types/assetInspection'

const API_BASE = '/api'

export async function listAssetInspections(
  assetId: number,
): Promise<AssetInspection[]> {
  const params = new URLSearchParams()

  params.set('asset_id', String(assetId))

  const response = await fetch(
    `${API_BASE}/asset-inspections?${params.toString()}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load inspections (${response.status})`,
    )
  }

  return response.json() as Promise<
    AssetInspection[]
  >
}