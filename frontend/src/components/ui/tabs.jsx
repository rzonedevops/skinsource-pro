import { useState } from 'react'

export function Tabs({ defaultValue, children, className = '' }) {
  const [value, setValue] = useState(defaultValue)
  return <div className={className}>{mapChildren(children, value, setValue)}</div>
}

export function TabsList({ children }) {
  return <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>{children}</div>
}

export function TabsTrigger({ children, value, __tabsValue, __setTabsValue }) {
  const active = value === __tabsValue
  return (
    <button onClick={() => __setTabsValue(value)} style={{ borderRadius: 8, border: '1px solid #d1d5db', background: active ? '#dcfce7' : '#fff', padding: '0.45rem 0.7rem', cursor: 'pointer' }}>
      {children}
    </button>
  )
}

export function TabsContent({ children, value, __tabsValue }) {
  if (value !== __tabsValue) return null
  return <div>{children}</div>
}

function mapChildren(children, value, setValue) {
  return Array.isArray(children)
    ? children.map((child) => clone(child, value, setValue))
    : clone(children, value, setValue)
}

function clone(node, value, setValue) {
  if (!node) return node
  if (typeof node !== 'object') return node
  const props = node.props || {}
  const patchedChildren = mapChildren(props.children, value, setValue)
  return {
    ...node,
    props: {
      ...props,
      __tabsValue: value,
      __setTabsValue: setValue,
      children: patchedChildren,
    },
  }
}
