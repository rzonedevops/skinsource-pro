from src.models import ProcurementRequest, RFQResponse

HEADERS_MANAGER = {"Content-Type": "application/json", "X-User-Id": "1", "X-User-Role": "manager"}
HEADERS_ANALYST = {"Content-Type": "application/json", "X-User-Id": "2", "X-User-Role": "analyst"}


def _create_request(client):
    response = client.post(
        "/api/procurement/requests",
        headers=HEADERS_ANALYST,
        json={
            "title": "Test RFQ",
            "ingredient_id": 1,
            "quantity_needed": 500,
            "target_price": 95,
            "deadline": "2026-06-20T10:00:00",
        },
    )
    assert response.status_code == 201
    return response.get_json()["data"]


def test_workflow_transitions_and_award(client):
    request_item = _create_request(client)

    target_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/suppliers",
        headers=HEADERS_ANALYST,
        json={"supplier_ids": [1, 2]},
    )
    assert target_response.status_code == 200

    send_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/send",
        headers=HEADERS_MANAGER,
        json={"deadline": "2026-06-25T10:00:00"},
    )
    assert send_response.status_code == 200

    first_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/responses",
        headers=HEADERS_ANALYST,
        json={"supplier_id": 1, "quoted_price": 88, "lead_time_days": 10},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/responses",
        headers=HEADERS_ANALYST,
        json={"supplier_id": 2, "quoted_price": 92, "lead_time_days": 14},
    )
    assert second_response.status_code == 201

    score_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/score",
        headers=HEADERS_ANALYST,
        json={"profile": "balanced"},
    )
    assert score_response.status_code == 200
    ranked = score_response.get_json()["data"]["ranked_responses"]
    assert ranked[0]["score_breakdown"]["total"] >= ranked[1]["score_breakdown"]["total"]

    award_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/award",
        headers=HEADERS_MANAGER,
        json={"response_id": ranked[0]["id"], "rationale": "Best total score"},
    )
    assert award_response.status_code == 200

    close_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/close",
        headers=HEADERS_MANAGER,
        json={"status": "completed"},
    )
    assert close_response.status_code == 200


def test_invalid_transition_rejected(client):
    request_item = _create_request(client)

    response = client.put(
        f"/api/procurement/requests/{request_item['id']}",
        headers=HEADERS_ANALYST,
        json={"status": "awarded"},
    )

    assert response.status_code == 409
    error = response.get_json()["error"]
    assert error["code"] == "invalid_transition"


def test_dashboard_metrics_use_awarded_data(client):
    request_item = _create_request(client)
    client.post(f"/api/procurement/requests/{request_item['id']}/suppliers", headers=HEADERS_ANALYST, json={"supplier_ids": [1]})
    client.post(f"/api/procurement/requests/{request_item['id']}/send", headers=HEADERS_MANAGER, json={})
    create_response = client.post(
        f"/api/procurement/requests/{request_item['id']}/responses",
        headers=HEADERS_ANALYST,
        json={"supplier_id": 1, "quoted_price": 80, "lead_time_days": 10},
    )
    response_id = create_response.get_json()["data"]["id"]
    client.post(f"/api/procurement/requests/{request_item['id']}/score", headers=HEADERS_ANALYST, json={"profile": "cost_first"})
    client.post(
        f"/api/procurement/requests/{request_item['id']}/award",
        headers=HEADERS_MANAGER,
        json={"response_id": response_id, "rationale": "Savings"},
    )

    dashboard = client.get("/api/procurement/dashboard")
    assert dashboard.status_code == 200
    savings = dashboard.get_json()["data"]["statistics"]["total_savings"]
    assert savings > 0


def test_intelligence_validation_errors(client):
    missing_param = client.get("/api/v1/intelligence/supplier-recommendations")
    assert missing_param.status_code == 400

    invalid_profile = client.get("/api/v1/intelligence/supplier-recommendations?ingredient_id=1&profile=unknown")
    assert invalid_profile.status_code == 400
