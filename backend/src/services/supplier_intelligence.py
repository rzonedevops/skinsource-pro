from datetime import datetime, timedelta
from statistics import mean
from typing import Dict, List

from src.models import Supplier, Ingredient, SupplierIngredient, RFQResponse, RFQRecipient, ProcurementRequest


WEIGHTING_PROFILES = {
    "cost_first": {"cost": 0.45, "quality": 0.2, "sustainability": 0.15, "lead_time": 0.15, "risk": 0.05},
    "quality_first": {"cost": 0.15, "quality": 0.4, "sustainability": 0.15, "lead_time": 0.15, "risk": 0.15},
    "sustainability_first": {"cost": 0.15, "quality": 0.2, "sustainability": 0.4, "lead_time": 0.15, "risk": 0.1},
    "balanced": {"cost": 0.25, "quality": 0.25, "sustainability": 0.2, "lead_time": 0.15, "risk": 0.15},
}


class SupplierIntelligenceService:
    def discover_suppliers(self, ingredient_name: str, region: str = None) -> List[Dict]:
        query = SupplierIngredient.query.join(Ingredient).join(Supplier).filter(
            Ingredient.name.ilike(f"%{ingredient_name}%"),
            Supplier.active_status.is_(True),
        )

        if region:
            query = query.filter(Supplier.country.ilike(f"%{region}%"))

        offerings = query.order_by(Supplier.overall_score.desc(), SupplierIngredient.price_per_kg.asc()).all()
        return [
            {
                "supplier": offering.supplier.to_dict(),
                "offering": offering.to_dict(),
                "confidence_score": round(self._confidence_score(offering), 3),
                "discovered_at": datetime.utcnow().isoformat(),
                "explainability": {
                    "why": self._discovery_reasons(offering),
                    "data_points": {
                        "quality_score": offering.supplier.quality_score,
                        "reliability_score": offering.supplier.reliability_score,
                        "sustainability_score": offering.supplier.sustainability_score,
                        "quoted_price_hint": offering.price_per_kg,
                        "lead_time_days": offering.lead_time_days,
                    },
                },
            }
            for offering in offerings
        ]

    def evaluate_supplier_performance(self, supplier_id: int) -> Dict:
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {"error": "Supplier not found"}

        responses = RFQResponse.query.filter_by(supplier_id=supplier_id).all()
        on_time_responses = [response for response in responses if response.lead_time_days is not None and response.lead_time_days <= 21]
        accepted = [response for response in responses if response.status == "accepted"]

        metrics = {
            "quality_score": round(supplier.quality_score or 0, 3),
            "reliability_score": round(supplier.reliability_score or 0, 3),
            "sustainability_score": round(supplier.sustainability_score or 0, 3),
            "price_competitiveness": round(supplier.price_competitiveness_score or 0, 3),
            "response_acceptance_rate": round(len(accepted) / len(responses), 3) if responses else 0,
            "on_time_response_rate": round(len(on_time_responses) / len(responses), 3) if responses else 0,
            "risk_assessment": self._assess_supplier_risk(supplier),
        }

        overall_score = round(
            metrics["quality_score"] * 0.3
            + metrics["reliability_score"] * 0.25
            + metrics["sustainability_score"] * 0.2
            + metrics["price_competitiveness"] * 0.15
            + metrics["response_acceptance_rate"] * 5 * 0.1,
            3,
        )

        return {
            "supplier_id": supplier_id,
            "company_name": supplier.company_name,
            "evaluation_date": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "overall_score": overall_score,
            "recommendations": self._generate_recommendations(metrics),
            "explainability": {
                "primary_drivers": self._top_drivers(metrics),
                "tradeoffs": self._tradeoffs(metrics),
            },
        }

    def optimize_pricing(self, ingredient_id: int, quantity: float) -> Dict:
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return {"error": "Ingredient not found"}

        offerings = SupplierIngredient.query.filter_by(ingredient_id=ingredient_id).all()
        if not offerings:
            return {"error": "No supplier offerings found"}

        comparison = []
        for offering in offerings:
            supplier = offering.supplier
            cost = (offering.price_per_kg or 0) * quantity
            value_score = self._value_score(offering, supplier)
            comparison.append(
                {
                    "supplier_id": supplier.id,
                    "supplier_name": supplier.company_name,
                    "price_per_kg": offering.price_per_kg,
                    "total_cost": round(cost, 2),
                    "lead_time_days": offering.lead_time_days,
                    "minimum_order_quantity": offering.minimum_order_quantity,
                    "meets_moq": quantity >= (offering.minimum_order_quantity or 0),
                    "value_score": round(value_score, 3),
                }
            )

        comparison.sort(key=lambda item: item["value_score"], reverse=True)
        prices = [item["price_per_kg"] for item in comparison if item["price_per_kg"] is not None]

        return {
            "ingredient_id": ingredient_id,
            "ingredient_name": ingredient.name,
            "requested_quantity": quantity,
            "analysis_date": datetime.utcnow().isoformat(),
            "market_overview": {
                "total_suppliers": len(comparison),
                "price_range": {
                    "min": min(prices) if prices else None,
                    "max": max(prices) if prices else None,
                    "average": round(mean(prices), 2) if prices else None,
                },
            },
            "supplier_comparison": comparison,
            "optimization_recommendations": self._pricing_recommendations(comparison),
        }

    def get_market_intelligence(self, ingredient_category: str) -> Dict:
        ingredient_ids = [item.id for item in Ingredient.query.filter(Ingredient.category.ilike(f"%{ingredient_category}%")).all()]

        offerings = SupplierIngredient.query.filter(SupplierIngredient.ingredient_id.in_(ingredient_ids)).all() if ingredient_ids else []
        request_ids = [
            req.id for req in ProcurementRequest.query.filter(ProcurementRequest.ingredient_id.in_(ingredient_ids)).all()
        ] if ingredient_ids else []
        responses = RFQResponse.query.filter(RFQResponse.procurement_request_id.in_(request_ids)).all() if request_ids else []

        prices = [offering.price_per_kg for offering in offerings if offering.price_per_kg]
        lead_times = [offering.lead_time_days for offering in offerings if offering.lead_time_days]

        return {
            "category": ingredient_category,
            "report_date": datetime.utcnow().isoformat(),
            "market_trends": {
                "price_trend": self._trend_from_range(prices),
                "lead_time_trend": self._trend_from_range(lead_times, inverse=True),
                "supplier_depth": len({offering.supplier_id for offering in offerings}),
                "responses_observed": len(responses),
            },
            "key_insights": self._market_insights(offerings),
            "risk_signals": self._global_risk_signals(offerings),
        }

    def get_supplier_recommendations(self, ingredient_id: int, profile: str = "balanced", limit: int = 10) -> Dict:
        profile = profile if profile in WEIGHTING_PROFILES else "balanced"
        weights = WEIGHTING_PROFILES[profile]

        offerings = SupplierIngredient.query.filter_by(ingredient_id=ingredient_id).all()
        if not offerings:
            return {"recommendations": [], "profile": profile}

        prices = [offering.price_per_kg for offering in offerings if offering.price_per_kg]
        min_price = min(prices) if prices else None
        max_price = max(prices) if prices else None

        scored = []
        for offering in offerings:
            supplier = offering.supplier

            cost_score = self._normalize_cost_score(offering.price_per_kg, min_price, max_price)
            quality_score = min(5.0, supplier.quality_score or 0)
            sustainability_score = min(5.0, supplier.sustainability_score or 0)
            lead_time_score = self._normalize_lead_time_score(offering.lead_time_days)
            risk_score, risk_signals = self._supplier_risk_score(supplier, offering)

            total_score = (
                cost_score * weights["cost"]
                + quality_score * weights["quality"]
                + sustainability_score * weights["sustainability"]
                + lead_time_score * weights["lead_time"]
                + risk_score * weights["risk"]
            )

            scored.append(
                {
                    "supplier": supplier.to_dict(),
                    "offering": offering.to_dict(),
                    "recommendation_score": round(total_score, 3),
                    "explainability": {
                        "weights": weights,
                        "score_breakdown": {
                            "cost": round(cost_score, 3),
                            "quality": round(quality_score, 3),
                            "sustainability": round(sustainability_score, 3),
                            "lead_time": round(lead_time_score, 3),
                            "risk": round(risk_score, 3),
                        },
                        "why": self._recommendation_reasons(cost_score, quality_score, sustainability_score, lead_time_score),
                    },
                    "risk_signals": risk_signals,
                }
            )

        scored.sort(key=lambda item: item["recommendation_score"], reverse=True)
        return {"recommendations": scored[:limit], "profile": profile, "total_found": len(scored)}

    def _normalize_cost_score(self, price, min_price, max_price):
        if price is None:
            return 1.0
        if min_price is None or max_price is None or min_price == max_price:
            return 5.0
        relative = (max_price - price) / (max_price - min_price)
        return max(1.0, min(5.0, 1 + relative * 4))

    def _normalize_lead_time_score(self, lead_time_days):
        if lead_time_days is None:
            return 2.5
        if lead_time_days <= 7:
            return 5.0
        if lead_time_days <= 14:
            return 4.0
        if lead_time_days <= 21:
            return 3.0
        if lead_time_days <= 35:
            return 2.0
        return 1.0

    def _supplier_risk_score(self, supplier, offering):
        risk_signals = []

        peer_offering_count = SupplierIngredient.query.filter_by(ingredient_id=offering.ingredient_id).count()
        if peer_offering_count <= 1:
            risk_signals.append("single_source_dependency")

        if offering.lead_time_days and offering.lead_time_days > 30:
            risk_signals.append("long_lead_time_volatility")

        certifications = supplier.to_dict().get("certifications", [])
        if len(certifications) < 2 or not supplier.verified_status:
            risk_signals.append("low_verification_coverage")

        risk_score = max(1.0, 5 - (len(risk_signals) * 1.2))
        return risk_score, risk_signals

    def _confidence_score(self, offering):
        supplier = offering.supplier
        base = 0.5
        if supplier.verified_status:
            base += 0.2
        if offering.price_per_kg:
            base += 0.1
        if offering.lead_time_days:
            base += 0.1
        if supplier.overall_score:
            base += min(0.1, supplier.overall_score / 50)
        return min(0.99, base)

    def _discovery_reasons(self, offering):
        reasons = []
        supplier = offering.supplier
        if supplier.verified_status:
            reasons.append("Supplier is verified")
        if offering.lead_time_days and offering.lead_time_days <= 14:
            reasons.append("Competitive lead time")
        if offering.price_per_kg:
            reasons.append("Known market pricing available")
        if supplier.sustainability_score and supplier.sustainability_score >= 4:
            reasons.append("Strong sustainability score")
        return reasons

    def _generate_recommendations(self, metrics):
        recs = []
        if metrics["response_acceptance_rate"] < 0.3:
            recs.append("Renegotiate commercial terms to improve acceptance outcomes")
        if metrics["on_time_response_rate"] < 0.5:
            recs.append("Tighten SLA and escalation for response turnaround")
        if metrics["risk_assessment"]["overall_risk"] == "high":
            recs.append("Create secondary source strategy before awarding additional volume")
        if not recs:
            recs.append("Performance is stable; maintain monitoring cadence")
        return recs

    def _top_drivers(self, metrics):
        ranked = sorted(
            [
                ("quality", metrics["quality_score"]),
                ("reliability", metrics["reliability_score"]),
                ("sustainability", metrics["sustainability_score"]),
                ("price", metrics["price_competitiveness"]),
            ],
            key=lambda item: item[1],
            reverse=True,
        )
        return [item[0] for item in ranked[:2]]

    def _tradeoffs(self, metrics):
        tradeoffs = []
        if metrics["quality_score"] > metrics["price_competitiveness"] + 1:
            tradeoffs.append("Quality premium may increase unit cost")
        if metrics["sustainability_score"] > metrics["price_competitiveness"] + 1:
            tradeoffs.append("Sustainability preference may reduce low-cost options")
        return tradeoffs

    def _assess_supplier_risk(self, supplier):
        active_recipients = RFQRecipient.query.filter_by(supplier_id=supplier.id).count()
        certifications = supplier.to_dict().get("certifications", [])
        risk_level = "low"
        if active_recipients > 25 or len(certifications) < 2 or not supplier.verified_status:
            risk_level = "medium"
        if len(certifications) == 0 and not supplier.verified_status:
            risk_level = "high"

        return {
            "single_source_exposure": active_recipients <= 2,
            "verification_gap": not supplier.verified_status,
            "certification_coverage": len(certifications),
            "overall_risk": risk_level,
        }

    def _value_score(self, offering, supplier):
        cost = self._normalize_cost_score(offering.price_per_kg, offering.price_per_kg, offering.price_per_kg)
        quality = min(5.0, supplier.quality_score or 0)
        reliability = min(5.0, supplier.reliability_score or 0)
        lead_time = self._normalize_lead_time_score(offering.lead_time_days)
        return (cost * 0.25) + (quality * 0.3) + (reliability * 0.25) + (lead_time * 0.2)

    def _pricing_recommendations(self, comparison):
        if not comparison:
            return []

        recs = []
        best_value = comparison[0]
        recs.append(f"Best value supplier is {best_value['supplier_name']} (score {best_value['value_score']:.2f})")

        fast = sorted([item for item in comparison if item["lead_time_days"] is not None], key=lambda item: item["lead_time_days"])
        if fast:
            recs.append(f"Fastest lead time supplier is {fast[0]['supplier_name']} ({fast[0]['lead_time_days']} days)")

        low_price = sorted([item for item in comparison if item["price_per_kg"] is not None], key=lambda item: item["price_per_kg"])
        if low_price:
            recs.append(f"Lowest unit price is offered by {low_price[0]['supplier_name']} (${low_price[0]['price_per_kg']}/kg)")

        return recs

    def _trend_from_range(self, values, inverse=False):
        if not values:
            return "unknown"
        spread = max(values) - min(values)
        avg = mean(values)
        ratio = spread / avg if avg else 0
        if ratio < 0.08:
            return "stable"
        if ratio < 0.2:
            return "moderate"
        return "volatile" if not inverse else "constrained"

    def _market_insights(self, offerings):
        if not offerings:
            return ["No active market data for this category"]

        lead_times = [offering.lead_time_days for offering in offerings if offering.lead_time_days]
        prices = [offering.price_per_kg for offering in offerings if offering.price_per_kg]

        insights = [f"{len({offering.supplier_id for offering in offerings})} active suppliers are available"]
        if prices:
            insights.append(f"Observed unit pricing spans ${min(prices):.2f} to ${max(prices):.2f} per kg")
        if lead_times:
            insights.append(f"Typical lead times range {min(lead_times)}-{max(lead_times)} days")
        return insights

    def _global_risk_signals(self, offerings):
        if not offerings:
            return []

        signals = []
        supplier_count = len({offering.supplier_id for offering in offerings})
        if supplier_count <= 2:
            signals.append("single_source_dependency")

        long_lead = [offering for offering in offerings if (offering.lead_time_days or 0) > 30]
        if long_lead:
            signals.append("long_lead_time_volatility")

        low_verified = [offering for offering in offerings if not offering.supplier.verified_status]
        if len(low_verified) >= max(1, supplier_count // 2):
            signals.append("low_verification_coverage")

        return signals

    def _recommendation_reasons(self, cost_score, quality_score, sustainability_score, lead_time_score):
        reasons = []
        if cost_score >= 4:
            reasons.append("Competitive cost position")
        if quality_score >= 4:
            reasons.append("Strong quality track record")
        if sustainability_score >= 4:
            reasons.append("Meets sustainability expectations")
        if lead_time_score >= 4:
            reasons.append("Reliable lead-time performance")
        return reasons or ["Balanced scorecard performance"]
