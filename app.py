import os

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask.cli import load_dotenv

from data_manager import DataManager
from help_functions import validate_user_name, get_or_create_movie_by_title
from models import db

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    """
    Home screen of the application. Shows a listing of all users and a form
    for adding new users.
    """
    users = manager.get_all_users()
    return render_template("index.html", users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """
    When the user submits the “Add User” form, a POST request is triggered.
    The server receives the new user data, adds it to the database, and then
    redirects back to /
    """
    try:
        users = manager.get_all_users()
        name_to_check = request.form.get("name", "").strip()

        if not name_to_check:
            flash("Enter a valid name.", "error")
            return redirect(url_for("home"))

        if validate_user_name(users, name_to_check):
            flash(f'User "{name_to_check}" already exists.', "error")
            return redirect(url_for("home"))

        user = manager.create_user(name_to_check)
        flash(f'User "{user.name}" successfully created.', "success")
        return redirect(url_for("home"))

    except Exception as error:
        flash(f"Error occurred: {error}", "error")
        return redirect(url_for("home"))


@app.route('/users', methods=['GET'])
def list_users():
    """
    Show all users.
    """
    users = manager.get_all_users()
    return render_template("users.html", users=users)


@app.route('/movies', methods=['GET', 'POST'])
def movies_handler():
    """
    Shows all movies in the database or add a new movie
    """
    movies = manager.get_all_movies()

    if request.method == "GET":
        return render_template("movies.html", movies=movies)

    title = request.form.get("title", "").strip()

    if not title:
        flash("Enter a valid movie title.", "error")
        return redirect(url_for("movies_handler"))

    existing_movie = manager.get_movie_by_title(title)
    if existing_movie is not None:
        flash(f'Movie "{existing_movie.title}" already exists in the database.', "error")
        return redirect(url_for("movies_handler"))

    movie = get_or_create_movie_by_title(title, manager, API_KEY)

    if movie is None:
        flash(f'Movie "{title}" was not found in OMDb.', "error")
        return redirect(url_for("movies_handler"))

    flash(f'Movie "{movie.title}" successfully added!', "success")
    return redirect(url_for("movies_handler"))


@app.route(
    '/movies/<int:movie_id>/update', methods=['POST']
)
def update_movie_name(movie_id):
    """
    Change the title of a specific movie in the movie database.
    """
    new_title = request.form.get("title", "").strip()

    if not new_title:
        flash("Enter a valid movie title.", "error")
        return redirect(url_for("movies_handler"))

    movie = manager.update_movie(movie_id, title=new_title)

    if movie is None:
        abort(404)
    else:
        flash(f'Movie title updated to "{movie.title}".', "success")

    return redirect(url_for("movies_handler"))


@app.route('/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(movie_id):
    """
    Remove a specific movie from the movie database.
    """
    deleted = manager.delete_movie(movie_id)

    if deleted:
        flash("Movie removed from database.", "success")
    else:
        abort(404)

    return redirect(url_for("movies_handler"))


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies_handler_user(user_id):
    """
    Show all movies assigned to a user or add a new movie.
    """
    user = manager.get_user_by_id(user_id)

    if not user:
        abort(404)

    if request.method == "GET":
        user_movies = manager.get_user_movies_for_user(user_id)
        return render_template(
            "user.html",
            user=user,
            user_movies=user_movies
        )

    title = request.form.get("title", "").strip()

    if not title:
        flash("Enter a valid movie title.", "error")
        return redirect(url_for("movies_handler_user", user_id=user_id))

    movie = get_or_create_movie_by_title(title, manager, API_KEY)

    if movie is None:
        flash(f'Movie "{title}" was not found in OMDb.', "error")
        return redirect(url_for("movies_handler_user", user_id=user_id))

    user_movie = manager.create_user_movie(user_id, movie.id)

    if user_movie is None:
        flash(f'"{movie.title}" is already in the user list.', "error")
    else:
        flash(f'Movie "{movie.title}" successfully added!', "success")

    return redirect(url_for("movies_handler_user", user_id=user_id))


@app.route(
    '/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST']
)
def update_movie_name_list_user(user_id, movie_id):
    """
    Change the title of a specific movie in a user's list without relying on
    OMDb for corrections.
    """
    new_title = request.form.get("title", "").strip()

    if not new_title:
        flash("Enter a valid movie title.", "error")
        return redirect(url_for("movies_handler_user", user_id=user_id))

    movie = manager.update_movie(movie_id, title=new_title)

    if movie is None:
        abort(404)
    else:
        flash(f'Movie title updated to "{movie.title}".', "success")

    return redirect(url_for("movies_handler_user", user_id=user_id))


@app.route(
    '/users/<int:user_id>/movies/<int:movie_id>/details/update',
    methods=['POST']
)
def update_user_movie_details(user_id, movie_id):
    """
    Update status, rating, and review for a specific user-movie relation.
    """
    user_movie = manager.get_user_movie_by_user_and_movie(user_id, movie_id)

    if user_movie is None:
        abort(404)

    status = request.form.get("status", "").strip()
    rating_raw = request.form.get("rating", "").strip()
    review = request.form.get("review", "").strip()

    if status not in {"watchlist", "watched", "favorite"}:
        status = "watchlist"

    rating = None
    if rating_raw:
        try:
            rating = int(rating_raw)
            if rating < 1 or rating > 10:
                flash("Rating must be between 1 and 10.", "error")
                return redirect(url_for("movies_handler_user", user_id=user_id))
        except ValueError:
            flash("Rating must be a number.", "error")
            return redirect(url_for("movies_handler_user", user_id=user_id))

    manager.update_user_movie(
        user_movie.id,
        status=status,
        rating=rating,
        review=review if review else None
    )

    flash("Movie details updated successfully.", "success")
    return redirect(url_for("movies_handler_user", user_id=user_id))


@app.route(
    '/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST']
)
def delete_movie_user_list(user_id, movie_id):
    """
    Remove a specific movie from a user's movie list.
    """
    deleted = manager.delete_user_movie_by_user_and_movie(user_id, movie_id)

    if deleted:
        flash("Movie removed from user list.", "success")
    else:
        abort(404)

    return redirect(url_for("movies_handler_user", user_id=user_id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500



# Determine the absolute path of the project directory
basedir = os.path.abspath(os.path.dirname(__file__))
# Create the /data folder if it does not already exist
os.makedirs(os.path.join(basedir, "data"), exist_ok=True)
# Configure the SQLite database path
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/movie_db.sqlite')}"
)
# SQLAlchemy should not track changes to objects in the background in this app:
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# "Secret" Key for proper functioning of flash messages
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

db.init_app(app)

with app.app_context():
    db.create_all()

manager = DataManager(db.session)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
