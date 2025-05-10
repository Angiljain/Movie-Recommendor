import streamlit as st
import pickle
import requests

# Page config for better appearance
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #FF4B4B;
        text-align: center;
    }
    .subheader {
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 2rem;
        text-align: center;
    }
    .movie-title {
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-align: center;
        height: 3em;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .recommendation-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin: 2rem 0 1rem 0;
        color: #FF4B4B;
        text-align: center;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        font-weight: 600;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# Cache API calls to improve performance
@st.cache_data
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=90ba7445de4b660876fe1830ffd7cc40"
        data = requests.get(url)
        data = data.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
            return full_path
        return "https://via.placeholder.com/500x750?text=No+Poster+Available"
    except Exception as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"

# Load data
@st.cache_resource
def load_data():
    try:
        movies = pickle.load(open("movies_list.pkl", 'rb'))
        similarity = pickle.load(open("similarity.pkl", 'rb'))
        return movies, similarity
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

movies, similarity = load_data()

if movies is not None and similarity is not None:
    movies_list = movies['title'].values
    
    # App header with gradient
    st.markdown('<div class="main-header">🎬 Movie Recommendation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Find movies similar to your favorites!</div>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown("### How it works")
        st.write("""
        1. Select a movie you like from the dropdown
        2. Click 'Get Recommendations'
        3. See 5 similar movies you might enjoy!
        """)
    
    with col1:
        # Add search functionality to dropdown
        selected_movie = st.selectbox(
            "Search for a movie you like:", 
            movies_list,
            index=None,
            placeholder="Type to search for a movie..."
        )
        
        if selected_movie:
            # Show selected movie poster
            movie_index = movies[movies['title'] == selected_movie].index[0]
            movie_id = movies.iloc[movie_index].id
            poster_path = fetch_poster(movie_id)
            
            st.image(poster_path, width=250, caption=selected_movie)
            
            recommend_button = st.button("Get Recommendations")
        else:
            recommend_button = False
            
            # Show some trending movies when no selection
            st.markdown("### Trending Movies")
            import streamlit.components.v1 as components
            
            imageCarouselComponent = components.declare_component(
                "image-carousel-component", 
                path="frontend/public"
            )
            
            trending_movie_ids = [1632, 299536, 17455, 2830, 429422, 9722, 13972]
            imageUrls = [fetch_poster(movie_id) for movie_id in trending_movie_ids]
            imageCarouselComponent(imageUrls=imageUrls, height=200)

    # Recommendation function
    def recommend(movie):
        try:
            index = movies[movies['title'] == movie].index[0]
            distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
            recommend_movies = []
            recommend_posters = []
            recommend_ratings = []  # You could add ratings if available in your data
            
            for i in distances[1:6]:
                movie_id = movies.iloc[i[0]].id
                recommend_movies.append(movies.iloc[i[0]].title)
                recommend_posters.append(fetch_poster(movie_id))
                # If you have rating data, you could add it here
                # recommend_ratings.append(movies.iloc[i[0]].vote_average)
            
            return recommend_movies, recommend_posters
        except Exception as e:
            st.error(f"Error generating recommendations: {e}")
            return [], []

    # Display recommendations
    if recommend_button and selected_movie:
        with st.spinner('Finding movies you might enjoy...'):
            st.markdown(f'<div class="recommendation-header">Movies similar to "{selected_movie}"</div>', unsafe_allow_html=True)
            movie_names, movie_posters = recommend(selected_movie)
            
            if movie_names and movie_posters:
                # Display recommendations in a grid
                cols = st.columns(5)
                for i, (col, name, poster) in enumerate(zip(cols, movie_names, movie_posters)):
                    with col:
                        st.image(poster, width=200, use_column_width=True)
                        st.markdown(f'<div class="movie-title">{name}</div>', unsafe_allow_html=True)
                        # Add a button to select this movie for new recommendations
                        if st.button(f"Select", key=f"btn_{i}"):
                            # This will trigger a rerun with the new selection
                            st.session_state.new_selection = name
                            st.experimental_rerun()
            else:
                st.info("No recommendations found. Please try another movie.")

    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ using Streamlit and TMDB API")
else:
    st.error("Failed to load necessary data. Please check your data files.")