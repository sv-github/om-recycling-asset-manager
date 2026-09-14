import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import {
  listCollectionAssets,
  listCollectionItems,
  listCollections,
} from '../api/collections'
import {
  createAsset,
} from '../api/assets'

import type { Asset } from '../types/asset'
import type {
  Collection,
  CollectionAsset,
  CollectionItem,
} from '../types/collection'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import './ReceivingPage.css'

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
    <div className="receiving-detail-field">
      <div className="receiving-detail-field-label">
        {label}
      </div>

      <div className="receiving-detail-field-value">
        {formatValue(value)}
      </div>
    </div>
  )
}

function ReceivingPage() {
  const navigate = useNavigate()
  const serialInputRef = useRef<HTMLInputElement>(null)

  const [collections, setCollections] = useState<
    Collection[]
  >([])

  const [selectedCollectionId, setSelectedCollectionId] =
    useState('')

  const [collectionItems, setCollectionItems] =
    useState<CollectionItem[]>([])

  const [receivedAssets, setReceivedAssets] = useState<
    CollectionAsset[]
  >([])

  const [loadingCollections, setLoadingCollections] =
    useState(true)

  const [loadingCollectionData, setLoadingCollectionData] =
    useState(false)

  const [collectionsError, setCollectionsError] =
    useState<string | null>(null)

  const [collectionDataError, setCollectionDataError] =
    useState<string | null>(null)

  const [serialNumber, setSerialNumber] =
    useState('')

  const [assetCategory, setAssetCategory] =
    useState('')

  const [manufacturer, setManufacturer] =
    useState('')

  const [model, setModel] = useState('')

  const [description, setDescription] =
    useState('')

  const [receivedBy, setReceivedBy] =
    useState('')

  const [receivingNotes, setReceivingNotes] =
    useState('')

  const [selectedCollectionItemId, setSelectedCollectionItemId] =
    useState('')

  const [submitting, setSubmitting] =
    useState(false)

  const [submitError, setSubmitError] =
    useState<string | null>(null)

  const [submitSuccess, setSubmitSuccess] =
    useState<string | null>(null)

  const selectedCollection = useMemo(
    () =>
      collections.find(
        (collection) =>
          String(collection.id) ===
          selectedCollectionId,
      ) || null,
    [collections, selectedCollectionId],
  )

  const selectedCollectionItem = useMemo(
    () =>
      collectionItems.find(
        (item) =>
          String(item.id) ===
          selectedCollectionItemId,
      ) || null,
    [
      collectionItems,
      selectedCollectionItemId,
    ],
  )

  useEffect(() => {
    let cancelled = false

    async function loadCollections() {
      setLoadingCollections(true)
      setCollectionsError(null)

      try {
        const data = await listCollections()

        if (!cancelled) {
          setCollections(data)
        }
      } catch (err) {
        if (!cancelled) {
          setCollectionsError(
            err instanceof Error
              ? err.message
              : 'Failed to load collections.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingCollections(false)
        }
      }
    }

    void loadCollections()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (!selectedCollectionId) {
      setCollectionItems([])
      setReceivedAssets([])
      setCollectionDataError(null)
      return
    }

    const numericCollectionId =
      Number(selectedCollectionId)

    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      return
    }

    let cancelled = false

    async function loadCollectionData() {
      setLoadingCollectionData(true)
      setCollectionDataError(null)

      try {
        const [
          items,
          assets,
        ] = await Promise.all([
          listCollectionItems(
            numericCollectionId,
          ),
          listCollectionAssets(
            numericCollectionId,
          ),
        ])

        if (!cancelled) {
          setCollectionItems(items)
          setReceivedAssets(assets)
        }
      } catch (err) {
        if (!cancelled) {
          setCollectionDataError(
            err instanceof Error
              ? err.message
              : 'Failed to load collection information.',
          )
        }
      } finally {
        if (!cancelled) {
          setLoadingCollectionData(false)
        }
      }
    }

    void loadCollectionData()

    return () => {
      cancelled = true
    }
  }, [selectedCollectionId])

  useEffect(() => {
    if (!selectedCollectionItem) {
      return
    }

    setAssetCategory(
      selectedCollectionItem.category,
    )

    setManufacturer(
      selectedCollectionItem.manufacturer || '',
    )

    setModel(
      selectedCollectionItem.model || '',
    )

    if (
      !description &&
      selectedCollectionItem.description
    ) {
      setDescription(
        selectedCollectionItem.description,
      )
    }
  }, [selectedCollectionItem])

  function resetAssetForm() {
    setSelectedCollectionItemId('')
    setSerialNumber('')
    setAssetCategory('')
    setManufacturer('')
    setModel('')
    setDescription('')
    setReceivedBy('')
    setReceivingNotes('')
    setSubmitError(null)
    setSubmitSuccess(null)
  }

  async function refreshReceivedAssets(
    collectionId: number,
  ) {
    const data = await listCollectionAssets(
      collectionId,
    )

    setReceivedAssets(data)
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    if (!selectedCollectionId) {
      setSubmitError(
        'Please select a collection.',
      )
      return
    }

    if (!assetCategory.trim()) {
      setSubmitError(
        'Asset category is required.',
      )
      return
    }

    const numericCollectionId =
      Number(selectedCollectionId)

    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      setSubmitError(
        'Invalid collection selected.',
      )
      return
    }

    setSubmitting(true)
    setSubmitError(null)
    setSubmitSuccess(null)

    try {
      const createdAsset: Asset =
        await createAsset({
          collection_id:
            numericCollectionId,

          collection_item_id:
            selectedCollectionItemId
              ? Number(
                  selectedCollectionItemId,
                )
              : null,

          serial_number:
            serialNumber.trim() || null,

          asset_category:
            assetCategory.trim(),

          manufacturer:
            manufacturer.trim() || null,

          model:
            model.trim() || null,

          description:
            description.trim() || null,

          received_by:
            receivedBy.trim() || null,

          receiving_notes:
            receivingNotes.trim() || null,

          notes: null,
        })

      await refreshReceivedAssets(
        numericCollectionId,
      )

      setSubmitSuccess(
        `${createdAsset.asset_code} registered successfully.`,
      )

      // Keep the receiving context and reusable asset details
      // for high-volume entry. Only clear per-asset fields.
      setSerialNumber('')
      setReceivingNotes('')

      // Return directly to the serial-number field for the next asset.
      window.requestAnimationFrame(() => {
        serialInputRef.current?.focus()
      })
    } catch (err) {
      setSubmitError(
        err instanceof Error
          ? err.message
          : 'Failed to register asset.',
      )
    } finally {
      setSubmitting(false)
    }
  }

  function openAsset(assetId: number) {
    navigate(`/assets/${assetId}`)
  }

  async function retryCollectionData() {
    if (!selectedCollectionId) {
      return
    }

    const numericCollectionId =
      Number(selectedCollectionId)

    if (
      !Number.isInteger(numericCollectionId) ||
      numericCollectionId <= 0
    ) {
      return
    }

    setLoadingCollectionData(true)
    setCollectionDataError(null)

    try {
      const [
        items,
        assets,
      ] = await Promise.all([
        listCollectionItems(
          numericCollectionId,
        ),
        listCollectionAssets(
          numericCollectionId,
        ),
      ])

      setCollectionItems(items)
      setReceivedAssets(assets)
    } catch (err) {
      setCollectionDataError(
        err instanceof Error
          ? err.message
          : 'Failed to load collection information.',
      )
    } finally {
      setLoadingCollectionData(false)
    }
  }

  return (
    <>
      <PageHeader
        title="Receiving"
        description="Register equipment received against a collection and create permanent Asset records."
      />

      <Card className="receiving-selection-card">
        <div className="receiving-selection-header">
          <div>
            <div className="receiving-card-title">
              Select Collection
            </div>

            <div className="receiving-card-description">
              Choose the collection against which the
              physical equipment is being received.
            </div>
          </div>
        </div>

        {loadingCollections && (
          <div className="receiving-state">
            Loading collections...
          </div>
        )}

        {!loadingCollections &&
          collectionsError && (
            <div className="receiving-state receiving-state-error">
              <div>{collectionsError}</div>

              <Button
                variant="secondary"
                onClick={() => {
                  setCollectionsError(null)
                  setLoadingCollections(true)

                  void listCollections()
                    .then(setCollections)
                    .catch((err) => {
                      setCollectionsError(
                        err instanceof Error
                          ? err.message
                          : 'Failed to load collections.',
                      )
                    })
                    .finally(() =>
                      setLoadingCollections(false),
                    )
                }}
              >
                Retry
              </Button>
            </div>
          )}

        {!loadingCollections &&
          !collectionsError && (
            <div className="receiving-selection-control">
              <label htmlFor="receiving-collection">
                Collection
              </label>

              <select
                id="receiving-collection"
                value={selectedCollectionId}
                onChange={(event) => {
                  setSelectedCollectionId(
                    event.target.value,
                  )
                  resetAssetForm()
                }}
              >
                <option value="">
                  Select a collection
                </option>

                {collections
                  .filter(
                    (collection) =>
                      collection.is_active,
                  )
                  .map((collection) => (
                    <option
                      key={collection.id}
                      value={collection.id}
                    >
                      {collection.collection_code}
                      {' — '}
                      {collection.status}
                      {' — '}
                      {formatDate(
                        collection.collection_date,
                      )}
                    </option>
                  ))}
              </select>
            </div>
          )}
      </Card>

      {selectedCollection && (
        <>
          <div className="receiving-grid">
            <Card className="receiving-card">
              <div className="receiving-card-title">
                Collection Information
              </div>

              <div className="receiving-detail-fields">
                <DetailField
                  label="Collection Code"
                  value={
                    selectedCollection.collection_code
                  }
                />

                <DetailField
                  label="Collection ID"
                  value={selectedCollection.id}
                />

                <DetailField
                  label="Collection Date"
                  value={formatDate(
                    selectedCollection.collection_date,
                  )}
                />

                <DetailField
                  label="Status"
                  value={
                    selectedCollection.status
                  }
                />

                <DetailField
                  label="Expected Item Count"
                  value={
                    selectedCollection.expected_item_count
                  }
                />

                <DetailField
                  label="Received Assets"
                  value={receivedAssets.length}
                />

                <DetailField
                  label="Pickup Receipt"
                  value={
                    selectedCollection.pickup_receipt_number
                  }
                />

                <DetailField
                  label="Transport Reference"
                  value={
                    selectedCollection.transport_reference
                  }
                />
              </div>
            </Card>

            <Card className="receiving-card">
              <div className="receiving-card-title">
                Collection Status
              </div>

              <div className="receiving-status-summary">
                <StatusBadge
                  variant={getStatusVariant(
                    selectedCollection.status,
                  )}
                >
                  {selectedCollection.status}
                </StatusBadge>

                <div className="receiving-progress">
                  <div className="receiving-progress-label">
                    <span>Expected</span>
                    <strong>
                      {formatValue(
                        selectedCollection.expected_item_count,
                      )}
                    </strong>
                  </div>

                  <div className="receiving-progress-label">
                    <span>Received</span>
                    <strong>
                      {receivedAssets.length}
                    </strong>
                  </div>

                  {selectedCollection.expected_item_count !==
                    null && (
                    <div className="receiving-progress-track">
                      <div
                        className="receiving-progress-fill"
                        style={{
                          width: `${Math.min(
                            100,
                            selectedCollection.expected_item_count >
                              0
                              ? (receivedAssets.length /
                                  selectedCollection.expected_item_count) *
                                  100
                              : 0,
                          )}%`,
                        }}
                      />
                    </div>
                  )}
                </div>
              </div>
            </Card>
          </div>

          {collectionDataError && (
            <Card className="receiving-card">
              <div className="receiving-state receiving-state-error">
                <div>{collectionDataError}</div>

                <Button
                  variant="secondary"
                  onClick={() =>
                    void retryCollectionData()
                  }
                >
                  Retry
                </Button>
              </div>
            </Card>
          )}

          {!collectionDataError && (
            <Card className="receiving-form-card">
              <div className="receiving-card-title">
                Register Received Asset
              </div>

              <div className="receiving-card-description">
                Register one physical unit at a time.
                The permanent Asset Code will be generated
                automatically.
              </div>

              {submitError && (
                <div className="receiving-form-message receiving-form-message-error">
                  {submitError}
                </div>
              )}

              {submitSuccess && (
                <div className="receiving-form-message receiving-form-message-success">
                  {submitSuccess}
                </div>
              )}

              <form
                className="receiving-form"
                onSubmit={handleSubmit}
              >
                <div className="receiving-form-grid">
                  <div className="receiving-form-field receiving-form-field-full">
                    <label htmlFor="receiving-item">
                      Collection Item
                    </label>

                    <select
                      id="receiving-item"
                      value={
                        selectedCollectionItemId
                      }
                      onChange={(event) =>
                        setSelectedCollectionItemId(
                          event.target.value,
                        )
                      }
                      disabled={
                        loadingCollectionData ||
                        submitting
                      }
                    >
                      <option value="">
                        No collection item / unspecified
                      </option>

                      {collectionItems.map(
                        (item) => (
                          <option
                            key={item.id}
                            value={item.id}
                          >
                            {item.category}
                            {' — '}
                            {item.manufacturer ||
                              'Unknown manufacturer'}
                            {' — '}
                            {item.model ||
                              'Unknown model'}
                            {' — expected '}
                            {item.expected_quantity}
                          </option>
                        ),
                      )}
                    </select>
                  </div>

                  <div className="receiving-form-field">
                    <label htmlFor="receiving-serial">
                      Serial Number
                    </label>

                    <input
                      ref={serialInputRef}
                      id="receiving-serial"
                      type="text"
                      value={serialNumber}
                      onChange={(event) =>
                        setSerialNumber(
                          event.target.value,
                        )
                      }
                      placeholder="Scan or enter serial number"
                      autoComplete="off"
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field receiving-form-field-received-by">
                    <label htmlFor="receiving-by">
                      Received By
                    </label>

                    <input
                      id="receiving-by"
                      type="text"
                      value={receivedBy}
                      onChange={(event) =>
                        setReceivedBy(
                          event.target.value,
                        )
                      }
                      placeholder="Name of receiving staff"
                      autoComplete="name"
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field">
                    <label htmlFor="receiving-category">
                      Asset Category
                    </label>

                    <input
                      id="receiving-category"
                      type="text"
                      value={assetCategory}
                      onChange={(event) =>
                        setAssetCategory(
                          event.target.value,
                        )
                      }
                      placeholder="e.g. Laptop"
                      required
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field">
                    <label htmlFor="receiving-manufacturer">
                      Manufacturer
                    </label>

                    <input
                      id="receiving-manufacturer"
                      type="text"
                      value={manufacturer}
                      onChange={(event) =>
                        setManufacturer(
                          event.target.value,
                        )
                      }
                      placeholder="e.g. Dell"
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field">
                    <label htmlFor="receiving-model">
                      Model
                    </label>

                    <input
                      id="receiving-model"
                      type="text"
                      value={model}
                      onChange={(event) =>
                        setModel(
                          event.target.value,
                        )
                      }
                      placeholder="e.g. Latitude 7410"
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field receiving-form-field-full">
                    <label htmlFor="receiving-description">
                      Description
                    </label>

                    <textarea
                      id="receiving-description"
                      value={description}
                      onChange={(event) =>
                        setDescription(
                          event.target.value,
                        )
                      }
                      placeholder="Optional equipment description"
                      rows={3}
                      disabled={submitting}
                    />
                  </div>

                  <div className="receiving-form-field receiving-form-field-full">
                    <label htmlFor="receiving-notes">
                      Receiving Notes
                    </label>

                    <textarea
                      id="receiving-notes"
                      value={receivingNotes}
                      onChange={(event) =>
                        setReceivingNotes(
                          event.target.value,
                        )
                      }
                      placeholder="Condition, accessories, visible damage, packaging, or other receiving observations"
                      rows={4}
                      disabled={submitting}
                    />
                  </div>
                </div>

                <div className="receiving-form-actions">
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={resetAssetForm}
                    disabled={submitting}
                  >
                    Clear Form
                  </Button>

                  <Button
                    type="submit"
                    disabled={
                      submitting ||
                      loadingCollectionData
                    }
                  >
                    {submitting
                      ? 'Registering...'
                      : 'Register Asset'}
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <div className="receiving-section">
            <div className="receiving-section-header">
              <div>
                <div className="receiving-section-title">
                  Received Assets
                </div>

                {!loadingCollectionData && (
                  <div className="receiving-section-count">
                    {receivedAssets.length}{' '}
                    {receivedAssets.length === 1
                      ? 'asset'
                      : 'assets'}
                  </div>
                )}
              </div>
            </div>

            <Card className="receiving-table-card">
              {loadingCollectionData && (
                <div className="receiving-state">
                  Loading received assets...
                </div>
              )}

              {!loadingCollectionData &&
                !collectionDataError &&
                receivedAssets.length === 0 && (
                  <div className="receiving-state">
                    No assets have been received
                    against this collection yet.
                  </div>
                )}

              {!loadingCollectionData &&
                !collectionDataError &&
                receivedAssets.length > 0 && (
                  <div className="receiving-table-wrapper">
                    <table className="receiving-table">
                      <thead>
                        <tr>
                          <th>Asset Code</th>
                          <th>Serial Number</th>
                          <th>Category</th>
                          <th>Manufacturer</th>
                          <th>Model</th>
                          <th>Received By</th>
                          <th>Received At</th>
                          <th>Status</th>
                        </tr>
                      </thead>

                      <tbody>
                        {receivedAssets.map(
                          (asset) => (
                            <tr key={asset.id}>
                              <td>
                                <button
                                  type="button"
                                  className="receiving-asset-code-button"
                                  onClick={() =>
                                    openAsset(
                                      asset.id,
                                    )
                                  }
                                >
                                  {
                                    asset.asset_code
                                  }
                                </button>
                              </td>

                              <td>
                                {asset.serial_number ||
                                  '—'}
                              </td>

                              <td>
                                {
                                  asset.asset_category
                                }
                              </td>

                              <td>
                                {asset.manufacturer ||
                                  '—'}
                              </td>

                              <td>
                                {asset.model ||
                                  '—'}
                              </td>

                              <td>
                                {asset.received_by ||
                                  '—'}
                              </td>

                              <td>
                                {formatDateTime(
                                  asset.received_at,
                                )}
                              </td>

                              <td>
                                <StatusBadge
                                  variant={getStatusVariant(
                                    asset.status,
                                  )}
                                >
                                  {
                                    asset.status
                                  }
                                </StatusBadge>
                              </td>
                            </tr>
                          ),
                        )}
                      </tbody>
                    </table>
                  </div>
                )}
            </Card>
          </div>
        </>
      )}

      {!selectedCollectionId &&
        !loadingCollections &&
        !collectionsError && (
          <Card className="receiving-empty-card">
            <div className="receiving-empty-title">
              Select a collection to begin receiving
            </div>

            <div className="receiving-empty-description">
              The collection information, receiving form,
              and received asset register will appear here
              after a collection is selected.
            </div>
          </Card>
        )}
    </>
  )
}

export default ReceivingPage