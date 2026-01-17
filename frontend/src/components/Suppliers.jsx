import { useState, useEffect } from 'react'
import { 
  Search, 
  MapPin, 
  Star,
  Globe,
  Mail,
  Phone,
  Award,
  TrendingUp,
  Filter
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import '../App.css'

const Suppliers = () => {
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCountry, setSelectedCountry] = useState('all')
  const [selectedRating, setSelectedRating] = useState('all')

  useEffect(() => {
    fetchSuppliers()
  }, [])

  const fetchSuppliers = async () => {
    try {
      const response = await fetch('/api/suppliers')
      const data = await response.json()
      setSuppliers(data.suppliers || [])
    } catch (error) {
      console.error('Failed to fetch suppliers:', error)
      // Mock data for demo
      setSuppliers([
        {
          id: 1,
          company_name: 'ChemCorp International',
          country: 'Germany',
          contact_email: 'sales@chemcorp.de',
          contact_phone: '+49-123-456-789',
          website: 'https://chemcorp.de',
          specialties: ['Actives', 'Antioxidants', 'Peptides'],
          certifications: ['ISO 9001', 'COSMOS', 'Halal'],
          scores: {
            quality: 4.8,
            reliability: 4.6,
            sustainability: 4.2,
            price_competitiveness: 3.9,
            overall: 4.4
          },
          verified_status: true,
          active_status: true
        },
        {
          id: 2,
          company_name: 'BioNaturals Ltd',
          country: 'United Kingdom',
          contact_email: 'info@bionaturals.co.uk',
          contact_phone: '+44-20-1234-5678',
          website: 'https://bionaturals.co.uk',
          specialties: ['Botanicals', 'Organic Extracts', 'Essential Oils'],
          certifications: ['Organic', 'COSMOS', 'Ecocert'],
          scores: {
            quality: 4.5,
            reliability: 4.7,
            sustainability: 4.9,
            price_competitiveness: 3.6,
            overall: 4.4
          },
          verified_status: true,
          active_status: true
        },
        {
          id: 3,
          company_name: 'Pacific Ingredients Co',
          country: 'South Korea',
          contact_email: 'export@pacific-ing.kr',
          contact_phone: '+82-2-1234-5678',
          website: 'https://pacific-ingredients.kr',
          specialties: ['Fermented Ingredients', 'K-Beauty Actives', 'Marine Extracts'],
          certifications: ['ISO 22716', 'KFDA', 'COSMOS'],
          scores: {
            quality: 4.6,
            reliability: 4.3,
            sustainability: 4.1,
            price_competitiveness: 4.2,
            overall: 4.3
          },
          verified_status: true,
          active_status: true
        },
        {
          id: 4,
          company_name: 'Alpine Botanics',
          country: 'Switzerland',
          contact_email: 'contact@alpine-botanics.ch',
          contact_phone: '+41-44-123-4567',
          website: 'https://alpine-botanics.ch',
          specialties: ['Alpine Extracts', 'Luxury Actives', 'Anti-Aging'],
          certifications: ['Swiss Quality', 'COSMOS', 'Vegan'],
          scores: {
            quality: 4.9,
            reliability: 4.8,
            sustainability: 4.6,
            price_competitiveness: 3.2,
            overall: 4.4
          },
          verified_status: true,
          active_status: true
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const filteredSuppliers = suppliers.filter(supplier => {
    const matchesSearch = supplier.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         supplier.specialties.some(s => s.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesCountry = selectedCountry === 'all' || supplier.country === selectedCountry
    const matchesRating = selectedRating === 'all' || 
                         (selectedRating === '4+' && supplier.scores.overall >= 4.0) ||
                         (selectedRating === '3+' && supplier.scores.overall >= 3.0)
    
    return matchesSearch && matchesCountry && matchesRating
  })

  const getScoreColor = (score) => {
    if (score >= 4.5) return 'text-green-600'
    if (score >= 4.0) return 'text-blue-600'
    if (score >= 3.5) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBg = (score) => {
    if (score >= 4.5) return 'bg-green-100'
    if (score >= 4.0) return 'bg-blue-100'
    if (score >= 3.5) return 'bg-yellow-100'
    return 'bg-red-100'
  }

  const renderStars = (score) => {
    const fullStars = Math.floor(score)
    const hasHalfStar = score % 1 >= 0.5
    
    return (
      <div className="flex items-center space-x-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            className={`h-4 w-4 ${
              i < fullStars 
                ? 'text-yellow-400 fill-current' 
                : i === fullStars && hasHalfStar
                ? 'text-yellow-400 fill-current'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="text-sm text-gray-600 ml-1">{score.toFixed(1)}</span>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Supplier Network</h2>
          <p className="text-gray-600">Manage and evaluate your supplier relationships</p>
        </div>
        <Button className="mt-4 sm:mt-0">
          <Search className="h-4 w-4 mr-2" />
          Find New Suppliers
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search suppliers by name or specialty..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedCountry} onValueChange={setSelectedCountry}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Country" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Countries</SelectItem>
            <SelectItem value="Germany">Germany</SelectItem>
            <SelectItem value="United Kingdom">United Kingdom</SelectItem>
            <SelectItem value="South Korea">South Korea</SelectItem>
            <SelectItem value="Switzerland">Switzerland</SelectItem>
          </SelectContent>
        </Select>
        <Select value={selectedRating} onValueChange={setSelectedRating}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Rating" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Ratings</SelectItem>
            <SelectItem value="4+">4+ Stars</SelectItem>
            <SelectItem value="3+">3+ Stars</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Suppliers Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredSuppliers.map((supplier) => (
          <Card key={supplier.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-xl flex items-center space-x-2">
                    <span>{supplier.company_name}</span>
                    {supplier.verified_status && (
                      <Award className="h-5 w-5 text-blue-500" />
                    )}
                  </CardTitle>
                  <CardDescription className="flex items-center space-x-1 mt-1">
                    <MapPin className="h-4 w-4" />
                    <span>{supplier.country}</span>
                  </CardDescription>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBg(supplier.scores.overall)} ${getScoreColor(supplier.scores.overall)}`}>
                  {supplier.scores.overall.toFixed(1)}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Contact Info */}
              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Mail className="h-4 w-4" />
                  <span>{supplier.contact_email}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Phone className="h-4 w-4" />
                  <span>{supplier.contact_phone}</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <Globe className="h-4 w-4" />
                  <a href={supplier.website} className="text-blue-600 hover:underline">
                    {supplier.website}
                  </a>
                </div>
              </div>

              {/* Specialties */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Specialties</h4>
                <div className="flex flex-wrap gap-1">
                  {supplier.specialties.map((specialty, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {specialty}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Certifications */}
              <div>
                <h4 className="text-sm font-medium text-gray-900 mb-2">Certifications</h4>
                <div className="flex flex-wrap gap-1">
                  {supplier.certifications.map((cert, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {cert}
                    </Badge>
                  ))}
                </div>
              </div>

              {/* Scores */}
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Quality</span>
                    <span className={`font-medium ${getScoreColor(supplier.scores.quality)}`}>
                      {supplier.scores.quality.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${(supplier.scores.quality / 5) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Reliability</span>
                    <span className={`font-medium ${getScoreColor(supplier.scores.reliability)}`}>
                      {supplier.scores.reliability.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-blue-500 h-2 rounded-full"
                      style={{ width: `${(supplier.scores.reliability / 5) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Sustainability</span>
                    <span className={`font-medium ${getScoreColor(supplier.scores.sustainability)}`}>
                      {supplier.scores.sustainability.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(supplier.scores.sustainability / 5) * 100}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Price</span>
                    <span className={`font-medium ${getScoreColor(supplier.scores.price_competitiveness)}`}>
                      {supplier.scores.price_competitiveness.toFixed(1)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                    <div 
                      className="bg-purple-500 h-2 rounded-full"
                      style={{ width: `${(supplier.scores.price_competitiveness / 5) * 100}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2 pt-2">
                <Button variant="outline" className="flex-1">
                  View Profile
                </Button>
                <Button className="flex-1">
                  Request Quote
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredSuppliers.length === 0 && (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No suppliers found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}
    </div>
  )
}

export default Suppliers

