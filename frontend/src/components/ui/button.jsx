export function Button({ children, variant = 'default', size = 'md', className = '', ...props }) {
  const styleMap = {
    default: 'background:#16a34a;color:white;border:1px solid #16a34a;',
    outline: 'background:white;color:#111827;border:1px solid #d1d5db;',
    ghost: 'background:transparent;color:#111827;border:1px solid transparent;',
    secondary: 'background:#f3f4f6;color:#111827;border:1px solid #e5e7eb;'
  }

  const sizeMap = {
    sm: 'padding:0.35rem 0.65rem;font-size:0.8rem;',
    md: 'padding:0.55rem 0.9rem;font-size:0.9rem;'
  }

  return (
    <button
      className={className}
      style={{ borderRadius: 8, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: 6, ...Object.fromEntries([]) }}
      {...props}
      dangerouslySetInnerHTML={undefined}
    >
      <span style={{ borderRadius: 8, ...inlineStyle(styleMap[variant] + sizeMap[size]) }}>{children}</span>
    </button>
  )
}

function inlineStyle(input) {
  return input.split(';').filter(Boolean).reduce((acc, entry) => {
    const [k, v] = entry.split(':')
    const key = k.trim().replace(/-([a-z])/g, (_, c) => c.toUpperCase())
    acc[key] = v.trim()
    return acc
  }, {})
}
