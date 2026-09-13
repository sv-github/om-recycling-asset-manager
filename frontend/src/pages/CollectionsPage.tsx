import {
  useEffect,
  useMemo,
  useState,
} from 'react'
import { useNavigate } from 'react-router-dom'

import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

import {
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

  useEffect(() => {
    async function loadFilterData() {
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

    void loadFilterData()
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

  return (
    <>
      <PageHeader
        title="Collections"
        description="View and manage equipment collections received by OM Recycling."
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