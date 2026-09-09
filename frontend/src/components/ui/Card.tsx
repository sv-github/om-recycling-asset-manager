type CardProps = {
  children: React.ReactNode
  className?: string
}

function Card({ children, className = '' }: CardProps) {
  return <section className={`ui-card ${className}`}>{children}</section>
}

export default Card