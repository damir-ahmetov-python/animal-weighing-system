"""Обычный юзер не должен получить доступ к чужой weighting-записи (404),
а admin должен видеть её без ограничений."""


def test_user_cannot_access_others_weighting_but_admin_can(
    client, register_and_activate, db_session
):
    from app.models import User
    from sqlalchemy import select

    owner_token = register_and_activate(
        "weighting_owner", "weighting_owner@example.com"
    )
    owner_headers = {"Authorization": f"Bearer {owner_token}"}

    type_id = client.post(
        "/animal_types", json={"name_type": "AType"}, headers=owner_headers
    ).json()["type_id"]
    breed_id = client.post(
        "/breeds", json={"name": "ABreed", "type_id": type_id}, headers=owner_headers
    ).json()["breed_id"]
    animal_id = client.post(
        "/animals",
        json={
            "inventory_number": "INV-ACC-1",
            "gender": "male",
            "arrival_date": "2026-01-01",
            "breed_id": breed_id,
        },
        headers=owner_headers,
    ).json()["animal_id"]

    weighting_id = client.post(
        "/weightings",
        json={"animal_id": animal_id, "date": "2026-02-01", "weight_kg": 200},
        headers=owner_headers,
    ).json()["weighting_id"]

    other_token = register_and_activate(
        "weighting_other", "weighting_other@example.com"
    )
    other_headers = {"Authorization": f"Bearer {other_token}"}

    forbidden_resp = client.get(f"/weightings/{weighting_id}", headers=other_headers)
    assert forbidden_resp.status_code == 404

    # Делаем "other" юзера admin'ом напрямую в БД - в проекте нет эндпоинта на
    # создание админа, это тоже соответствует реальному способу (ручной SQL).
    other_user = db_session.execute(
        select(User).where(User.login == "weighting_other")
    ).scalar_one()
    other_user.role = "admin"
    db_session.commit()

    admin_login_resp = client.post(
        "/auth/login",
        data={"username": "weighting_other", "password": "password123"},
    )
    admin_token = admin_login_resp.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    admin_resp = client.get(f"/weightings/{weighting_id}", headers=admin_headers)
    assert admin_resp.status_code == 200
    assert admin_resp.json()["weighting_id"] == weighting_id
