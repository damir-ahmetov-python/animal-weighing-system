"""Порода уникальна в рамках (type_id, name), но не глобально."""


def test_duplicate_breed_name_same_type_is_rejected(client, register_and_activate):
    token = register_and_activate("breed_user", "breed_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    type_id = client.post(
        "/animal_types", json={"name_type": "Cow"}, headers=headers
    ).json()["type_id"]

    first = client.post(
        "/breeds", json={"name": "Holstein", "type_id": type_id}, headers=headers
    )
    assert first.status_code == 200

    duplicate = client.post(
        "/breeds", json={"name": "Holstein", "type_id": type_id}, headers=headers
    )
    assert duplicate.status_code == 409

    other_type_id = client.post(
        "/animal_types", json={"name_type": "Horse"}, headers=headers
    ).json()["type_id"]

    # То же имя, но другой тип животного - это уже не дубль, должно пройти.
    different_type = client.post(
        "/breeds", json={"name": "Holstein", "type_id": other_type_id}, headers=headers
    )
    assert different_type.status_code == 200
