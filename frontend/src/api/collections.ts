import type {
  Collection,
  CollectionAsset,
  CollectionItem,
  CollectionStatus,
  Customer,
  CustomerLocation,
} from '../types/collection'

const API_BASE = '/api'

export type CollectionListFilters = {
  customerId?: number
  locationId?: number
  status?: string
}

export async function listCollections(
  filters: CollectionListFilters = {},
): Promise<Collection[]> {
  const params = new URLSearchParams()

  if (filters.customerId !== undefined) {
    params.set(
      'customer_id',
      String(filters.customerId),
    )
  }

  if (filters.locationId !== undefined) {
    params.set(
      'location_id',
      String(filters.locationId),
    )
  }

  if (filters.status !== undefined) {
    params.set(
      'status_filter',
      filters.status,
    )
  }

  const queryString = params.toString()

  const response = await fetch(
    `${API_BASE}/collections${
      queryString ? `?${queryString}` : ''
    }`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load collections (${response.status})`,
    )
  }

  return response.json() as Promise<Collection[]>
}

export async function getCollection(
  collectionId: number,
): Promise<Collection> {
  const response = await fetch(
    `${API_BASE}/collections/${collectionId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load collection (${response.status})`,
    )
  }

  return response.json() as Promise<Collection>
}

export async function listCustomers(): Promise<Customer[]> {
  const response = await fetch(
    `${API_BASE}/customers`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load customers (${response.status})`,
    )
  }

  return response.json() as Promise<Customer[]>
}

export async function getCustomer(
  customerId: number,
): Promise<Customer> {
  const response = await fetch(
    `${API_BASE}/customers/${customerId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load customer (${response.status})`,
    )
  }

  return response.json() as Promise<Customer>
}

export async function listCustomerLocations(
  customerIds: number[],
): Promise<CustomerLocation[]> {
  if (customerIds.length === 0) {
    return []
  }

  const responses = await Promise.all(
    customerIds.map(async (customerId) => {
      const response = await fetch(
        `${API_BASE}/customer-locations/customer/${customerId}`,
      )

      if (!response.ok) {
        throw new Error(
          `Failed to load customer locations (${response.status})`,
        )
      }

      return response.json() as Promise<
        CustomerLocation[]
      >
    }),
  )

  return responses.flat()
}

export async function getCustomerLocation(
  locationId: number,
): Promise<CustomerLocation> {
  const response = await fetch(
    `${API_BASE}/customer-locations/${locationId}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load customer location (${response.status})`,
    )
  }

  return response.json() as Promise<CustomerLocation>
}

export async function listCollectionStatuses(): Promise<
  CollectionStatus[]
> {
  const response = await fetch(
    `${API_BASE}/collection-statuses`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load collection statuses (${response.status})`,
    )
  }

  return response.json() as Promise<CollectionStatus[]>
}

export async function listCollectionItems(
  collectionId: number,
): Promise<CollectionItem[]> {
  const params = new URLSearchParams({
    collection_id: String(collectionId),
  })

  const response = await fetch(
    `${API_BASE}/collection-items?${params.toString()}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load collection items (${response.status})`,
    )
  }

  return response.json() as Promise<CollectionItem[]>
}

export async function listCollectionAssets(
  collectionId: number,
): Promise<CollectionAsset[]> {
  const params = new URLSearchParams({
    collection_id: String(collectionId),
  })

  const response = await fetch(
    `${API_BASE}/assets?${params.toString()}`,
  )

  if (!response.ok) {
    throw new Error(
      `Failed to load collection assets (${response.status})`,
    )
  }

  return response.json() as Promise<CollectionAsset[]>
}