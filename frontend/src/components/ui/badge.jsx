export function Badge({ children, className = '', variant = 'default' }) {
  // RegimA Zone palette (rzonedevops/rzodesys): monochrome navy + blue,
  // destructive red reserved for error states.
  const variants = {
    default: { background: 'var(--rz-blue-electric)', color: 'var(--rz-white)' },
    secondary: { background: 'var(--rz-bg-surface)', color: 'var(--rz-text-primary)' },
    destructive: { background: 'hsl(0 84% 60%)', color: 'var(--rz-white)' },
    outline: { background: 'transparent', color: 'var(--rz-text-primary)', border: '1px solid var(--rz-border)' }
  }

  return (
    <span className={className} style={{ ...variants[variant], borderRadius: 999, padding: '0.2rem 0.55rem', fontSize: '0.75rem', border: variants[variant].border || 'none' }}>
      {children}
    </span>
  )
}
