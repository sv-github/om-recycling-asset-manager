import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'

import BarcodeInput from '../components/ui/BarcodeInput'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import { listAssets } from '../api/assets'
import {
  createAssetProcessing,
  findAssetByBarcode,
  listAssetProcessing,
} from '../api/assetProcessing'

import type { Asset } from '../types/asset'
import type { AssetProcessing } from '../types/assetProcessing'

import './ProcessingPage.css'

const PROCESSING_TYPES = [
  ['grading', 'Grading'],
  ['refurbishment', 'Refurbishment'],
  ['grading_and_refurbishment', 'Grading & Refurbishment'],
] as const

const GRADES = ['A', 'B', 'C', 'D', 'SCRAP']

function getTodayDate() {
  return new Date().toISOString().slice(0, 10)
}

function formatDate(value: string) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleDateString()
}

function formatType(value: string) {
  return value.replaceAll('_', ' ')
}

function getVariant(status: string): 'neutral' | 'success' | 'warning' | 'danger' | 'info' {
  if (status === 'completed') return 'success'
  if (status === 'in_progress') return 'info'
  if (status === 'pending') return 'warning'
  if (status === 'failed') return 'danger'
  return 'neutral'
}

function ProcessingPage() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [records, setRecords] = useState<Array<{ asset: Asset; processing: AssetProcessing }>>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [barcode, setBarcode] = useState('')
  const [barcodeFocusSignal, setBarcodeFocusSignal] = useState(0)
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const [processingType, setProcessingType] = useState('grading_and_refurbishment')
  const [grade, setGrade] = useState('')
  const [refurbishmentStatus, setRefurbishmentStatus] = useState('pending')
  const [processor, setProcessor] = useState('')
  const [processingDate, setProcessingDate] = useState(getTodayDate())
  const [conditionSummary, setConditionSummary] = useState('')
  const [repairsPerformed, setRepairsPerformed] = useState('')
  const [partsReplaced, setPartsReplaced] = useState('')
  const [testingNotes, setTestingNotes] = useState('')
  const [processingReference, setProcessingReference] = useState('')
  const [cost, setCost] = useState('')
  const [notes, setNotes] = useState('')

  async function loadWorkspace() {
    setLoading(true)
    setError(null)
    try {
      const assetData = await listAssets()
      setAssets(assetData)

      const latest = await Promise.all(
        assetData.map(async (asset) => {
          const history = await listAssetProcessing(asset.id)
          return history[0] ? { asset, processing: history[0] } : null
        }),
      )

      setRecords(latest.filter(
        (record): record is { asset: Asset; processing: AssetProcessing } => record !== null,
      ))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load processing workspace.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadWorkspace()
  }, [])

  const counts = useMemo(() => ({
    pending: records.filter(({ processing }) => processing.refurbishment_status === 'pending').length,
    inProgress: records.filter(({ processing }) => processing.refurbishment_status === 'in_progress').length,
    completed: records.filter(({ processing }) => processing.refurbishment_status === 'completed').length,
  }), [records])

  function resetForm() {
    setProcessingType('grading_and_refurbishment')
    setGrade('')
    setRefurbishmentStatus('pending')
    setProcessor('')
    setProcessingDate(getTodayDate())
    setConditionSummary('')
    setRepairsPerformed('')
    setPartsReplaced('')
    setTestingNotes('')
    setProcessingReference('')
    setCost('')
    setNotes('')
    setFormError(null)
  }

  function openProcessingForm(asset: Asset) {
    if (asset.status === 'closed' || asset.status === 'disposed') {
      setFormError(`Asset ${asset.asset_code} cannot be processed while its status is '${asset.status}'.`)
      return
    }
    resetForm()
    setSelectedAsset(asset)
    setShowForm(true)
  }

  function handleBarcodeScan(value: string) {
    const asset = findAssetByBarcode(assets, value)
    if (!asset) {
      setFormError(`No asset found for barcode '${value}'.`)
      return
    }
    setFormError(null)
    setBarcode(asset.asset_code)
    openProcessingForm(asset)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setFormError(null)

    if (!selectedAsset) {
      setFormError('Select an asset before creating a processing record.')
      return
    }

    if (processingType === 'grading' && !['not_required', 'completed'].includes(refurbishmentStatus)) {
      setFormError('A grading-only record must use not required or completed.')
      return
    }

    if (processingType !== 'grading' && !['pending', 'in_progress'].includes(refurbishmentStatus)) {
      setFormError('A new refurbishment record must start as pending or in progress.')
      return
    }

    if (refurbishmentStatus === 'completed' && !grade) {
      setFormError('A completed processing record must have a grade.')
      return
    }

    setSubmitting(true)
    try {
      await createAssetProcessing({
        asset_id: selectedAsset.id,
        processing_type: processingType,
        grade: grade || null,
        refurbishment_status: refurbishmentStatus,
        processor: processor.trim() || null,
        processing_date: processingDate,
        condition_summary: conditionSummary.trim() || null,
        repairs_performed: repairsPerformed.trim() || null,
        parts_replaced: partsReplaced.trim() || null,
        testing_notes: testingNotes.trim() || null,
        processing_reference: processingReference.trim() || null,
        cost: cost.trim() || null,
        notes: notes.trim() || null,
      })

      setShowForm(false)
      setSelectedAsset(null)
      setBarcode('')
      resetForm()
      await loadWorkspace()
      setBarcodeFocusSignal((current) => current + 1)
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Failed to create processing record.')
    } finally {
      setSubmitting(false)
    }
  }

  const displayedRecords = useMemo(
    () => [...records].sort(
      (a, b) => new Date(b.processing.processing_date).getTime() -
        new Date(a.processing.processing_date).getTime(),
    ),
    [records],
  )

  return (
    <div className="processing-page">
      <PageHeader
        title="Processing"
        description="Grade and refurbish assets using barcode-first processing."
      />

      <section className="processing-scan-card">
        <div className="processing-scan-heading">
          <div>
            <h2>Scan Asset</h2>
            <p>Scan an Asset Code or enter a serial number.</p>
          </div>
          <span className="processing-scan-hint">USB / Bluetooth scanner supported</span>
        </div>

        <BarcodeInput
          value={barcode}
          onChange={(value) => {
            setBarcode(value)
            setFormError(null)
          }}
          onScan={handleBarcodeScan}
          placeholder="Scan Asset Code or serial number"
          autoFocus
          focusSignal={barcodeFocusSignal}
        />

        {formError && !showForm && <div className="processing-error">{formError}</div>}
      </section>

      <div className="processing-summary">
        <Card><div className="processing-summary-value">{counts.pending}</div><div className="processing-summary-label">Pending</div></Card>
        <Card><div className="processing-summary-value">{counts.inProgress}</div><div className="processing-summary-label">In Progress</div></Card>
        <Card><div className="processing-summary-value">{counts.completed}</div><div className="processing-summary-label">Completed</div></Card>
      </div>

      {showForm && selectedAsset && (
        <Card>
          <div className="processing-form-header">
            <div>
              <h2>
                Process <Link to={`/assets/${selectedAsset.id}/overview`}>{selectedAsset.asset_code}</Link>
              </h2>
              <p>
                {selectedAsset.asset_category}
                {selectedAsset.manufacturer ? ` · ${selectedAsset.manufacturer}` : ''}
                {selectedAsset.model ? ` · ${selectedAsset.model}` : ''}
              </p>
            </div>
            <Button type="button" variant="secondary" onClick={() => setShowForm(false)} disabled={submitting}>Cancel</Button>
          </div>

          <form className="processing-form" onSubmit={handleSubmit}>
            <div className="processing-form-grid">
              <label>
                Processing Type
                <select value={processingType} onChange={(e) => {
                  const value = e.target.value
                  setProcessingType(value)
                  setRefurbishmentStatus(value === 'grading' ? 'not_required' : 'pending')
                }} disabled={submitting}>
                  {PROCESSING_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>

              <label>
                Grade
                <select value={grade} onChange={(e) => setGrade(e.target.value)} disabled={submitting}>
                  <option value="">Not assigned</option>
                  {GRADES.map((value) => <option key={value} value={value}>{value}</option>)}
                </select>
              </label>

              <label>
                Refurbishment Status
                <select value={refurbishmentStatus} onChange={(e) => setRefurbishmentStatus(e.target.value)} disabled={submitting}>
                  {(processingType === 'grading' ? ['not_required', 'completed'] : ['pending', 'in_progress'])
                    .map((value) => <option key={value} value={value}>{value.replaceAll('_', ' ')}</option>)}
                </select>
              </label>

              <label>Processor<input value={processor} onChange={(e) => setProcessor(e.target.value)} placeholder="Processor name" autoComplete="name" disabled={submitting} /></label>
              <label>Processing Date<input type="date" value={processingDate} onChange={(e) => setProcessingDate(e.target.value)} disabled={submitting} /></label>
              <label>Processing Reference<input value={processingReference} onChange={(e) => setProcessingReference(e.target.value)} placeholder="Reference / job number" disabled={submitting} /></label>

              <label className="processing-field-wide">Condition Summary<textarea value={conditionSummary} onChange={(e) => setConditionSummary(e.target.value)} rows={3} disabled={submitting} /></label>
              <label>Repairs Performed<textarea value={repairsPerformed} onChange={(e) => setRepairsPerformed(e.target.value)} rows={3} disabled={submitting} /></label>
              <label>Parts Replaced<textarea value={partsReplaced} onChange={(e) => setPartsReplaced(e.target.value)} rows={3} disabled={submitting} /></label>
              <label>Testing Notes<textarea value={testingNotes} onChange={(e) => setTestingNotes(e.target.value)} rows={3} disabled={submitting} /></label>
              <label>Cost<input value={cost} onChange={(e) => setCost(e.target.value)} inputMode="decimal" placeholder="0.00" disabled={submitting} /></label>
              <label className="processing-field-wide">Notes<textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} disabled={submitting} /></label>
            </div>

            {formError && <div className="processing-error">{formError}</div>}

            <div className="processing-form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowForm(false)} disabled={submitting}>Cancel</Button>
              <Button type="submit" disabled={submitting}>{submitting ? 'Saving…' : 'Start Processing'}</Button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <div className="processing-queue-header">
          <div><h2>Processing Queue</h2><p>Latest processing record for each asset.</p></div>
          <span>{displayedRecords.length} asset{displayedRecords.length === 1 ? '' : 's'}</span>
        </div>

        {loading ? <div className="processing-empty">Loading processing queue…</div>
          : error ? <div className="processing-error">{error}</div>
          : displayedRecords.length === 0 ? <div className="processing-empty">No processing records yet.</div>
          : (
            <div className="processing-table-wrapper">
              <table className="processing-table">
                <thead><tr><th>Asset</th><th>Category</th><th>Serial</th><th>Type</th><th>Grade</th><th>Status</th><th>Processor</th><th>Date</th><th /></tr></thead>
                <tbody>
                  {displayedRecords.map(({ asset, processing }) => (
                    <tr key={processing.id}>
                      <td><Link to={`/assets/${asset.id}/overview`}>{asset.asset_code}</Link></td>
                      <td>{asset.asset_category}</td>
                      <td>{asset.serial_number || '—'}</td>
                      <td>{formatType(processing.processing_type)}</td>
                      <td>{processing.grade || '—'}</td>
                      <td>  
                        <StatusBadge variant={getVariant(processing.refurbishment_status)}>
                        {processing.refurbishment_status.replaceAll('_', ' ')}  
                        </StatusBadge>
                      </td>
                      <td>{processing.processor || '—'}</td>
                      <td>{formatDate(processing.processing_date)}</td>
                      <td><Button type="button" variant="secondary" onClick={() => openProcessingForm(asset)}>Process Again</Button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
      </Card>
    </div>
  )
}

export default ProcessingPage
