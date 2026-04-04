import os

from flask import Flask, render_template, request, redirect, url_for, flash
import requests
from flask.cli import load_dotenv

from data_manager import DataManager
from models import db

load_dotenv()

API_KEY = os.getenv("API_KEY")
OMDB_URL = "http://www.omdbapi.com/"

app = Flask(__name__)


def fetch_movie_from_omdb(title):
    """
    Fetch movie data from OMDb by title.
    Returns a dictionary if found, otherwise None.
    """
    url = OMDB_URL
    params = {
        "apikey": API_KEY,
        "t": title
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if data.get("Response") == "False":
        return None

    return data


def extract_year(year_value):
    """
    Try to extract a valid year as integer from OMDb data.
    Returns None if parsing fails.
    """
    if not year_value:
        return None

    year_text = str(year_value).strip()

    if len(year_text) >= 4 and year_text[:4].isdigit():
        return int(year_text[:4])

    return None


def validate_user_name(users, name_to_check):
    """
    Check whether a user name already exists in the database.
    Return True if the name already exists, otherwise False.
    """
    prep_name = name_to_check.lower().replace(" ", "").strip()
    for user in users:
        user_name = user.name.lower().replace(" ", "").strip()
        if user_name == prep_name:
            return True
    return False


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
    Return all users.
    """
    users = manager.get_all_users()
    return {
        "users": [
            {"id": user.id, "name": user.name}
            for user in users
        ]
    }


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies_handler_user(user_id):
    """
    Show all movies assigned to a user or add a new movie.
    """
    user = manager.get_user_by_id(user_id)

    if not user:
        flash("User not found.", "error")
        return redirect(url_for("home"))

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

    movie = manager.get_movie_by_title(title)

    if movie is None:
        movie_data = fetch_movie_from_omdb(title)

        if movie_data is None:
            flash(f'Movie "{title}" was not found in OMDb.', "error")
            return redirect(url_for("movies_handler_user", user_id=user_id))

        omdb_title = movie_data.get("Title", title)

        omdb_year = movie_data.get("Year")
        extracted_year = extract_year(omdb_year)
        if extracted_year is None:
            extracted_year = 0

        omdb_director = movie_data.get("Director", "Unknown")

        omdb_poster_url = movie_data.get("Poster")
        if not omdb_poster_url or omdb_poster_url == "N/A":
            omdb_poster_url = url_for(
                "static",
                filename="movie_poster_not_found.png"
            )

        movie = manager.create_movie(
            omdb_title,
            omdb_director,
            extracted_year,
            omdb_poster_url
        )

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
    pass


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
        flash("Movie entry was not found in the user list.", "error")

    return redirect(url_for("movies_handler_user", user_id=user_id))

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
