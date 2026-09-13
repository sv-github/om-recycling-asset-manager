import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import {
  createCollection,
  createCustomer,
  createCustomerLocation,
  listCollectionStatuses,
  listCollections,
  listCustomerLocations,
  listCustomers,
} from '../api/collections'

import type {
  Collection,
  CollectionStatus,
  Customer,
  CustomerLocation,
} from '../types/collection'

import './CollectionsPage.css'

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

function formatCollectionDate(
  value: string,
): string {
  const [year, month, day] = value.split('-')

  if (!year || !month || !day) {
    return value
  }

  return `${day}-${month}-${year}`
}

function getTodayDate(): string {
  return new Date().toISOString().slice(0, 10)
}

function CollectionsPage() {
  const navigate = useNavigate()

  const [collections, setCollections] = useState<
    Collection[]
  >([])

  const [customers, setCustomers] = useState<
    Customer[]
  >([])

  const [locations, setLocations] = useState<
    CustomerLocation[]
  >([])

  const [statuses, setStatuses] = useState<
    CollectionStatus[]
  >([])

  const [search, setSearch] = useState('')
  const [customerFilter, setCustomerFilter] =
    useState('')
  const [locationFilter, setLocationFilter] =
    useState('')
  const [statusFilter, setStatusFilter] =
    useState('')

  const [loading, setLoading] = useState(true)

  const [filterDataLoading, setFilterDataLoading] =
    useState(true)

  const [error, setError] = useState<string | null>(
    null,
  )

  const [showCreateForm, setShowCreateForm] =
    useState(false)

  const [createCustomerId, setCreateCustomerId] =
    useState('')

  const [createLocationId, setCreateLocationId] =
    useState('')

  const [createCollectionDate, setCreateCollectionDate] =
    useState(getTodayDate())

  const [
    createPickupReceiptNumber,
    setCreatePickupReceiptNumber,
  ] = useState('')

  const [createSourceType, setCreateSourceType] =
    useState('customer')

  const [createStatus, setCreateStatus] =
    useState('scheduled')

  const [
    createExpectedItemCount,
    setCreateExpectedItemCount,
  ] = useState('')

  const [
    createTransportReference,
    setCreateTransportReference,
  ] = useState('')

  const [createNotes, setCreateNotes] =
    useState('')

  const [createSubmitting, setCreateSubmitting] =
    useState(false)

  const [createError, setCreateError] =
    useState<string | null>(null)

  const [showNewCustomer, setShowNewCustomer] =
    useState(false)

  const [newCustomerCompanyName, setNewCustomerCompanyName] =
    useState('')

  const [newCustomerLegalName, setNewCustomerLegalName] =
    useState('')

  const [newCustomerGstin, setNewCustomerGstin] =
    useState('')

  const [
    newCustomerContactName,
    setNewCustomerContactName,
  ] = useState('')

  const [
    newCustomerContactEmail,
    setNewCustomerContactEmail,
  ] = useState('')

  const [
    newCustomerContactPhone,
    setNewCustomerContactPhone,
  ] = useState('')

  const [newCustomerAddress, setNewCustomerAddress] =
    useState('')

  const [newCustomerNotes, setNewCustomerNotes] =
    useState('')

  const [
    newCustomerSubmitting,
    setNewCustomerSubmitting,
  ] = useState(false)

  const [
    newCustomerError,
    setNewCustomerError,
  ] = useState<string | null>(null)

  const [showNewLocation, setShowNewLocation] =
    useState(false)

  const [newLocationName, setNewLocationName] =
    useState('')

  const [newLocationAddress, setNewLocationAddress] =
    useState('')

  const [newLocationContactName, setNewLocationContactName] =
    useState('')

  const [
    newLocationContactEmail,
    setNewLocationContactEmail,
  ] = useState('')

  const [
    newLocationContactPhone,
    setNewLocationContactPhone,
  ] = useState('')

  const [newLocationNotes, setNewLocationNotes] =
    useState('')

  const [
    newLocationSubmitting,
    setNewLocationSubmitting,
  ] = useState(false)

  const [
    newLocationError,
    setNewLocationError,
  ] = useState<string | null>(null)

  async function loadCollections() {
    setLoading(true)
    setError(null)

    try {
      const data = await listCollections({
        customerId: customerFilter
          ? Number(customerFilter)
          : undefined,

        locationId: locationFilter
          ? Number(locationFilter)
          : undefined,

        status: statusFilter || undefined,
      })

      setCollections(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load collections.',
      )
    } finally {
      setLoading(false)
    }
  }

  async function loadReferenceData() {
    setFilterDataLoading(true)
    setError(null)

    try {
      const [
        customerData,
        statusData,
      ] = await Promise.all([
        listCustomers(),
        listCollectionStatuses(),
      ])

      const locationData =
        await listCustomerLocations(
          customerData.map(
            (customer) => customer.id,
          ),
        )

      setCustomers(customerData)
      setLocations(locationData)
      setStatuses(statusData)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Failed to load collection filters.',
      )
    } finally {
      setFilterDataLoading(false)
    }
  }

  useEffect(() => {
    void loadReferenceData()
  }, [])

  useEffect(() => {
    if (!filterDataLoading) {
      void loadCollections()
    }
  }, [
    customerFilter,
    locationFilter,
    statusFilter,
    filterDataLoading,
  ])

  const customerMap = useMemo(() => {
    return new Map(
      customers.map((customer) => [
        customer.id,
        customer,
      ]),
    )
  }, [customers])

  const locationMap = useMemo(() => {
    return new Map(
      locations.map((location) => [
        location.id,
        location,
      ]),
    )
  }, [locations])

  const filteredLocations = useMemo(() => {
    if (!customerFilter) {
      return locations
    }

    return locations.filter(
      (location) =>
        location.customer_id ===
        Number(customerFilter),
    )
  }, [locations, customerFilter])

  const createLocations = useMemo(() => {
    if (!createCustomerId) {
      return []
    }

    return locations.filter(
      (location) =>
        location.customer_id ===
        Number(createCustomerId),
    )
  }, [locations, createCustomerId])

  const filteredCollections = useMemo(() => {
    const searchTerm =
      search.trim().toLowerCase()

    if (!searchTerm) {
      return collections
    }

    return collections.filter((collection) => {
      const customer = customerMap.get(
        collection.customer_id,
      )

      const location = locationMap.get(
        collection.location_id,
      )

      return [
        collection.collection_code,
        collection.pickup_receipt_number,
        collection.source_type,
        collection.transport_reference,
        customer?.company_name,
        customer?.customer_code,
        location?.location_name,
        location?.location_code,
        collection.status,
      ].some((value) =>
        value
          ?.toString()
          .toLowerCase()
          .includes(searchTerm),
      )
    })
  }, [
    collections,
    search,
    customerMap,
    locationMap,
  ])

  function resetCreateForm() {
    setCreateCustomerId('')
    setCreateLocationId('')
    setCreateCollectionDate(getTodayDate())
    setCreatePickupReceiptNumber('')
    setCreateSourceType('customer')
    setCreateStatus(
      statuses[0]?.code || 'scheduled',
    )
    setCreateExpectedItemCount('')
    setCreateTransportReference('')
    setCreateNotes('')
    setCreateError(null)

    setShowNewCustomer(false)
    setShowNewLocation(false)

    resetNewCustomerForm()
    resetNewLocationForm()
  }

  function resetNewCustomerForm() {
    setNewCustomerCompanyName('')
    setNewCustomerLegalName('')
    setNewCustomerGstin('')
    setNewCustomerContactName('')
    setNewCustomerContactEmail('')
    setNewCustomerContactPhone('')
    setNewCustomerAddress('')
    setNewCustomerNotes('')
    setNewCustomerError(null)
  }

  function resetNewLocationForm() {
    setNewLocationName('')
    setNewLocationAddress('')
    setNewLocationContactName('')
    setNewLocationContactEmail('')
    setNewLocationContactPhone('')
    setNewLocationNotes('')
    setNewLocationError(null)
  }

  function openCreateForm() {
    resetCreateForm()
    setShowCreateForm(true)
  }

  function closeCreateForm() {
    if (
      createSubmitting ||
      newCustomerSubmitting ||
      newLocationSubmitting
    ) {
      return
    }

    setShowCreateForm(false)
    resetCreateForm()
  }

  function openNewCustomer() {
    setShowNewCustomer(true)
    setShowNewLocation(false)
    setNewCustomerError(null)
  }

  function cancelNewCustomer() {
    if (newCustomerSubmitting) {
      return
    }

    setShowNewCustomer(false)
    resetNewCustomerForm()
  }

  async function handleCreateCustomer(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setNewCustomerError(null)

    if (!newCustomerCompanyName.trim()) {
      setNewCustomerError(
        'Company name is required.',
      )
      return
    }

    setNewCustomerSubmitting(true)

    try {
      const customer = await createCustomer({
        company_name:
          newCustomerCompanyName.trim(),

        legal_name:
          newCustomerLegalName.trim() || null,

        gstin:
          newCustomerGstin.trim() || null,

        primary_contact_name:
          newCustomerContactName.trim() || null,

        primary_contact_email:
          newCustomerContactEmail.trim() || null,

        primary_contact_phone:
          newCustomerContactPhone.trim() || null,

        address:
          newCustomerAddress.trim() || null,

        notes:
          newCustomerNotes.trim() || null,
      })

      setCustomers((current) =>
        [...current, customer].sort(
          (a, b) =>
            a.company_name.localeCompare(
              b.company_name,
            ),
        ),
      )

      setCreateCustomerId(
        String(customer.id),
      )

      setCreateLocationId('')

      setShowNewCustomer(false)
      resetNewCustomerForm()
    } catch (err) {
      setNewCustomerError(
        err instanceof Error
          ? err.message
          : 'Failed to create customer.',
      )
    } finally {
      setNewCustomerSubmitting(false)
    }
  }

  function openNewLocation() {
    if (!createCustomerId) {
      setCreateError(
        'Please select a customer before creating a location.',
      )
      return
    }

    setShowNewLocation(true)
    setShowNewCustomer(false)
    setNewLocationError(null)
  }

  function cancelNewLocation() {
    if (newLocationSubmitting) {
      return
    }

    setShowNewLocation(false)
    resetNewLocationForm()
  }

  async function handleCreateLocation(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setNewLocationError(null)

    if (!createCustomerId) {
      setNewLocationError(
        'Please select a customer first.',
      )
      return
    }

    if (!newLocationName.trim()) {
      setNewLocationError(
        'Location name is required.',
      )
      return
    }

    setNewLocationSubmitting(true)

    try {
      const location =
        await createCustomerLocation({
          customer_id:
            Number(createCustomerId),

          location_name:
            newLocationName.trim(),

          address:
            newLocationAddress.trim() || null,

          contact_name:
            newLocationContactName.trim() || null,

          contact_email:
            newLocationContactEmail.trim() || null,

          contact_phone:
            newLocationContactPhone.trim() || null,

          notes:
            newLocationNotes.trim() || null,
        })

      setLocations((current) => [
        ...current,
        location,
      ])

      setCreateLocationId(
        String(location.id),
      )

      setShowNewLocation(false)
      resetNewLocationForm()
    } catch (err) {
      setNewLocationError(
        err instanceof Error
          ? err.message
          : 'Failed to create customer location.',
      )
    } finally {
      setNewLocationSubmitting(false)
    }
  }

  async function handleCreateCollection(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()

    setCreateError(null)

    if (!createCustomerId) {
      setCreateError(
        'Please select a customer.',
      )
      return
    }

    if (!createLocationId) {
      setCreateError(
        'Please select a customer location.',
      )
      return
    }

    if (!createCollectionDate) {
      setCreateError(
        'Please select a collection date.',
      )
      return
    }

    if (!createSourceType.trim()) {
      setCreateError(
        'Please enter a source type.',
      )
      return
    }

    if (
      createExpectedItemCount !== '' &&
      (
        !Number.isInteger(
          Number(createExpectedItemCount),
        ) ||
        Number(createExpectedItemCount) < 0
      )
    ) {
      setCreateError(
        'Expected item count must be a non-negative whole number.',
      )
      return
    }

    setCreateSubmitting(true)

    try {
      const createdCollection =
        await createCollection({
          customer_id:
            Number(createCustomerId),

          location_id:
            Number(createLocationId),

          collection_date:
            createCollectionDate,

          pickup_receipt_number:
            createPickupReceiptNumber.trim() ||
            null,

          source_type:
            createSourceType.trim(),

          status:
            createStatus || 'scheduled',

          expected_item_count:
            createExpectedItemCount === ''
              ? null
              : Number(
                  createExpectedItemCount,
                ),

          transport_reference:
            createTransportReference.trim() ||
            null,

          notes:
            createNotes.trim() || null,
        })

      setShowCreateForm(false)
      resetCreateForm()

      navigate(
        `/collections/${createdCollection.id}`,
      )
    } catch (err) {
      setCreateError(
        err instanceof Error
          ? err.message
          : 'Failed to create collection.',
      )
    } finally {
      setCreateSubmitting(false)
    }
  }

  if (showCreateForm) {
    return (
      <>
        <PageHeader
          title="New Collection"
          description="Create a new equipment collection for OM Recycling."
          actions={
            <Button
              variant="secondary"
              onClick={closeCreateForm}
              disabled={
                createSubmitting ||
                newCustomerSubmitting ||
                newLocationSubmitting
              }
            >
              Cancel
            </Button>
          }
        />

        <Card className="collections-create-card">
          <div className="collections-create-form">
            <div className="collections-create-section">
              <div className="collections-create-section-title">
                Customer
              </div>

              {!showNewCustomer && (
                <>
                  <div className="collections-create-grid">
                    <div className="collections-create-field">
                      <label htmlFor="create-customer">
                        Customer *
                      </label>

                      <select
                        id="create-customer"
                        value={createCustomerId}
                        onChange={(event) => {
                          setCreateCustomerId(
                            event.target.value,
                          )
                          setCreateLocationId('')
                          setCreateError(null)
                        }}
                        disabled={
                          filterDataLoading ||
                          createSubmitting
                        }
                      >
                        <option value="">
                          Select customer
                        </option>

                        {customers
                          .filter(
                            (customer) =>
                              customer.is_active,
                          )
                          .map((customer) => (
                            <option
                              key={customer.id}
                              value={customer.id}
                            >
                              {
                                customer.company_name
                              }
                            </option>
                          ))}
                      </select>
                    </div>
                  </div>

                  <div className="collections-inline-action">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={openNewCustomer}
                      disabled={
                        createSubmitting
                      }
                    >
                      + Create New Customer
                    </Button>
                  </div>
                </>
              )}

              {showNewCustomer && (
                <form
                  className="collections-subform"
                  onSubmit={
                    handleCreateCustomer
                  }
                >
                  <div className="collections-subform-header">
                    <div>
                      <div className="collections-subform-title">
                        New Customer
                      </div>

                      <div className="collections-subform-description">
                        Customer code will be
                        generated automatically.
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant="ghost"
                      onClick={
                        cancelNewCustomer
                      }
                      disabled={
                        newCustomerSubmitting
                      }
                    >
                      Cancel
                    </Button>
                  </div>

                  <div className="collections-create-grid">
                    <div className="collections-create-field">
                      <label htmlFor="new-customer-company">
                        Company Name *
                      </label>

                      <input
                        id="new-customer-company"
                        type="text"
                        value={
                          newCustomerCompanyName
                        }
                        onChange={(event) =>
                          setNewCustomerCompanyName(
                            event.target.value,
                          )
                        }
                        maxLength={200}
                        disabled={
                          newCustomerSubmitting
                        }
                        required
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-customer-legal">
                        Legal Name
                      </label>

                      <input
                        id="new-customer-legal"
                        type="text"
                        value={
                          newCustomerLegalName
                        }
                        onChange={(event) =>
                          setNewCustomerLegalName(
                            event.target.value,
                          )
                        }
                        maxLength={250}
                        disabled={
                          newCustomerSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-customer-gstin">
                        GSTIN
                      </label>

                      <input
                        id="new-customer-gstin"
                        type="text"
                        value={
                          newCustomerGstin
                        }
                        onChange={(event) =>
                          setNewCustomerGstin(
                            event.target.value,
                          )
                        }
                        maxLength={15}
                        disabled={
                          newCustomerSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-customer-contact">
                        Primary Contact Name
                      </label>

                      <input
                        id="new-customer-contact"
                        type="text"
                        value={
                          newCustomerContactName
                        }
                        onChange={(event) =>
                          setNewCustomerContactName(
                            event.target.value,
                          )
                        }
                        maxLength={150}
                        disabled={
                          newCustomerSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-customer-email">
                        Primary Contact Email
                      </label>

                      <input
                        id="new-customer-email"
                        type="email"
                        value={
                          newCustomerContactEmail
                        }
                        onChange={(event) =>
                          setNewCustomerContactEmail(
                            event.target.value,
                          )
                        }
                        disabled={
                          newCustomerSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-customer-phone">
                        Primary Contact Phone
                      </label>

                      <input
                        id="new-customer-phone"
                        type="text"
                        value={
                          newCustomerContactPhone
                        }
                        onChange={(event) =>
                          setNewCustomerContactPhone(
                            event.target.value,
                          )
                        }
                        maxLength={30}
                        disabled={
                          newCustomerSubmitting
                        }
                      />
                    </div>
                  </div>

                  <div className="collections-create-field collections-create-field-full">
                    <label htmlFor="new-customer-address">
                      Address
                    </label>

                    <textarea
                      id="new-customer-address"
                      value={
                        newCustomerAddress
                      }
                      onChange={(event) =>
                        setNewCustomerAddress(
                          event.target.value,
                        )
                      }
                      rows={3}
                      disabled={
                        newCustomerSubmitting
                      }
                    />
                  </div>

                  <div className="collections-create-field collections-create-field-full">
                    <label htmlFor="new-customer-notes">
                      Notes
                    </label>

                    <textarea
                      id="new-customer-notes"
                      value={
                        newCustomerNotes
                      }
                      onChange={(event) =>
                        setNewCustomerNotes(
                          event.target.value,
                        )
                      }
                      rows={3}
                      disabled={
                        newCustomerSubmitting
                      }
                    />
                  </div>

                  {newCustomerError && (
                    <div className="collections-create-error">
                      {newCustomerError}
                    </div>
                  )}

                  <div className="collections-subform-actions">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={
                        cancelNewCustomer
                      }
                      disabled={
                        newCustomerSubmitting
                      }
                    >
                      Cancel
                    </Button>

                    <Button
                      type="submit"
                      variant="primary"
                      disabled={
                        newCustomerSubmitting
                      }
                    >
                      {newCustomerSubmitting
                        ? 'Creating...'
                        : 'Create Customer'}
                    </Button>
                  </div>
                </form>
              )}

              {!showNewCustomer &&
                createCustomerId && (
                  <div className="collections-selected-record">
                    <span>
                      Selected customer
                    </span>

                    <strong>
                      {
                        customerMap.get(
                          Number(
                            createCustomerId,
                          ),
                        )?.company_name
                      }
                    </strong>
                  </div>
                )}
            </div>

            <div className="collections-create-section">
              <div className="collections-create-section-title">
                Customer Location
              </div>

              {!showNewLocation && (
                <>
                  <div className="collections-create-grid">
                    <div className="collections-create-field">
                      <label htmlFor="create-location">
                        Customer Location *
                      </label>

                      <select
                        id="create-location"
                        value={createLocationId}
                        onChange={(event) => {
                          setCreateLocationId(
                            event.target.value,
                          )
                          setCreateError(null)
                        }}
                        disabled={
                          !createCustomerId ||
                          filterDataLoading ||
                          createSubmitting
                        }
                      >
                        <option value="">
                          {createCustomerId
                            ? 'Select location'
                            : 'Select customer first'}
                        </option>

                        {createLocations
                          .filter(
                            (location) =>
                              location.is_active,
                          )
                          .map((location) => (
                            <option
                              key={location.id}
                              value={location.id}
                            >
                              {
                                location.location_name
                              }
                            </option>
                          ))}
                      </select>
                    </div>
                  </div>

                  <div className="collections-inline-action">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={openNewLocation}
                      disabled={
                        !createCustomerId ||
                        createSubmitting
                      }
                    >
                      + Create New Location
                    </Button>
                  </div>
                </>
              )}

              {showNewLocation && (
                <form
                  className="collections-subform"
                  onSubmit={
                    handleCreateLocation
                  }
                >
                  <div className="collections-subform-header">
                    <div>
                      <div className="collections-subform-title">
                        New Customer Location
                      </div>

                      <div className="collections-subform-description">
                        Location code will be
                        generated automatically.
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant="ghost"
                      onClick={
                        cancelNewLocation
                      }
                      disabled={
                        newLocationSubmitting
                      }
                    >
                      Cancel
                    </Button>
                  </div>

                  <div className="collections-create-grid">
                    <div className="collections-create-field">
                      <label htmlFor="new-location-name">
                        Location Name *
                      </label>

                      <input
                        id="new-location-name"
                        type="text"
                        value={
                          newLocationName
                        }
                        onChange={(event) =>
                          setNewLocationName(
                            event.target.value,
                          )
                        }
                        maxLength={150}
                        disabled={
                          newLocationSubmitting
                        }
                        required
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-location-contact">
                        Contact Name
                      </label>

                      <input
                        id="new-location-contact"
                        type="text"
                        value={
                          newLocationContactName
                        }
                        onChange={(event) =>
                          setNewLocationContactName(
                            event.target.value,
                          )
                        }
                        maxLength={150}
                        disabled={
                          newLocationSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-location-email">
                        Contact Email
                      </label>

                      <input
                        id="new-location-email"
                        type="email"
                        value={
                          newLocationContactEmail
                        }
                        onChange={(event) =>
                          setNewLocationContactEmail(
                            event.target.value,
                          )
                        }
                        disabled={
                          newLocationSubmitting
                        }
                      />
                    </div>

                    <div className="collections-create-field">
                      <label htmlFor="new-location-phone">
                        Contact Phone
                      </label>

                      <input
                        id="new-location-phone"
                        type="text"
                        value={
                          newLocationContactPhone
                        }
                        onChange={(event) =>
                          setNewLocationContactPhone(
                            event.target.value,
                          )
                        }
                        maxLength={30}
                        disabled={
                          newLocationSubmitting
                        }
                      />
                    </div>
                  </div>

                  <div className="collections-create-field collections-create-field-full">
                    <label htmlFor="new-location-address">
                      Address
                    </label>

                    <textarea
                      id="new-location-address"
                      value={
                        newLocationAddress
                      }
                      onChange={(event) =>
                        setNewLocationAddress(
                          event.target.value,
                        )
                      }
                      rows={3}
                      disabled={
                        newLocationSubmitting
                      }
                    />
                  </div>

                  <div className="collections-create-field collections-create-field-full">
                    <label htmlFor="new-location-notes">
                      Notes
                    </label>

                    <textarea
                      id="new-location-notes"
                      value={
                        newLocationNotes
                      }
                      onChange={(event) =>
                        setNewLocationNotes(
                          event.target.value,
                        )
                      }
                      rows={3}
                      disabled={
                        newLocationSubmitting
                      }
                    />
                  </div>

                  {newLocationError && (
                    <div className="collections-create-error">
                      {newLocationError}
                    </div>
                  )}

                  <div className="collections-subform-actions">
                    <Button
                      type="button"
                      variant="secondary"
                      onClick={
                        cancelNewLocation
                      }
                      disabled={
                        newLocationSubmitting
                      }
                    >
                      Cancel
                    </Button>

                    <Button
                      type="submit"
                      variant="primary"
                      disabled={
                        newLocationSubmitting
                      }
                    >
                      {newLocationSubmitting
                        ? 'Creating...'
                        : 'Create Location'}
                    </Button>
                  </div>
                </form>
              )}

              {!showNewLocation &&
                createLocationId && (
                  <div className="collections-selected-record">
                    <span>
                      Selected location
                    </span>

                    <strong>
                      {
                        locationMap.get(
                          Number(
                            createLocationId,
                          ),
                        )?.location_name
                      }
                    </strong>
                  </div>
                )}
            </div>

            <div className="collections-create-section">
              <div className="collections-create-section-title">
                Collection Information
              </div>

              <div className="collections-create-grid">
                <div className="collections-create-field">
                  <label htmlFor="create-date">
                    Collection Date *
                  </label>

                  <input
                    id="create-date"
                    type="date"
                    value={createCollectionDate}
                    onChange={(event) =>
                      setCreateCollectionDate(
                        event.target.value,
                      )
                    }
                    disabled={createSubmitting}
                    required
                  />
                </div>

                <div className="collections-create-field">
                  <label htmlFor="create-status">
                    Status
                  </label>

                  <select
                    id="create-status"
                    value={createStatus}
                    onChange={(event) =>
                      setCreateStatus(
                        event.target.value,
                      )
                    }
                    disabled={
                      filterDataLoading ||
                      createSubmitting
                    }
                  >
                    {statuses.map((status) => (
                      <option
                        key={status.id}
                        value={status.code}
                      >
                        {status.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="collections-create-field">
                  <label htmlFor="create-source-type">
                    Source Type *
                  </label>

                  <input
                    id="create-source-type"
                    type="text"
                    value={createSourceType}
                    onChange={(event) =>
                      setCreateSourceType(
                        event.target.value,
                      )
                    }
                    maxLength={30}
                    disabled={createSubmitting}
                    required
                  />
                </div>

                <div className="collections-create-field">
                  <label htmlFor="create-expected-count">
                    Expected Item Count
                  </label>

                  <input
                    id="create-expected-count"
                    type="number"
                    min="0"
                    step="1"
                    value={
                      createExpectedItemCount
                    }
                    onChange={(event) =>
                      setCreateExpectedItemCount(
                        event.target.value,
                      )
                    }
                    placeholder="0"
                    disabled={createSubmitting}
                  />
                </div>

                <div className="collections-create-field">
                  <label htmlFor="create-receipt">
                    Pickup Receipt Number
                  </label>

                  <input
                    id="create-receipt"
                    type="text"
                    value={
                      createPickupReceiptNumber
                    }
                    onChange={(event) =>
                      setCreatePickupReceiptNumber(
                        event.target.value,
                      )
                    }
                    maxLength={50}
                    disabled={createSubmitting}
                  />
                </div>

                <div className="collections-create-field">
                  <label htmlFor="create-transport">
                    Transport Reference
                  </label>

                  <input
                    id="create-transport"
                    type="text"
                    value={
                      createTransportReference
                    }
                    onChange={(event) =>
                      setCreateTransportReference(
                        event.target.value,
                      )
                    }
                    maxLength={100}
                    disabled={createSubmitting}
                  />
                </div>
              </div>
            </div>

            <div className="collections-create-section">
              <div className="collections-create-section-title">
                Notes
              </div>

              <div className="collections-create-field">
                <label htmlFor="create-notes">
                  Collection Notes
                </label>

                <textarea
                  id="create-notes"
                  value={createNotes}
                  onChange={(event) =>
                    setCreateNotes(
                      event.target.value,
                    )
                  }
                  placeholder="Additional collection information..."
                  rows={5}
                  disabled={createSubmitting}
                />
              </div>
            </div>

            {createError && (
              <div className="collections-create-error">
                {createError}
              </div>
            )}

            <div className="collections-create-actions">
              <Button
                type="button"
                variant="secondary"
                onClick={closeCreateForm}
                disabled={
                  createSubmitting ||
                  newCustomerSubmitting ||
                  newLocationSubmitting
                }
              >
                Cancel
              </Button>

              <Button
                type="button"
                variant="primary"
                onClick={() => {
                  const form =
                    document.getElementById(
                      'collection-create-submit-form',
                    ) as HTMLFormElement | null

                  form?.requestSubmit()
                }}
                disabled={
                  createSubmitting ||
                  newCustomerSubmitting ||
                  newLocationSubmitting
                }
              >
                {createSubmitting
                  ? 'Creating...'
                  : 'Create Collection'}
              </Button>
            </div>

            <form
              id="collection-create-submit-form"
              onSubmit={
                handleCreateCollection
              }
              style={{
                display: 'none',
              }}
            />
          </div>
        </Card>
      </>
    )
  }

  return (
    <>
      <PageHeader
        title="Collections"
        description="View and manage equipment collections received by OM Recycling."
        actions={
          <Button
            variant="primary"
            onClick={openCreateForm}
          >
            New Collection
          </Button>
        }
      />

      <Card className="collections-filter-card">
        <div className="collections-filters">
          <div className="collections-search">
            <label htmlFor="collection-search">
              Search collections
            </label>

            <input
              id="collection-search"
              type="search"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Collection code, receipt, customer, location..."
            />
          </div>

          <div className="collections-filter">
            <label htmlFor="collection-customer">
              Customer
            </label>

            <select
              id="collection-customer"
              value={customerFilter}
              onChange={(event) => {
                setCustomerFilter(
                  event.target.value,
                )
                setLocationFilter('')
              }}
              disabled={filterDataLoading}
            >
              <option value="">
                All customers
              </option>

              {customers
                .filter(
                  (customer) =>
                    customer.is_active,
                )
                .map((customer) => (
                  <option
                    key={customer.id}
                    value={customer.id}
                  >
                    {customer.company_name}
                  </option>
                ))}
            </select>
          </div>

          <div className="collections-filter">
            <label htmlFor="collection-location">
              Location
            </label>

            <select
              id="collection-location"
              value={locationFilter}
              onChange={(event) =>
                setLocationFilter(
                  event.target.value,
                )
              }
              disabled={filterDataLoading}
            >
              <option value="">
                All locations
              </option>

              {filteredLocations
                .filter(
                  (location) =>
                    location.is_active,
                )
                .map((location) => (
                  <option
                    key={location.id}
                    value={location.id}
                  >
                    {location.location_name}
                  </option>
                ))}
            </select>
          </div>

          <div className="collections-filter">
            <label htmlFor="collection-status">
              Status
            </label>

            <select
              id="collection-status"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value,
                )
              }
              disabled={filterDataLoading}
            >
              <option value="">
                All statuses
              </option>

              {statuses.map((status) => (
                <option
                  key={status.id}
                  value={status.code}
                >
                  {status.name}
                </option>
              ))}
            </select>
          </div>

          <div className="collections-filter-action">
            <Button
              variant="secondary"
              onClick={() => {
                setSearch('')
                setCustomerFilter('')
                setLocationFilter('')
                setStatusFilter('')
              }}
            >
              Clear
            </Button>
          </div>
        </div>
      </Card>

      <div className="collections-list-header">
        <div>
          <span className="collections-list-title">
            Collection Register
          </span>

          {!loading && (
            <span className="collections-list-count">
              {filteredCollections.length}{' '}
              {filteredCollections.length === 1
                ? 'collection'
                : 'collections'}
            </span>
          )}
        </div>
      </div>

      <Card className="collections-table-card">
        {loading && (
          <div className="collections-state">
            Loading collections...
          </div>
        )}

        {!loading && error && (
          <div className="collections-state collections-state-error">
            <div>{error}</div>

            <Button
              variant="secondary"
              onClick={() =>
                void loadCollections()
              }
            >
              Retry
            </Button>
          </div>
        )}

        {!loading &&
          !error &&
          filteredCollections.length === 0 && (
            <div className="collections-state">
              No collections found.
            </div>
          )}

        {!loading &&
          !error &&
          filteredCollections.length > 0 && (
            <div className="collections-table-wrapper">
              <table className="collections-table">
                <thead>
                  <tr>
                    <th>Collection Code</th>
                    <th>Customer</th>
                    <th>Location</th>
                    <th>Collection Date</th>
                    <th>Expected Items</th>
                    <th>Status</th>
                  </tr>
                </thead>

                <tbody>
                  {filteredCollections.map(
                    (collection) => {
                      const customer =
                        customerMap.get(
                          collection.customer_id,
                        )

                      const location =
                        locationMap.get(
                          collection.location_id,
                        )

                      return (
                        <tr
                          key={collection.id}
                        >
                          <td>
                            <button
                              type="button"
                              className="collection-code-button"
                              onClick={() =>
                                navigate(
                                  `/collections/${collection.id}`,
                                )
                              }
                            >
                              {
                                collection.collection_code
                              }
                            </button>
                          </td>

                          <td>
                            {customer?.company_name ||
                              '—'}
                          </td>

                          <td>
                            {location?.location_name ||
                              '—'}
                          </td>

                          <td>
                            {formatCollectionDate(
                              collection.collection_date,
                            )}
                          </td>

                          <td>
                            {collection.expected_item_count ??
                              '—'}
                          </td>

                          <td>
                            <StatusBadge
                              variant={getStatusVariant(
                                collection.status,
                              )}
                            >
                              {collection.status}
                            </StatusBadge>
                          </td>
                        </tr>
                      )
                    },
                  )}
                </tbody>
              </table>
            </div>
          )}
      </Card>
    </>
  )
}

export default CollectionsPage