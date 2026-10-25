from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from app.models import Base, User

DATABASE_PATH = Path(__file__).parent / "trekking.db"
DATABASE_URL = "sqlite:///" + DATABASE_PATH.as_posix()
ADMIN_PASSWORD = "pass123"
engine = create_engine(DATABASE_URL)


def create_admin():
    with Session(engine) as session:
        admin = session.query(User).filter_by(email="admin@mail.com").first()
        if admin is None:
            admin = User(
                name="Admin",
                email="admin@mail.com",
                password_hash=generate_password_hash(ADMIN_PASSWORD),
                role="Admin",
            )
            session.add(admin)
            session.commit()
        elif not admin.password_hash:
            admin.password_hash = generate_password_hash(ADMIN_PASSWORD)
            session.commit()


def initialize_database():
    Base.metadata.create_all(engine)
    create_admin()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DATABASE_PATH}")
