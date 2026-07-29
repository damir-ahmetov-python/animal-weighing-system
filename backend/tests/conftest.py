"""
Общие fixtures для тестов.

Поднимаем настоящий Postgres (через pgserver, embedded-бинарник без root)
на время тестовой сессии - не SQLite, потому что тесты специально проверяют
поведение, завязанное на реальные constraints БД (FK RESTRICT, UNIQUE),
а SQLite эмулирует их иначе.
"""
import os
import tempfile

os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

import pgserver
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models import Base, User
from app.db.session import get_db


@pytest.fixture(scope="session")
def engine():
    """Свежий временный Postgres на всю тестовую сессию - каждый прогон pytest
    стартует с чистой, только что созданной БД."""
    tmp_dir = tempfile.mkdtemp(prefix="animal_weighing_test_pg_")
    server = pgserver.get_server(tmp_dir)
    test_engine = create_engine(server.get_uri())
    Base.metadata.create_all(test_engine)

    yield test_engine

    test_engine.dispose()
    server.cleanup()


@pytest.fixture()
def db_session(engine):
    session_maker = sessionmaker(bind=engine, expire_on_commit=True)
    session = session_maker()
    yield session
    session.close()


@pytest.fixture()
def client(db_session):
    """TestClient с подменённым get_db - все запросы идут в тестовую БД."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def register_and_activate(client, db_session):
    """Регистрирует пользователя, активирует его (токен достаём прямо из БД -
    email реально не отправляется, ссылка только логируется) и возвращает JWT."""

    def _register_and_activate(login: str, email: str, password: str = "password123") -> str:
        resp = client.post(
            "/auth/register",
            json={"login": login, "email": email, "password": password},
        )
        assert resp.status_code == 200, resp.text

        user = db_session.execute(select(User).where(User.login == login)).scalar_one()
        token = user.activation_token

        activate_resp = client.get(f"/auth/activate/{token}")
        assert activate_resp.status_code == 200, activate_resp.text

        login_resp = client.post(
            "/auth/login",
            data={"username": login, "password": password},
        )
        assert login_resp.status_code == 200, login_resp.text

        return login_resp.json()["access_token"]

    return _register_and_activate
