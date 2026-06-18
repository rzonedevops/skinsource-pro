#!/usr/bin/env python3
"""Deterministic seed data for end-to-end procurement scenarios."""

import json
import os
import sys
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.main import app
from src.models import (
    db,
    User,
    Ingredient,
    Supplier,
    SupplierIngredient,
    ProcurementRequest,
    RFQRecipient,
    RFQResponse,
    ProcurementAward,
    ProcurementEvent,
)


BASE_TIME = datetime(2026, 1, 15, 10, 0, 0)


def create_users():
    users = [
        User(username="proc_manager", email="manager@skinsource.io", role="manager"),
        User(username="proc_analyst", email="analyst@skinsource.io", role="analyst"),
        User(username="proc_viewer", email="viewer@skinsource.io", role="viewer"),
    ]
    db.session.add_all(users)
    return users


def create_ingredients():
    ingredient_payloads = [
        {
            "name": "Vitamin C (L-Ascorbic Acid)",
            "inci_name": "Ascorbic Acid",
            "cas_number": "50-81-7",
            "category": "active",
            "function": "Antioxidant, brightening",
            "description": "High-purity L-Ascorbic Acid for premium serums",
            "sustainability_score": 4.1,
            "price_range_min": 78.0,
            "price_range_max": 125.0,
            "evidence_level": "strong",
            "regulatory_status": {"FDA": "approved", "EU": "approved", "COSMOS": "approved"},
        },
        {
            "name": "Niacinamide",
            "inci_name": "Niacinamide",
            "cas_number": "98-92-0",
            "category": "active",
            "function": "Pore minimizing, barrier support",
            "description": "Pharmaceutical grade niacinamide",
            "sustainability_score": 4.0,
            "price_range_min": 22.0,
            "price_range_max": 38.0,
            "evidence_level": "strong",
            "regulatory_status": {"FDA": "approved", "EU": "approved", "COSMOS": "approved"},
        },
        {
            "name": "Bakuchiol",
            "inci_name": "Bakuchiol",
            "cas_number": "10309-37-2",
            "category": "active",
            "function": "Retinol alternative",
            "description": "Plant-derived anti-aging active",
            "sustainability_score": 4.7,
            "price_range_min": 300.0,
            "price_range_max": 450.0,
            "evidence_level": "limited",
            "regulatory_status": {"FDA": "approved", "EU": "approved", "COSMOS": "approved"},
        },
    ]

    ingredients = []
    for payload in ingredient_payloads:
        ingredient = Ingredient(
            name=payload["name"],
            inci_name=payload["inci_name"],
            cas_number=payload["cas_number"],
            category=payload["category"],
            function=payload["function"],
            description=payload["description"],
            sustainability_score=payload["sustainability_score"],
            price_range_min=payload["price_range_min"],
            price_range_max=payload["price_range_max"],
            evidence_level=payload["evidence_level"],
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )
        ingredient.set_regulatory_status(payload["regulatory_status"])
        db.session.add(ingredient)
        ingredients.append(ingredient)

    return ingredients


def create_suppliers():
    supplier_payloads = [
        {
            "company_name": "ChemCorp International",
            "country": "Germany",
            "contact_email": "sales@chemcorp.example",
            "contact_phone": "+49-30-1234-6789",
            "website": "https://chemcorp.example",
            "certifications": ["ISO 9001", "COSMOS", "GMP"],
            "quality_score": 4.7,
            "reliability_score": 4.5,
            "sustainability_score": 4.2,
            "price_competitiveness_score": 4.0,
            "verified_status": True,
            "specialties": ["Actives", "Antioxidants"],
        },
        {
            "company_name": "BioNaturals Ltd",
            "country": "United Kingdom",
            "contact_email": "contact@bionaturals.example",
            "contact_phone": "+44-20-2244-7788",
            "website": "https://bionaturals.example",
            "certifications": ["COSMOS", "Ecocert", "Vegan"],
            "quality_score": 4.6,
            "reliability_score": 4.4,
            "sustainability_score": 4.8,
            "price_competitiveness_score": 3.7,
            "verified_status": True,
            "specialties": ["Botanical actives", "Organic extracts"],
        },
        {
            "company_name": "Pacific Ingredients Co",
            "country": "South Korea",
            "contact_email": "export@pacific.example",
            "contact_phone": "+82-2-1122-3344",
            "website": "https://pacific.example",
            "certifications": ["ISO 22716", "KFDA"],
            "quality_score": 4.3,
            "reliability_score": 4.2,
            "sustainability_score": 3.9,
            "price_competitiveness_score": 4.5,
            "verified_status": True,
            "specialties": ["Fermented ingredients", "K-Beauty actives"],
        },
    ]

    suppliers = []
    for payload in supplier_payloads:
        supplier = Supplier(
            company_name=payload["company_name"],
            country=payload["country"],
            contact_email=payload["contact_email"],
            contact_phone=payload["contact_phone"],
            website=payload["website"],
            quality_score=payload["quality_score"],
            reliability_score=payload["reliability_score"],
            sustainability_score=payload["sustainability_score"],
            price_competitiveness_score=payload["price_competitiveness_score"],
            verified_status=payload["verified_status"],
            created_at=BASE_TIME,
            updated_at=BASE_TIME,
        )
        supplier.set_certifications(payload["certifications"])
        supplier.specialties = json.dumps(payload["specialties"])
        supplier.geographic_regions = json.dumps([payload["country"]])
        supplier.calculate_overall_score()
        db.session.add(supplier)
        suppliers.append(supplier)

    return suppliers


def create_offerings(ingredients, suppliers):
    offerings = [
        (0, 0, 88.0, 120, 10),
        (0, 1, 92.0, 100, 14),
        (0, 2, 82.0, 250, 18),
        (1, 0, 27.0, 200, 7),
        (1, 1, 30.0, 120, 9),
        (1, 2, 24.5, 500, 16),
        (2, 0, 360.0, 50, 15),
        (2, 1, 345.0, 80, 18),
        (2, 2, 325.0, 120, 24),
    ]

    for ingredient_idx, supplier_idx, price_per_kg, moq, lead_time in offerings:
        db.session.add(
            SupplierIngredient(
                ingredient_id=ingredients[ingredient_idx].id,
                supplier_id=suppliers[supplier_idx].id,
                price_per_kg=price_per_kg,
                minimum_order_quantity=moq,
                lead_time_days=lead_time,
                availability_status="available",
                grade="Cosmetic",
                purity_percentage=98.5,
                created_at=BASE_TIME,
                last_updated=BASE_TIME,
            )
        )


def create_rfq_scenario(users, ingredients, suppliers):
    manager = users[0]
    analyst = users[1]

    request_item = ProcurementRequest(
        user_id=analyst.id,
        ingredient_id=ingredients[0].id,
        title="Vitamin C for anti-aging serum Q1",
        description="Need 500kg high-purity L-Ascorbic Acid for new line",
        quantity_needed=500,
        target_price=95,
        delivery_date=date(2026, 2, 28),
        specifications=json.dumps({"purity": "99%", "form": "powder"}),
        quality_requirements=json.dumps({"coa_required": True, "msds_required": True}),
        priority="high",
        status="awarded",
        created_at=BASE_TIME,
        updated_at=BASE_TIME,
        sent_at=BASE_TIME + timedelta(hours=6),
        deadline=BASE_TIME + timedelta(days=7),
        awarded_at=BASE_TIME + timedelta(days=5),
    )
    db.session.add(request_item)
    db.session.flush()

    recipients = []
    for idx, supplier in enumerate(suppliers):
        recipient = RFQRecipient(
            procurement_request_id=request_item.id,
            supplier_id=supplier.id,
            status="responded",
            invited_at=BASE_TIME + timedelta(hours=2),
            sent_at=BASE_TIME + timedelta(hours=6),
            responded_at=BASE_TIME + timedelta(days=idx + 2),
        )
        recipients.append(recipient)
        db.session.add(recipient)

    db.session.flush()

    response_specs = [
        (suppliers[0], recipients[0], 88.0, 10, 4.52, "accepted"),
        (suppliers[1], recipients[1], 92.0, 14, 4.28, "rejected"),
        (suppliers[2], recipients[2], 82.0, 18, 4.11, "rejected"),
    ]

    winning_response = None
    for supplier, recipient, quoted_price, lead_time, total_score, status in response_specs:
        response = RFQResponse(
            procurement_request_id=request_item.id,
            supplier_id=supplier.id,
            recipient_id=recipient.id,
            quoted_price=quoted_price,
            total_price=quoted_price * request_item.quantity_needed,
            lead_time_days=lead_time,
            minimum_order_quantity=100,
            payment_terms="Net 30",
            validity_days=30,
            coa_provided=True,
            msds_provided=True,
            status=status,
            price_score=4.5 if supplier.id == suppliers[0].id else 3.9,
            lead_time_score=4.6 if supplier.id == suppliers[0].id else 3.8,
            quality_score=supplier.quality_score,
            sustainability_score=supplier.sustainability_score,
            risk_score=4.1 if supplier.id == suppliers[0].id else 3.6,
            total_score=total_score,
            scoring_profile="balanced",
            response_date=BASE_TIME + timedelta(days=2),
            reviewed_at=BASE_TIME + timedelta(days=5),
        )
        db.session.add(response)
        if status == "accepted":
            winning_response = response

    db.session.flush()

    award = ProcurementAward(
        procurement_request_id=request_item.id,
        rfq_response_id=winning_response.id,
        supplier_id=winning_response.supplier_id,
        rationale="Best balance of lead time and quality while still under target price",
        decision_notes="Low risk and complete documentation",
        decided_by_user_id=manager.id,
        created_at=BASE_TIME + timedelta(days=5),
    )
    db.session.add(award)

    events = [
        ("request_created", "draft", None, BASE_TIME),
        ("status_transition", "draft", "sent", BASE_TIME + timedelta(hours=6)),
        ("response_received", "sent", "received", BASE_TIME + timedelta(days=2)),
        ("responses_scored", "received", "evaluated", BASE_TIME + timedelta(days=4)),
        ("request_awarded", "evaluated", "awarded", BASE_TIME + timedelta(days=5)),
    ]

    for event_type, from_status, to_status, event_time in events:
        db.session.add(
            ProcurementEvent(
                procurement_request_id=request_item.id,
                event_type=event_type,
                from_status=from_status,
                to_status=to_status,
                actor_user_id=manager.id,
                event_metadata=json.dumps({"seeded": True}),
                created_at=event_time,
            )
        )


def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = create_users()
        ingredients = create_ingredients()
        suppliers = create_suppliers()
        db.session.flush()

        create_offerings(ingredients, suppliers)
        create_rfq_scenario(users, ingredients, suppliers)

        db.session.commit()
        print("Seed completed with deterministic RFQ lifecycle data")


if __name__ == "__main__":
    seed_database()
