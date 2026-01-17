import requests
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from src.models.user import db
from src.models import Supplier, Ingredient, SupplierIngredient

class SupplierIntelligenceService:
    """
    Service for intelligent supplier discovery, evaluation, and market analysis
    """
    
    def __init__(self):
        self.market_data_sources = [
            'chemical_industry_reports',
            'trade_publications',
            'supplier_directories',
            'market_intelligence_apis'
        ]
    
    def discover_suppliers(self, ingredient_name: str, region: str = None) -> List[Dict]:
        """
        Discover potential suppliers for a given ingredient using multiple sources
        """
        # Simulate intelligent supplier discovery
        discovered_suppliers = []
        
        # Mock supplier discovery based on ingredient type and region
        base_suppliers = [
            {
                'company_name': 'Global Ingredients Corp',
                'country': 'USA',
                'specialties': ['Actives', 'Antioxidants'],
                'estimated_score': 4.2,
                'discovery_source': 'trade_directory'
            },
            {
                'company_name': 'European Botanicals Ltd',
                'country': 'Netherlands',
                'specialties': ['Botanicals', 'Organic Extracts'],
                'estimated_score': 4.5,
                'discovery_source': 'industry_report'
            },
            {
                'company_name': 'Asian Specialty Chemicals',
                'country': 'Japan',
                'specialties': ['Fermented Ingredients', 'Marine Extracts'],
                'estimated_score': 4.1,
                'discovery_source': 'market_intelligence'
            },
            {
                'company_name': 'Nordic Natural Solutions',
                'country': 'Sweden',
                'specialties': ['Natural Actives', 'Sustainable Ingredients'],
                'estimated_score': 4.6,
                'discovery_source': 'sustainability_database'
            }
        ]
        
        # Filter by region if specified
        if region:
            region_mapping = {
                'europe': ['Netherlands', 'Sweden', 'Germany', 'Switzerland'],
                'asia': ['Japan', 'South Korea', 'China'],
                'americas': ['USA', 'Canada', 'Brazil']
            }
            target_countries = region_mapping.get(region.lower(), [])
            base_suppliers = [s for s in base_suppliers if s['country'] in target_countries]
        
        # Add discovery metadata
        for supplier in base_suppliers:
            supplier.update({
                'discovered_at': datetime.utcnow().isoformat(),
                'confidence_score': random.uniform(0.7, 0.95),
                'estimated_lead_time': random.randint(14, 45),
                'estimated_price_range': {
                    'min': random.randint(50, 200),
                    'max': random.randint(250, 500)
                }
            })
            discovered_suppliers.append(supplier)
        
        return discovered_suppliers
    
    def evaluate_supplier_performance(self, supplier_id: int) -> Dict:
        """
        Comprehensive supplier evaluation using multiple metrics
        """
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'error': 'Supplier not found'}
        
        # Calculate performance metrics
        evaluation = {
            'supplier_id': supplier_id,
            'company_name': supplier.company_name,
            'evaluation_date': datetime.utcnow().isoformat(),
            'metrics': {
                'quality_score': self._calculate_quality_score(supplier),
                'reliability_score': self._calculate_reliability_score(supplier),
                'sustainability_score': self._calculate_sustainability_score(supplier),
                'price_competitiveness': self._calculate_price_competitiveness(supplier),
                'innovation_index': self._calculate_innovation_index(supplier),
                'risk_assessment': self._assess_supplier_risk(supplier)
            },
            'recommendations': self._generate_recommendations(supplier),
            'market_position': self._analyze_market_position(supplier)
        }
        
        # Update supplier overall score
        overall_score = sum([
            evaluation['metrics']['quality_score'] * 0.25,
            evaluation['metrics']['reliability_score'] * 0.25,
            evaluation['metrics']['sustainability_score'] * 0.20,
            evaluation['metrics']['price_competitiveness'] * 0.15,
            evaluation['metrics']['innovation_index'] * 0.15
        ])
        
        supplier.overall_score = overall_score
        db.session.commit()
        
        evaluation['overall_score'] = overall_score
        return evaluation
    
    def optimize_pricing(self, ingredient_id: int, quantity: float) -> Dict:
        """
        Analyze pricing across suppliers and suggest optimization strategies
        """
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return {'error': 'Ingredient not found'}
        
        # Get all supplier offerings for this ingredient
        supplier_offerings = SupplierIngredient.query.filter_by(
            ingredient_id=ingredient_id
        ).all()
        
        if not supplier_offerings:
            return {'error': 'No supplier offerings found'}
        
        pricing_analysis = {
            'ingredient_id': ingredient_id,
            'ingredient_name': ingredient.name,
            'requested_quantity': quantity,
            'analysis_date': datetime.utcnow().isoformat(),
            'market_overview': {
                'total_suppliers': len(supplier_offerings),
                'price_range': {
                    'min': min([s.price_per_kg for s in supplier_offerings if s.price_per_kg]),
                    'max': max([s.price_per_kg for s in supplier_offerings if s.price_per_kg]),
                    'average': sum([s.price_per_kg for s in supplier_offerings if s.price_per_kg]) / len([s for s in supplier_offerings if s.price_per_kg])
                }
            },
            'supplier_comparison': [],
            'optimization_recommendations': []
        }
        
        # Analyze each supplier offering
        for offering in supplier_offerings:
            supplier = Supplier.query.get(offering.supplier_id)
            if not supplier or not offering.price_per_kg:
                continue
            
            total_cost = offering.price_per_kg * quantity
            meets_moq = quantity >= (offering.minimum_order_quantity or 0)
            
            supplier_analysis = {
                'supplier_name': supplier.company_name,
                'price_per_kg': offering.price_per_kg,
                'total_cost': total_cost,
                'lead_time_days': offering.lead_time_days,
                'minimum_order_quantity': offering.minimum_order_quantity,
                'meets_moq': meets_moq,
                'supplier_score': supplier.overall_score,
                'value_score': self._calculate_value_score(offering, supplier, quantity)
            }
            
            pricing_analysis['supplier_comparison'].append(supplier_analysis)
        
        # Sort by value score
        pricing_analysis['supplier_comparison'].sort(
            key=lambda x: x['value_score'], reverse=True
        )
        
        # Generate optimization recommendations
        pricing_analysis['optimization_recommendations'] = self._generate_pricing_recommendations(
            pricing_analysis['supplier_comparison'], quantity
        )
        
        return pricing_analysis
    
    def get_market_intelligence(self, ingredient_category: str) -> Dict:
        """
        Provide market intelligence and trends for ingredient categories
        """
        # Simulate market intelligence data
        market_data = {
            'category': ingredient_category,
            'report_date': datetime.utcnow().isoformat(),
            'market_trends': {
                'price_trend': random.choice(['increasing', 'stable', 'decreasing']),
                'demand_trend': random.choice(['high', 'moderate', 'low']),
                'supply_stability': random.choice(['stable', 'volatile', 'constrained']),
                'innovation_activity': random.choice(['high', 'moderate', 'low'])
            },
            'key_insights': [
                f"Global demand for {ingredient_category} ingredients has increased by {random.randint(5, 25)}% this year",
                f"New regulatory approvals in EU market expected to boost {ingredient_category} adoption",
                f"Supply chain disruptions affecting {random.randint(15, 35)}% of {ingredient_category} suppliers",
                f"Sustainability certifications becoming critical for {ingredient_category} procurement"
            ],
            'price_forecast': {
                'next_quarter': f"{random.choice(['+', '-'])}{random.randint(2, 15)}%",
                'next_year': f"{random.choice(['+', '-'])}{random.randint(5, 30)}%",
                'confidence_level': random.choice(['high', 'medium', 'low'])
            },
            'supplier_landscape': {
                'total_suppliers': random.randint(50, 200),
                'new_entrants': random.randint(3, 15),
                'market_concentration': random.choice(['high', 'medium', 'low']),
                'geographic_distribution': {
                    'asia': random.randint(30, 50),
                    'europe': random.randint(25, 40),
                    'americas': random.randint(15, 35),
                    'others': random.randint(5, 15)
                }
            },
            'recommendations': [
                "Consider diversifying supplier base to reduce risk",
                "Monitor regulatory changes in key markets",
                "Evaluate sustainable sourcing options",
                "Negotiate long-term contracts to lock in pricing"
            ]
        }
        
        return market_data
    
    def _calculate_quality_score(self, supplier: Supplier) -> float:
        """Calculate quality score based on certifications and track record"""
        base_score = 3.0
        
        # Add points for certifications
        if supplier.certifications:
            cert_data = json.loads(supplier.certifications) if isinstance(supplier.certifications, str) else supplier.certifications
            if isinstance(cert_data, list):
                base_score += len(cert_data) * 0.2
        
        # Add randomization for demo
        return min(5.0, base_score + random.uniform(-0.5, 1.0))
    
    def _calculate_reliability_score(self, supplier: Supplier) -> float:
        """Calculate reliability score based on delivery performance"""
        # Simulate based on supplier age and verification status
        base_score = 3.5 if supplier.verified_status else 3.0
        return min(5.0, base_score + random.uniform(-0.5, 1.0))
    
    def _calculate_sustainability_score(self, supplier: Supplier) -> float:
        """Calculate sustainability score"""
        return supplier.sustainability_score or random.uniform(3.0, 5.0)
    
    def _calculate_price_competitiveness(self, supplier: Supplier) -> float:
        """Calculate price competitiveness score"""
        return supplier.price_competitiveness_score or random.uniform(3.0, 5.0)
    
    def _calculate_innovation_index(self, supplier: Supplier) -> float:
        """Calculate innovation index based on R&D and new products"""
        # Simulate innovation score
        return random.uniform(2.5, 4.8)
    
    def _assess_supplier_risk(self, supplier: Supplier) -> Dict:
        """Assess various risk factors"""
        return {
            'financial_risk': random.choice(['low', 'medium', 'high']),
            'geographic_risk': random.choice(['low', 'medium', 'high']),
            'regulatory_risk': random.choice(['low', 'medium', 'high']),
            'supply_chain_risk': random.choice(['low', 'medium', 'high']),
            'overall_risk': random.choice(['low', 'medium', 'high'])
        }
    
    def _generate_recommendations(self, supplier: Supplier) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if supplier.overall_score < 3.5:
            recommendations.append("Consider additional due diligence before engagement")
        
        if not supplier.verified_status:
            recommendations.append("Recommend supplier verification and audit")
        
        if supplier.sustainability_score < 4.0:
            recommendations.append("Discuss sustainability improvement initiatives")
        
        recommendations.append("Monitor performance metrics quarterly")
        
        return recommendations
    
    def _analyze_market_position(self, supplier: Supplier) -> Dict:
        """Analyze supplier's market position"""
        return {
            'market_share': f"{random.randint(1, 15)}%",
            'competitive_position': random.choice(['leader', 'challenger', 'follower', 'niche']),
            'growth_trajectory': random.choice(['growing', 'stable', 'declining']),
            'differentiation': random.choice(['high', 'medium', 'low'])
        }
    
    def _calculate_value_score(self, offering: SupplierIngredient, supplier: Supplier, quantity: float) -> float:
        """Calculate overall value score combining price, quality, and reliability"""
        price_score = 5.0 - (offering.price_per_kg / 200)  # Normalize price
        quality_score = supplier.quality_score or 4.0
        reliability_score = supplier.reliability_score or 4.0
        
        # Weight the scores
        value_score = (price_score * 0.4 + quality_score * 0.3 + reliability_score * 0.3)
        
        # Adjust for MOQ compliance
        if quantity < (offering.minimum_order_quantity or 0):
            value_score *= 0.7
        
        return min(5.0, max(1.0, value_score))
    
    def _generate_pricing_recommendations(self, supplier_comparison: List[Dict], quantity: float) -> List[str]:
        """Generate pricing optimization recommendations"""
        recommendations = []
        
        if len(supplier_comparison) > 1:
            best_value = supplier_comparison[0]
            lowest_price = min(supplier_comparison, key=lambda x: x['price_per_kg'])
            
            if best_value != lowest_price:
                recommendations.append(
                    f"Best value option: {best_value['supplier_name']} "
                    f"(${best_value['price_per_kg']}/kg, score: {best_value['value_score']:.1f})"
                )
                recommendations.append(
                    f"Lowest price option: {lowest_price['supplier_name']} "
                    f"(${lowest_price['price_per_kg']}/kg)"
                )
            
            # Check for bulk discounts
            if quantity > 1000:
                recommendations.append("Consider negotiating bulk discounts for large quantities")
            
            # Lead time considerations
            fast_delivery = min(supplier_comparison, key=lambda x: x['lead_time_days'] or 999)
            recommendations.append(
                f"Fastest delivery: {fast_delivery['supplier_name']} "
                f"({fast_delivery['lead_time_days']} days)"
            )
        
        return recommendations

