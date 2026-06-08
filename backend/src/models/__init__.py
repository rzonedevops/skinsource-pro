import json
from datetime import datetime

from src.models.user import db, User


PROCUREMENT_STATUSES = [
    "draft",
    "sent",
    "received",
    "evaluated",
    "awarded",
    "completed",
    "cancelled",
]

RESPONSE_STATUSES = [
    "submitted",
    "under_review",
    "accepted",
    "rejected",
    "withdrawn",
    "expired",
]

RECIPIENT_STATUSES = ["targeted", "sent", "responded", "declined", "no_response"]


class Ingredient(db.Model):
    __tablename__ = "ingredients"

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    procurement_requests = db.relationship("ProcurementRequest", back_populates="ingredient")

    def to_dict(self):
        regulatory_data = {}
        if self.regulatory_status:
            try:
                regulatory_data = json.loads(self.regulatory_status)
            except (json.JSONDecodeError, TypeError):
                regulatory_data = {}

        return {
            "id": self.id,
            "name": self.name,
            "inci_name": self.inci_name,
            "cas_number": self.cas_number,
            "category": self.category,
            "function": self.function,
            "description": self.description,
            "regulatory_status": regulatory_data,
            "sustainability_score": self.sustainability_score,
            "price_range": {"min": self.price_range_min, "max": self.price_range_max},
            "evidence_level": self.evidence_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def set_regulatory_status(self, regulatory_dict):
        self.regulatory_status = json.dumps(regulatory_dict or {})


class Supplier(db.Model):
    __tablename__ = "suppliers"

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    supplier_ingredients = db.relationship("SupplierIngredient", back_populates="supplier", cascade="all, delete-orphan")
    rfq_recipients = db.relationship("RFQRecipient", back_populates="supplier", cascade="all, delete-orphan")
    rfq_responses = db.relationship("RFQResponse", back_populates="supplier", cascade="all, delete-orphan")

    def to_dict(self):
        def _safe_json(value, fallback):
            if not value:
                return fallback
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return fallback

        return {
            "id": self.id,
            "company_name": self.company_name,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "website": self.website,
            "address": self.address,
            "country": self.country,
            "contact_info": _safe_json(self.contact_info, {}),
            "certifications": _safe_json(self.certifications, []),
            "geographic_regions": _safe_json(self.geographic_regions, []),
            "specialties": _safe_json(self.specialties, []),
            "scores": {
                "quality": self.quality_score,
                "reliability": self.reliability_score,
                "sustainability": self.sustainability_score,
                "price_competitiveness": self.price_competitiveness_score,
                "overall": self.overall_score,
            },
            "verified_status": self.verified_status,
            "active_status": self.active_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def set_contact_info(self, contact_dict):
        self.contact_info = json.dumps(contact_dict or {})

    def set_certifications(self, certifications_list):
        self.certifications = json.dumps(certifications_list or [])

    def calculate_overall_score(self):
        scores = [
            self.quality_score or 0,
            self.reliability_score or 0,
            self.sustainability_score or 0,
            self.price_competitiveness_score or 0,
        ]
        self.overall_score = sum(scores) / len(scores) if scores else 0
        return self.overall_score


class SupplierIngredient(db.Model):
    __tablename__ = "supplier_ingredients"

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False, index=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False, index=True)
    price_per_kg = db.Column(db.Float, nullable=True)
    minimum_order_quantity = db.Column(db.Integer, nullable=True)
    lead_time_days = db.Column(db.Integer, nullable=True)
    availability_status = db.Column(db.String(50), default="available")
    grade = db.Column(db.String(100), nullable=True)
    purity_percentage = db.Column(db.Float, nullable=True)
    packaging_options = db.Column(db.Text, nullable=True)
    storage_conditions = db.Column(db.String(200), nullable=True)
    shelf_life_months = db.Column(db.Integer, nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    supplier = db.relationship("Supplier", back_populates="supplier_ingredients")
    ingredient = db.relationship("Ingredient")

    __table_args__ = (
        db.UniqueConstraint("supplier_id", "ingredient_id", name="uq_supplier_ingredient"),
    )

    def to_dict(self):
        packaging_data = []
        if self.packaging_options:
            try:
                packaging_data = json.loads(self.packaging_options)
            except (json.JSONDecodeError, TypeError):
                packaging_data = []

        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "ingredient_id": self.ingredient_id,
            "price_per_kg": self.price_per_kg,
            "minimum_order_quantity": self.minimum_order_quantity,
            "lead_time_days": self.lead_time_days,
            "availability_status": self.availability_status,
            "grade": self.grade,
            "purity_percentage": self.purity_percentage,
            "packaging_options": packaging_data,
            "storage_conditions": self.storage_conditions,
            "shelf_life_months": self.shelf_life_months,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def set_packaging_options(self, packaging_list):
        self.packaging_options = json.dumps(packaging_list or [])


class ProcurementRequest(db.Model):
    __tablename__ = "procurement_requests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    ingredient_id = db.Column(db.Integer, db.ForeignKey("ingredients.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity_needed = db.Column(db.Float, nullable=False)
    target_price = db.Column(db.Float, nullable=True)
    delivery_date = db.Column(db.Date, nullable=True)
    specifications = db.Column(db.Text, nullable=True)
    quality_requirements = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="draft", nullable=False, index=True)
    priority = db.Column(db.String(20), default="medium", nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True, index=True)
    awarded_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User")
    ingredient = db.relationship("Ingredient", back_populates="procurement_requests")
    rfq_recipients = db.relationship("RFQRecipient", back_populates="procurement_request", cascade="all, delete-orphan")
    rfq_responses = db.relationship("RFQResponse", back_populates="procurement_request", cascade="all, delete-orphan")
    awards = db.relationship("ProcurementAward", back_populates="procurement_request", cascade="all, delete-orphan")
    negotiations = db.relationship("NegotiationRound", back_populates="procurement_request", cascade="all, delete-orphan")
    events = db.relationship("ProcurementEvent", back_populates="procurement_request", cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('draft','sent','received','evaluated','awarded','completed','cancelled')",
            name="ck_procurement_status",
        ),
        db.CheckConstraint(
            "priority IN ('low','medium','high','urgent')",
            name="ck_procurement_priority",
        ),
        db.Index("idx_procurement_status_priority", "status", "priority"),
        db.Index("idx_procurement_ingredient_status", "ingredient_id", "status"),
    )

    def to_dict(self):
        def _safe_json(value, fallback):
            if not value:
                return fallback
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return fallback

        return {
            "id": self.id,
            "user_id": self.user_id,
            "ingredient_id": self.ingredient_id,
            "title": self.title,
            "description": self.description,
            "quantity_needed": self.quantity_needed,
            "target_price": self.target_price,
            "delivery_date": self.delivery_date.isoformat() if self.delivery_date else None,
            "specifications": _safe_json(self.specifications, {}),
            "quality_requirements": _safe_json(self.quality_requirements, {}),
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "awarded_at": self.awarded_at.isoformat() if self.awarded_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "is_overdue": bool(self.deadline and datetime.utcnow() > self.deadline and self.status not in {"completed", "cancelled"}),
        }


class RFQRecipient(db.Model):
    __tablename__ = "rfq_recipients"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False, index=True)
    status = db.Column(db.String(20), default="targeted", nullable=False, index=True)
    invited_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime, nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)
    last_reminder_at = db.Column(db.DateTime, nullable=True)

    procurement_request = db.relationship("ProcurementRequest", back_populates="rfq_recipients")
    supplier = db.relationship("Supplier", back_populates="rfq_recipients")
    response = db.relationship("RFQResponse", back_populates="recipient", uselist=False)

    __table_args__ = (
        db.UniqueConstraint("procurement_request_id", "supplier_id", name="uq_rfq_recipient"),
        db.CheckConstraint(
            "status IN ('targeted','sent','responded','declined','no_response')",
            name="ck_rfq_recipient_status",
        ),
        db.Index("idx_rfq_recipient_request_status", "procurement_request_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "procurement_request_id": self.procurement_request_id,
            "supplier_id": self.supplier_id,
            "status": self.status,
            "invited_at": self.invited_at.isoformat() if self.invited_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "last_reminder_at": self.last_reminder_at.isoformat() if self.last_reminder_at else None,
        }


class RFQResponse(db.Model):
    __tablename__ = "rfq_responses"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False, index=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("rfq_recipients.id"), nullable=True)
    quoted_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=True)
    lead_time_days = db.Column(db.Integer, nullable=False)
    minimum_order_quantity = db.Column(db.Float, nullable=True)
    terms_conditions = db.Column(db.Text, nullable=True)
    payment_terms = db.Column(db.String(200), nullable=True)
    validity_days = db.Column(db.Integer, default=30)
    documents = db.Column(db.Text, nullable=True)
    coa_provided = db.Column(db.Boolean, default=False)
    msds_provided = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="submitted", nullable=False, index=True)
    notes = db.Column(db.Text, nullable=True)
    price_score = db.Column(db.Float, nullable=True)
    lead_time_score = db.Column(db.Float, nullable=True)
    quality_score = db.Column(db.Float, nullable=True)
    sustainability_score = db.Column(db.Float, nullable=True)
    risk_score = db.Column(db.Float, nullable=True)
    total_score = db.Column(db.Float, nullable=True, index=True)
    scoring_profile = db.Column(db.String(30), nullable=True)
    response_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    procurement_request = db.relationship("ProcurementRequest", back_populates="rfq_responses")
    supplier = db.relationship("Supplier", back_populates="rfq_responses")
    recipient = db.relationship("RFQRecipient", back_populates="response")

    __table_args__ = (
        db.UniqueConstraint("procurement_request_id", "supplier_id", name="uq_rfq_response"),
        db.CheckConstraint(
            "status IN ('submitted','under_review','accepted','rejected','withdrawn','expired')",
            name="ck_rfq_response_status",
        ),
        db.Index("idx_rfq_response_request_status", "procurement_request_id", "status"),
    )

    def to_dict(self):
        documents_data = []
        if self.documents:
            try:
                documents_data = json.loads(self.documents)
            except (json.JSONDecodeError, TypeError):
                documents_data = []

        return {
            "id": self.id,
            "procurement_request_id": self.procurement_request_id,
            "supplier_id": self.supplier_id,
            "recipient_id": self.recipient_id,
            "quoted_price": self.quoted_price,
            "total_price": self.total_price,
            "lead_time_days": self.lead_time_days,
            "minimum_order_quantity": self.minimum_order_quantity,
            "terms_conditions": self.terms_conditions,
            "payment_terms": self.payment_terms,
            "validity_days": self.validity_days,
            "documents": documents_data,
            "coa_provided": self.coa_provided,
            "msds_provided": self.msds_provided,
            "status": self.status,
            "notes": self.notes,
            "score_breakdown": {
                "price": self.price_score,
                "lead_time": self.lead_time_score,
                "quality": self.quality_score,
                "sustainability": self.sustainability_score,
                "risk": self.risk_score,
                "total": self.total_score,
                "profile": self.scoring_profile,
            },
            "response_date": self.response_date.isoformat() if self.response_date else None,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


class ProcurementAward(db.Model):
    __tablename__ = "procurement_awards"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True)
    rfq_response_id = db.Column(db.Integer, db.ForeignKey("rfq_responses.id"), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False, index=True)
    rationale = db.Column(db.Text, nullable=False)
    decision_notes = db.Column(db.Text, nullable=True)
    decided_by_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    procurement_request = db.relationship("ProcurementRequest", back_populates="awards")
    rfq_response = db.relationship("RFQResponse")
    supplier = db.relationship("Supplier")
    decided_by = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "procurement_request_id": self.procurement_request_id,
            "rfq_response_id": self.rfq_response_id,
            "supplier_id": self.supplier_id,
            "rationale": self.rationale,
            "decision_notes": self.decision_notes,
            "decided_by_user_id": self.decided_by_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class NegotiationRound(db.Model):
    __tablename__ = "negotiation_rounds"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False, index=True)
    round_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="open")
    proposal = db.Column(db.Text, nullable=True)
    outcome = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    procurement_request = db.relationship("ProcurementRequest", back_populates="negotiations")
    supplier = db.relationship("Supplier")

    __table_args__ = (
        db.UniqueConstraint("procurement_request_id", "supplier_id", "round_number", name="uq_negotiation_round"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "procurement_request_id": self.procurement_request_id,
            "supplier_id": self.supplier_id,
            "round_number": self.round_number,
            "status": self.status,
            "proposal": json.loads(self.proposal) if self.proposal else {},
            "outcome": json.loads(self.outcome) if self.outcome else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
        }


class ProcurementEvent(db.Model):
    __tablename__ = "procurement_events"

    id = db.Column(db.Integer, primary_key=True)
    procurement_request_id = db.Column(db.Integer, db.ForeignKey("procurement_requests.id"), nullable=False, index=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)
    from_status = db.Column(db.String(20), nullable=True)
    to_status = db.Column(db.String(20), nullable=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    event_metadata = db.Column("metadata", db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    procurement_request = db.relationship("ProcurementRequest", back_populates="events")
    actor = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "event_type": self.event_type,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "actor_user_id": self.actor_user_id,
            "metadata": json.loads(self.event_metadata) if self.event_metadata else {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class IntelligenceAudit(db.Model):
    __tablename__ = "intelligence_audit"

    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(200), nullable=False, index=True)
    actor_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    remote_addr = db.Column(db.String(100), nullable=True)
    query_params = db.Column(db.Text, nullable=True)
    request_payload = db.Column(db.Text, nullable=True)
    response_status = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    actor = db.relationship("User")

    def to_dict(self):
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "actor_user_id": self.actor_user_id,
            "remote_addr": self.remote_addr,
            "query_params": json.loads(self.query_params) if self.query_params else {},
            "request_payload": json.loads(self.request_payload) if self.request_payload else {},
            "response_status": self.response_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = [
    "db",
    "User",
    "Ingredient",
    "Supplier",
    "SupplierIngredient",
    "ProcurementRequest",
    "RFQRecipient",
    "RFQResponse",
    "ProcurementAward",
    "NegotiationRound",
    "ProcurementEvent",
    "IntelligenceAudit",
    "PROCUREMENT_STATUSES",
    "RESPONSE_STATUSES",
    "RECIPIENT_STATUSES",
]
