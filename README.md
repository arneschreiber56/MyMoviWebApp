🎬 MyMovieWebApp

A simple Flask web application to manage users and their movie collections.

⸻

🚀 Features
	•	👤 Create and manage users
	•	🎥 Add movies via OMDb API
	•	🗄️ Store movies in a local SQLite database
	•	🔗 Assign movies to users
	•	⭐ Track per-user movie status (watchlist, watched, favorite)
	•	🔢 Add ratings (1–10) and reviews
	•	✏️ Update and delete movies
	•	⚠️ Error handling (404 / 500 pages)
	•	🎨 Clean UI with custom CSS

⸻

🛠️ Tech Stack
	•	Python
	•	Flask
	•	SQLAlchemy
	•	SQLite
	•	HTML / CSS
	•	OMDb API

⸻

⚙️ Setup

1. Clone the repository

git clone 
cd MyMovieWebApp

2. Create virtual environment

python -m venv venv
source venv/bin/activate   (Mac/Linux)
venv\Scripts\activate      (Windows)

3. Install dependencies

pip install -r requirements.txt

4. Create .env file

API_KEY=your_omdb_api_key
SECRET_KEY=your_secret_key

5. Run the app

python app.py

6. Open in browser

http://localhost:5001

⸻

📁 Project Structure

MyMovieWebApp/
│
├── app.py                # Flask routes and app setup
├── data_manager.py       # CRUD logic
├── models.py             # Database models
├── help_functions.py     # Helper functions (OMDb, validation)
│
├── templates/            # HTML templates
├── static/               # CSS, images
├── data/                 # SQLite database
│
├── requirements.txt
└── README.md

⸻

🧠 Notes
	•	Movies are fetched from the OMDb API
	•	Duplicate users and movies are prevented
	•	User-specific data (status, rating, review) is stored separately

⸻

🔮 Future Improvements
	•	🔍 Search and filtering
	•	📄 Pagination
	•	🔐 User authentication
	•	🌐 REST API endpoints
	•	🧪 Automated tests

⸻

👤 Author

Arne