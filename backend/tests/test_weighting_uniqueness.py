"""У одного животного не может быть двух взвешиваний в одну дату (UNIQUE в БД)."""


def test_duplicate_weighting_same_animal_and_date_is_rejected(client, register_and_activate):
    token = register_and_activate(
        "weighting_dup_user", "weighting_dup_user@example.com"
    )
    headers = {"Authorization": f"Bearer {token}"}

    type_id = client.post(
        "/animal_types", json={"name_type": "WType"}, headers=headers
    ).json()["type_id"]
    breed_id = client.post(
        "/breeds", json={"name": "WBreed", "type_id": type_id}, headers=headers
    ).json()["breed_id"]
    animal_id = client.post(
        "/animals",
        json={
            "inventory_number": "INV-W-1",
            "gender": "female",
            "arrival_date": "2026-01-01",
            "breed_id": breed_id,
        },
        headers=headers,
    ).json()["animal_id"]

    first = client.post(
        "/weightings",
        json={"animal_id": animal_id, "date": "2026-01-10", "weight_kg": 120.5},
        headers=headers,
    )
    assert first.status_code == 200, first.text

    duplicate = client.post(
        "/weightings",
        json={"animal_id": animal_id, "date": "2026-01-10", "weight_kg": 121.0},
        headers=headers,
    )
    assert duplicate.status_code == 409

    different_date = client.post(
        "/weightings",
        json={"animal_id": animal_id, "date": "2026-01-11", "weight_kg": 121.0},
        headers=headers,
    )
    assert different_date.status_code == 200
