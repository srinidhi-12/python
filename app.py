import streamlit as st
import pickle
import requests
import pandas as pd

API_KEY = '9e7a194d06177b46d762e6e7c60e730b'
POSTER_PLACEHOLDER = "https://via.placeholder.com/200x300.png?text=No+Poster+Available"

def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        description = data.get('overview', 'No description available.')
        rating = data.get('vote_average', 'No rating available.')
        genre_list = data.get('genres', [])
        genre = ', '.join([genre['name'] for genre in genre_list]) if genre_list else 'No genre available.'
        vote_count = data.get('vote_count', 0)
        likes = f"{vote_count} likes ❤️"
        full_path = f"https://image.tmdb.org/t/p/w200/{poster_path}" if poster_path else POSTER_PLACEHOLDER
        return full_path, description, rating, genre, likes
    except requests.exceptions.RequestException:
        return POSTER_PLACEHOLDER, "No description available.", "No rating available.", "No genre available.", "0 likes ❤️"

def load_data():
    try:
        movies = pickle.load(open("movies_list.pkl", 'rb'))
        similarity = pickle.load(open("similarity.pkl", 'rb'))
        dataset = pd.read_csv("dataset.csv")
        return movies, similarity, dataset
    except Exception as e:
        st.error(f"Error loading files. Ensure 'movies_list.pkl', 'similarity.pkl', and 'dataset.csv' are available. Error: {e}")
        st.stop()

def recommend(movie, movies, similarity):
    try:
        index = movies[movies['title'] == movie].index[0]
        distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
        recommend_movie = []
        recommend_poster = []
        recommend_description = []
        recommend_rating = []
        recommend_genre = []
        recommend_likes = []
        for i in distance[1:6]:
            movie_id = movies.iloc[i[0]].id
            recommend_movie.append(movies.iloc[i[0]].title)
            poster, description, rating, genre, likes = fetch_movie_details(movie_id)
            recommend_poster.append(poster)
            recommend_description.append(description)
            recommend_rating.append(rating)
            recommend_genre.append(genre)
            recommend_likes.append(likes)
        return recommend_movie, recommend_poster, recommend_description, recommend_rating, recommend_genre, recommend_likes
    except Exception as e:
        st.error(f"Error in recommendation process. Error: {e}")
        return [], [], [], [], [], []

movies, similarity, dataset = load_data()
movies_list = movies['title'].values

# Exclude "Top Gun: Maverick" from movies list
movies_list = [movie for movie in movies_list if movie != "Top Gun: Maverick"]

st.header("Movie Recommender System")

st.subheader("Movie Recommendation")
selectvalue = st.selectbox("Select movie from dropdown", movies_list)

if st.button("Show Recommend"):
    movie_names, movie_posters, movie_descriptions, movie_ratings, movie_genres, movie_likes = recommend(selectvalue, movies, similarity)
    if movie_names and movie_posters and movie_descriptions and movie_ratings and movie_genres and movie_likes:
        st.subheader("Recommended Movies")
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if idx < len(movie_names):
                with col:
                    st.markdown(f"**{movie_names[idx]}**", unsafe_allow_html=True)
                    st.image(movie_posters[idx])
                    st.caption(movie_descriptions[idx])
                    st.markdown(f"**Rating: {movie_ratings[idx]}**")
                    st.markdown(f"<span style='color: green; font-family:Arial;'>{movie_genres[idx]}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: red; font-family:Arial;'>{movie_likes[idx]}</span>", unsafe_allow_html=True)
    else:
        st.error("No recommendations found.")

st.subheader("Most Liked Movies")
num_movies = st.slider("Select number of movies to be displayed", 1, 20, 10)
top_rated_movies = dataset.nlargest(num_movies, 'vote_count')[['title', 'id']]

movie_row = st.columns(num_movies)

for idx, row in enumerate(top_rated_movies.itertuples()):
    movie_id = row.id
    poster, _, rating, genre, likes = fetch_movie_details(movie_id)
    with movie_row[idx]:
        st.markdown(f"**{row.title}**")
        st.image(poster)
        st.markdown(f"**Rating: {rating}**")
        st.markdown(f"<span style='color: green; font-family:Arial;'>{genre}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='color: red; font-family:Arial;'>{likes}</span>", unsafe_allow_html=True)

# Display top-rated movies based on selected genre
st.subheader("Select the genre")
genres_to_display = ['Drama', 'Crime', 'Comedy', 'Romance', 'Thriller']
selected_genre = st.selectbox("Select genre", genres_to_display)

if selected_genre:
    genre_movies = dataset[dataset['genre'].str.contains(selected_genre, na=False)]
    top_genre_movies = genre_movies.nlargest(num_movies, 'vote_count')[['title', 'id']]
    genre_row = st.columns(num_movies)

    for idx, row in enumerate(top_genre_movies.itertuples()):
        movie_id = row.id
        poster, _, rating, genre, likes = fetch_movie_details(movie_id)
        with genre_row[idx]:
            st.markdown(f"**{row.title}**")
            st.image(poster)
            st.markdown(f"**Rating: {rating}**")
            st.markdown(f"<span style='color: green; font-family:Arial;'>{genre}</span>", unsafe_allow_html=True)
            st.markdown(f"<span style='color: red; font-family:Arial;'>{likes}</span>", unsafe_allow_html=True)
