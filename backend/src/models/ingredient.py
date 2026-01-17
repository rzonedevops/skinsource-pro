from datetime import datetime
import json

class Ingredient:
    pass
    __tablename__ = 'ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    inci_name = db.Column(db.String(200), nullable=True)  # International Nomenclature
    cas_number = db.Column(db.String(50), nullable=True)
    category = db.Column(db.String(100), nullable=False)  # active, emollient, preservative, etc.
    function = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    regulatory_status = db.Column(db.Text, nullable=True)  # JSON string
    sustainability_score = db.Column(db.Float, nullable=True)
    price_range_min = db.Column(db.Float, nullable=True)
    price_range_max = db.Column(db.Float, nullable=True)
    evidence_level = db.Column(db.String(50), nullable=True)  # strong, limited, emerging, none
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Ingredient {self.name}>'

    def to_dict(self):
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
        """Set regulatory status from dictionary"""
        self.regulatory_status = json.dumps(regulatory_dict)

    def get_regulatory_status(self):
        """Get regulatory status as dictionary"""
        if self.regulatory_status:
            try:
                return json.loads(self.regulatory_status)
            except:
                return {}
        return {}

