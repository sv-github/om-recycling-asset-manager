type StatusBadgeProps = {
  children: React.ReactNode
  variant?: 'neutral' | 'success' | 'warning' | 'danger' | 'info'
}

function StatusBadge({
  children,
  variant = 'neutral',
}: StatusBadgeProps) {
  return (
    <span className={`ui-status-badge ui-status-${variant}`}>
      {children}
    </span>
  )
}

export default StatusBadge