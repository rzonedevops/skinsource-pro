export function Button({ children, variant = 'default', size = 'md', className = '', ...props }) {
  // RegimA Zone palette (rzonedevops/rzodesys): electric-blue primary actions.
  const styleMap = {
    default: 'background:var(--rz-blue-electric);color:var(--rz-white);border:1px solid var(--rz-blue-electric);',
    outline: 'background:transparent;color:var(--rz-text-primary);border:1px solid rgba(255,255,255,0.3);',
    ghost: 'background:transparent;color:var(--rz-text-primary);border:1px solid transparent;',
    secondary: 'background:var(--rz-bg-surface);color:var(--rz-text-primary);border:1px solid var(--rz-border);'
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
