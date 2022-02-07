from app import db, create_app
from app.main.models import User, Post
from app.cli import register

app = create_app()
register(app)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": db,
        "User": User,
        "Post": Post
    }
