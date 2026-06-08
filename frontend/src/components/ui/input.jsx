export function Input({ className = '', ...props }) {
  return <input className={className} style={{ width: '100%', padding: '0.55rem 0.75rem', border: '1px solid #d1d5db', borderRadius: 8 }} {...props} />
}
