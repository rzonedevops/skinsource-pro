from datetime import datetime
from src.models.user import db

class SupplierIngredient(db.Model):
    __tablename__ = 'supplier_ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    
    # Pricing and availability
    price_per_kg = db.Column(db.Float, nullable=True)
    minimum_order_quantity = db.Column(db.Integer, nullable=True)  # in kg
    lead_time_days = db.Column(db.Integer, nullable=True)
    availability_status = db.Column(db.String(50), default='available')  # available, limited, out_of_stock
    
    # Quality specifications
    grade = db.Column(db.String(100), nullable=True)  # USP, pharmaceutical, cosmetic, etc.
    purity_percentage = db.Column(db.Float, nullable=True)
    
    # Additional specifications
    packaging_options = db.Column(db.Text, nullable=True)  # JSON string
    storage_conditions = db.Column(db.String(200), nullable=True)
    shelf_life_months = db.Column(db.Integer, nullable=True)
    
    # Tracking
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SupplierIngredient {self.supplier_id}-{self.ingredient_id}>'

    def to_dict(self):
        packaging_data = []
        try:
            if self.packaging_options:
                import json
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

    def set_packaging_options(self, packaging_list):
        """Set packaging options from list"""
        import json
        self.packaging_options = json.dumps(packaging_list)

    def get_packaging_options(self):
        """Get packaging options as list"""
        if self.packaging_options:
            try:
                import json
                return json.loads(self.packaging_options)
            except:
                return []
        return []

