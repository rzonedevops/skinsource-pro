import json
import os
import tempfile
from datetime import datetime, timedelta

import pytest

from src.main import app
from src.models import db, User, Ingredient, Supplier, SupplierIngredient


@pytest.fixture()
def client():
    db_fd, db_path = tempfile.mkstemp()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    )

    with app.app_context():
        db.drop_all()
        db.create_all()

        manager = User(username="manager", email="manager@example.com", role="manager")
        analyst = User(username="analyst", email="analyst@example.com", role="analyst")
        db.session.add_all([manager, analyst])

        ingredient = Ingredient(
            name="Vitamin C",
            inci_name="Ascorbic Acid",
            category="active",
            function="Antioxidant",
            sustainability_score=4.0,
            price_range_min=80,
            price_range_max=120,
            evidence_level="strong",
        )
        ingredient.set_regulatory_status({"FDA": "approved"})
        db.session.add(ingredient)

        supplier_a = Supplier(company_name="Supplier A", country="DE", quality_score=4.6, reliability_score=4.5, sustainability_score=4.2, price_competitiveness_score=4.1, verified_status=True)
        supplier_b = Supplier(company_name="Supplier B", country="FR", quality_score=4.0, reliability_score=3.8, sustainability_score=4.7, price_competitiveness_score=3.5, verified_status=True)
        supplier_a.calculate_overall_score()
        supplier_b.calculate_overall_score()
        db.session.add_all([supplier_a, supplier_b])
        db.session.flush()

        db.session.add_all([
            SupplierIngredient(supplier_id=supplier_a.id, ingredient_id=ingredient.id, price_per_kg=90, minimum_order_quantity=100, lead_time_days=10),
            SupplierIngredient(supplier_id=supplier_b.id, ingredient_id=ingredient.id, price_per_kg=95, minimum_order_quantity=100, lead_time_days=12),
        ])

        db.session.commit()

    with app.test_client() as test_client:
        yield test_client

    os.close(db_fd)
    os.unlink(db_path)
