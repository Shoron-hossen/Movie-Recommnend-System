
🎬 Movie Recommender System
Content-Based Movie Recommendation using Machine Learning

The Movie Recommender System is a content-based recommendation engine that suggests similar movies based on movie metadata such as genres, keywords, cast, crew (director), and plot overview. The system applies Natural Language Processing (NLP) and Cosine Similarity to provide accurate and fast recommendations through an interactive Streamlit web application.

🚀 Features

Content-based movie recommendation

Uses TMDB 5000 Movies & Credits dataset

NLP-based text processing

Cosine similarity for movie matching

Real-time posters, ratings, and trailers using TMDB API

Fast and interactive Streamlit interface

Optimized performance with parallel API calls

🧠 Working Principle

Movie metadata is cleaned and merged from TMDB datasets

Important text features are combined into a single tags column

Text data is vectorized using Bag of Words (CountVectorizer)

Cosine Similarity is computed between movie vectors

Top 5 similar movies are recommended based on similarity score

📊 Dataset

Source: TMDB 5000 Movie Dataset (Kaggle)

Total Movies: 4,800+

Selected Features:

Genres

Keywords

Cast (Top 3 actors)

Crew (Director)

Overview

Numeric attributes such as budget and revenue are removed to focus only on content similarity.

🛠️ Technologies Used

Programming Language: Python 3.9

Libraries:

Pandas

NumPy

Scikit-learn

NLTK

Streamlit

Requests

Model Storage: Pickle

API: TMDB API
