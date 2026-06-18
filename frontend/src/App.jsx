import { useState } from 'react'
import Layout from './components/Layout.jsx'
import Dashboard from './components/Dashboard.jsx'
import Ingredients from './components/Ingredients.jsx'
import Suppliers from './components/Suppliers.jsx'
import Procurement from './components/Procurement.jsx'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const pages = {
    dashboard: <Dashboard />,
    ingredients: <Ingredients />,
    suppliers: <Suppliers />,
    procurement: <Procurement />,
  }

  return (
    <Layout currentPage={currentPage} onPageChange={setCurrentPage}>
      {pages[currentPage] || pages.dashboard}
    </Layout>
  )
}

export default App
