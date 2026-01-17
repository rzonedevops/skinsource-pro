import { useState, useEffect } from 'react'
import { 
  Search, 
  Filter, 
  Plus,
  Star,
  Leaf,
  Shield,
  DollarSign,
  Info
} from 'lucide-react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import '../App.css'

const Ingredients = () => {
  const [ingredients, setIngredients] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedEvidence, setSelectedEvidence] = useState('all')

  useEffect(() => {
    fetchIngredients()
  }, [])

  const fetchIngredients = async () => {
    try {
      const response = await fetch('/api/ingredients')
      const data = await response.json()
      setIngredients(data.ingredients || [])
    } catch (error) {
      console.error('Failed to fetch ingredients:', error)
      // Mock data for demo
      setIngredients([
        {
          id: 1,
          name: 'Vitamin C (L-Ascorbic Acid)',
          inci_name: 'Ascorbic Acid',
          category: 'active',
          function: 'Antioxidant, brightening, anti-aging',
          description: 'Pure L-Ascorbic Acid, the most potent form of Vitamin C for skincare applications.',
          sustainability_score: 4.2,
          price_range: { min: 80, max: 120 },
          evidence_level: 'strong',
          regulatory_status: { FDA: 'approved', EU: 'approved', COSMOS: 'approved' }
        },
        {
          id: 2,
          name: 'Hyaluronic Acid (High MW)',
          inci_name: 'Sodium Hyaluronate',
          category: 'moisturizer',
          function: 'Hydrating, plumping, moisture retention',
          description: 'High molecular weight hyaluronic acid for superior skin hydration and plumping effects.',
          sustainability_score: 4.5,
          price_range: { min: 400, max: 600 },
          evidence_level: 'strong',
          regulatory_status: { FDA: 'approved', EU: 'approved', COSMOS: 'approved' }
        },
        {
          id: 3,
          name: 'Niacinamide',
          inci_name: 'Niacinamide',
          category: 'active',
          function: 'Pore minimizing, oil control, brightening',
          description: 'Vitamin B3 derivative known for its pore-minimizing and oil-controlling properties.',
          sustainability_score: 4.0,
          price_range: { min: 20, max: 35 },
          evidence_level: 'strong',
          regulatory_status: { FDA: 'approved', EU: 'approved', COSMOS: 'approved' }
        },
        {
          id: 4,
          name: 'Bakuchiol',
          inci_name: 'Bakuchiol',
          category: 'active',
          function: 'Anti-aging, retinol alternative',
          description: 'Plant-based retinol alternative derived from Psoralea corylifolia with anti-aging benefits.',
          sustainability_score: 4.8,
          price_range: { min: 320, max: 450 },
          evidence_level: 'limited',
          regulatory_status: { FDA: 'approved', EU: 'approved', COSMOS: 'approved' }
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const filteredIngredients = ingredients.filter(ingredient => {
    const matchesSearch = ingredient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         ingredient.function.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || ingredient.category === selectedCategory
    const matchesEvidence = selectedEvidence === 'all' || ingredient.evidence_level === selectedEvidence
    
    return matchesSearch && matchesCategory && matchesEvidence
  })

  const getCategoryColor = (category) => {
    const colors = {
      active: 'bg-blue-100 text-blue-800',
      moisturizer: 'bg-green-100 text-green-800',
      emollient: 'bg-purple-100 text-purple-800',
      preservative: 'bg-red-100 text-red-800',
      other: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || colors.other
  }

  const getEvidenceIcon = (level) => {
    switch (level) {
      case 'strong':
        return <Star className="h-4 w-4 text-yellow-500" />
      case 'limited':
        return <Info className="h-4 w-4 text-blue-500" />
      default:
        return <Info className="h-4 w-4 text-gray-400" />
    }
  }

  const getSustainabilityColor = (score) => {
    if (score >= 4.5) return 'text-green-600'
    if (score >= 3.5) return 'text-yellow-600'
    return 'text-red-600'
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
          <h2 className="text-2xl font-bold text-gray-900">Ingredient Catalog</h2>
          <p className="text-gray-600">Discover and source skincare ingredients</p>
        </div>
        <Button className="mt-4 sm:mt-0">
          <Plus className="h-4 w-4 mr-2" />
          Add Ingredient
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search ingredients by name or function..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={selectedCategory} onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="moisturizer">Moisturizer</SelectItem>
            <SelectItem value="emollient">Emollient</SelectItem>
            <SelectItem value="preservative">Preservative</SelectItem>
          </SelectContent>
        </Select>
        <Select value={selectedEvidence} onValueChange={setSelectedEvidence}>
          <SelectTrigger className="w-full sm:w-48">
            <SelectValue placeholder="Evidence Level" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Evidence</SelectItem>
            <SelectItem value="strong">Strong</SelectItem>
            <SelectItem value="limited">Limited</SelectItem>
            <SelectItem value="emerging">Emerging</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Results */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredIngredients.map((ingredient) => (
          <Card key={ingredient.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">{ingredient.name}</CardTitle>
                  <CardDescription className="text-sm text-gray-500">
                    INCI: {ingredient.inci_name}
                  </CardDescription>
                </div>
                <Badge className={getCategoryColor(ingredient.category)}>
                  {ingredient.category}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">{ingredient.function}</p>
              
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-1">
                  {getEvidenceIcon(ingredient.evidence_level)}
                  <span className="text-gray-600">Evidence: {ingredient.evidence_level}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Leaf className={`h-4 w-4 ${getSustainabilityColor(ingredient.sustainability_score)}`} />
                  <span className={getSustainabilityColor(ingredient.sustainability_score)}>
                    {ingredient.sustainability_score}/5
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-1">
                  <DollarSign className="h-4 w-4 text-gray-400" />
                  <span className="text-gray-600">
                    ${ingredient.price_range.min}-${ingredient.price_range.max}/kg
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Shield className="h-4 w-4 text-green-500" />
                  <span className="text-green-600">Approved</span>
                </div>
              </div>

              <div className="pt-2">
                <Button variant="outline" className="w-full">
                  View Details
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredIngredients.length === 0 && (
        <div className="text-center py-12">
          <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No ingredients found</h3>
          <p className="text-gray-600">Try adjusting your search criteria or filters.</p>
        </div>
      )}
    </div>
  )
}

export default Ingredients

