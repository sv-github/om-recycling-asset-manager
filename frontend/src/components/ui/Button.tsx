type ButtonProps = {
  children: React.ReactNode
  type?: 'button' | 'submit' | 'reset'
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  disabled?: boolean
  onClick?: () => void
}

function Button({
  children,
  type = 'button',
  variant = 'primary',
  disabled = false,
  onClick,
}: ButtonProps) {
  return (
    <button
      type={type}
      className={`ui-button ui-button-${variant}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  )
}

export default Button