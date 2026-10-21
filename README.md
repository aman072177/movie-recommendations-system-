# CineMatch - Movie Recommendation System using NLP and Python

Recommends movies from a plot description or a movie you already like.

## How the NLP works
1. **Text cleaning:** lowercase, tokenise, remove stop words, stem words (`recommender.py`).
2. **TF-IDF vectorisation:** each movie (plot + genres + keywords) becomes a weighted word vector.
3. **Cosine similarity:** the closest vectors are the best recommendations.
   - *Similar to a movie*: compares that movie with all others.
   - *Describe what you want*: converts your sentence into a vector and compares it.

## Run locally
```bash
pip install -r requirements.txt
python app.py        # open http://localhost:5000
```

## Movie posters (TMDB)
Posters come from the free TMDB API. Without a key the site still works and shows styled title cards.
1. Create a free account at themoviedb.org, then Settings -> API -> request an API key.
2. Set the environment variable `TMDB_API_KEY` (locally or on Render).

## Deploy on Render
1. Push this repo to GitHub.
2. Render -> New -> Web Service -> connect the repo.
3. Runtime **Python 3**. Build command: `pip install -r requirements.txt`. Start command: `gunicorn app:app`.
4. Under **Environment**, add `TMDB_API_KEY` with your key. Create the service.

## Files
| File | Purpose |
|---|---|
| `app.py` | Flask API and poster lookup |
| `recommender.py` | NLP engine (TF-IDF, cosine similarity) |
| `movies.csv` | Dataset: 105 movies (66 Hindi, 39 English) with IMDb ratings; easy to extend |
| `static/index.html` | Website |
