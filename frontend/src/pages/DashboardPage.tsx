import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import PageHeader from '../components/ui/PageHeader'
import StatusBadge from '../components/ui/StatusBadge'

function DashboardPage() {
  return (
    <>
      <PageHeader
        title="UI Foundation"
        description="Component preview for the OM Recycling asset management system."
        actions={
          <>
            <Button variant="secondary">Secondary</Button>
            <Button>Primary Action</Button>
          </>
        }
      />

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
        }}
      >
        <Card>
          <div style={{ padding: '20px' }}>
            <div
              style={{
                marginBottom: '8px',
                color: '#6b7280',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              RECEIVED
            </div>

            <div
              style={{
                color: '#111827',
                fontSize: '28px',
                fontWeight: 650,
              }}
            >
              24
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ padding: '20px' }}>
            <div
              style={{
                marginBottom: '8px',
                color: '#6b7280',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              PROCESSING
            </div>

            <div
              style={{
                color: '#111827',
                fontSize: '28px',
                fontWeight: 650,
              }}
            >
              8
            </div>
          </div>
        </Card>

        <Card>
          <div style={{ padding: '20px' }}>
            <div
              style={{
                marginBottom: '10px',
                color: '#6b7280',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              STATUS
            </div>

            <StatusBadge variant="success">Operational</StatusBadge>
          </div>
        </Card>

        <Card>
          <div style={{ padding: '20px' }}>
            <div
              style={{
                marginBottom: '10px',
                color: '#6b7280',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              REVIEW
            </div>

            <StatusBadge variant="warning">Requires Review</StatusBadge>
          </div>
        </Card>
      </div>

      <Card className="ui-foundation-actions">
        <div style={{ padding: '20px' }}>
          <h2
            style={{
              margin: '0 0 8px',
              color: '#111827',
              fontSize: '16px',
              fontWeight: 650,
            }}
          >
            Button states
          </h2>

          <p
            style={{
              margin: '0 0 16px',
              color: '#6b7280',
              fontSize: '13px',
            }}
          >
            Basic action variants used throughout the application.
          </p>

          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '8px',
            }}
          >
            <Button>Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="danger">Danger</Button>
            <Button variant="ghost">Ghost</Button>
            <Button disabled>Disabled</Button>
          </div>
        </div>
      </Card>
    </>
  )
}

export default DashboardPage