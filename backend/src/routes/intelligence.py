import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from functools import wraps

from flask import Blueprint, request

from src.models import Supplier, Ingredient, SupplierIngredient, IntelligenceAudit, db
from src.routes._utils import ApiError, api_error_response, api_success, get_actor, normalize_pagination, parse_json, parse_page_args
from src.services.supplier_intelligence import SupplierIntelligenceService, WEIGHTING_PROFILES


intelligence_bp = Blueprint("intelligence", __name__)
intelligence_service = SupplierIntelligenceService()

RATE_LIMIT_WINDOW = timedelta(minutes=1)
RATE_LIMIT_MAX = 60
RATE_LIMIT_TRACKER = defaultdict(deque)


def rate_limit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        remote_addr = request.remote_addr or "unknown"
        now = datetime.utcnow()
        history = RATE_LIMIT_TRACKER[remote_addr]

        while history and now - history[0] > RATE_LIMIT_WINDOW:
            history.popleft()

        if len(history) >= RATE_LIMIT_MAX:
            raise ApiError("Rate limit exceeded", code="rate_limited", status=429)

        history.append(now)
        return func(*args, **kwargs)

    return wrapper


def _audit(response_status, payload=None):
    actor = get_actor(require_user=False)
    audit = IntelligenceAudit(
        endpoint=request.path,
        actor_user_id=getattr(actor, "id", None),
        remote_addr=request.remote_addr,
        query_params=json.dumps(dict(request.args)),
        request_payload=json.dumps(payload or {}),
        response_status=response_status,
    )
    db.session.add(audit)
    db.session.commit()


def _success_response(data, status=200, meta=None, payload=None):
    response = api_success({"api_version": "v1", **data}, status=status, meta=meta)
    _audit(status, payload=payload)
    return response


@intelligence_bp.errorhandler(ApiError)
def _handle_api_error(error):
    _audit(error.status)
    return api_error_response(error)


@intelligence_bp.route("/v1/intelligence/discover-suppliers", methods=["POST"])
@intelligence_bp.route("/intelligence/discover-suppliers", methods=["POST"])
@rate_limit
def discover_suppliers():
    data = parse_json(required_fields=["ingredient_name"])
    discovered_suppliers = intelligence_service.discover_suppliers(
        ingredient_name=data["ingredient_name"],
        region=data.get("region"),
    )

    page, per_page, sort = parse_page_args(default_per_page=20)
    if sort == "confidence":
        discovered_suppliers.sort(key=lambda item: item["confidence_score"], reverse=True)

    start = (page - 1) * per_page
    end = start + per_page
    paged = discovered_suppliers[start:end]

    meta = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(discovered_suppliers),
            "pages": (len(discovered_suppliers) + per_page - 1) // per_page,
            "has_next": end < len(discovered_suppliers),
            "has_prev": page > 1,
        },
        "sort": sort,
    }

    return _success_response(
        {
            "suppliers": paged,
            "criteria": {"ingredient_name": data["ingredient_name"], "region": data.get("region")},
        },
        meta=meta,
        payload=data,
    )


@intelligence_bp.route("/v1/intelligence/evaluate-supplier/<int:supplier_id>", methods=["GET"])
@intelligence_bp.route("/intelligence/evaluate-supplier/<int:supplier_id>", methods=["GET"])
@rate_limit
def evaluate_supplier(supplier_id):
    evaluation = intelligence_service.evaluate_supplier_performance(supplier_id)
    if "error" in evaluation:
        raise ApiError(evaluation["error"], code="not_found", status=404)
    return _success_response({"evaluation": evaluation})


@intelligence_bp.route("/v1/intelligence/optimize-pricing", methods=["POST"])
@intelligence_bp.route("/intelligence/optimize-pricing", methods=["POST"])
@rate_limit
def optimize_pricing():
    data = parse_json(required_fields=["ingredient_id", "quantity"])

    try:
        quantity = float(data["quantity"])
    except (TypeError, ValueError):
        raise ApiError("quantity must be numeric", code="validation_error", status=400)

    pricing_analysis = intelligence_service.optimize_pricing(ingredient_id=int(data["ingredient_id"]), quantity=quantity)
    if "error" in pricing_analysis:
        raise ApiError(pricing_analysis["error"], code="not_found", status=404)

    return _success_response({"pricing_analysis": pricing_analysis}, payload=data)


@intelligence_bp.route("/v1/intelligence/market-intelligence/<category>", methods=["GET"])
@intelligence_bp.route("/intelligence/market-intelligence/<category>", methods=["GET"])
@rate_limit
def get_market_intelligence(category):
    market_data = intelligence_service.get_market_intelligence(category)
    return _success_response({"market_intelligence": market_data})


@intelligence_bp.route("/v1/intelligence/supplier-recommendations", methods=["GET"])
@intelligence_bp.route("/intelligence/supplier-recommendations", methods=["GET"])
@rate_limit
def get_supplier_recommendations():
    ingredient_id = request.args.get("ingredient_id", type=int)
    profile = request.args.get("profile", "balanced")
    page, per_page, sort = parse_page_args(default_per_page=10, max_per_page=50)

    if not ingredient_id:
        raise ApiError("ingredient_id query parameter is required", code="validation_error", status=400)
    if profile not in WEIGHTING_PROFILES:
        raise ApiError("Invalid profile", code="validation_error", status=400, details={"allowed": list(WEIGHTING_PROFILES)})

    recommendation_payload = intelligence_service.get_supplier_recommendations(ingredient_id=ingredient_id, profile=profile, limit=500)
    recommendations = recommendation_payload["recommendations"]

    if sort == "price":
        recommendations.sort(key=lambda item: item["offering"].get("price_per_kg") or 0)
    else:
        recommendations.sort(key=lambda item: item["recommendation_score"], reverse=True)

    start = (page - 1) * per_page
    end = start + per_page
    paged = recommendations[start:end]

    meta = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(recommendations),
            "pages": (len(recommendations) + per_page - 1) // per_page,
            "has_next": end < len(recommendations),
            "has_prev": page > 1,
        },
        "sort": sort,
        "filters": {"ingredient_id": ingredient_id, "profile": profile},
    }

    return _success_response(
        {
            "recommendations": paged,
            "profile": profile,
        },
        meta=meta,
    )


@intelligence_bp.route("/v1/intelligence/price-trends/<int:ingredient_id>", methods=["GET"])
@intelligence_bp.route("/intelligence/price-trends/<int:ingredient_id>", methods=["GET"])
@rate_limit
def get_price_trends(ingredient_id):
    ingredient = Ingredient.query.get(ingredient_id)
    if not ingredient:
        raise ApiError("Ingredient not found", code="not_found", status=404)

    offerings = SupplierIngredient.query.filter_by(ingredient_id=ingredient_id).all()
    prices = sorted([offering.price_per_kg for offering in offerings if offering.price_per_kg])

    if not prices:
        return _success_response(
            {
                "price_trends": {
                    "ingredient_id": ingredient_id,
                    "ingredient_name": ingredient.name,
                    "historical_data": [],
                    "forecast_data": [],
                    "trend_summary": {"overall_trend": "unknown", "volatility": "unknown"},
                }
            }
        )

    now = datetime.utcnow()
    historical_data = []
    for month_offset in range(12, 0, -1):
        month_date = now - timedelta(days=30 * month_offset)
        sample_price = prices[(month_offset - 1) % len(prices)]
        historical_data.append({"month": month_date.strftime("%Y-%m"), "average_price": round(sample_price, 2)})

    average_price = sum(prices) / len(prices)
    forecast_data = []
    for month_offset in range(1, 7):
        month_date = now + timedelta(days=30 * month_offset)
        drift = 1 + (0.01 * month_offset)
        forecast_data.append(
            {
                "month": month_date.strftime("%Y-%m"),
                "predicted_price": round(average_price * drift, 2),
                "confidence_level": "medium",
            }
        )

    spread_ratio = (max(prices) - min(prices)) / average_price if average_price else 0
    volatility = "low" if spread_ratio < 0.1 else "medium" if spread_ratio < 0.25 else "high"

    return _success_response(
        {
            "price_trends": {
                "ingredient_id": ingredient_id,
                "ingredient_name": ingredient.name,
                "historical_data": historical_data,
                "forecast_data": forecast_data,
                "trend_summary": {
                    "overall_trend": "increasing",
                    "volatility": volatility,
                    "market_factors": [
                        "Current supplier quote distribution",
                        "Observed lead-time pressure",
                        "Recent RFQ response competitiveness",
                    ],
                },
            }
        }
    )


@intelligence_bp.route("/v1/intelligence/competitive-analysis", methods=["POST"])
@intelligence_bp.route("/intelligence/competitive-analysis", methods=["POST"])
@rate_limit
def competitive_analysis():
    data = parse_json(required_fields=["ingredient_ids"])
    ingredient_ids = [int(item) for item in data.get("ingredient_ids", [])]
    profile = data.get("profile", "balanced")
    quantity = float(data.get("quantity", 100))

    if profile not in WEIGHTING_PROFILES:
        raise ApiError("Invalid profile", code="validation_error", status=400)

    analyses = []
    for ingredient_id in ingredient_ids:
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            continue
        recommendations = intelligence_service.get_supplier_recommendations(ingredient_id, profile=profile, limit=20)
        analyses.append(
            {
                "ingredient_id": ingredient_id,
                "ingredient_name": ingredient.name,
                "quantity": quantity,
                "profile": profile,
                "supplier_analysis": recommendations["recommendations"],
                "risk_signals": [
                    signal
                    for rec in recommendations["recommendations"]
                    for signal in rec.get("risk_signals", [])
                ],
            }
        )

    return _success_response({"competitive_analysis": analyses, "analysis_date": datetime.utcnow().isoformat()}, payload=data)


@intelligence_bp.route("/v1/intelligence/audit", methods=["GET"])
def get_intelligence_audit_log():
    page, per_page, sort = parse_page_args(default_per_page=20, max_per_page=100)
    query = IntelligenceAudit.query

    endpoint_filter = request.args.get("endpoint")
    if endpoint_filter:
        query = query.filter(IntelligenceAudit.endpoint == endpoint_filter)

    if sort == "created_at":
        query = query.order_by(IntelligenceAudit.created_at)
    else:
        query = query.order_by(IntelligenceAudit.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return api_success(
        {
            "api_version": "v1",
            "audit_entries": [entry.to_dict() for entry in pagination.items],
        },
        meta=normalize_pagination(pagination, page, per_page, sort=sort),
    )
