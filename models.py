"""
Database models for MyMovieWebApp.

Quick overview:

- User: someone using the app
- Movie: a movie in the database
- UserMovie: connects users and movies

Instead of a simple many-to-many table, I use an association model in UserMovie
because the relationship itself has data:
- status (watchlist, watched, favorite)
- rating
- review

Important:
A user can only have one entry per movie.
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    """
    Represents a user of the app.

    A user can have multiple movies via UserMovie entries.
    These entries store things like rating, review, and status.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    user_movies = db.relationship(
        "UserMovie",
        back_populates="user",
        cascade="all, delete-orphan" # delete association rows if parent is deleted
    )

    def __repr__(self):
        return f"User(user_id={self.id}, name={self.name})"


class Movie(db.Model):
    """
    Represents a movie.

    A movie can be linked to many users.
    The actual relation (including rating, etc.) is defined in UserMovie.
    """
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(200), nullable=False)

    user_movies = db.relationship(
        "UserMovie",
        back_populates="movie",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Movie(movie_id={self.id}, title={self.title})"


class UserMovie(db.Model):
    """
    Connects a user with a movie.

    Here is also the personalized data stored:
    - status (watchlist, watched, favorite)
    - rating
    - review

    Note:
    Each user can only have one entry per movie (UniqueConstraint).
    """
    __tablename__ = "user_movies"
    # Prevents duplicate user-movie pairs:
    # the same user cannot store the same movie more than once.
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"), nullable=False)
    movie_id = db.Column(db.Integer, ForeignKey("movies.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    review = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="watchlist")
    # e.g.: "watchlist", "watched", "favourite"

    user = db.relationship("User", back_populates="user_movies")
    movie = db.relationship("Movie", back_populates="user_movies")
