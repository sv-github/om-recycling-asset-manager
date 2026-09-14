import { useEffect, useRef } from 'react'
import type { KeyboardEvent } from 'react'

type BarcodeInputProps = {
  value: string
  onChange: (value: string) => void
  onScan?: (value: string) => void
  placeholder?: string
  disabled?: boolean
  autoFocus?: boolean
  focusSignal?: number
}

function BarcodeInput({
  value,
  onChange,
  onScan,
  placeholder = 'Scan or enter barcode',
  disabled = false,
  autoFocus = false,
  focusSignal = 0,
}: BarcodeInputProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (autoFocus || focusSignal > 0) {
      inputRef.current?.focus()
    }
  }, [autoFocus, focusSignal])

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key !== 'Enter') return
    event.preventDefault()
    const scannedValue = value.trim()
    if (scannedValue) onScan?.(scannedValue)
  }

  return (
    <div className="barcode-input">
      <span className="barcode-input-icon" aria-hidden="true">▥</span>
      <input
        ref={inputRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoComplete="off"
        spellCheck={false}
        disabled={disabled}
        aria-label="Asset barcode"
      />
      {value && (
        <button
          type="button"
          className="barcode-input-clear"
          onClick={() => {
            onChange('')
            inputRef.current?.focus()
          }}
          disabled={disabled}
          aria-label="Clear barcode"
        >
          ×
        </button>
      )}
    </div>
  )
}

export default BarcodeInput
