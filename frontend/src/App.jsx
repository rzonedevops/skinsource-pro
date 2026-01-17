import { useState } from 'react'
import Layout from './components/Layout.jsx'
import Dashboard from './components/Dashboard.jsx'
import Ingredients from './components/Ingredients.jsx'
import Suppliers from './components/Suppliers.jsx'
import Procurement from './components/Procurement.jsx'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />
      case 'ingredients':
        return <Ingredients />
      case 'suppliers':
        return <Suppliers />
      case 'procurement':
        return <Procurement />
      case 'reports':
        return (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Reports & Analytics</h3>
            <p className="text-gray-600">Advanced reporting features coming soon.</p>
          </div>
        )
      default:
        return <Dashboard />
    }
  }

  return (
    <Layout currentPage={currentPage} onPageChange={setCurrentPage}>
      {renderPage()}
    </Layout>
  )
}

export default App
