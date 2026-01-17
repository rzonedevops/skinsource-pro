#!/usr/bin/env python3
"""
Seed data script for SkinSource Pro backend
Populates the database with sample ingredients, suppliers, and relationships
"""

import os
import sys
import json
from datetime import datetime, date

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.ingredient import Ingredient
from src.models.supplier import Supplier
from src.models.supplier_ingredient import SupplierIngredient
from src.models.procurement import ProcurementRequest, RFQResponse
from src.main import app

def create_sample_ingredients():
    """Create sample skincare ingredients"""
    ingredients_data = [
        {
            'name': 'Vitamin C (L-Ascorbic Acid)',
            'inci_name': 'Ascorbic Acid',
            'cas_number': '50-81-7',
            'category': 'active',
            'function': 'Antioxidant, brightening, anti-aging',
            'description': 'Pure L-Ascorbic Acid, the most potent form of Vitamin C for skincare applications.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'approved'},
            'sustainability_score': 4.2,
            'price_range_min': 80.0,
            'price_range_max': 120.0,
            'evidence_level': 'strong'
        },
        {
            'name': 'Hyaluronic Acid (High MW)',
            'inci_name': 'Sodium Hyaluronate',
            'cas_number': '9067-32-7',
            'category': 'moisturizer',
            'function': 'Hydrating, plumping, moisture retention',
            'description': 'High molecular weight hyaluronic acid for superior skin hydration and plumping effects.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'approved'},
            'sustainability_score': 4.5,
            'price_range_min': 400.0,
            'price_range_max': 600.0,
            'evidence_level': 'strong'
        },
        {
            'name': 'Niacinamide',
            'inci_name': 'Niacinamide',
            'cas_number': '98-92-0',
            'category': 'active',
            'function': 'Pore minimizing, oil control, brightening',
            'description': 'Vitamin B3 derivative known for its pore-minimizing and oil-controlling properties.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'approved'},
            'sustainability_score': 4.0,
            'price_range_min': 20.0,
            'price_range_max': 35.0,
            'evidence_level': 'strong'
        },
        {
            'name': 'Bakuchiol',
            'inci_name': 'Bakuchiol',
            'cas_number': '10309-37-2',
            'category': 'active',
            'function': 'Anti-aging, retinol alternative',
            'description': 'Plant-based retinol alternative derived from Psoralea corylifolia with anti-aging benefits.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'approved'},
            'sustainability_score': 4.8,
            'price_range_min': 320.0,
            'price_range_max': 450.0,
            'evidence_level': 'limited'
        },
        {
            'name': 'Glycerin',
            'inci_name': 'Glycerin',
            'cas_number': '56-81-5',
            'category': 'moisturizer',
            'function': 'Humectant, moisturizing',
            'description': 'Versatile humectant that attracts moisture to the skin.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'approved'},
            'sustainability_score': 4.3,
            'price_range_min': 2.0,
            'price_range_max': 5.0,
            'evidence_level': 'strong'
        },
        {
            'name': 'Salicylic Acid',
            'inci_name': 'Salicylic Acid',
            'cas_number': '69-72-7',
            'category': 'active',
            'function': 'Exfoliant, acne treatment, pore clearing',
            'description': 'Beta hydroxy acid (BHA) that penetrates pores to clear acne and exfoliate skin.',
            'regulatory_status': {'FDA': 'approved', 'EU': 'approved', 'COSMOS': 'restricted'},
            'sustainability_score': 3.8,
            'price_range_min': 15.0,
            'price_range_max': 25.0,
            'evidence_level': 'strong'
        }
    ]
    
    ingredients = []
    for data in ingredients_data:
        ingredient = Ingredient(
            name=data['name'],
            inci_name=data['inci_name'],
            cas_number=data['cas_number'],
            category=data['category'],
            function=data['function'],
            description=data['description'],
            sustainability_score=data['sustainability_score'],
            price_range_min=data['price_range_min'],
            price_range_max=data['price_range_max'],
            evidence_level=data['evidence_level']
        )
        ingredient.set_regulatory_status(data['regulatory_status'])
        ingredients.append(ingredient)
        db.session.add(ingredient)
    
    return ingredients

def create_sample_suppliers():
    """Create sample suppliers"""
    suppliers_data = [
        {
            'company_name': 'ChemCorp International',
            'contact_email': 'procurement@chemcorp.com',
            'contact_phone': '+49-30-12345678',
            'website': 'https://www.chemcorp.com',
            'address': 'Industriestraße 123, 10115 Berlin',
            'country': 'Germany',
            'certifications': ['ISO 9001:2015', 'COSMOS Organic', 'FDA Registered', 'REACH Compliant'],
            'geographic_regions': ['Europe', 'North America', 'Asia'],
            'specialties': ['Active ingredients', 'Pharmaceutical grade', 'Organic certified'],
            'quality_score': 4.8,
            'reliability_score': 4.6,
            'sustainability_score': 4.9,
            'price_competitiveness_score': 4.2,
            'verified_status': True
        },
        {
            'company_name': 'Global Ingredients Ltd',
            'contact_email': 'sales@globalingredients.com',
            'contact_phone': '+1-555-0123',
            'website': 'https://www.globalingredients.com',
            'address': '1234 Industrial Blvd, Newark, NJ 07102',
            'country': 'United States',
            'certifications': ['ISO 9001:2015', 'FDA Registered', 'NSF Certified'],
            'geographic_regions': ['North America', 'South America'],
            'specialties': ['Bulk ingredients', 'Custom formulations', 'Fast delivery'],
            'quality_score': 4.5,
            'reliability_score': 4.7,
            'sustainability_score': 4.1,
            'price_competitiveness_score': 4.6,
            'verified_status': True
        },
        {
            'company_name': 'PureChem Solutions',
            'contact_email': 'info@purechem.com',
            'contact_phone': '+86-21-12345678',
            'website': 'https://www.purechem.com',
            'address': '789 Chemical Park, Shanghai 200000',
            'country': 'China',
            'certifications': ['ISO 9001:2015', 'GMP Certified', 'REACH Compliant'],
            'geographic_regions': ['Asia', 'Europe', 'North America'],
            'specialties': ['Cost-effective solutions', 'Large volume orders', 'Custom synthesis'],
            'quality_score': 4.3,
            'reliability_score': 4.2,
            'sustainability_score': 3.8,
            'price_competitiveness_score': 4.8,
            'verified_status': True
        },
        {
            'company_name': 'BioNaturals Inc',
            'contact_email': 'contact@bionaturals.com',
            'contact_phone': '+33-1-23456789',
            'website': 'https://www.bionaturals.com',
            'address': '456 Rue de la Chimie, 75001 Paris',
            'country': 'France',
            'certifications': ['ECOCERT', 'COSMOS Natural', 'ISO 14001', 'Organic Certified'],
            'geographic_regions': ['Europe', 'North America'],
            'specialties': ['Natural ingredients', 'Sustainable sourcing', 'Botanical extracts'],
            'quality_score': 4.7,
            'reliability_score': 4.4,
            'sustainability_score': 4.9,
            'price_competitiveness_score': 3.9,
            'verified_status': True
        }
    ]
    
    suppliers = []
    for data in suppliers_data:
        supplier = Supplier(
            company_name=data['company_name'],
            contact_email=data['contact_email'],
            contact_phone=data['contact_phone'],
            website=data['website'],
            address=data['address'],
            country=data['country'],
            quality_score=data['quality_score'],
            reliability_score=data['reliability_score'],
            sustainability_score=data['sustainability_score'],
            price_competitiveness_score=data['price_competitiveness_score'],
            verified_status=data['verified_status']
        )
        
        supplier.set_certifications(data['certifications'])
        supplier.geographic_regions = json.dumps(data['geographic_regions'])
        supplier.specialties = json.dumps(data['specialties'])
        supplier.calculate_overall_score()
        
        suppliers.append(supplier)
        db.session.add(supplier)
    
    return suppliers

def create_supplier_ingredient_relationships(ingredients, suppliers):
    """Create relationships between suppliers and ingredients"""
    relationships_data = [
        # ChemCorp International (supplier 0)
        {'supplier_idx': 0, 'ingredient_idx': 0, 'price_per_kg': 85.0, 'lead_time_days': 7, 'grade': 'USP'},
        {'supplier_idx': 0, 'ingredient_idx': 1, 'price_per_kg': 450.0, 'lead_time_days': 14, 'grade': 'Cosmetic'},
        {'supplier_idx': 0, 'ingredient_idx': 2, 'price_per_kg': 25.0, 'lead_time_days': 5, 'grade': 'USP'},
        
        # Global Ingredients Ltd (supplier 1)
        {'supplier_idx': 1, 'ingredient_idx': 0, 'price_per_kg': 95.0, 'lead_time_days': 10, 'grade': 'Pharmaceutical'},
        {'supplier_idx': 1, 'ingredient_idx': 2, 'price_per_kg': 22.0, 'lead_time_days': 7, 'grade': 'Cosmetic'},
        {'supplier_idx': 1, 'ingredient_idx': 4, 'price_per_kg': 3.5, 'lead_time_days': 3, 'grade': 'USP'},
        {'supplier_idx': 1, 'ingredient_idx': 5, 'price_per_kg': 18.0, 'lead_time_days': 5, 'grade': 'USP'},
        
        # PureChem Solutions (supplier 2)
        {'supplier_idx': 2, 'ingredient_idx': 0, 'price_per_kg': 75.0, 'lead_time_days': 21, 'grade': 'Industrial'},
        {'supplier_idx': 2, 'ingredient_idx': 1, 'price_per_kg': 380.0, 'lead_time_days': 28, 'grade': 'Cosmetic'},
        {'supplier_idx': 2, 'ingredient_idx': 4, 'price_per_kg': 2.2, 'lead_time_days': 14, 'grade': 'Technical'},
        
        # BioNaturals Inc (supplier 3)
        {'supplier_idx': 3, 'ingredient_idx': 3, 'price_per_kg': 380.0, 'lead_time_days': 21, 'grade': 'Organic'},
        {'supplier_idx': 3, 'ingredient_idx': 4, 'price_per_kg': 4.2, 'lead_time_days': 10, 'grade': 'Organic'},
    ]
    
    for rel in relationships_data:
        supplier_ingredient = SupplierIngredient(
            supplier_id=suppliers[rel['supplier_idx']].id,
            ingredient_id=ingredients[rel['ingredient_idx']].id,
            price_per_kg=rel['price_per_kg'],
            lead_time_days=rel['lead_time_days'],
            grade=rel['grade'],
            minimum_order_quantity=25,  # Default 25kg minimum
            availability_status='available'
        )
        db.session.add(supplier_ingredient)

def create_sample_users():
    """Create sample users"""
    users_data = [
        {'username': 'john_doe', 'email': 'john.doe@beautyco.com'},
        {'username': 'sarah_chen', 'email': 'sarah.chen@skintech.com'},
        {'username': 'mike_johnson', 'email': 'mike.johnson@cosmeticsinc.com'}
    ]
    
    users = []
    for data in users_data:
        user = User(username=data['username'], email=data['email'])
        users.append(user)
        db.session.add(user)
    
    return users

def create_sample_procurement_requests(users, ingredients):
    """Create sample procurement requests"""
    requests_data = [
        {
            'user_idx': 0,
            'ingredient_idx': 0,  # Vitamin C
            'title': 'Vitamin C for Anti-Aging Serum',
            'description': 'Need high-quality L-Ascorbic Acid for new anti-aging serum line',
            'quantity_needed': 500.0,
            'target_price': 90.0,
            'delivery_date': date(2025, 9, 15),
            'status': 'sent',
            'priority': 'high'
        },
        {
            'user_idx': 1,
            'ingredient_idx': 2,  # Niacinamide
            'title': 'Niacinamide for Pore Minimizer',
            'description': 'Sourcing niacinamide for new pore minimizing product',
            'quantity_needed': 200.0,
            'target_price': 25.0,
            'delivery_date': date(2025, 8, 30),
            'status': 'received',
            'priority': 'medium'
        },
        {
            'user_idx': 2,
            'ingredient_idx': 3,  # Bakuchiol
            'title': 'Bakuchiol for Natural Retinol Alternative',
            'description': 'Looking for sustainable bakuchiol source for clean beauty line',
            'quantity_needed': 100.0,
            'target_price': 400.0,
            'delivery_date': date(2025, 10, 1),
            'status': 'draft',
            'priority': 'medium'
        }
    ]
    
    requests = []
    for data in requests_data:
        request = ProcurementRequest(
            user_id=users[data['user_idx']].id,
            ingredient_id=ingredients[data['ingredient_idx']].id,
            title=data['title'],
            description=data['description'],
            quantity_needed=data['quantity_needed'],
            target_price=data['target_price'],
            delivery_date=data['delivery_date'],
            status=data['status'],
            priority=data['priority']
        )
        
        if data['status'] == 'sent':
            request.sent_at = datetime.utcnow()
        
        requests.append(request)
        db.session.add(request)
    
    return requests

def seed_database():
    """Main function to seed the database"""
    print("Starting database seeding...")
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        db.drop_all()
        db.create_all()
        
        # Create sample data
        print("Creating sample users...")
        users = create_sample_users()
        
        print("Creating sample ingredients...")
        ingredients = create_sample_ingredients()
        
        print("Creating sample suppliers...")
        suppliers = create_sample_suppliers()
        
        # Commit to get IDs
        db.session.commit()
        
        print("Creating supplier-ingredient relationships...")
        create_supplier_ingredient_relationships(ingredients, suppliers)
        
        print("Creating sample procurement requests...")
        requests = create_sample_procurement_requests(users, ingredients)
        
        # Final commit
        db.session.commit()
        
        print(f"Database seeded successfully!")
        print(f"Created {len(users)} users")
        print(f"Created {len(ingredients)} ingredients")
        print(f"Created {len(suppliers)} suppliers")
        print(f"Created {len(requests)} procurement requests")

if __name__ == '__main__':
    seed_database()

