from app import create_app
from database import initialize_database


app = create_app()


if __name__ == "__main__":
    initialize_database()
    app.run()
