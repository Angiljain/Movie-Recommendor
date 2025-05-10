# app.py
from flask import Flask, render_template, request, jsonify
import pickle
import requests
import os

app = Flask(__name__)

# Load data
def load_data():
    movies = pickle.load(open("movies_list.pkl", 'rb'))
    similarity = pickle.load(open("similarity.pkl", 'rb'))
    return movies, similarity

movies, similarity = load_data()
movies_list = movies['title'].values.tolist()

# Fetch movie poster
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=90ba7445de4b660876fe1830ffd7cc40"
        response = requests.get(url)
        data = response.json()
        
        # Check if API returned valid result
        if 'poster_path' in data and data['poster_path']:
            return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        else:
            print(f"No poster found for movie ID: {movie_id} - {data.get('status_message', '')}")
            return "https://via.placeholder.com/300x450?text=No+Poster"
    except Exception as e:
        print(f"Error fetching poster for movie ID {movie_id}: {e}")
        return "https://via.placeholder.com/300x450?text=No+Poster"


# Get recommendations
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movies = []
    recommend_posters = []
    for i in distance[1:6]:
        movie_id = movies.iloc[i[0]].id
        recommend_movies.append({
            'title': movies.iloc[i[0]].title,
            'poster': fetch_poster(movie_id)
        })
    return recommend_movies

# Define trending movies
TRENDING_MOVIES = [1632, 299536, 17455, 2830, 429422, 9722, 13972,1547]

@app.route('/')
def home():
    # Get trending movie posters for the carousel
    trending_movies = []
    for movie_id in TRENDING_MOVIES:
        # Find movie title from id
        movie_title = ""
        for i, movie in movies.iterrows():
            if movie.id == movie_id:
                movie_title = movie.title
                break
        
        trending_movies.append({
            'id': movie_id,
            'title': movie_title,
            'poster': fetch_poster(movie_id)
        })
    
    return render_template('index.html', movies_list=movies_list, trending_movies=trending_movies)

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    movie = request.form['movie']
    recommendations = recommend(movie)
    
    # Get selected movie details
    selected_movie_index = movies[movies['title'] == movie].index[0]
    selected_movie_id = movies.iloc[selected_movie_index].id
    selected_movie_poster = fetch_poster(selected_movie_id)
    
    return render_template(
        'recommendations.html', 
        selected_movie=movie,
        selected_movie_poster=selected_movie_poster,
        recommendations=recommendations
    )

@app.route('/search', methods=['GET'])
def search_movies():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify([])
    
    # Filter movies that contain the query string
    filtered_movies = [movie for movie in movies_list if query in movie.lower()]
    return jsonify(filtered_movies[:10])  # Return top 10 matches

if __name__ == '__main__':
    app.run(debug=True)