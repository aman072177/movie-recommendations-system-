import json, os, urllib.parse, urllib.request
from flask import Flask, jsonify, request, send_from_directory
from recommender import Recommender

app = Flask(__name__, static_folder="static")
rec = Recommender(os.path.join(os.path.dirname(__file__), "movies.csv"))
TMDB_KEY = os.environ.get("TMDB_API_KEY", "")
poster_cache = {}

@app.get("/")
def home():
    return send_from_directory("static", "index.html")

@app.get("/api/movies")
def movies():
    return jsonify(rec.movies)

@app.get("/api/recommend")
def recommend():
    result = rec.similar(request.args.get("title", ""), int(request.args.get("n", 6)), request.args.get("lang", ""))
    if result is None:
        return jsonify(error="Movie not found. Pick a title from the list."), 404
    return jsonify(result)

@app.get("/api/search")
def search():
    q = request.args.get("q", "").strip()
    if len(q) < 3:
        return jsonify(error="Please describe the movie in a few words."), 400
    result = rec.search(q, int(request.args.get("n", 6)), request.args.get("lang", ""))
    if not result:
        return jsonify(error="No matches. Try different words."), 404
    return jsonify(result)

@app.get("/api/poster")
def poster():
    """Look up a poster on TMDB (needs the free TMDB_API_KEY environment variable)."""
    title, year = request.args.get("title", ""), request.args.get("year", "")
    key = f"{title}|{year}"
    if key not in poster_cache:
        url = None
        if TMDB_KEY:
            try:
                q = urllib.parse.urlencode({"api_key": TMDB_KEY, "query": title, "year": year})
                with urllib.request.urlopen(f"https://api.themoviedb.org/3/search/movie?{q}", timeout=6) as r:
                    results = json.load(r).get("results", [])
                path = next((x["poster_path"] for x in results if x.get("poster_path")), None)
                url = f"https://image.tmdb.org/t/p/w342{path}" if path else None
            except Exception:
                url = None
        poster_cache[key] = url
    return jsonify(url=poster_cache[key])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
