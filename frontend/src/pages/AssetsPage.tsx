import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'

import { listAssets } from '../api/assets'
import type { Asset } from '../types/asset'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import './AssetsPage.css'

function getStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'received':
      return 'info'

    case 'processing':
      return 'warning'

    case 'disposed':
      return 'success'

    case 'closed':
      return 'neutral'

    default:
      return 'neutral'
  }
}

function AssetsPage() {
  const navigate = useNavigate()

  const [assets, setAssets] = useState<Asset[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function loadAssets() {
    setLoading(true)
    setError(null)

    try {
      const data = await listAssets(
        statusFilter
          ? {
              status: statusFilter,
            }
          : {},
      )

      setAssets(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load assets.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadAssets()
  }, [statusFilter])

  const filteredAssets = useMemo(() => {
    const searchTerm = search.trim().toLowerCase()

    if (!searchTerm) {
      return assets
    }

    return assets.filter((asset) => {
      return [
        asset.asset_code,
        asset.serial_number,
        asset.asset_category,
        asset.manufacturer,
        asset.model,
      ].some((value) =>
        value?.toLowerCase().includes(searchTerm),
      )
    })
  }, [assets, search])

  return (
    <>
      <PageHeader
        title="Assets"
        description="View and manage equipment received by OM Recycling."
      />

      <Card className="assets-filter-card">
        <div className="assets-filters">
          <div className="assets-search">
            <label htmlFor="asset-search">
              Search assets
            </label>

            <input
              id="asset-search"
              type="search"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Asset code, serial, category, manufacturer..."
            />
          </div>

          <div className="assets-status-filter">
            <label htmlFor="asset-status">
              Status
            </label>

            <select
              id="asset-status"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(event.target.value)
              }
            >
              <option value="">All statuses</option>
              <option value="received">Received</option>
              <option value="processing">Processing</option>
              <option value="disposed">Disposed</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div className="assets-filter-action">
            <Button
              variant="secondary"
              onClick={() => {
                setSearch('')
                setStatusFilter('')
              }}
            >
              Clear
            </Button>
          </div>
        </div>
      </Card>

      <div className="assets-list-header">
        <div>
          <span className="assets-list-title">
            Asset Register
          </span>

          {!loading && (
            <span className="assets-list-count">
              {filteredAssets.length}{' '}
              {filteredAssets.length === 1
                ? 'asset'
                : 'assets'}
            </span>
          )}
        </div>
      </div>

      <Card className="assets-table-card">
        {loading && (
          <div className="assets-state">
            Loading assets...
          </div>
        )}

        {!loading && error && (
          <div className="assets-state assets-state-error">
            <div>{error}</div>

            <Button
              variant="secondary"
              onClick={() => void loadAssets()}
            >
              Retry
            </Button>
          </div>
        )}

        {!loading &&
          !error &&
          filteredAssets.length === 0 && (
            <div className="assets-state">
              No assets found.
            </div>
          )}

        {!loading &&
          !error &&
          filteredAssets.length > 0 && (
            <div className="assets-table-wrapper">
              <table className="assets-table">
                <thead>
                  <tr>
                    <th>Asset Code</th>
                    <th>Serial Number</th>
                    <th>Category</th>
                    <th>Manufacturer</th>
                    <th>Model</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredAssets.map((asset) => (
                    <tr key={asset.id}>
                      <td>
                        <button
                          type="button"
                          className="asset-code-button"
                          onClick={() =>
                            navigate(
                              `/assets/${asset.id}`,
                            )
                          }
                        >
                          {asset.asset_code}
                        </button>
                      </td>

                      <td>
                        {asset.serial_number || '—'}
                      </td>

                      <td>
                        {asset.asset_category}
                      </td>

                      <td>
                        {asset.manufacturer || '—'}
                      </td>

                      <td>
                        {asset.model || '—'}
                      </td>

                      <td>
                        <StatusBadge
                          variant={getStatusVariant(
                            asset.status,
                          )}
                        >
                          {asset.status}
                        </StatusBadge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </Card>
    </>
  )
}

export default AssetsPage