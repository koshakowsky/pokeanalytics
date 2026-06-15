"""Smoke tests that hold regardless of whether the DB has been seeded.

These cover wiring, validation and error handling — not data correctness —
so they are safe to run in CI against an empty database.
"""


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_docs_available(client):
    assert client.get("/api/docs").status_code == 200


def test_pokemon_list_shape(client):
    r = client.get("/api/pokemon/?limit=5")
    assert r.status_code == 200
    body = r.json()
    for key in ("items", "total", "limit", "offset", "has_more"):
        assert key in body
    assert body["limit"] == 5
    assert isinstance(body["items"], list)


def test_invalid_sort_does_not_500(client):
    # sort_by is allowlisted server-side and must fall back, not error.
    r = client.get("/api/pokemon/?sort_by=__class__&limit=3")
    assert r.status_code == 200


def test_limit_out_of_range_is_422(client):
    assert client.get("/api/pokemon/?limit=0").status_code == 422
    assert client.get("/api/pokemon/?limit=9999").status_code == 422


def test_missing_pokemon_is_404(client):
    assert client.get("/api/pokemon/999999").status_code == 404


def test_compare_requires_two_to_six(client):
    assert client.post("/api/compare/", json={"pokemon_ids": [1]}).status_code == 400
    assert client.post("/api/compare/", json={"pokemon_ids": list(range(1, 8))}).status_code == 400


def test_seed_disabled_without_token(client):
    # SEED_TOKEN is unset in the test env -> endpoint must refuse.
    assert client.post("/api/admin/seed").status_code == 403


def test_types_list(client):
    r = client.get("/api/types/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_type_effectiveness_404_for_unknown_type(client):
    assert client.get("/api/types/999999/effectiveness").status_code == 404
