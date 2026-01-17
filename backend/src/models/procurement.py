from datetime import datetime
import json
from src.models.user import db

class ProcurementRequest(db.Model):
    __tablename__ = 'procurement_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    
    # Request details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity_needed = db.Column(db.Float, nullable=False)  # in kg
    target_price = db.Column(db.Float, nullable=True)  # per kg
    delivery_date = db.Column(db.Date, nullable=True)
    
    # Specifications as JSON
    specifications = db.Column(db.Text, nullable=True)  # JSON string
    quality_requirements = db.Column(db.Text, nullable=True)  # JSON string
    
    # Status tracking
    status = db.Column(db.String(50), default='draft')  # draft, sent, received, awarded, completed, cancelled
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<ProcurementRequest {self.title}>'

    def to_dict(self):
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

class RFQResponse(db.Model):
    __tablename__ = 'rfq_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey('procurement_requests.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=False)
    
    # Response details
    quoted_price = db.Column(db.Float, nullable=False)  # per kg
    total_price = db.Column(db.Float, nullable=True)
    lead_time_days = db.Column(db.Integer, nullable=False)
    minimum_order_quantity = db.Column(db.Float, nullable=True)
    
    # Terms and conditions
    terms_conditions = db.Column(db.Text, nullable=True)
    payment_terms = db.Column(db.String(200), nullable=True)
    validity_days = db.Column(db.Integer, default=30)
    
    # Documents and certifications
    documents = db.Column(db.Text, nullable=True)  # JSON string with document URLs/paths
    coa_provided = db.Column(db.Boolean, default=False)
    msds_provided = db.Column(db.Boolean, default=False)
    
    # Response status
    status = db.Column(db.String(50), default='submitted')  # submitted, under_review, accepted, rejected
    notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    response_date = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<RFQResponse {self.procurement_request_id}-{self.supplier_id}>'

    def to_dict(self):
        documents_data = []
        
        try:
            if self.documents:
                documents_data = json.loads(self.documents)
        except:
            pass
            
        return {
            'id': self.id,
            'procurement_request_id': self.procurement_request_id,
            'supplier_id': self.supplier_id,
            'quoted_price': self.quoted_price,
            'total_price': self.total_price,
            'lead_time_days': self.lead_time_days,
            'minimum_order_quantity': self.minimum_order_quantity,
            'terms_conditions': self.terms_conditions,
            'payment_terms': self.payment_terms,
            'validity_days': self.validity_days,
            'documents': documents_data,
            'coa_provided': self.coa_provided,
            'msds_provided': self.msds_provided,
            'status': self.status,
            'notes': self.notes,
            'response_date': self.response_date.isoformat() if self.response_date else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None
        }

