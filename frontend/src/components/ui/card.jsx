export function Card({ children, className = '' }) {
  return <div className={`card ${className}`}>{children}</div>
}

export function CardHeader({ children, className = '' }) {
  return <div className={className} style={{ padding: '1rem 1rem 0.5rem' }}>{children}</div>
}

export function CardTitle({ children, className = '' }) {
  return <h3 className={className} style={{ margin: 0, fontSize: '1rem' }}>{children}</h3>
}

export function CardDescription({ children, className = '' }) {
  return <p className={className} style={{ margin: '0.25rem 0 0', color: '#6b7280', fontSize: '0.9rem' }}>{children}</p>
}

export function CardContent({ children, className = '' }) {
  return <div className={className} style={{ padding: '0.5rem 1rem 1rem' }}>{children}</div>
}
