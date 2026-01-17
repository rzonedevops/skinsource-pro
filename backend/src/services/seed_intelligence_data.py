#!/usr/bin/env python3
"""
Seed script to populate the database with sample supplier-ingredient relationships
and enhanced data for intelligence features
"""

import os
import sys
import json
from datetime import datetime, timedelta
import random

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.user import db
from src.models import Ingredient, Supplier, SupplierIngredient
from src.main import app

def seed_supplier_ingredient_relationships():
    """Create realistic supplier-ingredient relationships with pricing and availability"""
    
    print("Creating supplier-ingredient relationships...")
    
    # Get all ingredients and suppliers
    ingredients = Ingredient.query.all()
    suppliers = Supplier.query.all()
    
    if not ingredients or not suppliers:
        print("No ingredients or suppliers found. Please run the main seed script first.")
        return
    
    # Clear existing relationships
    SupplierIngredient.query.delete()
    
    # Define ingredient-supplier compatibility matrix
    ingredient_supplier_matrix = {
        'Vitamin C (L-Ascorbic Acid)': ['ChemCorp International', 'Pacific Ingredients Co', 'Alpine Botanics'],
        'Hyaluronic Acid (High MW)': ['ChemCorp International', 'BioNaturals Ltd', 'Alpine Botanics'],
        'Niacinamide': ['ChemCorp International', 'Pacific Ingredients Co', 'BioNaturals Ltd'],
        'Bakuchiol': ['BioNaturals Ltd', 'Alpine Botanics', 'Pacific Ingredients Co']
    }
    
    # Create relationships
    for ingredient in ingredients:
        compatible_suppliers = ingredient_supplier_matrix.get(ingredient.name, [])
        
        # Add some random suppliers if not enough compatible ones
        if len(compatible_suppliers) < 2:
            available_suppliers = [s.company_name for s in suppliers if s.company_name not in compatible_suppliers]
            compatible_suppliers.extend(random.sample(available_suppliers, min(2, len(available_suppliers))))
        
        for supplier_name in compatible_suppliers:
            supplier = Supplier.query.filter_by(company_name=supplier_name).first()
            if not supplier:
                continue
            
            # Generate realistic pricing based on ingredient base price
            base_price = ingredient.price_range_min or 100
            price_variation = random.uniform(0.8, 1.3)  # ±30% variation
            price_per_kg = round(base_price * price_variation, 2)
            
            # Generate other attributes
            moq = random.choice([50, 100, 250, 500, 1000])
            lead_time = random.randint(7, 45)
            grade = random.choice(['Pharmaceutical', 'Cosmetic', 'Food Grade', 'Technical'])
            purity = random.uniform(95.0, 99.9)
            
            packaging_options = random.sample([
                '25kg drums',
                '50kg drums', 
                '200kg drums',
                '1kg bottles',
                '5kg containers',
                'Bulk tanker'
            ], random.randint(2, 4))
            
            storage_conditions = random.choice([
                'Store in cool, dry place',
                'Refrigerated storage required',
                'Store below 25°C',
                'Protect from light and moisture'
            ])
            
            shelf_life = random.choice([12, 18, 24, 36])
            
            # Create supplier-ingredient relationship
            relationship = SupplierIngredient(
                supplier_id=supplier.id,
                ingredient_id=ingredient.id,
                price_per_kg=price_per_kg,
                minimum_order_quantity=moq,
                lead_time_days=lead_time,
                availability_status=random.choice(['available', 'limited', 'on_request']),
                grade=grade,
                purity_percentage=round(purity, 1),
                packaging_options=json.dumps(packaging_options),
                storage_conditions=storage_conditions,
                shelf_life_months=shelf_life,
                last_updated=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            
            db.session.add(relationship)
    
    db.session.commit()
    print(f"Created {SupplierIngredient.query.count()} supplier-ingredient relationships")

def enhance_supplier_data():
    """Enhance supplier data with additional intelligence features"""
    
    print("Enhancing supplier data...")
    
    suppliers = Supplier.query.all()
    
    for supplier in suppliers:
        # Add more realistic certifications
        certifications = []
        cert_pool = [
            'ISO 9001', 'ISO 14001', 'ISO 22716', 'COSMOS', 'Ecocert', 
            'Halal', 'Kosher', 'USDA Organic', 'FDA Registered', 
            'GMP Certified', 'REACH Compliant', 'Vegan Society'
        ]
        
        # Each supplier gets 3-6 certifications
        num_certs = random.randint(3, 6)
        certifications = random.sample(cert_pool, num_certs)
        supplier.set_certifications(certifications)
        
        # Add geographic regions
        regions = []
        region_pool = ['North America', 'Europe', 'Asia-Pacific', 'Latin America', 'Middle East', 'Africa']
        
        # Primary region based on country
        if supplier.country in ['Germany', 'United Kingdom', 'Switzerland']:
            regions.append('Europe')
        elif supplier.country in ['South Korea', 'Japan', 'China']:
            regions.append('Asia-Pacific')
        elif supplier.country in ['USA', 'Canada']:
            regions.append('North America')
        
        # Add 1-2 additional regions
        additional_regions = [r for r in region_pool if r not in regions]
        regions.extend(random.sample(additional_regions, random.randint(1, 2)))
        
        supplier.geographic_regions = json.dumps(regions)
        
        # Update scores with more realistic values
        supplier.quality_score = round(random.uniform(3.5, 5.0), 1)
        supplier.reliability_score = round(random.uniform(3.2, 4.9), 1)
        supplier.sustainability_score = round(random.uniform(2.8, 4.8), 1)
        supplier.price_competitiveness_score = round(random.uniform(3.0, 4.5), 1)
        
        # Calculate overall score
        supplier.calculate_overall_score()
        
        # Set verification status (80% verified)
        supplier.verified_status = random.random() < 0.8
    
    db.session.commit()
    print(f"Enhanced data for {len(suppliers)} suppliers")

def create_sample_ingredients():
    """Create additional sample ingredients for testing"""
    
    print("Creating additional sample ingredients...")
    
    additional_ingredients = [
        {
            'name': 'Retinol',
            'inci_name': 'Retinol',
            'category': 'active',
            'function': 'Anti-aging, cell renewal, wrinkle reduction',
            'description': 'Pure retinol for advanced anti-aging formulations.',
            'sustainability_score': 3.8,
            'price_range_min': 800.0,
            'price_range_max': 1200.0,
            'evidence_level': 'strong',
            'regulatory_status': json.dumps({"FDA": "approved", "EU": "restricted", "COSMOS": "not_approved"})
        },
        {
            'name': 'Ceramide NP',
            'inci_name': 'Ceramide NP',
            'category': 'moisturizer',
            'function': 'Barrier repair, moisture retention, skin protection',
            'description': 'Synthetic ceramide for barrier function restoration.',
            'sustainability_score': 4.1,
            'price_range_min': 1500.0,
            'price_range_max': 2200.0,
            'evidence_level': 'strong',
            'regulatory_status': json.dumps({"FDA": "approved", "EU": "approved", "COSMOS": "approved"})
        },
        {
            'name': 'Kojic Acid',
            'inci_name': 'Kojic Acid',
            'category': 'active',
            'function': 'Skin brightening, melanin inhibition, anti-pigmentation',
            'description': 'Natural skin brightening agent derived from fungi.',
            'sustainability_score': 4.3,
            'price_range_min': 180.0,
            'price_range_max': 280.0,
            'evidence_level': 'moderate',
            'regulatory_status': json.dumps({"FDA": "approved", "EU": "restricted", "COSMOS": "approved"})
        },
        {
            'name': 'Squalane',
            'inci_name': 'Squalane',
            'category': 'emollient',
            'function': 'Moisturizing, skin conditioning, non-comedogenic',
            'description': 'Plant-derived squalane for lightweight moisturization.',
            'sustainability_score': 4.7,
            'price_range_min': 120.0,
            'price_range_max': 200.0,
            'evidence_level': 'strong',
            'regulatory_status': json.dumps({"FDA": "approved", "EU": "approved", "COSMOS": "approved"})
        },
        {
            'name': 'Zinc Oxide',
            'inci_name': 'Zinc Oxide',
            'category': 'active',
            'function': 'UV protection, anti-inflammatory, antimicrobial',
            'description': 'Mineral sunscreen and skin protectant.',
            'sustainability_score': 4.0,
            'price_range_min': 25.0,
            'price_range_max': 45.0,
            'evidence_level': 'strong',
            'regulatory_status': json.dumps({"FDA": "approved", "EU": "approved", "COSMOS": "approved"})
        }
    ]
    
    for ingredient_data in additional_ingredients:
        # Check if ingredient already exists
        existing = Ingredient.query.filter_by(name=ingredient_data['name']).first()
        if existing:
            continue
        
        ingredient = Ingredient(
            name=ingredient_data['name'],
            inci_name=ingredient_data['inci_name'],
            category=ingredient_data['category'],
            function=ingredient_data['function'],
            description=ingredient_data['description'],
            sustainability_score=ingredient_data['sustainability_score'],
            price_range_min=ingredient_data['price_range_min'],
            price_range_max=ingredient_data['price_range_max'],
            evidence_level=ingredient_data['evidence_level'],
            regulatory_status=ingredient_data['regulatory_status'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(ingredient)
    
    db.session.commit()
    print(f"Added {len(additional_ingredients)} additional ingredients")

def seed_intelligence_data():
    """Main function to seed all intelligence-related data"""
    
    print("Starting intelligence data seeding...")
    
    with app.app_context():
        # Create additional ingredients first
        create_sample_ingredients()
        
        # Enhance supplier data
        enhance_supplier_data()
        
        # Create supplier-ingredient relationships
        seed_supplier_ingredient_relationships()
        
        print("Intelligence data seeding completed successfully!")

if __name__ == '__main__':
    seed_intelligence_data()

