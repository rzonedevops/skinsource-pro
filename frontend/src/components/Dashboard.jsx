import { useState, useEffect } from 'react'
import { 
  Search, 
  Users, 
  Package, 
  DollarSign,
  TrendingUp,
  Activity,
  Clock,
  CheckCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import '../App.css'

const Dashboard = () => {
  const [stats, setStats] = useState({
    statistics: {
      total_requests: 0,
      active_rfqs: 0,
      pending_orders: 0,
      completed_orders: 0,
      total_savings: 0,
      active_suppliers: 0
    },
    recent_requests: [],
    recent_responses: []
  })

  useEffect(() => {
    // Fetch dashboard data from API
    fetch('/api/procurement/dashboard')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Failed to fetch dashboard data:', err))
  }, [])

  const statCards = [
    {
      title: 'Active RFQs',
      value: stats.statistics.active_rfqs,
      icon: Search,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Suppliers',
      value: stats.statistics.active_suppliers,
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Pending Orders',
      value: stats.statistics.pending_orders,
      icon: Package,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    },
    {
      title: 'Total Savings',
      value: `$${(stats.statistics.total_savings / 1000).toFixed(1)}K`,
      icon: DollarSign,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-100'
    }
  ]

  const getStatusBadge = (status) => {
    const statusConfig = {
      draft: { variant: 'secondary', label: 'Draft' },
      sent: { variant: 'default', label: 'Sent' },
      received: { variant: 'default', label: 'Received' },
      awarded: { variant: 'default', label: 'Awarded' },
      completed: { variant: 'default', label: 'Completed' },
      high: { variant: 'destructive', label: 'High' },
      medium: { variant: 'default', label: 'Medium' },
      low: { variant: 'secondary', label: 'Low' }
    }
    
    const config = statusConfig[status] || { variant: 'secondary', label: status }
    return <Badge variant={config.variant}>{config.label}</Badge>
  }

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <Card key={index}>
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className={`p-2 rounded-lg ${stat.bgColor}`}>
                  <stat.icon className={`h-6 w-6 ${stat.color}`} />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Orders by Category</CardTitle>
            <CardDescription>Distribution of ingredient orders</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { category: 'Botanicals', percentage: 35, color: 'bg-blue-500' },
                { category: 'Emollients', percentage: 25, color: 'bg-green-500' },
                { category: 'Antioxidants', percentage: 20, color: 'bg-purple-500' },
                { category: 'Moisturizers', percentage: 15, color: 'bg-orange-500' },
                { category: 'Oils', percentage: 5, color: 'bg-red-500' }
              ].map((item, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${item.color}`} />
                  <span className="text-sm text-gray-600 flex-1">{item.category}</span>
                  <span className="text-sm font-medium">{item.percentage}%</span>
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${item.color}`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Cost by Category</CardTitle>
            <CardDescription>Spending breakdown by ingredient type</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { category: 'Botanicals', amount: '$45K', percentage: 40 },
                { category: 'Emollients', amount: '$32K', percentage: 30 },
                { category: 'Antioxidants', amount: '$18K', percentage: 20 },
                { category: 'Moisturizers', amount: '$8K', percentage: 7 },
                { category: 'Surfactants', amount: '$3K', percentage: 3 }
              ].map((item, index) => (
                <div key={index} className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">{item.category}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">{item.amount}</span>
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full bg-green-500"
                        style={{ width: `${item.percentage}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Recent Activity</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  company: 'Grant-Heaps',
                  action: 'Submitted RFQ',
                  time: '2 hours ago',
                  status: 'received'
                },
                {
                  company: 'Keeling, Ullrich and Spencer',
                  action: 'Updated pricing',
                  time: '1 hour ago',
                  status: 'updated'
                },
                {
                  company: 'Murray LLC',
                  action: 'Submitted RFQ',
                  time: '7 hours ago',
                  status: 'received'
                },
                {
                  company: 'Choy-Purdy',
                  action: 'Order completed',
                  time: '5 hours ago',
                  status: 'completed'
                }
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 rounded-lg bg-gray-50">
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{activity.company}</p>
                    <p className="text-sm text-gray-500">{activity.action}</p>
                  </div>
                  <div className="flex-shrink-0 text-sm text-gray-500">
                    {activity.time}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Clock className="h-5 w-5" />
              <span>Recent Requests</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  title: 'Vitamin C for Anti-Aging Serum',
                  quantity: '500kg',
                  status: 'sent',
                  priority: 'high'
                },
                {
                  title: 'Niacinamide for Pore Minimizer',
                  quantity: '200kg',
                  status: 'received',
                  priority: 'medium'
                },
                {
                  title: 'Bakuchiol for Natural Retinol Alternative',
                  quantity: '100kg',
                  status: 'draft',
                  priority: 'medium'
                }
              ].map((request, index) => (
                <div key={index} className="p-3 rounded-lg border border-gray-200">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{request.title}</p>
                      <p className="text-sm text-gray-500">Quantity: {request.quantity}</p>
                    </div>
                    <div className="flex flex-col items-end space-y-1">
                      {getStatusBadge(request.status)}
                      {getStatusBadge(request.priority)}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard

