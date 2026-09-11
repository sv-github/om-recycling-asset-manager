import { useEffect, useState } from 'react'
import {
  useLocation,
  useNavigate,
  useParams,
} from 'react-router-dom'

import { listAssetDispositions } from '../api/assetDispositions'
import { listAssetInspections } from '../api/assetInspections'
import { listAssetProcessing } from '../api/assetProcessing'
import { listAssetSanitization } from '../api/dataSanitization'
import { getAsset } from '../api/assets'

import type { AssetDisposition } from '../types/assetDisposition'
import type { AssetInspection } from '../types/assetInspection'
import type { AssetProcessing } from '../types/assetProcessing'
import type { AssetSanitization } from '../types/assetSanitization'
import type { Asset } from '../types/asset'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import './AssetDetailPage.css'

type DetailTab =
  | 'overview'
  | 'inspection'
  | 'processing'
  | 'sanitization'
  | 'disposition'
  | 'history'

const detailTabs: {
  id: DetailTab
  label: string
}[] = [
  {
    id: 'overview',
    label: 'Overview',
  },
  {
    id: 'inspection',
    label: 'Inspection',
  },
  {
    id: 'processing',
    label: 'Processing',
  },
  {
    id: 'sanitization',
    label: 'Sanitization',
  },
  {
    id: 'disposition',
    label: 'Disposition',
  },
  {
    id: 'history',
    label: 'History',
  },
]

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

function getInspectionStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'working':
    case 'good':
    case 'present':
      return 'success'

    case 'partially_working':
    case 'fair':
      return 'warning'

    case 'not_working':
    case 'poor':
    case 'damaged':
    case 'faulty':
      return 'danger'

    case 'not_tested':
    case 'not_present':
    case 'not_applicable':
      return 'neutral'

    default:
      return 'neutral'
  }
}

function getProcessingStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'success'

    case 'in_progress':
    case 'pending':
      return 'warning'

    case 'failed':
      return 'danger'

    case 'not_required':
      return 'neutral'

    default:
      return 'neutral'
  }
}

function getSanitizationStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'passed':
      return 'success'

    case 'in_progress':
      return 'warning'

    case 'failed':
      return 'danger'

    case 'not_started':
      return 'neutral'

    default:
      return 'neutral'
  }
}

function getDispositionStatusVariant(
  status: string,
): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  switch (status.toLowerCase()) {
    case 'completed':
      return 'success'

    case 'approved':
      return 'info'

    case 'pending':
      return 'warning'

    case 'cancelled':
      return 'danger'

    default:
      return 'neutral'
  }
}

function formatInspectionValue(
  value: string | null,
) {
  if (!value) {
    return '—'
  }

  return value
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (character) =>
      character.toUpperCase(),
    )
}

function formatDate(value: string | null) {
  if (!value) {
    return '—'
  }

  return new Date(value).toLocaleString()
}

function formatDispositionAmount(
  amount: string | null,
  currency: string | null,
) {
  if (!amount) {
    return null
  }

  if (!currency) {
    return amount
  }

  return `${currency} ${amount}`
}

function DetailField({
  label,
  value,
}: {
  label: string
  value: string | number | null
}) {
  return (
    <div className="asset-detail-field">
      <div className="asset-detail-field-label">
        {label}
      </div>

      <div className="asset-detail-field-value">
        {value === null ||
        value === undefined ||
        value === ''
          ? '—'
          : value}
      </div>
    </div>
  )
}

function InspectionField({
  label,
  value,
}: {
  label: string
  value: string | null
}) {
  return (
    <div className="asset-detail-field">
      <div className="asset-detail-field-label">
        {label}
      </div>

      <div className="asset-detail-inspection-value">
        <StatusBadge
          variant={getInspectionStatusVariant(
            value || '',
          )}
        >
          {formatInspectionValue(value)}
        </StatusBadge>
      </div>
    </div>
  )
}

function DispositionStatusField({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="asset-detail-field">
      <div className="asset-detail-field-label">
        {label}
      </div>

      <div className="asset-detail-inspection-value">
        <StatusBadge
          variant={getDispositionStatusVariant(
            value,
          )}
        >
          {formatInspectionValue(value)}
        </StatusBadge>
      </div>
    </div>
  )
}

function getActiveTab(
  pathname: string,
  assetId: string,
): DetailTab {
  const prefix = `/assets/${assetId}/`

  if (!pathname.startsWith(prefix)) {
    return 'overview'
  }

  const tab = pathname
    .slice(prefix.length)
    .split('/')[0] as DetailTab

  const validTab = detailTabs.some(
    (item) => item.id === tab,
  )

  return validTab ? tab : 'overview'
}

function AssetDetailPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { assetId } = useParams()

  const [asset, setAsset] = useState<Asset | null>(
    null,
  )

  const [inspections, setInspections] = useState<
    AssetInspection[]
  >([])

  const [processingRecords, setProcessingRecords] =
    useState<AssetProcessing[]>([])

  const [sanitizationRecords, setSanitizationRecords] =
    useState<AssetSanitization[]>([])

  const [dispositionRecords, setDispositionRecords] =
    useState<AssetDisposition[]>([])

  const [loading, setLoading] = useState(true)

  const [inspectionLoading, setInspectionLoading] =
    useState(false)

  const [processingLoading, setProcessingLoading] =
    useState(false)

  const [sanitizationLoading, setSanitizationLoading] =
    useState(false)

  const [dispositionLoading, setDispositionLoading] =
    useState(false)

  const [error, setError] = useState<string | null>(
    null,
  )

  const [
    inspectionError,
    setInspectionError,
  ] = useState<string | null>(null)

  const [
    processingError,
    setProcessingError,
  ] = useState<string | null>(null)

  const [
    sanitizationError,
    setSanitizationError,
  ] = useState<string | null>(null)

  const [
    dispositionError,
    setDispositionError,
  ] = useState<string | null>(null)

  const activeTab = assetId
    ? getActiveTab(location.pathname, assetId)
    : 'overview'

  useEffect(() => {
    if (!assetId) {
      setError('Asset ID is missing.')
      setLoading(false)
      return
    }

    const numericAssetId = Number(assetId)

    if (
      !Number.isInteger(numericAssetId) ||
      numericAssetId <= 0
    ) {
      setError('Invalid asset ID.')
      setLoading(false)
      return
    }

    async function loadAsset() {
      setLoading(true)
      setError(null)

      try {
        const data = await getAsset(numericAssetId)
        setAsset(data)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Failed to load asset.',
        )
      } finally {
        setLoading(false)
      }
    }

    void loadAsset()
  }, [assetId])

  useEffect(() => {
    if (
      activeTab !== 'inspection' ||
      !assetId
    ) {
      return
    }

    const numericAssetId = Number(assetId)

    if (
      !Number.isInteger(numericAssetId) ||
      numericAssetId <= 0
    ) {
      return
    }

    async function loadInspections() {
      setInspectionLoading(true)
      setInspectionError(null)

      try {
        const data =
          await listAssetInspections(
            numericAssetId,
          )

        setInspections(data)
      } catch (err) {
        setInspectionError(
          err instanceof Error
            ? err.message
            : 'Failed to load inspections.',
        )
      } finally {
        setInspectionLoading(false)
      }
    }

    void loadInspections()
  }, [activeTab, assetId])

  useEffect(() => {
    if (
      activeTab !== 'processing' ||
      !assetId
    ) {
      return
    }

    const numericAssetId = Number(assetId)

    if (
      !Number.isInteger(numericAssetId) ||
      numericAssetId <= 0
    ) {
      return
    }

    async function loadProcessing() {
      setProcessingLoading(true)
      setProcessingError(null)

      try {
        const data =
          await listAssetProcessing(
            numericAssetId,
          )

        setProcessingRecords(data)
      } catch (err) {
        setProcessingError(
          err instanceof Error
            ? err.message
            : 'Failed to load processing history.',
        )
      } finally {
        setProcessingLoading(false)
      }
    }

    void loadProcessing()
  }, [activeTab, assetId])

  useEffect(() => {
    if (
      activeTab !== 'sanitization' ||
      !assetId
    ) {
      return
    }

    const numericAssetId = Number(assetId)

    if (
      !Number.isInteger(numericAssetId) ||
      numericAssetId <= 0
    ) {
      return
    }

    async function loadSanitization() {
      setSanitizationLoading(true)
      setSanitizationError(null)

      try {
        const data =
          await listAssetSanitization(
            numericAssetId,
          )

        setSanitizationRecords(data)
      } catch (err) {
        setSanitizationError(
          err instanceof Error
            ? err.message
            : 'Failed to load sanitization history.',
        )
      } finally {
        setSanitizationLoading(false)
      }
    }

    void loadSanitization()
  }, [activeTab, assetId])

  useEffect(() => {
    if (
      activeTab !== 'disposition' ||
      !assetId
    ) {
      return
    }

    const numericAssetId = Number(assetId)

    if (
      !Number.isInteger(numericAssetId) ||
      numericAssetId <= 0
    ) {
      return
    }

    async function loadDispositions() {
      setDispositionLoading(true)
      setDispositionError(null)

      try {
        const data =
          await listAssetDispositions(
            numericAssetId,
          )

        setDispositionRecords(data)
      } catch (err) {
        setDispositionError(
          err instanceof Error
            ? err.message
            : 'Failed to load disposition history.',
        )
      } finally {
        setDispositionLoading(false)
      }
    }

    void loadDispositions()
  }, [activeTab, assetId])

  function openTab(tab: DetailTab) {
    if (!assetId) {
      return
    }

    navigate(`/assets/${assetId}/${tab}`)
  }

  function goBackToAssets() {
    navigate('/assets')
  }

  if (loading) {
    return (
      <>
        <PageHeader
          title="Asset Detail"
          description="Loading asset information..."
        />

        <Card>
          <div className="asset-detail-state">
            Loading asset...
          </div>
        </Card>
      </>
    )
  }

  if (error || !asset) {
    return (
      <>
        <PageHeader
          title="Asset Detail"
          description="Unable to load the requested asset."
        />

        <Card>
          <div className="asset-detail-state asset-detail-state-error">
            <div>
              {error || 'Asset not found.'}
            </div>

            <Button
              variant="secondary"
              onClick={goBackToAssets}
            >
              Back to Assets
            </Button>
          </div>
        </Card>
      </>
    )
  }

  const activeDisposition =
    dispositionRecords.find(
      (record) =>
        record.disposition_status === 'pending' ||
        record.disposition_status === 'approved',
    ) ?? null

  const latestDisposition =
    dispositionRecords[0] ?? null

  return (
    <>
      <div className="asset-detail-header">
        <div className="asset-detail-header-main">
          <PageHeader
            title={asset.asset_code}
            description="Asset record and current lifecycle information."
          />

          <div className="asset-detail-status-row">
            <span className="asset-detail-status-label">
              Current Status
            </span>

            <StatusBadge
              variant={getStatusVariant(
                asset.status,
              )}
            >
              {asset.status}
            </StatusBadge>
          </div>
        </div>

        <div className="asset-detail-header-action">
          <Button
            variant="secondary"
            onClick={goBackToAssets}
          >
            Back to Assets
          </Button>
        </div>
      </div>

      <div className="asset-detail-tabs">
        <div
          className="asset-detail-tab-list"
          role="tablist"
          aria-label="Asset detail sections"
        >
          {detailTabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={
                activeTab === tab.id
              }
              className={
                activeTab === tab.id
                  ? 'asset-detail-tab asset-detail-tab-active'
                  : 'asset-detail-tab'
              }
              onClick={() =>
                openTab(tab.id)
              }
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {activeTab === 'overview' && (
        <div className="asset-detail-grid">
          <Card className="asset-detail-card">
            <div className="asset-detail-card-title">
              Asset Identification
            </div>

            <div className="asset-detail-fields">
              <DetailField
                label="Asset Code"
                value={asset.asset_code}
              />

              <DetailField
                label="Asset ID"
                value={asset.id}
              />

              <DetailField
                label="Serial Number"
                value={asset.serial_number}
              />

              <DetailField
                label="Category"
                value={asset.asset_category}
              />

              <DetailField
                label="Manufacturer"
                value={asset.manufacturer}
              />

              <DetailField
                label="Model"
                value={asset.model}
              />
            </div>
          </Card>

          <Card className="asset-detail-card">
            <div className="asset-detail-card-title">
              Collection
            </div>

            <div className="asset-detail-fields">
              <DetailField
                label="Collection ID"
                value={asset.collection_id}
              />

              <DetailField
                label="Collection Item ID"
                value={
                  asset.collection_item_id
                }
              />

              <DetailField
                label="Received At"
                value={formatDate(
                  asset.received_at,
                )}
              />

              <DetailField
                label="Received By"
                value={asset.received_by}
              />

              <DetailField
                label="Receiving Notes"
                value={
                  asset.receiving_notes
                }
              />
            </div>
          </Card>

          <Card className="asset-detail-card">
            <div className="asset-detail-card-title">
              Data Sanitization
            </div>

            <div className="asset-detail-fields">
              <DetailField
                label="Status"
                value={
                  asset.data_wipe_status
                }
              />

              <DetailField
                label="Method"
                value={
                  asset.data_wipe_method
                }
              />

              <DetailField
                label="Date"
                value={formatDate(
                  asset.data_wipe_date,
                )}
              />

              <DetailField
                label="Reference"
                value={
                  asset.data_wipe_reference
                }
              />
            </div>
          </Card>

          <Card className="asset-detail-card">
            <div className="asset-detail-card-title">
              Disposition
            </div>

            <div className="asset-detail-fields">
              <DetailField
                label="Final Disposition"
                value={
                  asset.final_disposition
                }
              />

              <DetailField
                label="Notes"
                value={asset.notes}
              />
            </div>
          </Card>
        </div>
      )}

      {activeTab === 'inspection' && (
        <div className="asset-inspection-workspace">
          {inspectionLoading && (
            <Card>
              <div className="asset-detail-state">
                Loading inspection history...
              </div>
            </Card>
          )}

          {!inspectionLoading &&
            inspectionError && (
              <Card>
                <div className="asset-detail-state asset-detail-state-error">
                  <div>
                    {inspectionError}
                  </div>

                  <Button
                    variant="secondary"
                    onClick={() =>
                      navigate(
                        `/assets/${asset.id}/inspection`,
                      )
                    }
                  >
                    Retry
                  </Button>
                </div>
              </Card>
            )}

          {!inspectionLoading &&
            !inspectionError &&
            inspections.length === 0 && (
              <Card>
                <div className="asset-detail-state">
                  No inspections recorded for
                  this asset.
                </div>
              </Card>
            )}

          {!inspectionLoading &&
            !inspectionError &&
            inspections.length > 0 && (
              <>
                {inspections.map(
                  (inspection, index) => (
                    <Card
                      key={inspection.id}
                      className="asset-inspection-card"
                    >
                      <div className="asset-detail-card-title">
                        {index === 0
                          ? 'Latest Inspection'
                          : `Inspection ${inspections.length - index}`}
                      </div>

                      <div className="asset-inspection-summary">
                        <div className="asset-detail-fields">
                          <DetailField
                            label="Inspection Type"
                            value={formatInspectionValue(
                              inspection.inspection_type,
                            )}
                          />

                          <DetailField
                            label="Inspection Date"
                            value={formatDate(
                              inspection.inspection_date,
                            )}
                          />

                          <DetailField
                            label="Inspected By"
                            value={
                              inspection.inspected_by
                            }
                          />

                          <InspectionField
                            label="Working Status"
                            value={
                              inspection.working_status
                            }
                          />

                          <InspectionField
                            label="Overall Condition"
                            value={
                              inspection.overall_condition
                            }
                          />
                        </div>
                      </div>

                      <div className="asset-inspection-section">
                        <div className="asset-inspection-section-title">
                          Physical Condition
                        </div>

                        <div className="asset-detail-fields">
                          <InspectionField
                            label="Display"
                            value={
                              inspection.display_condition
                            }
                          />

                          <InspectionField
                            label="Body"
                            value={
                              inspection.body_condition
                            }
                          />

                          <InspectionField
                            label="Keyboard"
                            value={
                              inspection.keyboard_condition
                            }
                          />

                          <InspectionField
                            label="Touchpad"
                            value={
                              inspection.touchpad_condition
                            }
                          />

                          <InspectionField
                            label="Hinge"
                            value={
                              inspection.hinge_condition
                            }
                          />

                          <InspectionField
                            label="Ports"
                            value={
                              inspection.ports_condition
                            }
                          />

                          <InspectionField
                            label="Battery"
                            value={
                              inspection.battery_condition
                            }
                          />

                          <InspectionField
                            label="Charger"
                            value={
                              inspection.charger_status
                            }
                          />
                        </div>
                      </div>

                      <div className="asset-inspection-section">
                        <div className="asset-inspection-section-title">
                          Internal Components
                        </div>

                        <div className="asset-detail-fields">
                          <InspectionField
                            label="RAM"
                            value={
                              inspection.ram_status
                            }
                          />

                          <InspectionField
                            label="Storage"
                            value={
                              inspection.storage_status
                            }
                          />

                          <InspectionField
                            label="CPU"
                            value={
                              inspection.cpu_status
                            }
                          />

                          <InspectionField
                            label="GPU"
                            value={
                              inspection.gpu_status
                            }
                          />
                        </div>
                      </div>

                      <div className="asset-inspection-section">
                        <div className="asset-detail-fields">
                          <DetailField
                            label="Accessories"
                            value={
                              inspection.accessories
                            }
                          />

                          <DetailField
                            label="Inspection Notes"
                            value={
                              inspection.inspection_notes
                            }
                          />
                        </div>
                      </div>
                    </Card>
                  ),
                )}
              </>
            )}
        </div>
      )}

      {activeTab === 'processing' && (
        <div className="asset-processing-workspace">
          {processingLoading && (
            <Card>
              <div className="asset-detail-state">
                Loading processing history...
              </div>
            </Card>
          )}

          {!processingLoading &&
            processingError && (
              <Card>
                <div className="asset-detail-state asset-detail-state-error">
                  <div>
                    {processingError}
                  </div>

                  <Button
                    variant="secondary"
                    onClick={() =>
                      navigate(
                        `/assets/${asset.id}/processing`,
                      )
                    }
                  >
                    Retry
                  </Button>
                </div>
              </Card>
            )}

          {!processingLoading &&
            !processingError &&
            processingRecords.length === 0 && (
              <Card>
                <div className="asset-detail-state">
                  No processing records
                  recorded for this asset.
                </div>
              </Card>
            )}

          {!processingLoading &&
            !processingError &&
            processingRecords.length > 0 && (
              <>
                {processingRecords.map(
                  (processing, index) => (
                    <Card
                      key={processing.id}
                      className="asset-processing-card"
                    >
                      <div className="asset-detail-card-title">
                        {index === 0
                          ? 'Latest Processing'
                          : `Processing ${processingRecords.length - index}`}
                      </div>

                      <div className="asset-detail-fields">
                        <DetailField
                          label="Processing Type"
                          value={formatInspectionValue(
                            processing.processing_type,
                          )}
                        />

                        <DetailField
                          label="Processing Date"
                          value={formatDate(
                            processing.processing_date,
                          )}
                        />

                        <DetailField
                          label="Processor"
                          value={
                            processing.processor
                          }
                        />

                        <DetailField
                          label="Grade"
                          value={
                            processing.grade
                          }
                        />

                        <div className="asset-detail-field">
                          <div className="asset-detail-field-label">
                            Refurbishment Status
                          </div>

                          <div className="asset-detail-inspection-value">
                            <StatusBadge
                              variant={getProcessingStatusVariant(
                                processing.refurbishment_status,
                              )}
                            >
                              {formatInspectionValue(
                                processing.refurbishment_status,
                              )}
                            </StatusBadge>
                          </div>
                        </div>

                        <DetailField
                          label="Processing Reference"
                          value={
                            processing.processing_reference
                          }
                        />

                        <DetailField
                          label="Cost"
                          value={
                            processing.cost
                              ? `₹ ${processing.cost}`
                              : null
                          }
                        />
                      </div>

                      <div className="asset-processing-section">
                        <div className="asset-processing-section-title">
                          Condition & Work
                        </div>

                        <div className="asset-detail-fields">
                          <DetailField
                            label="Condition Summary"
                            value={
                              processing.condition_summary
                            }
                          />

                          <DetailField
                            label="Repairs Performed"
                            value={
                              processing.repairs_performed
                            }
                          />

                          <DetailField
                            label="Parts Replaced"
                            value={
                              processing.parts_replaced
                            }
                          />

                          <DetailField
                            label="Testing Notes"
                            value={
                              processing.testing_notes
                            }
                          />
                        </div>
                      </div>

                      <div className="asset-processing-section">
                        <div className="asset-detail-fields">
                          <DetailField
                            label="Notes"
                            value={
                              processing.notes
                            }
                          />
                        </div>
                      </div>
                    </Card>
                  ),
                )}
              </>
            )}
        </div>
      )}

      {activeTab === 'sanitization' && (
        <div className="asset-sanitization-workspace">
          <Card className="asset-sanitization-card">
            <div className="asset-detail-card-title">
              Current Status
            </div>

            <div className="asset-detail-fields">
              <div className="asset-detail-field">
                <div className="asset-detail-field-label">
                  Data Wipe Status
                </div>

                <div className="asset-detail-inspection-value">
                  <StatusBadge
                    variant={getSanitizationStatusVariant(
                      asset.data_wipe_status,
                    )}
                  >
                    {formatInspectionValue(
                      asset.data_wipe_status,
                    )}
                  </StatusBadge>
                </div>
              </div>

              <DetailField
                label="Method"
                value={asset.data_wipe_method}
              />

              <DetailField
                label="Date"
                value={formatDate(
                  asset.data_wipe_date,
                )}
              />

              <DetailField
                label="Reference"
                value={asset.data_wipe_reference}
              />
            </div>
          </Card>

          {sanitizationLoading && (
            <Card>
              <div className="asset-detail-state">
                Loading sanitization history...
              </div>
            </Card>
          )}

          {!sanitizationLoading &&
            sanitizationError && (
              <Card>
                <div className="asset-detail-state asset-detail-state-error">
                  <div>
                    {sanitizationError}
                  </div>

                  <Button
                    variant="secondary"
                    onClick={() =>
                      navigate(
                        `/assets/${asset.id}/sanitization`,
                      )
                    }
                  >
                    Retry
                  </Button>
                </div>
              </Card>
            )}

          {!sanitizationLoading &&
            !sanitizationError &&
            sanitizationRecords.length === 0 && (
              <Card>
                <div className="asset-detail-state">
                  No sanitization history recorded
                  for this asset.
                </div>
              </Card>
            )}

          {!sanitizationLoading &&
            !sanitizationError &&
            sanitizationRecords.length > 0 && (
              <div className="asset-sanitization-history">
                {sanitizationRecords.map(
                  (record, index) => (
                    <Card
                      key={record.id}
                      className="asset-sanitization-card"
                    >
                      <div className="asset-detail-card-title">
                        Sanitization Record {index + 1}
                      </div>

                      <div className="asset-detail-fields">
                        <div className="asset-detail-field">
                          <div className="asset-detail-field-label">
                            Data Wipe Status
                          </div>

                          <div className="asset-detail-inspection-value">
                            <StatusBadge
                              variant={getSanitizationStatusVariant(
                                record.data_wipe_status,
                              )}
                            >
                              {formatInspectionValue(
                                record.data_wipe_status,
                              )}
                            </StatusBadge>
                          </div>
                        </div>

                        <DetailField
                          label="Method"
                          value={
                            record.data_wipe_method
                          }
                        />

                        <DetailField
                          label="Date"
                          value={formatDate(
                            record.data_wipe_date,
                          )}
                        />

                        <DetailField
                          label="Reference"
                          value={
                            record.data_wipe_reference
                          }
                        />

                        <DetailField
                          label="Recorded At"
                          value={formatDate(
                            record.created_at,
                          )}
                        />

                        <DetailField
                          label="Updated At"
                          value={formatDate(
                            record.updated_at,
                          )}
                        />
                      </div>
                    </Card>
                  ),
                )}
              </div>
            )}
        </div>
      )}

      {activeTab === 'disposition' && (
        <div className="asset-disposition-workspace">
          <Card className="asset-disposition-card">
            <div className="asset-detail-card-title">
              Current Disposition
            </div>

            <div className="asset-detail-fields">
              <DetailField
                label="Current Asset Status"
                value={asset.status}
              />

              <DetailField
                label="Final Disposition"
                value={asset.final_disposition}
              />

              {activeDisposition ? (
                <>
                  <DetailField
                    label="Disposition Type"
                    value={formatInspectionValue(
                      activeDisposition.disposition_type,
                    )}
                  />

                  <DispositionStatusField
                    label="Disposition Status"
                    value={
                      activeDisposition.disposition_status
                    }
                  />

                  <DetailField
                    label="Disposition Date"
                    value={formatDate(
                      activeDisposition.disposition_date,
                    )}
                  />

                  <DetailField
                    label="Processed By"
                    value={
                      activeDisposition.processed_by
                    }
                  />

                  <DetailField
                    label="Reference"
                    value={
                      activeDisposition.disposition_reference
                    }
                  />

                  <DetailField
                    label="Recipient"
                    value={
                      activeDisposition.recipient_name
                    }
                  />

                  <DetailField
                    label="Recipient Reference"
                    value={
                      activeDisposition.recipient_reference
                    }
                  />

                  <DetailField
                    label="Amount"
                    value={formatDispositionAmount(
                      activeDisposition.amount,
                      activeDisposition.currency,
                    )}
                  />

                  <DetailField
                    label="Notes"
                    value={
                      activeDisposition.notes
                    }
                  />
                </>
              ) : (
                <div className="asset-disposition-current-message">
                  No active disposition is currently
                  pending or approved for this asset.
                </div>
              )}
            </div>
          </Card>

          {!dispositionLoading &&
            !dispositionError &&
            !activeDisposition &&
            latestDisposition && (
              <Card className="asset-disposition-card">
                <div className="asset-detail-card-title">
                  Latest Disposition
                </div>

                <div className="asset-detail-fields">
                  <DetailField
                    label="Disposition Type"
                    value={formatInspectionValue(
                      latestDisposition.disposition_type,
                    )}
                  />

                  <DispositionStatusField
                    label="Disposition Status"
                    value={
                      latestDisposition.disposition_status
                    }
                  />

                  <DetailField
                    label="Disposition Date"
                    value={formatDate(
                      latestDisposition.disposition_date,
                    )}
                  />

                  <DetailField
                    label="Processed By"
                    value={
                      latestDisposition.processed_by
                    }
                  />

                  <DetailField
                    label="Reference"
                    value={
                      latestDisposition.disposition_reference
                    }
                  />

                  <DetailField
                    label="Recipient"
                    value={
                      latestDisposition.recipient_name
                    }
                  />

                  <DetailField
                    label="Recipient Reference"
                    value={
                      latestDisposition.recipient_reference
                    }
                  />

                  <DetailField
                    label="Amount"
                    value={formatDispositionAmount(
                      latestDisposition.amount,
                      latestDisposition.currency,
                    )}
                  />

                  <DetailField
                    label="Notes"
                    value={
                      latestDisposition.notes
                    }
                  />
                </div>
              </Card>
            )}

          {dispositionLoading && (
            <Card>
              <div className="asset-detail-state">
                Loading disposition history...
              </div>
            </Card>
          )}

          {!dispositionLoading &&
            dispositionError && (
              <Card>
                <div className="asset-detail-state asset-detail-state-error">
                  <div>
                    {dispositionError}
                  </div>

                  <Button
                    variant="secondary"
                    onClick={() =>
                      navigate(
                        `/assets/${asset.id}/disposition`,
                      )
                    }
                  >
                    Retry
                  </Button>
                </div>
              </Card>
            )}

          {!dispositionLoading &&
            !dispositionError &&
            dispositionRecords.length === 0 && (
              <Card>
                <div className="asset-detail-state">
                  No disposition records recorded
                  for this asset.
                </div>
              </Card>
            )}

          {!dispositionLoading &&
            !dispositionError &&
            dispositionRecords.length > 0 && (
              <div className="asset-disposition-history">
                {dispositionRecords.map(
                  (record, index) => (
                    <Card
                      key={record.id}
                      className="asset-disposition-card"
                    >
                      <div className="asset-detail-card-title">
                        Disposition Record {index + 1}
                      </div>

                      <div className="asset-detail-fields">
                        <DetailField
                          label="Disposition Type"
                          value={formatInspectionValue(
                            record.disposition_type,
                          )}
                        />

                        <DispositionStatusField
                          label="Disposition Status"
                          value={
                            record.disposition_status
                          }
                        />

                        <DetailField
                          label="Disposition Date"
                          value={formatDate(
                            record.disposition_date,
                          )}
                        />

                        <DetailField
                          label="Processed By"
                          value={
                            record.processed_by
                          }
                        />

                        <DetailField
                          label="Reference"
                          value={
                            record.disposition_reference
                          }
                        />

                        <DetailField
                          label="Recipient"
                          value={
                            record.recipient_name
                          }
                        />

                        <DetailField
                          label="Recipient Reference"
                          value={
                            record.recipient_reference
                          }
                        />

                        <DetailField
                          label="Amount"
                          value={formatDispositionAmount(
                            record.amount,
                            record.currency,
                          )}
                        />

                        <DetailField
                          label="Notes"
                          value={record.notes}
                        />

                        <DetailField
                          label="Recorded At"
                          value={formatDate(
                            record.created_at,
                          )}
                        />

                        <DetailField
                          label="Updated At"
                          value={formatDate(
                            record.updated_at,
                          )}
                        />
                      </div>
                    </Card>
                  ),
                )}
              </div>
            )}
        </div>
      )}

      {activeTab === 'history' && (
        <Card>
          <div className="asset-detail-placeholder">
            <div className="asset-detail-placeholder-title">
              History Workspace
            </div>

            <div className="asset-detail-placeholder-text">
              The consolidated asset history will be
              implemented in a future development step.
            </div>
          </div>
        </Card>
      )}
    </>
  )
}

export default AssetDetailPage