# SkinSource Pro API Reference Guide

## Overview

The SkinSource Pro API provides comprehensive access to all platform functionality through RESTful endpoints. This guide covers all available endpoints, request/response formats, and usage examples.

**Base URL:** `https://5000-is4zwuoambse3f5y253qv-f85324d8.manusvm.computer/api`

## Authentication

Currently, the API operates in demo mode without authentication requirements. For production deployment, implement:
- JWT token-based authentication
- API key management
- Role-based access control
- Rate limiting per user/organization

## Core API Endpoints

### Ingredients API

#### GET /ingredients
Retrieve the ingredient catalog with optional filtering and pagination.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20, max: 100)
- `category` (string): Filter by ingredient category
- `evidence_level` (string): Filter by evidence level (strong, moderate, limited)
- `min_price` (float): Minimum price per kg
- `max_price` (float): Maximum price per kg
- `search` (string): Search term for name or function

**Response Example:**
```json
{
  "ingredients": [
    {
      "id": 1,
      "name": "Retinol",
      "inci_name": "Retinol",
      "category": "active",
      "function": "Anti-aging, cell renewal, wrinkle reduction",
      "description": "Pure retinol for advanced anti-aging formulations.",
      "evidence_level": "strong",
      "sustainability_score": 3.8,
      "price_range": {
        "min": 800.0,
        "max": 1200.0
      },
      "regulatory_status": {
        "FDA": "approved",
        "EU": "restricted",
        "COSMOS": "not_approved"
      },
      "created_at": "2025-07-22T15:25:43.202684",
      "updated_at": "2025-07-22T15:25:43.202687"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 5,
    "has_next": false,
    "has_prev": false
  }
}
```

#### GET /ingredients/{id}
Retrieve detailed information for a specific ingredient.

**Path Parameters:**
- `id` (integer): Ingredient ID

**Response Example:**
```json
{
  "ingredient": {
    "id": 1,
    "name": "Retinol",
    "inci_name": "Retinol",
    "category": "active",
    "function": "Anti-aging, cell renewal, wrinkle reduction",
    "description": "Pure retinol for advanced anti-aging formulations.",
    "evidence_level": "strong",
    "sustainability_score": 3.8,
    "price_range": {
      "min": 800.0,
      "max": 1200.0
    },
    "regulatory_status": {
      "FDA": "approved",
      "EU": "restricted",
      "COSMOS": "not_approved"
    },
    "suppliers": [
      {
        "supplier_id": 1,
        "company_name": "ChemCorp International",
        "price_per_kg": 950.0,
        "lead_time_days": 21,
        "availability_status": "available"
      }
    ]
  }
}
```

### Suppliers API

#### GET /suppliers
Retrieve the supplier directory with filtering options.

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `per_page` (integer): Items per page (default: 20)
- `country` (string): Filter by supplier country
- `min_rating` (float): Minimum overall score (1-5)
- `specialties` (string): Filter by specialty areas
- `verified_only` (boolean): Show only verified suppliers

**Response Example:**
```json
{
  "suppliers": [
    {
      "id": 1,
      "company_name": "ChemCorp International",
      "country": "Germany",
      "contact_email": "sales@chemcorp.de",
      "phone": "+49-123-456-789",
      "website": "https://chemcorp.de",
      "specialties": ["Actives", "Antioxidants", "Peptides"],
      "certifications": ["ISO 9001", "COSMOS", "Halal"],
      "overall_score": 4.4,
      "quality_score": 4.8,
      "reliability_score": 4.6,
      "sustainability_score": 4.2,
      "price_competitiveness_score": 3.9,
      "verified_status": true,
      "geographic_regions": ["Europe", "North America"]
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 4,
    "has_next": false,
    "has_prev": false
  }
}
```

#### GET /suppliers/{id}
Retrieve detailed profile for a specific supplier.

**Path Parameters:**
- `id` (integer): Supplier ID

**Response Example:**
```json
{
  "supplier": {
    "id": 1,
    "company_name": "ChemCorp International",
    "country": "Germany",
    "contact_email": "sales@chemcorp.de",
    "phone": "+49-123-456-789",
    "website": "https://chemcorp.de",
    "specialties": ["Actives", "Antioxidants", "Peptides"],
    "certifications": ["ISO 9001", "COSMOS", "Halal"],
    "overall_score": 4.4,
    "performance_metrics": {
      "quality_score": 4.8,
      "reliability_score": 4.6,
      "sustainability_score": 4.2,
      "price_competitiveness_score": 3.9
    },
    "verified_status": true,
    "geographic_regions": ["Europe", "North America"],
    "ingredients_offered": [
      {
        "ingredient_id": 1,
        "ingredient_name": "Retinol",
        "price_per_kg": 950.0,
        "lead_time_days": 21,
        "minimum_order_quantity": 100
      }
    ]
  }
}
```

### Procurement API

#### GET /procurement/requests
Retrieve all procurement requests with filtering options.

**Query Parameters:**
- `status` (string): Filter by status (draft, sent, received, awarded, completed)
- `priority` (string): Filter by priority (high, medium, low)
- `date_from` (string): Start date filter (YYYY-MM-DD)
- `date_to` (string): End date filter (YYYY-MM-DD)

**Response Example:**
```json
{
  "requests": [
    {
      "id": 1,
      "title": "Vitamin C for Anti-Aging Serum",
      "description": "High-purity L-Ascorbic Acid for premium anti-aging serum formulation",
      "ingredient_name": "Vitamin C (L-Ascorbic Acid)",
      "quantity_needed": 500,
      "target_price": 95,
      "delivery_date": "2025-08-15",
      "status": "sent",
      "priority": "high",
      "responses_count": 3,
      "created_at": "2025-07-20T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 1,
    "per_page": 20,
    "total": 4
  }
}
```

#### POST /procurement/requests
Create a new procurement request.

**Request Body:**
```json
{
  "title": "Niacinamide for Sensitive Skin Formula",
  "description": "High-purity niacinamide for sensitive skin formulation",
  "ingredient_id": 3,
  "quantity_needed": 250,
  "target_price": 30.0,
  "delivery_date": "2025-09-01",
  "priority": "medium",
  "specifications": {
    "purity": "≥99%",
    "grade": "Pharmaceutical",
    "packaging": "25kg drums",
    "storage": "Cool, dry place"
  }
}
```

**Response Example:**
```json
{
  "request": {
    "id": 5,
    "title": "Niacinamide for Sensitive Skin Formula",
    "status": "draft",
    "created_at": "2025-07-22T15:30:00Z"
  },
  "message": "Procurement request created successfully"
}
```

### Intelligence API

#### POST /intelligence/discover-suppliers
Discover potential suppliers for specific ingredient requirements.

**Request Body:**
```json
{
  "ingredient_name": "Vitamin C",
  "region": "europe",
  "quantity": 500,
  "specifications": {
    "grade": "Pharmaceutical",
    "purity": "≥99%"
  }
}
```

**Response Example:**
```json
{
  "discovered_suppliers": [
    {
      "company_name": "European Botanicals Ltd",
      "country": "Netherlands",
      "specialties": ["Botanicals", "Organic Extracts"],
      "estimated_score": 4.5,
      "confidence_score": 0.87,
      "discovery_source": "industry_report",
      "estimated_lead_time": 30,
      "estimated_price_range": {
        "min": 188,
        "max": 258
      },
      "discovered_at": "2025-07-22T15:29:02.000448"
    }
  ],
  "total_found": 2,
  "search_criteria": {
    "ingredient_name": "Vitamin C",
    "region": "europe"
  }
}
```

#### GET /intelligence/market-intelligence/{category}
Get market intelligence for a specific ingredient category.

**Path Parameters:**
- `category` (string): Ingredient category (actives, moisturizers, etc.)

**Response Example:**
```json
{
  "category": "actives",
  "report_date": "2025-07-22T15:28:55.690919",
  "market_trends": {
    "price_trend": "decreasing",
    "demand_trend": "moderate",
    "supply_stability": "volatile",
    "innovation_activity": "low"
  },
  "price_forecast": {
    "next_quarter": "-6%",
    "next_year": "+25%",
    "confidence_level": "high"
  },
  "key_insights": [
    "Global demand for actives ingredients has increased by 25% this year",
    "New regulatory approvals in EU market expected to boost actives adoption",
    "Supply chain disruptions affecting 17% of actives suppliers",
    "Sustainability certifications becoming critical for actives procurement"
  ],
  "supplier_landscape": {
    "total_suppliers": 179,
    "new_entrants": 7,
    "market_concentration": "low",
    "geographic_distribution": {
      "asia": 45,
      "europe": 27,
      "americas": 17,
      "others": 9
    }
  },
  "recommendations": [
    "Consider diversifying supplier base to reduce risk",
    "Monitor regulatory changes in key markets",
    "Evaluate sustainable sourcing options",
    "Negotiate long-term contracts to lock in pricing"
  ]
}
```

#### POST /intelligence/optimize-pricing
Analyze pricing across suppliers and provide optimization recommendations.

**Request Body:**
```json
{
  "ingredient_id": 1,
  "quantity": 500
}
```

**Response Example:**
```json
{
  "ingredient_id": 1,
  "ingredient_name": "Retinol",
  "requested_quantity": 500,
  "analysis_date": "2025-07-22T15:30:00.000000",
  "market_overview": {
    "total_suppliers": 3,
    "price_range": {
      "min": 850.0,
      "max": 1150.0,
      "average": 975.0
    }
  },
  "supplier_comparison": [
    {
      "supplier_name": "ChemCorp International",
      "price_per_kg": 950.0,
      "total_cost": 475000.0,
      "lead_time_days": 21,
      "minimum_order_quantity": 100,
      "meets_moq": true,
      "supplier_score": 4.4,
      "value_score": 4.2
    }
  ],
  "optimization_recommendations": [
    "Best value option: ChemCorp International ($950.0/kg, score: 4.2)",
    "Consider negotiating bulk discounts for large quantities",
    "Fastest delivery: ChemCorp International (21 days)"
  ]
}
```

#### POST /intelligence/competitive-analysis
Perform competitive analysis across suppliers for multiple ingredients.

**Request Body:**
```json
{
  "ingredient_ids": [1, 2],
  "requirements": {
    "quantity": 500,
    "delivery_timeline": "Q3 2025",
    "quality_priority": "high"
  }
}
```

**Response Example:**
```json
{
  "competitive_analysis": [
    {
      "ingredient_id": 1,
      "ingredient_name": "Retinol",
      "supplier_analysis": [
        {
          "supplier_name": "ChemCorp International",
          "supplier_id": 1,
          "price_per_kg": 950.0,
          "lead_time_days": 21,
          "quality_score": 4.8,
          "reliability_score": 4.6,
          "sustainability_score": 4.2,
          "overall_score": 4.4,
          "competitive_score": 4.2,
          "strengths": ["Best overall value proposition", "Superior quality"],
          "weaknesses": []
        }
      ],
      "market_summary": {
        "total_suppliers": 3,
        "price_range": {
          "min": 850.0,
          "max": 1150.0
        },
        "average_lead_time": 23.5
      }
    }
  ],
  "analysis_date": "2025-07-22T15:30:00.000000",
  "requirements": {
    "quantity": 500,
    "delivery_timeline": "Q3 2025",
    "quality_priority": "high"
  }
}
```

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### Error Response Format
```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {
    "field": "Additional error details"
  }
}
```

## Rate Limiting

Current implementation:
- No rate limiting in demo mode
- Production recommendations:
  - 1000 requests per hour per API key
  - 100 requests per minute for intelligence endpoints
  - Burst allowance for authenticated users

## SDK and Integration Examples

### Python Example
```python
import requests

base_url = "https://5000-is4zwuoambse3f5y253qv-f85324d8.manusvm.computer/api"

# Get ingredients
response = requests.get(f"{base_url}/ingredients")
ingredients = response.json()

# Discover suppliers
discovery_data = {
    "ingredient_name": "Vitamin C",
    "region": "europe"
}
response = requests.post(f"{base_url}/intelligence/discover-suppliers", json=discovery_data)
suppliers = response.json()
```

### JavaScript Example
```javascript
const baseUrl = "https://5000-is4zwuoambse3f5y253qv-f85324d8.manusvm.computer/api";

// Get market intelligence
async function getMarketIntelligence(category) {
  const response = await fetch(`${baseUrl}/intelligence/market-intelligence/${category}`);
  return await response.json();
}

// Create procurement request
async function createProcurementRequest(requestData) {
  const response = await fetch(`${baseUrl}/procurement/requests`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData)
  });
  return await response.json();
}
```

## Webhook Support (Future)

Planned webhook events:
- `procurement.request.created`
- `procurement.request.updated`
- `supplier.response.received`
- `market.intelligence.updated`

## API Versioning

Current version: v1 (implicit)
Future versions will use URL versioning: `/api/v2/`

## Support and Documentation

- API documentation updates: Check this guide regularly
- Issue reporting: Use the platform's support system
- Feature requests: Submit through the feedback mechanism
- Community support: Access user forums and discussions

---

**Last Updated:** July 22, 2025  
**API Version:** 1.0  
**Base URL:** https://5000-is4zwuoambse3f5y253qv-f85324d8.manusvm.computer/api

