export function Badge({ children, className = '', variant = 'default' }) {
  const variants = {
    default: { background: '#dcfce7', color: '#166534' },
    secondary: { background: '#f3f4f6', color: '#374151' },
    destructive: { background: '#fee2e2', color: '#991b1b' },
    outline: { background: '#fff', color: '#374151', border: '1px solid #d1d5db' }
  }

  return (
    <span className={className} style={{ ...variants[variant], borderRadius: 999, padding: '0.2rem 0.55rem', fontSize: '0.75rem', border: variants[variant].border || 'none' }}>
      {children}
    </span>
  )
}
