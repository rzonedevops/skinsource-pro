# Import datetime at module level
from datetime import datetime
from src.models.user import db, User

# Define all models here to avoid circular imports
class Ingredient(db.Model):
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inci_name = db.Column(db.String(200), nullable=True)
    cas_number = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(100), nullable=False)
    function = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    regulatory_status = db.Column(db.Text, nullable=True)
    sustainability_score = db.Column(db.Float, nullable=True)
    price_range_min = db.Column(db.Float, nullable=True)
    price_range_max = db.Column(db.Float, nullable=True)
    evidence_level = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Ingredient {self.name}>'

    def to_dict(self):
        import json
        regulatory_data = {}
        if self.regulatory_status:
            try:
                regulatory_data = json.loads(self.regulatory_status)
            except:
                regulatory_data = {}
                
        return {
            'id': self.id,
            'name': self.name,
            'inci_name': self.inci_name,
            'cas_number': self.cas_number,
            'category': self.category,
            'function': self.function,
            'description': self.description,
            'regulatory_status': regulatory_data,
            'sustainability_score': self.sustainability_score,
            'price_range': {
                'min': self.price_range_min,
                'max': self.price_range_max
            },
            'evidence_level': self.evidence_level,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_regulatory_status(self, regulatory_dict):
        import json
        self.regulatory_status = json.dumps(regulatory_dict)

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    contact_info = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    geographic_regions = db.Column(db.Text, nullable=True)
    specialties = db.Column(db.Text, nullable=True)
    quality_score = db.Column(db.Float, default=0.0)
    reliability_score = db.Column(db.Float, default=0.0)
    sustainability_score = db.Column(db.Float, default=0.0)
    price_competitiveness_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    verified_status = db.Column(db.Boolean, default=False)
    active_status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.company_name}>'

    def to_dict(self):
        import json
        contact_data = {}
        certifications_data = []
        regions_data = []
        specialties_data = []
        
        try:
            if self.contact_info:
                contact_data = json.loads(self.contact_info)
            if self.certifications:
                certifications_data = json.loads(self.certifications)
            if self.geographic_regions:
                regions_data = json.loads(self.geographic_regions)
            if self.specialties:
                specialties_data = json.loads(self.specialties)
        except:
            pass
                
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'website': self.website,
            'address': self.address,
            'country': self.country,
            'contact_info': contact_data,
            'certifications': certifications_data,
            'geographic_regions': regions_data,
            'specialties': specialties_data,
            'scores': {
                'quality': self.quality_score,
                'reliability': self.reliability_score,
                'sustainability': self.sustainability_score,
                'price_competitiveness': self.price_competitiveness_score,
                'overall': self.overall_score
            },
            'verified_status': self.verified_status,
            'active_status': self.active_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def set_certifications(self, certifications_list):
        import json
        self.certifications = json.dumps(certifications_list)

    def calculate_overall_score(self):
        scores = [
            self.quality_score or 0,
            self.reliability_score or 0,
            self.sustainability_score or 0,
            self.price_competitiveness_score or 0
        ]
        self.overall_score = sum(scores) / len(scores) if scores else 0
        return self.overall_score

class SupplierIngredient(db.Model):
    __tablename__ = 'supplier_ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    price_per_kg = db.Column(db.Float, nullable=True)
    minimum_order_quantity = db.Column(db.Integer, nullable=True)
    lead_time_days = db.Column(db.Integer, nullable=True)
    availability_status = db.Column(db.String(50), default='available')
    grade = db.Column(db.String(100), nullable=True)
    purity_percentage = db.Column(db.Float, nullable=True)
    packaging_options = db.Column(db.Text, nullable=True)
    storage_conditions = db.Column(db.String(200), nullable=True)
    shelf_life_months = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SupplierIngredient {self.supplier_id}-{self.ingredient_id}>'

    def to_dict(self):
        import json
        packaging_data = []
        try:
            if self.packaging_options:
                packaging_data = json.loads(self.packaging_options)
        except:
            pass
            
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'ingredient_id': self.ingredient_id,
            'price_per_kg': self.price_per_kg,
            'minimum_order_quantity': self.minimum_order_quantity,
            'lead_time_days': self.lead_time_days,
            'availability_status': self.availability_status,
            'grade': self.grade,
            'purity_percentage': self.purity_percentage,
            'packaging_options': packaging_data,
            'storage_conditions': self.storage_conditions,
            'shelf_life_months': self.shelf_life_months,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProcurementRequest(db.Model):
    __tablename__ = 'procurement_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity_needed = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float, nullable=True)
    delivery_date = db.Column(db.Date, nullable=True)
    specifications = db.Column(db.Text, nullable=True)
    quality_requirements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='draft')
    priority = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ProcurementRequest {self.title}>'

    def to_dict(self):
        import json
        specs_data = {}
        quality_data = {}
        
        try:
            if self.specifications:
                specs_data = json.loads(self.specifications)
            if self.quality_requirements:
                quality_data = json.loads(self.quality_requirements)
        except:
            pass
            
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ingredient_id': self.ingredient_id,
            'title': self.title,
            'description': self.description,
            'quantity_needed': self.quantity_needed,
            'target_price': self.target_price,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'specifications': specs_data,
            'quality_requirements': quality_data,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'deadline': self.deadline.isoformat() if self.deadline else None
        }

