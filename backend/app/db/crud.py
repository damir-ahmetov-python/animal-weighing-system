from app.models import User
from sqlalchemy import select
from sqlalchemy.orm import Session

def create_user(
        session: Session,
        login: str,
        email: str,
        hashed_password: str,
        activation_token: str | None = None
) -> User | None:

    user = User(
        login=login,
        email=email,
        hashed_password=hashed_password,
        activation_token=activation_token,
    )

    session.add(user)

    session.commit()
    session.refresh(user)

    return user


def get_by_email(session: Session, email: str) -> User | None:
    res = session.execute(select(User).where(User.email == email))

    return res.scalar_one_or_none()


def get_by_login(session: Session, login: str) -> User | None:
    res = session.execute(select(User).where(User.login == login))

    return res.scalar_one_or_none()


def get_by_id(session: Session, user_id: int) -> User | None:
    res = session.execute(select(User).where(User.id == user_id))

    return res.scalar_one_or_none()
