#!/usr/bin/env python3
"""Supplemental deterministic intelligence seed scenarios."""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.main import app
from src.models import (
    db,
    Ingredient,
    Supplier,
    SupplierIngredient,
    ProcurementRequest,
    RFQRecipient,
    RFQResponse,
    ProcurementEvent,
)


def _ensure_supplier(name, country, quality, reliability, sustainability, price_competitiveness, verified=True):
    supplier = Supplier.query.filter_by(company_name=name).first()
    if supplier:
        return supplier

    supplier = Supplier(
        company_name=name,
        country=country,
        contact_email=f"contact@{name.lower().replace(' ', '')}.example",
        quality_score=quality,
        reliability_score=reliability,
        sustainability_score=sustainability,
        price_competitiveness_score=price_competitiveness,
        verified_status=verified,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    supplier.set_certifications(["ISO 9001", "COSMOS"] if verified else ["ISO 9001"])
    supplier.specialties = json.dumps(["Actives", "Specialty chemicals"])
    supplier.calculate_overall_score()
    db.session.add(supplier)
    db.session.flush()
    return supplier


def _ensure_offering(supplier_id, ingredient_id, price, lead_time, moq):
    existing = SupplierIngredient.query.filter_by(supplier_id=supplier_id, ingredient_id=ingredient_id).first()
    if existing:
        existing.price_per_kg = price
        existing.lead_time_days = lead_time
        existing.minimum_order_quantity = moq
        existing.last_updated = datetime.utcnow()
        return existing

    offering = SupplierIngredient(
        supplier_id=supplier_id,
        ingredient_id=ingredient_id,
        price_per_kg=price,
        lead_time_days=lead_time,
        minimum_order_quantity=moq,
        availability_status="available",
        grade="Cosmetic",
        purity_percentage=98.0,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
    )
    db.session.add(offering)
    return offering


def create_additional_rfq_scenario():
    ingredient = Ingredient.query.filter_by(name="Niacinamide").first()
    if not ingredient:
        return

    req = ProcurementRequest.query.filter_by(title="Niacinamide replenishment Q2").first()
    if req:
        return

    analyst = Supplier.query.first()
    user_id = 1
    req = ProcurementRequest(
        user_id=user_id,
        ingredient_id=ingredient.id,
        title="Niacinamide replenishment Q2",
        description="Replenishment RFQ for pore-minimizer line",
        quantity_needed=800,
        target_price=29,
        status="received",
        priority="medium",
        created_at=datetime.utcnow() - timedelta(days=10),
        sent_at=datetime.utcnow() - timedelta(days=9),
        deadline=datetime.utcnow() - timedelta(days=2),
    )
    db.session.add(req)
    db.session.flush()

    supplier_a = _ensure_supplier("Aurora Actives", "Netherlands", 4.4, 4.2, 4.6, 3.8)
    supplier_b = _ensure_supplier("Vertex Materials", "India", 4.1, 3.9, 3.6, 4.4, verified=False)

    _ensure_offering(supplier_a.id, ingredient.id, 28.5, 11, 100)
    _ensure_offering(supplier_b.id, ingredient.id, 25.0, 26, 500)

    recipient_a = RFQRecipient(
        procurement_request_id=req.id,
        supplier_id=supplier_a.id,
        status="responded",
        invited_at=req.created_at,
        sent_at=req.sent_at,
        responded_at=req.sent_at + timedelta(days=2),
        last_reminder_at=req.deadline - timedelta(days=1),
    )
    recipient_b = RFQRecipient(
        procurement_request_id=req.id,
        supplier_id=supplier_b.id,
        status="sent",
        invited_at=req.created_at,
        sent_at=req.sent_at,
        last_reminder_at=req.deadline - timedelta(days=1),
    )
    db.session.add_all([recipient_a, recipient_b])
    db.session.flush()

    response = RFQResponse(
        procurement_request_id=req.id,
        supplier_id=supplier_a.id,
        recipient_id=recipient_a.id,
        quoted_price=28.5,
        total_price=22800,
        lead_time_days=11,
        minimum_order_quantity=100,
        status="submitted",
        price_score=4.2,
        lead_time_score=4.3,
        quality_score=4.4,
        sustainability_score=4.6,
        risk_score=4.1,
        total_score=4.31,
        scoring_profile="balanced",
        response_date=req.sent_at + timedelta(days=2),
    )
    db.session.add(response)

    db.session.add(
        ProcurementEvent(
            procurement_request_id=req.id,
            event_type="overdue_detected",
            from_status="sent",
            to_status="received",
            actor_user_id=user_id,
            event_metadata=json.dumps({"reason": "deadline_passed_without_full_responses"}),
            created_at=datetime.utcnow() - timedelta(days=1),
        )
    )


def seed_intelligence_data():
    with app.app_context():
        create_additional_rfq_scenario()
        db.session.commit()
        print("Supplemental intelligence seed data applied")


if __name__ == "__main__":
    seed_intelligence_data()
