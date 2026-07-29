"""Флоу регистрации: неактивен -> логин отклонён -> активация -> логин проходит."""


def test_registration_activation_login_flow(client, db_session):
    from app.models import User
    from sqlalchemy import select

    register_resp = client.post(
        "/auth/register",
        json={
            "login": "flow_user",
            "email": "flow_user@example.com",
            "password": "password123",
        },
    )
    assert register_resp.status_code == 200, register_resp.text
    assert register_resp.json()["is_active"] is False

    # Неактивный пользователь не должен иметь возможность войти, даже зная пароль.
    login_before_activation = client.post(
        "/auth/login",
        data={"username": "flow_user", "password": "password123"},
    )
    assert login_before_activation.status_code == 400
    assert login_before_activation.json()["detail"] == "User is not active"

    user = db_session.execute(
        select(User).where(User.login == "flow_user")
    ).scalar_one()
    assert user.activation_token is not None

    activate_resp = client.get(f"/auth/activate/{user.activation_token}")
    assert activate_resp.status_code == 200, activate_resp.text
    assert activate_resp.json()["is_active"] is True

    login_after_activation = client.post(
        "/auth/login",
        data={"username": "flow_user", "password": "password123"},
    )
    assert login_after_activation.status_code == 200
    assert "access_token" in login_after_activation.json()
