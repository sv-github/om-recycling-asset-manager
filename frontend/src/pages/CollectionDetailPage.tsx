import {
  useEffect,
  useState,
} from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import {
  getCollection,
  getCustomer,
  getCustomerLocation,
  listCollectionAssets,
  listCollectionItems,
} from '../api/collections'

import type {
  Collection,
  CollectionAsset,
  CollectionItem,
  Customer,
  CustomerLocation,
} from '../types/collection'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import './CollectionDetailPage.css'

function getStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'scheduled':
      return 'info'

    case 'in_transit':
      return 'warning'

    case 'received':
      return 'info'

    case 'completed':
      return 'success'

    case 'cancelled':
      return 'danger'

    default:
      return 'neutral'
  }
}

function formatDate(value: string | null) {
  if (!value) {
    return '—'
  }

  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}-${month}-${year}`
}

function formatDateTime(value: string | null) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}

function formatValue(
  value: string | number | null | undefined,
) {
  if (
    value === null ||
    value === undefined ||
    value === ''
  ) {
    return '—'
  }

  return value
}

function DetailField({
  label,
  value,
}: {
  label: string
  value: string | number | null | undefined
}) {
  return (
    <div className="collection-detail-field">
      <div className="collection-detail-field-label">
        {label}
      </div>

      <div className="collection-detail-field-value">
        {formatValue(value)}
      </div>
    </div>
  )
}

function CollectionDetailPage() {
  const navigate = useNavigate()
  const { collectionId } = useParams()

  const [collection, setCollection] =
    useState<Collection | null>(null)

  const [customer, setCustomer] =
    useState<Customer | null>(null)

  const [location, setLocation] =
    useState<CustomerLocation | null>(null)

  const [items, setItems] =
    useState<CollectionItem[]>([])

  const [assets, setAssets] =
    useState<CollectionAsset[]>([])

  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)

  const [itemsLoading, setItemsLoading] =
    useState(true)

  const [assetsLoading, setAssetsLoading] =
    useState(true)

  const [itemsError, setItemsError] =
    useState<string | null>(null)

  const [assetsError, setAssetsError] =
    useState<string | null>(null)

  const numericCollectionId = Number(collectionId)

  useEffect(() => {
    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      setError('Invalid collection ID.')
      setLoading(false)
      return
    }

    let cancelled = false

    async function loadCollection() {
      setLoading(true)
      setError(null)

      try {
        const collectionData =
          await getCollection(
            numericCollectionId,
          )

        if (cancelled) {
          return
        }

        setCollection(collectionData)

        const [
          customerData,
          locationData,
        ] = await Promise.all([
          getCustomer(
            collectionData.customer_id,
          ),
          getCustomerLocation(
            collectionData.location_id,
          ),
        ])

        if (!cancelled) {
          setCustomer(customerData)
          setLocation(locationData)
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error
              ? err.message
              : 'Failed to load collection.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadCollection()

    return () => {
      cancelled = true
    }
  }, [numericCollectionId])

  useEffect(() => {
    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      return
    }

    let cancelled = false

    async function loadItems() {
      setItemsLoading(true)
      setItemsError(null)

      try {
        const data =
          await listCollectionItems(
            numericCollectionId,
          )

        if (!cancelled) {
          setItems(data)
        }
      } catch (err) {
        if (!cancelled) {
          setItemsError(
            err instanceof Error
              ? err.message
              : 'Failed to load collection items.',
          )
        }
      } finally {
        if (!cancelled) {
          setItemsLoading(false)
        }
      }
    }

    void loadItems()

    return () => {
      cancelled = true
    }
  }, [numericCollectionId])

  useEffect(() => {
    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      return
    }

    let cancelled = false

    async function loadAssets() {
      setAssetsLoading(true)
      setAssetsError(null)

      try {
        const data =
          await listCollectionAssets(
            numericCollectionId,
          )

        if (!cancelled) {
          setAssets(data)
        }
      } catch (err) {
        if (!cancelled) {
          setAssetsError(
            err instanceof Error
              ? err.message
              : 'Failed to load received assets.',
          )
        }
      } finally {
        if (!cancelled) {
          setAssetsLoading(false)
        }
      }
    }

    void loadAssets()

    return () => {
      cancelled = true
    }
  }, [numericCollectionId])

  function goBackToCollections() {
    navigate('/collections')
  }

  function openAsset(assetId: number) {
    navigate(`/assets/${assetId}`)
  }

  if (loading) {
    return (
      <>
        <PageHeader
          title="Collection Detail"
          description="Loading collection information..."
        />

        <Card>
          <div className="collection-detail-state">
            Loading collection...
          </div>
        </Card>
      </>
    )
  }

  if (error || !collection) {
    return (
      <>
        <PageHeader
          title="Collection Detail"
          description="Unable to load the requested collection."
        />

        <Card>
          <div className="collection-detail-state collection-detail-state-error">
            <div>
              {error || 'Collection not found.'}
            </div>

            <Button
              variant="secondary"
              onClick={goBackToCollections}
            >
              Back to Collections
            </Button>
          </div>
        </Card>
      </>
    )
  }

  return (
    <>
      <div className="collection-detail-header">
        <div className="collection-detail-header-main">
          <PageHeader
            title={collection.collection_code}
            description="Collection record and equipment received under this collection."
          />

          <div className="collection-detail-status-row">
            <span className="collection-detail-status-label">
              Current Status
            </span>

            <StatusBadge
              variant={getStatusVariant(
                collection.status,
              )}
            >
              {collection.status}
            </StatusBadge>
          </div>
        </div>

        <div className="collection-detail-header-action">
          <Button
            variant="secondary"
            onClick={goBackToCollections}
          >
            Back to Collections
          </Button>
        </div>
      </div>

      <div className="collection-detail-grid">
        <Card className="collection-detail-card">
          <div className="collection-detail-card-title">
            Collection Information
          </div>

          <div className="collection-detail-fields">
            <DetailField
              label="Collection Code"
              value={collection.collection_code}
            />

            <DetailField
              label="Collection ID"
              value={collection.id}
            />

            <DetailField
              label="Collection Date"
              value={formatDate(
                collection.collection_date,
              )}
            />

            <DetailField
              label="Source Type"
              value={collection.source_type}
            />

            <DetailField
              label="Pickup Receipt Number"
              value={
                collection.pickup_receipt_number
              }
            />

            <DetailField
              label="Expected Item Count"
              value={
                collection.expected_item_count
              }
            />

            <DetailField
              label="Transport Reference"
              value={
                collection.transport_reference
              }
            />

            <DetailField
              label="Active"
              value={
                collection.is_active
                  ? 'Yes'
                  : 'No'
              }
            />
          </div>
        </Card>

        <Card className="collection-detail-card">
          <div className="collection-detail-card-title">
            Customer & Location
          </div>

          <div className="collection-detail-fields">
            <DetailField
              label="Customer"
              value={customer?.company_name}
            />

            <DetailField
              label="Customer Code"
              value={customer?.customer_code}
            />

            <DetailField
              label="Location"
              value={location?.location_name}
            />

            <DetailField
              label="Location Code"
              value={location?.location_code}
            />

            <DetailField
              label="Location Address"
              value={location?.address}
            />

            <DetailField
              label="Location Contact"
              value={location?.contact_name}
            />
          </div>
        </Card>
      </div>

      <Card className="collection-detail-card collection-detail-notes-card">
        <div className="collection-detail-card-title">
          Notes
        </div>

        <div className="collection-detail-notes">
          {collection.notes || '—'}
        </div>
      </Card>

      <div className="collection-detail-section">
        <div className="collection-detail-section-header">
          <div>
            <div className="collection-detail-section-title">
              Collection Items
            </div>

            {!itemsLoading && (
              <div className="collection-detail-section-count">
                {items.length}{' '}
                {items.length === 1
                  ? 'item'
                  : 'items'}
              </div>
            )}
          </div>
        </div>

        <Card className="collection-detail-table-card">
          {itemsLoading && (
            <div className="collection-detail-state">
              Loading collection items...
            </div>
          )}

          {!itemsLoading && itemsError && (
            <div className="collection-detail-state collection-detail-state-error">
              <div>{itemsError}</div>

              <Button
                variant="secondary"
                onClick={() => {
                  setItemsError(null)
                  setItemsLoading(true)

                  void listCollectionItems(
                    numericCollectionId,
                  )
                    .then(setItems)
                    .catch((err) => {
                      setItemsError(
                        err instanceof Error
                          ? err.message
                          : 'Failed to load collection items.',
                      )
                    })
                    .finally(() =>
                      setItemsLoading(false),
                    )
                }}
              >
                Retry
              </Button>
            </div>
          )}

          {!itemsLoading &&
            !itemsError &&
            items.length === 0 && (
              <div className="collection-detail-state">
                No collection items found.
              </div>
            )}

          {!itemsLoading &&
            !itemsError &&
            items.length > 0 && (
              <div className="collection-detail-table-wrapper">
                <table className="collection-detail-table">
                  <thead>
                    <tr>
                      <th>Category</th>
                      <th>Manufacturer</th>
                      <th>Model</th>
                      <th>Description</th>
                      <th>Expected Quantity</th>
                      <th>Notes</th>
                    </tr>
                  </thead>

                  <tbody>
                    {items.map((item) => (
                      <tr key={item.id}>
                        <td>{item.category}</td>
                        <td>
                          {item.manufacturer || '—'}
                        </td>
                        <td>
                          {item.model || '—'}
                        </td>
                        <td>
                          {item.description || '—'}
                        </td>
                        <td>
                          {item.expected_quantity}
                        </td>
                        <td>
                          {item.notes || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
        </Card>
      </div>

      <div className="collection-detail-section">
        <div className="collection-detail-section-header">
          <div>
            <div className="collection-detail-section-title">
              Received Assets
            </div>

            {!assetsLoading && (
              <div className="collection-detail-section-count">
                {assets.length}{' '}
                {assets.length === 1
                  ? 'asset'
                  : 'assets'}
              </div>
            )}
          </div>
        </div>

        <Card className="collection-detail-table-card">
          {assetsLoading && (
            <div className="collection-detail-state">
              Loading received assets...
            </div>
          )}

          {!assetsLoading && assetsError && (
            <div className="collection-detail-state collection-detail-state-error">
              <div>{assetsError}</div>

              <Button
                variant="secondary"
                onClick={() => {
                  setAssetsError(null)
                  setAssetsLoading(true)

                  void listCollectionAssets(
                    numericCollectionId,
                  )
                    .then(setAssets)
                    .catch((err) => {
                      setAssetsError(
                        err instanceof Error
                          ? err.message
                          : 'Failed to load received assets.',
                      )
                    })
                    .finally(() =>
                      setAssetsLoading(false),
                    )
                }}
              >
                Retry
              </Button>
            </div>
          )}

          {!assetsLoading &&
            !assetsError &&
            assets.length === 0 && (
              <div className="collection-detail-state">
                No received assets found.
              </div>
            )}

          {!assetsLoading &&
            !assetsError &&
            assets.length > 0 && (
              <div className="collection-detail-table-wrapper">
                <table className="collection-detail-table">
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
                    {assets.map((asset) => (
                      <tr key={asset.id}>
                        <td>
                          <button
                            type="button"
                            className="collection-asset-code-button"
                            onClick={() =>
                              openAsset(asset.id)
                            }
                          >
                            {asset.asset_code}
                          </button>
                        </td>

                        <td>
                          {asset.serial_number ||
                            '—'}
                        </td>

                        <td>
                          {asset.asset_category}
                        </td>

                        <td>
                          {asset.manufacturer ||
                            '—'}
                        </td>

                        <td>
                          {asset.model || '—'}
                        </td>

                        <td>
                          <StatusBadge
                            variant={
                              asset.status ===
                              'received'
                                ? 'info'
                                : asset.status ===
                                    'processing'
                                  ? 'warning'
                                  : asset.status ===
                                      'disposed'
                                    ? 'success'
                                    : 'neutral'
                            }
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
      </div>

      <div className="collection-detail-metadata">
        Created: {formatDateTime(collection.created_at)}
        {' · '}
        Updated: {formatDateTime(collection.updated_at)}
      </div>
    </>
  )
}

export default CollectionDetailPage