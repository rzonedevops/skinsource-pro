from functools import wraps

from flask import jsonify, request

from src.models import User


ROLE_LEVEL = {"viewer": 1, "analyst": 2, "manager": 3}


class ApiError(Exception):
    def __init__(self, message, code="bad_request", status=400, details=None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status
        self.details = details or {}


def api_success(data, status=200, meta=None):
    payload = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def api_error_response(error):
    return jsonify({"error": {"code": error.code, "message": error.message, "details": error.details}}), error.status


def parse_json(required_fields=None):
    data = request.get_json(silent=True)
    if data is None:
        raise ApiError("JSON body is required", code="invalid_json", status=400)
    required_fields = required_fields or []
    missing = [field for field in required_fields if field not in data or data[field] in (None, "")]
    if missing:
        raise ApiError("Missing required fields", code="validation_error", status=400, details={"missing": missing})
    return data


def get_actor(require_user=False):
    user_id = request.headers.get("X-User-Id", type=int)
    role = request.headers.get("X-User-Role")

    if user_id:
        user = User.query.get(user_id)
        if user:
            return user

    if role:
        role = role.lower()
        if role not in ROLE_LEVEL:
            raise ApiError("Invalid user role", code="authorization_error", status=403)
        return type("RequestActor", (), {"id": user_id, "role": role})()

    if require_user:
        raise ApiError("Authentication required", code="authentication_required", status=401)

    return type("RequestActor", (), {"id": user_id, "role": "viewer"})()


def require_role(min_role):
    min_level = ROLE_LEVEL[min_role]

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            actor = get_actor(require_user=True)
            actor_level = ROLE_LEVEL.get(getattr(actor, "role", "viewer"), 0)
            if actor_level < min_level:
                raise ApiError("Insufficient permissions", code="authorization_error", status=403)
            request.actor = actor
            return func(*args, **kwargs)

        return wrapper

    return decorator


def parse_page_args(default_per_page=20, max_per_page=100):
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", default_per_page, type=int)
    sort = request.args.get("sort", "-created_at")

    if page < 1 or per_page < 1 or per_page > max_per_page:
        raise ApiError(
            "Invalid pagination arguments",
            code="validation_error",
            status=400,
            details={"page": page, "per_page": per_page, "max_per_page": max_per_page},
        )

    return page, per_page, sort


def normalize_pagination(pagination, page, per_page, sort=None):
    meta = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev,
        }
    }
    if sort is not None:
        meta["sort"] = sort
    return meta
