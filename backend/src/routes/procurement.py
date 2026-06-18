import json
from datetime import datetime

from flask import Blueprint, request
from sqlalchemy import desc

from src.models import (
    ProcurementRequest,
    Ingredient,
    Supplier,
    RFQResponse,
    RFQRecipient,
    ProcurementAward,
    ProcurementEvent,
    NegotiationRound,
    db,
)
from src.routes._utils import (
    ApiError,
    api_error_response,
    api_success,
    get_actor,
    normalize_pagination,
    parse_json,
    parse_page_args,
    require_role,
)


procurement_bp = Blueprint("procurement", __name__)

ALLOWED_TRANSITIONS = {
    "draft": {"sent", "cancelled"},
    "sent": {"received", "evaluated", "cancelled"},
    "received": {"evaluated", "cancelled"},
    "evaluated": {"awarded", "cancelled"},
    "awarded": {"completed", "cancelled"},
    "completed": set(),
    "cancelled": set(),
}


SCORING_PROFILES = {
    "cost_first": {"price": 0.4, "lead_time": 0.2, "quality": 0.15, "sustainability": 0.1, "risk": 0.15},
    "quality_first": {"price": 0.15, "lead_time": 0.2, "quality": 0.35, "sustainability": 0.1, "risk": 0.2},
    "sustainability_first": {"price": 0.15, "lead_time": 0.15, "quality": 0.2, "sustainability": 0.35, "risk": 0.15},
    "balanced": {"price": 0.25, "lead_time": 0.2, "quality": 0.25, "sustainability": 0.15, "risk": 0.15},
}


def _record_event(procurement_request, event_type, from_status=None, to_status=None, metadata=None, actor_id=None):
    event = ProcurementEvent(
        procurement_request_id=procurement_request.id,
        event_type=event_type,
        from_status=from_status,
        to_status=to_status,
        actor_user_id=actor_id,
        event_metadata=json.dumps(metadata or {}),
    )
    db.session.add(event)


def _transition_status(procurement_request, next_status, actor_id=None, metadata=None):
    if procurement_request.status == next_status:
        return

    allowed_next = ALLOWED_TRANSITIONS.get(procurement_request.status, set())
    if next_status not in allowed_next:
        raise ApiError(
            "Invalid status transition",
            code="invalid_transition",
            status=409,
            details={"from": procurement_request.status, "to": next_status},
        )

    previous_status = procurement_request.status
    procurement_request.status = next_status

    now = datetime.utcnow()
    if next_status == "sent":
        procurement_request.sent_at = now
    elif next_status == "awarded":
        procurement_request.awarded_at = now
    elif next_status == "completed":
        procurement_request.completed_at = now
    elif next_status == "cancelled":
        procurement_request.cancelled_at = now

    _record_event(
        procurement_request,
        event_type="status_transition",
        from_status=previous_status,
        to_status=next_status,
        metadata=metadata,
        actor_id=actor_id,
    )


def _serialize_request(procurement_request, include_relations=False):
    request_data = procurement_request.to_dict()
    request_data["ingredient"] = procurement_request.ingredient.to_dict() if procurement_request.ingredient else None
    request_data["user"] = procurement_request.user.to_dict() if procurement_request.user else None
    request_data["response_count"] = len(procurement_request.rfq_responses)
    request_data["recipient_count"] = len(procurement_request.rfq_recipients)

    if include_relations:
        request_data["recipients"] = [recipient.to_dict() | {"supplier": recipient.supplier.to_dict()} for recipient in procurement_request.rfq_recipients]
        request_data["responses"] = [response.to_dict() | {"supplier": response.supplier.to_dict()} for response in procurement_request.rfq_responses]
        request_data["awards"] = [award.to_dict() for award in procurement_request.awards]
        request_data["negotiation_rounds"] = [round_item.to_dict() for round_item in procurement_request.negotiations]
        request_data["events"] = [event.to_dict() for event in procurement_request.events]

    return request_data


def _parse_optional_deadline(data):
    deadline = data.get("deadline")
    if not deadline:
        return None
    try:
        return datetime.fromisoformat(deadline.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError as exc:
        raise ApiError("Invalid deadline format", code="validation_error", status=400, details={"deadline": str(exc)})


def _score_response(response, profile_name="balanced"):
    profile = SCORING_PROFILES.get(profile_name, SCORING_PROFILES["balanced"])

    request_item = response.procurement_request
    supplier = response.supplier

    target_price = request_item.target_price or response.quoted_price or 1
    price_score = min(5.0, max(1.0, (target_price / max(response.quoted_price, 1)) * 5))

    deadline = request_item.deadline
    if deadline and request_item.sent_at:
        expected_days = max((deadline - request_item.sent_at).days, 1)
    else:
        expected_days = 30
    lead_time_score = min(5.0, max(1.0, (expected_days / max(response.lead_time_days, 1)) * 5))

    quality_score = supplier.quality_score or 3.0
    sustainability_score = supplier.sustainability_score or 3.0

    risk_penalty = 0.0
    if not supplier.verified_status:
        risk_penalty += 1.2
    if response.lead_time_days > expected_days:
        risk_penalty += 0.8
    risk_score = max(1.0, min(5.0, 5 - risk_penalty))

    total_score = (
        price_score * profile["price"]
        + lead_time_score * profile["lead_time"]
        + quality_score * profile["quality"]
        + sustainability_score * profile["sustainability"]
        + risk_score * profile["risk"]
    )

    response.price_score = round(price_score, 3)
    response.lead_time_score = round(lead_time_score, 3)
    response.quality_score = round(quality_score, 3)
    response.sustainability_score = round(sustainability_score, 3)
    response.risk_score = round(risk_score, 3)
    response.total_score = round(total_score, 3)
    response.scoring_profile = profile_name


@procurement_bp.errorhandler(ApiError)
def _handle_api_error(error):
    return api_error_response(error)


@procurement_bp.route("/procurement/requests", methods=["GET"])
def get_procurement_requests():
    page, per_page, sort = parse_page_args()

    query = ProcurementRequest.query
    user_id = request.args.get("user_id", type=int)
    status = request.args.get("status")
    priority = request.args.get("priority")
    ingredient_id = request.args.get("ingredient_id", type=int)

    if user_id:
        query = query.filter(ProcurementRequest.user_id == user_id)
    if status:
        query = query.filter(ProcurementRequest.status == status)
    if priority:
        query = query.filter(ProcurementRequest.priority == priority)
    if ingredient_id:
        query = query.filter(ProcurementRequest.ingredient_id == ingredient_id)

    if sort == "created_at":
        query = query.order_by(ProcurementRequest.created_at)
    else:
        query = query.order_by(desc(ProcurementRequest.created_at))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    data = [_serialize_request(item) for item in pagination.items]
    return api_success(data, meta=normalize_pagination(pagination, page, per_page, sort=sort))


@procurement_bp.route("/procurement/requests/<int:request_id>", methods=["GET"])
def get_procurement_request(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    return api_success(_serialize_request(procurement_request, include_relations=True))


@procurement_bp.route("/procurement/requests", methods=["POST"])
@require_role("analyst")
def create_procurement_request():
    data = parse_json(required_fields=["title", "ingredient_id", "quantity_needed"])

    Ingredient.query.get_or_404(data["ingredient_id"])

    delivery_date = None
    if data.get("delivery_date"):
        try:
            delivery_date = datetime.strptime(data["delivery_date"], "%Y-%m-%d").date()
        except ValueError:
            raise ApiError("Invalid delivery_date format. Use YYYY-MM-DD", code="validation_error", status=400)

    actor = request.actor
    procurement_request = ProcurementRequest(
        user_id=data.get("user_id") or actor.id or 1,
        ingredient_id=data["ingredient_id"],
        title=data["title"],
        description=data.get("description"),
        quantity_needed=float(data["quantity_needed"]),
        target_price=data.get("target_price"),
        delivery_date=delivery_date,
        priority=data.get("priority", "medium"),
        status="draft",
        deadline=_parse_optional_deadline(data),
    )
    if "specifications" in data:
        procurement_request.specifications = json.dumps(data["specifications"])
    if "quality_requirements" in data:
        procurement_request.quality_requirements = json.dumps(data["quality_requirements"])

    db.session.add(procurement_request)
    db.session.flush()
    _record_event(procurement_request, "request_created", metadata={"title": procurement_request.title}, actor_id=actor.id)
    db.session.commit()

    return api_success(_serialize_request(procurement_request), status=201)


@procurement_bp.route("/procurement/requests/<int:request_id>", methods=["PUT"])
@require_role("analyst")
def update_procurement_request(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json()

    if procurement_request.status in {"completed", "cancelled"}:
        raise ApiError("Closed requests cannot be modified", code="invalid_state", status=409)

    updatable_fields = ["title", "description", "quantity_needed", "target_price", "priority"]
    for field in updatable_fields:
        if field in data:
            setattr(procurement_request, field, data[field])

    if "delivery_date" in data and data["delivery_date"]:
        try:
            procurement_request.delivery_date = datetime.strptime(data["delivery_date"], "%Y-%m-%d").date()
        except ValueError:
            raise ApiError("Invalid delivery_date format. Use YYYY-MM-DD", code="validation_error", status=400)

    if "deadline" in data:
        procurement_request.deadline = _parse_optional_deadline(data)

    if "specifications" in data:
        procurement_request.specifications = json.dumps(data["specifications"])
    if "quality_requirements" in data:
        procurement_request.quality_requirements = json.dumps(data["quality_requirements"])

    if "status" in data:
        _transition_status(procurement_request, data["status"], actor_id=request.actor.id)

    db.session.commit()
    return api_success(_serialize_request(procurement_request))


@procurement_bp.route("/procurement/requests/<int:request_id>/suppliers", methods=["POST"])
@require_role("analyst")
def select_suppliers(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json(required_fields=["supplier_ids"])

    supplier_ids = sorted({int(supplier_id) for supplier_id in data.get("supplier_ids", [])})
    if not supplier_ids:
        raise ApiError("At least one supplier must be selected", code="validation_error", status=400)

    suppliers = Supplier.query.filter(Supplier.id.in_(supplier_ids), Supplier.active_status.is_(True)).all()
    if len(suppliers) != len(supplier_ids):
        raise ApiError("One or more suppliers not found or inactive", code="validation_error", status=400)

    existing_by_supplier = {item.supplier_id: item for item in procurement_request.rfq_recipients}
    created = []
    for supplier_id in supplier_ids:
        if supplier_id in existing_by_supplier:
            continue
        recipient = RFQRecipient(
            procurement_request_id=procurement_request.id,
            supplier_id=supplier_id,
            status="targeted",
        )
        db.session.add(recipient)
        created.append(supplier_id)

    _record_event(
        procurement_request,
        "suppliers_targeted",
        metadata={"supplier_ids": supplier_ids, "new_suppliers": created},
        actor_id=request.actor.id,
    )
    db.session.commit()

    return api_success(
        {
            "request_id": procurement_request.id,
            "suppliers": [recipient.to_dict() for recipient in procurement_request.rfq_recipients],
        }
    )


@procurement_bp.route("/procurement/requests/<int:request_id>/send", methods=["POST"])
@require_role("manager")
def send_rfq(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json()

    if not procurement_request.rfq_recipients:
        raise ApiError("Select suppliers before sending RFQ", code="invalid_state", status=409)

    deadline = _parse_optional_deadline(data)
    if deadline:
        procurement_request.deadline = deadline

    now = datetime.utcnow()
    for recipient in procurement_request.rfq_recipients:
        recipient.status = "sent"
        recipient.sent_at = now

    _transition_status(
        procurement_request,
        "sent",
        actor_id=request.actor.id,
        metadata={"recipient_count": len(procurement_request.rfq_recipients)},
    )

    db.session.commit()
    return api_success(_serialize_request(procurement_request, include_relations=True))


@procurement_bp.route("/procurement/requests/<int:request_id>/responses", methods=["GET"])
def list_rfq_responses(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    sort = request.args.get("sort", "-total_score")

    query = RFQResponse.query.filter(RFQResponse.procurement_request_id == request_id)
    if sort == "quoted_price":
        query = query.order_by(RFQResponse.quoted_price)
    else:
        query = query.order_by(desc(RFQResponse.total_score), desc(RFQResponse.response_date))

    responses = [
        response.to_dict() | {"supplier": response.supplier.to_dict(), "recipient": response.recipient.to_dict() if response.recipient else None}
        for response in query.all()
    ]

    return api_success({"request": _serialize_request(procurement_request), "responses": responses})


@procurement_bp.route("/procurement/requests/<int:request_id>/responses", methods=["POST"])
@require_role("analyst")
def create_rfq_response(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json(required_fields=["supplier_id", "quoted_price", "lead_time_days"])

    supplier_id = int(data["supplier_id"])
    recipient = RFQRecipient.query.filter_by(procurement_request_id=request_id, supplier_id=supplier_id).first()
    if not recipient:
        raise ApiError("Supplier is not targeted for this RFQ", code="validation_error", status=400)

    existing = RFQResponse.query.filter_by(procurement_request_id=request_id, supplier_id=supplier_id).first()
    if existing:
        raise ApiError("Response from this supplier already exists", code="conflict", status=409)

    rfq_response = RFQResponse(
        procurement_request_id=request_id,
        supplier_id=supplier_id,
        recipient_id=recipient.id,
        quoted_price=float(data["quoted_price"]),
        total_price=data.get("total_price"),
        lead_time_days=int(data["lead_time_days"]),
        minimum_order_quantity=data.get("minimum_order_quantity"),
        terms_conditions=data.get("terms_conditions"),
        payment_terms=data.get("payment_terms"),
        validity_days=data.get("validity_days", 30),
        coa_provided=bool(data.get("coa_provided", False)),
        msds_provided=bool(data.get("msds_provided", False)),
        notes=data.get("notes"),
        status=data.get("status", "submitted"),
    )

    if "documents" in data:
        rfq_response.documents = json.dumps(data["documents"])

    recipient.status = "responded"
    recipient.responded_at = datetime.utcnow()

    db.session.add(rfq_response)

    if procurement_request.status == "sent":
        _transition_status(procurement_request, "received", actor_id=request.actor.id)

    _record_event(
        procurement_request,
        "response_received",
        metadata={"supplier_id": supplier_id, "quoted_price": rfq_response.quoted_price},
        actor_id=request.actor.id,
    )

    db.session.commit()
    return api_success(rfq_response.to_dict(), status=201)


@procurement_bp.route("/procurement/responses/<int:response_id>", methods=["PUT"])
@require_role("analyst")
def update_rfq_response(response_id):
    rfq_response = RFQResponse.query.get_or_404(response_id)
    data = parse_json()

    for field in [
        "quoted_price",
        "total_price",
        "lead_time_days",
        "minimum_order_quantity",
        "terms_conditions",
        "payment_terms",
        "validity_days",
        "coa_provided",
        "msds_provided",
        "notes",
        "status",
    ]:
        if field in data:
            setattr(rfq_response, field, data[field])

    if "documents" in data:
        rfq_response.documents = json.dumps(data["documents"])

    if data.get("status") in {"under_review", "accepted", "rejected"}:
        rfq_response.reviewed_at = datetime.utcnow()

    db.session.commit()
    return api_success(rfq_response.to_dict())


@procurement_bp.route("/procurement/requests/<int:request_id>/score", methods=["POST"])
@require_role("analyst")
def score_rfq_responses(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json()

    profile = data.get("profile", "balanced")
    if profile not in SCORING_PROFILES:
        raise ApiError("Invalid scoring profile", code="validation_error", status=400, details={"profile": profile})

    responses = RFQResponse.query.filter_by(procurement_request_id=request_id).all()
    if not responses:
        raise ApiError("No responses available for scoring", code="invalid_state", status=409)

    for response in responses:
        _score_response(response, profile_name=profile)

    _transition_status(procurement_request, "evaluated", actor_id=request.actor.id, metadata={"profile": profile})
    _record_event(procurement_request, "responses_scored", metadata={"profile": profile}, actor_id=request.actor.id)

    db.session.commit()

    ranked = sorted(responses, key=lambda item: item.total_score or 0, reverse=True)
    return api_success(
        {
            "request_id": request_id,
            "profile": profile,
            "ranked_responses": [response.to_dict() for response in ranked],
        }
    )


@procurement_bp.route("/procurement/requests/<int:request_id>/award", methods=["POST"])
@require_role("manager")
def award_request(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json(required_fields=["response_id", "rationale"])

    response = RFQResponse.query.filter_by(id=data["response_id"], procurement_request_id=request_id).first()
    if not response:
        raise ApiError("Response not found for this request", code="validation_error", status=404)

    response.status = "accepted"
    response.reviewed_at = datetime.utcnow()

    for other_response in procurement_request.rfq_responses:
        if other_response.id != response.id and other_response.status not in {"rejected", "withdrawn", "expired"}:
            other_response.status = "rejected"
            other_response.reviewed_at = datetime.utcnow()

    award = ProcurementAward(
        procurement_request_id=request_id,
        rfq_response_id=response.id,
        supplier_id=response.supplier_id,
        rationale=data["rationale"],
        decision_notes=data.get("decision_notes"),
        decided_by_user_id=request.actor.id or procurement_request.user_id,
    )

    db.session.add(award)
    _transition_status(procurement_request, "awarded", actor_id=request.actor.id)
    _record_event(
        procurement_request,
        "request_awarded",
        metadata={"response_id": response.id, "supplier_id": response.supplier_id, "rationale": data["rationale"]},
        actor_id=request.actor.id,
    )

    db.session.commit()
    return api_success({"award": award.to_dict(), "request": _serialize_request(procurement_request, include_relations=True)})


@procurement_bp.route("/procurement/requests/<int:request_id>/close", methods=["POST"])
@require_role("manager")
def close_request(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json()
    final_status = data.get("status", "completed")
    if final_status not in {"completed", "cancelled"}:
        raise ApiError("Final status must be completed or cancelled", code="validation_error", status=400)

    _transition_status(procurement_request, final_status, actor_id=request.actor.id)
    _record_event(procurement_request, "request_closed", metadata={"status": final_status}, actor_id=request.actor.id)

    db.session.commit()
    return api_success(_serialize_request(procurement_request))


@procurement_bp.route("/procurement/requests/<int:request_id>/negotiations", methods=["POST"])
@require_role("analyst")
def add_negotiation_round(request_id):
    procurement_request = ProcurementRequest.query.get_or_404(request_id)
    data = parse_json(required_fields=["supplier_id", "round_number"])

    round_item = NegotiationRound(
        procurement_request_id=request_id,
        supplier_id=data["supplier_id"],
        round_number=data["round_number"],
        status=data.get("status", "open"),
        proposal=json.dumps(data.get("proposal", {})),
        outcome=json.dumps(data.get("outcome", {})),
        closed_at=datetime.utcnow() if data.get("status") in {"closed", "accepted", "rejected"} else None,
    )

    db.session.add(round_item)
    _record_event(
        procurement_request,
        "negotiation_round_recorded",
        metadata={"supplier_id": data["supplier_id"], "round_number": data["round_number"]},
        actor_id=request.actor.id,
    )
    db.session.commit()

    return api_success(round_item.to_dict(), status=201)


@procurement_bp.route("/procurement/reminders", methods=["GET"])
@require_role("analyst")
def get_overdue_reminders():
    now = datetime.utcnow()
    overdue_requests = (
        ProcurementRequest.query.filter(
            ProcurementRequest.deadline.isnot(None),
            ProcurementRequest.deadline < now,
            ProcurementRequest.status.in_(["sent", "received", "evaluated"]),
        )
        .order_by(ProcurementRequest.deadline)
        .all()
    )

    reminders = []
    for req in overdue_requests:
        pending_recipients = [recipient for recipient in req.rfq_recipients if recipient.status in {"targeted", "sent", "no_response"}]
        for recipient in pending_recipients:
            reminders.append(
                {
                    "request_id": req.id,
                    "request_title": req.title,
                    "supplier_id": recipient.supplier_id,
                    "supplier_name": recipient.supplier.company_name if recipient.supplier else None,
                    "deadline": req.deadline.isoformat() if req.deadline else None,
                    "days_overdue": (now - req.deadline).days if req.deadline else None,
                }
            )
            recipient.last_reminder_at = now

    db.session.commit()
    return api_success({"generated_at": now.isoformat(), "reminders": reminders})


@procurement_bp.route("/procurement/dashboard", methods=["GET"])
def get_procurement_dashboard():
    total_requests = ProcurementRequest.query.count()
    active_rfqs = ProcurementRequest.query.filter(ProcurementRequest.status.in_(["sent", "received", "evaluated"])).count()
    pending_orders = ProcurementRequest.query.filter_by(status="awarded").count()
    completed_orders = ProcurementRequest.query.filter_by(status="completed").count()
    active_suppliers = Supplier.query.filter_by(active_status=True).count()

    awarded_responses = (
        db.session.query(ProcurementRequest, RFQResponse)
        .join(ProcurementAward, ProcurementAward.procurement_request_id == ProcurementRequest.id)
        .join(RFQResponse, RFQResponse.id == ProcurementAward.rfq_response_id)
        .all()
    )

    total_savings = 0.0
    for req, response in awarded_responses:
        baseline = (req.target_price or response.quoted_price or 0) * (req.quantity_needed or 0)
        actual = (response.quoted_price or 0) * (req.quantity_needed or 0)
        total_savings += max(0.0, baseline - actual)

    recent_requests = ProcurementRequest.query.order_by(desc(ProcurementRequest.created_at)).limit(5).all()
    recent_events = ProcurementEvent.query.order_by(desc(ProcurementEvent.created_at)).limit(8).all()

    return api_success(
        {
            "statistics": {
                "total_requests": total_requests,
                "active_rfqs": active_rfqs,
                "pending_orders": pending_orders,
                "completed_orders": completed_orders,
                "total_savings": round(total_savings, 2),
                "active_suppliers": active_suppliers,
            },
            "recent_requests": [_serialize_request(req) for req in recent_requests],
            "recent_events": [event.to_dict() for event in recent_events],
        }
    )


@procurement_bp.route("/procurement/health", methods=["GET"])
def procurement_health():
    actor = get_actor(require_user=False)
    return api_success({"status": "ok", "actor_role": actor.role, "api_version": "v1"})
