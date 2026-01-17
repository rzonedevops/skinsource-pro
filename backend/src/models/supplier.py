from datetime import datetime
import json
from src.models.user import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    address = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    
    # Contact information as JSON
    contact_info = db.Column(db.Text, nullable=True)  # JSON string
    
    # Certifications and specialties as JSON
    certifications = db.Column(db.Text, nullable=True)  # JSON string
    geographic_regions = db.Column(db.Text, nullable=True)  # JSON string
    specialties = db.Column(db.Text, nullable=True)  # JSON string
    
    # Scoring metrics
    quality_score = db.Column(db.Float, default=0.0)
    reliability_score = db.Column(db.Float, default=0.0)
    sustainability_score = db.Column(db.Float, default=0.0)
    price_competitiveness_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    
    # Status and verification
    verified_status = db.Column(db.Boolean, default=False)
    active_status = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Supplier {self.company_name}>'

    def to_dict(self):
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

    def set_contact_info(self, contact_dict):
        """Set contact info from dictionary"""
        self.contact_info = json.dumps(contact_dict)

    def get_contact_info(self):
        """Get contact info as dictionary"""
        if self.contact_info:
            try:
                return json.loads(self.contact_info)
            except:
                return {}
        return {}

    def set_certifications(self, certifications_list):
        """Set certifications from list"""
        self.certifications = json.dumps(certifications_list)

    def get_certifications(self):
        """Get certifications as list"""
        if self.certifications:
            try:
                return json.loads(self.certifications)
            except:
                return []
        return []

    def calculate_overall_score(self):
        """Calculate overall score from individual metrics"""
        scores = [
            self.quality_score or 0,
            self.reliability_score or 0,
            self.sustainability_score or 0,
            self.price_competitiveness_score or 0
        ]
        self.overall_score = sum(scores) / len(scores) if scores else 0
        return self.overall_score

