# **Movie Review Website**
A Django-based website for reviewing movies and TV series, allowing users to explore movie information, manage watchlists, and filter or sort movies by genres, awards, and more. This site integrates with the TMDb API to fetch movie and TV show data.

Features
### 1. **Movie Search**
Search for movies using a custom search bar powered by the TMDb API.
Quickly find details about your favorite movies and TV series.
### 2. **Watchlist**
Users can add movies and TV shows to their personal watchlist.
View, manage, and organize the watchlist according to preferences.
###3. **Filters and Sorting**
Genre and Award Filters: Narrow down movie results by genre or award categories.
Sorting Options: Sort movies by title, release date, or rating to easily browse content.
### 4. **Follow System**
Follow actors, directors, and other users to receive updates.
Get notified when new movies or shows featuring followed actors or directed by followed directors are released.


### **API Integration:**
This project integrates with the TMDb API to fetch real-time movie and TV series data, including:

- Titles
- Overviews
- Release Dates
- Posters and Backdrops

## Installation

1. **Clone the Repository**

   Clone the project from GitHub to your local machine:

   ```bash
   git clone https://github.com/RoelVillaluz/Movie-Website.git
   cd Movie-Website
2. **Create and Activate a Virtual Environment**
    ``` bash
    # Create a virtual environment
    python -m venv venv

    # Activate the virtual environment

    # On Windows
    venv\Scripts\activate

    # On macOS/Linux
    source venv/bin/activate

3. **Install project dependancies**
   ```bash
   pip install -r requirements.txt

4. **Set Up the Database**
   ```bash
   python manage.py migrate

5. **Create a Superuser (Optional)**
   ```bash
   python manage.py createsuperuser

6. **Run the Development Server**
   ```bash
   python manage.py runserver
You can now access the project at http://127.0.0.1:8000/.






