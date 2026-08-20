from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    google_id = db.Column(db.String(255), unique=True, nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False)

    name = db.Column(db.String(255))

    picture = db.Column(db.Text)

    created_at = db.Column(db.DateTime, server_default=db.func.now())