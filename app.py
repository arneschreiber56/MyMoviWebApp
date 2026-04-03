import os
from flask import Flask, render_template, request, redirect, url_for

from data_manager import DataManager
from models import db

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
    pass


@app.route('/users', methods=['GET'])
def list_users():
    """
    Lists users by using a Class DataManager method.
    """
    users = manager.get_all_users()
    return str(users)


@app.route('/users/<int:user_id>/movies', methods=['GET', 'POST'])
def movies_handler_user(user_id):
    """
    This route will show a list of all movies assigned to the user or will add
    a new movie. If it is a GET request, it retrieves the movie list.
    If it is a POST request, it adds a new movie. When a user adds a new movie,
    try to retrieve the information from OMDb, consolidate it into a
    Movie object, and use the DataManager to add the movie.
    """
    pass


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
    Remove a specific movie from a user's movie list..
    """
    pass

# Determine the absolute path of the project directory
basedir = os.path.abspath(os.path.dirname(__file__))

# Create the /data folder if it does not already exist
os.makedirs(os.path.join(basedir, "data"), exist_ok=True)

# Configure the SQLite database path
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/movie_db.sqlite')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

manager = DataManager(db.session)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
