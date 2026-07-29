"""Удаление breed/animal type, на которые ссылаются animal, должно блокироваться (409),
а не тихо обнулять ссылку - это тот самый passive_deletes-баг, который был найден и исправлен."""


def test_cannot_delete_breed_referenced_by_animal(client, register_and_activate):
    token = register_and_activate("cascade_user", "cascade_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    type_id = client.post(
        "/animal_types", json={"name_type": "CascadeType"}, headers=headers
    ).json()["type_id"]

    breed_id = client.post(
        "/breeds", json={"name": "CascadeBreed", "type_id": type_id}, headers=headers
    ).json()["breed_id"]

    animal_resp = client.post(
        "/animals",
        json={
            "inventory_number": "INV-CASCADE-1",
            "gender": "male",
            "arrival_date": "2026-01-01",
            "breed_id": breed_id,
        },
        headers=headers,
    )
    assert animal_resp.status_code == 200, animal_resp.text
    animal_id = animal_resp.json()["animal_id"]

    # На породу ссылается животное - удаление должно быть заблокировано.
    delete_breed_resp = client.delete(f"/breeds/{breed_id}", headers=headers)
    assert delete_breed_resp.status_code == 409

    # Порода всё ещё должна существовать и breed_id у животного - не обнулился.
    animal_after = client.get(f"/animals/{animal_id}", headers=headers)
    assert animal_after.json()["breed_id"] == breed_id

    # Удаляем животное - теперь породу удалить можно.
    assert client.delete(f"/animals/{animal_id}", headers=headers).json() is True
    assert client.delete(f"/breeds/{breed_id}", headers=headers).json() is True
