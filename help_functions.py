"""Provides helper functions for flask route functions in app.py"""
import requests


def fetch_movie_from_omdb(
    title: str,
    api_key: str,
    omdb_url: str = "http://www.omdbapi.com/"
) -> dict | None:
    """
    Fetch movie data from OMDb by title.

    Returns a dictionary if found, otherwise None.
    """
    params = {
        "apikey": api_key,
        "t": title
    }

    try:
        response = requests.get(omdb_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None

    if data.get("Response") == "False":
        return None

    return data


def extract_year(year_value) -> int | None:
    """
    Try to extract a valid year as integer from OMDb data.

    Returns None if extraction fails.
    """
    if not year_value:
        return None

    year_text = str(year_value).strip()

    if len(year_text) >= 4 and year_text[:4].isdigit():
        return int(year_text[:4])

    return None


def validate_user_name(users, name_to_check: str) -> bool:
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


def get_or_create_movie_by_title(title: str, manager, api_key: str) -> object | None:
    """
    Return an existing movie by title or create it from OMDb data.

    Returns:
        Movie: if the movie exists or was successfully created
        None: if the movie was not found in OMDb or the request failed
    """
    movie = manager.get_movie_by_title(title)

    if movie is not None:
        return movie

    movie_data = fetch_movie_from_omdb(title, api_key)
    if movie_data is None:
        return None

    omdb_title = movie_data.get("Title", title)

    omdb_year = movie_data.get("Year")
    extracted_year = extract_year(omdb_year)
    if extracted_year is None:
        extracted_year = 0

    omdb_director = movie_data.get("Director", "Unknown")

    omdb_poster_url = movie_data.get("Poster")
    if not omdb_poster_url or omdb_poster_url == "N/A":
        omdb_poster_url = "/static/movie_poster_not_found.png"

    movie = manager.create_movie(
        omdb_title,
        omdb_director,
        extracted_year,
        omdb_poster_url
    )

    return movie