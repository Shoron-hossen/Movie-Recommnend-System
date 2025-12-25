📌 Project Overview

The Movie Recommender System is a content-based recommendation engine that suggests similar movies based on metadata such as genres, keywords, cast, crew (director), and plot overview. The system leverages Natural Language Processing (NLP) techniques and Cosine Similarity to deliver fast and accurate movie recommendations through an interactive Streamlit web application.

✨ Key Features

Content-based movie recommendation

NLP-driven similarity matching

Uses TMDB 5000 Movies & Credits dataset

Real-time movie posters, ratings, and trailers via TMDB API

Fast response time with parallel API requests

Clean and user-friendly Streamlit interface

🧠 How the System Works

Movie datasets are cleaned and merged

Important textual features are combined into a single representation

Text data is vectorized using Bag of Words (BoW)

Cosine Similarity is calculated between movie vectors

Top-N similar movies are recommended

📊 Dataset Information

Source: TMDB 5000 Movie Dataset (Kaggle)

Total Movies: 4,800+

Selected Features:

Genres

Keywords

Cast (Top 3 actors)

Crew (Director)

Overview

Numeric attributes (budget, revenue, etc.) are excluded to focus strictly on content similarity.

🛠️ Technologies Used

Programming Language

Python 3.9+

Libraries & Tools

Pandas & NumPy

Scikit-learn

NLTK

Streamlit

Requests

Pickle (model storage)

API

TMDB API
