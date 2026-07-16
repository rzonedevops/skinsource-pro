import { useId } from 'react'

export function Select({ value, onValueChange, children }) {
  return children({ value, onValueChange })
}

export function SelectTrigger({ className = '', children }) {
  return <div className={className}>{children}</div>
}

export function SelectValue({ placeholder }) {
  return <span>{placeholder}</span>
}

export function SelectContent({ children }) {
  return <>{children}</>
}

export function SelectItem({ value, children }) {
  return <option value={value}>{children}</option>
}

export function NativeSelect({ value, onChange, children, className = '' }) {
  const id = useId()
  return <select id={id} className={`rz-field__input ${className}`} style={{ width: 'auto' }} value={value} onChange={onChange}>{children}</select>
}
