"""CRUD layer class for the User, Movie, and UserMovie models
used in the MyMovieWebApp project."""

from sqlalchemy.exc import IntegrityError
from models import User, Movie, UserMovie


class DataManager:
    """
    Handles database CRUD operations for User, Movie, and UserMovie.

    The class uses an SQLAlchemy session and keeps database access logic
    in one place, so the rest of the app can stay cleaner.
    """

    def __init__(self, session):
        """
        Create a new DataManager instance.

        Args:
            session: SQLAlchemy session object -> db.session
        """
        self.session = session

    # ====================
    # USER CRUD
    # ====================

    def create_user(self, name: str) -> User:
        """
        Creates a new user and save it to the database.
        """
        user = User(name=name)
        self.session.add(user)
        self.session.commit()
        return user

    def get_user_by_id(self, user_id: int) -> User | None:
        """
        Returns a user by id or None if not found.
        """
        return self.session.get(User, user_id)

    def get_all_users(self) -> list[User]:
        """
        Returns all users.
        """
        return self.session.query(User).all()

    def update_user(self, user_id: int, new_name: str) -> User | None:
        """
        Updates a user name.
        Returns the updated user or None if not found.
        """
        user = self.session.get(User, user_id)
        if not user:
            return None

        user.name = new_name
        self.session.commit()
        return user

    def delete_user(self, user_id: int) -> bool:
        """
        Deletes a user by id.
        Returns True if deleted, False if not found.
        """
        user = self.session.get(User, user_id)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

    # ====================
    # MOVIE CRUD
    # ====================

    def create_movie(
        self,
        title: str,
        director: str,
        year: int,
        poster_url: str
    ) -> Movie:
        """
        Creates a new movie and saves it to the database.
        """
        movie = Movie(
            title=title,
            director=director,
            year=year,
            poster_url=poster_url
        )
        self.session.add(movie)
        self.session.commit()
        return movie

    def get_movie_by_id(self, movie_id: int) -> Movie | None:
        """
        Returns a movie by id or None if not found.
        """
        return self.session.get(Movie, movie_id)

    def get_movie_by_title(self, title: str) -> Movie | None:
        """
        Return a movie by exact title or None if not found.
        """
        return self.session.query(Movie).filter_by(title=title).first()


    def get_all_movies(self) -> list[Movie]:
        """
        Returns all movies.
        """
        return self.session.query(Movie).all()

    def update_movie(
        self,
        movie_id: int,
        title: str | None = None,
        director: str | None = None,
        year: int | None = None,
        poster_url: str | None = None,
    ) -> Movie | None:
        """
        Updates one or more movie fields.
        Returns the updated movie or None if not found.
        """
        movie = self.session.get(Movie, movie_id)
        if not movie:
            return None

        if title is not None:
            movie.title = title
        if director is not None:
            movie.director = director
        if year is not None:
            movie.year = year
        if poster_url is not None:
            movie.poster_url = poster_url

        self.session.commit()
        return movie

    def delete_movie(self, movie_id: int) -> bool:
        """
        Deletes a movie by id.
        Returns True if deleted, False if not found.
        """
        movie = self.session.get(Movie, movie_id)
        if not movie:
            return False

        self.session.delete(movie)
        self.session.commit()
        return True

    # ============================
    # USERMOVIE CRUD / LOGIC
    # ============================

    def create_user_movie(
        self,
        user_id: int,
        movie_id: int,
        status: str = "watchlist",
        rating: int | None = None,
        review: str | None = None
    ) -> UserMovie | None:
        """
        Links a user and a movie via a UserMovie entry.

        Returns the created entry.
        Returns None if the user-movie pair already exists.
        Raises ValueError if user or movie does not exist.
        """
        user = self.session.get(User, user_id)
        movie = self.session.get(Movie, movie_id)

        if not user:
            raise ValueError(f"User (id: {user_id}) does not exist.")
        if not movie:
            raise ValueError(f"Movie (id: {movie_id}) does not exist.")

        user_movie = UserMovie(
            user_id=user_id,
            movie_id=movie_id,
            status=status,
            rating=rating,
            review=review
        )

        self.session.add(user_movie)

        try:
            self.session.commit()
            return user_movie
        except IntegrityError:
            self.session.rollback()
            return None

    def get_user_movie_by_id(self, user_movie_id: int) -> UserMovie | None:
        """
        Returns a UserMovie entry by id or None if not found.
        """
        return self.session.get(UserMovie, user_movie_id)

    def get_user_movie_by_user_and_movie(
        self,
        user_id: int,
        movie_id: int
    ) -> UserMovie | None:
        """
        Returns the UserMovie entry for a given user-movie pair.
        """
        return self.session.query(UserMovie).filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()

    def get_user_movies_for_user(self, user_id: int) -> list[UserMovie]:
        """
        Returns all UserMovie entries for a given user.
        """
        return self.session.query(UserMovie).filter_by(user_id=user_id).all()

    def get_user_movies_for_movie(self, movie_id: int) -> list[UserMovie]:
        """
        Returns all UserMovie entries for a given movie.
        """
        return self.session.query(UserMovie).filter_by(movie_id=movie_id).all()

    def update_user_movie(
        self,
        user_movie_id: int,
        status: str | None = None,
        rating: int | None = None,
        review: str | None = None
    ) -> UserMovie | None:
        """
        Updates status, rating, and/or review of a UserMovie entry.
        Returns the updated entry or None if not found.
        """
        user_movie = self.session.get(UserMovie, user_movie_id)
        if not user_movie:
            return None

        if status is not None:
            user_movie.status = status
        if rating is not None:
            user_movie.rating = rating
        if review is not None:
            user_movie.review = review

        self.session.commit()
        return user_movie

    def delete_user_movie(self, user_movie_id: int) -> bool:
        """
        Deletes a UserMovie entry by id.
        Returns True if deleted, False if not found.
        """
        user_movie = self.session.get(UserMovie, user_movie_id)
        if not user_movie:
            return False

        self.session.delete(user_movie)
        self.session.commit()
        return True

    def delete_user_movie_by_user_and_movie(self, user_id: int,
                                            movie_id: int) -> bool:
        """
        Delete a UserMovie entry by user_id and movie_id.
        Returns True if deleted, otherwise False.
        """
        user_movie = self.session.query(UserMovie).filter_by(
            user_id=user_id,
            movie_id=movie_id
        ).first()

        if not user_movie:
            return False

        self.session.delete(user_movie)
        self.session.commit()
        return True