from flask import Flask, render_template, request
import pandas as pd
import heapq

app = Flask(__name__)

# Load movie data from the CSV
def load_movies():
    df = pd.read_csv('imdb_top_1000.csv')
    # Select only necessary columns
    movies = df[['Series_Title', 'Released_Year', 'Genre', 'IMDB_Rating', 'No_of_Votes']].copy()
    # Convert necessary columns to numeric types
    movies['Released_Year'] = pd.to_numeric(movies['Released_Year'], errors='coerce')
    movies['IMDB_Rating'] = pd.to_numeric(movies['IMDB_Rating'], errors='coerce')
    movies['No_of_Votes'] = pd.to_numeric(movies['No_of_Votes'], errors='coerce')
    return movies

# Filter movies by IMDb rating range
def filter_movies_by_rating(movies, min_rating=None, max_rating=None):
    filtered_movies = movies
    if min_rating:
        filtered_movies = filtered_movies[filtered_movies['IMDB_Rating'] >= float(min_rating)]
    if max_rating:
        filtered_movies = filtered_movies[filtered_movies['IMDB_Rating'] <= float(max_rating)]
    return filtered_movies

# A* search to find the best movie in a genre
def a_star_search_best_movie(movies, genre=None):
    def heuristic(movie):
        # Heuristic is a weighted combination of IMDb rating, votes, and recency
        rating_weight = 1.0
        votes_weight = 0.3
        year_weight = 0.1
        
        score = (rating_weight * movie['IMDB_Rating'] + 
                 votes_weight * movie['No_of_Votes'] / 1e6 + 
                 year_weight * (2024 - movie['Released_Year']))  # Assuming 2024 as current year
        return -score  # Negating to use with a min-heap
    
    # Filter movies by genre
    genre_filtered_movies = movies[movies['Genre'].str.contains(genre, case=False, na=False)] if genre else movies
    
    # Priority queue (min-heap)
    priority_queue = []
    for _, movie in genre_filtered_movies.iterrows():
        heapq.heappush(priority_queue, (heuristic(movie), movie))
    
    # Return the movie with the best heuristic score (highest IMDb, votes, etc.)
    if priority_queue:
        best_movie = heapq.heappop(priority_queue)[1]
        return best_movie
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    movies = load_movies()  # Always reset to the full dataset at the start of a request
    
    # Initialize filtered_movies as the full dataset
    filtered_movies = movies.copy()
    
    if request.method == 'POST':
        min_rating = request.form.get('min_rating')
        max_rating = request.form.get('max_rating')
        genre = request.form.get('genre')
        genre_only = request.form.get('genre_only')

        # Print the filtering parameters
        print(f"Filtering with min_rating: {min_rating}, max_rating: {max_rating}, genre: {genre}, genre_only: {genre_only}") 

        # If the user submitted a genre search without ratings
        if genre_only:
            filtered_movies = filtered_movies[filtered_movies['Genre'].str.contains(genre_only, case=False, na=False)]
        else:
            # Start by filtering by IMDb rating range
            filtered_movies = filter_movies_by_rating(filtered_movies, min_rating, max_rating)

            # Check if a genre has been specified and filter by genre as well
            if genre:
                filtered_movies = filtered_movies[filtered_movies['Genre'].str.contains(genre, case=False, na=False)]

            # Debug: Check how many movies are left after rating and genre filtering
            print(f"Filtered movies count after rating and genre filter: {len(filtered_movies)}")  
        
        if len(filtered_movies) > 0:
            print("Filtered Movies After Rating and Genre Filter:")
            print(filtered_movies[['Series_Title', 'IMDB_Rating', 'Released_Year', 'Genre', 'No_of_Votes']])  

    # Render all filtered movies or the whole dataset if no filters are applied
    return render_template('index.html', movies=filtered_movies.to_dict('records'))



if __name__ == '__main__':
    app.run(debug=True)
