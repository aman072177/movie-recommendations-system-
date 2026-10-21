import json, os, urllib.parse, urllib.request
from flask import Flask, jsonify, request, send_from_directory
from recommender import Recommender

app = Flask(__name__, static_folder="static")
rec = Recommender(os.path.join(os.path.dirname(__file__), "movies.csv"))
TMDB_KEY = os.environ.get("TMDB_API_KEY", "").strip().strip('"').strip("'")
poster_cache = {}

def tmdb_get(path, params):
    """Call TMDB. Works with the short v3 API Key and the long Read Access Token."""
    headers = {"Accept": "application/json", "User-Agent": "CineMatch/1.0"}
    if len(TMDB_KEY) > 40:                      # long token (JWT) -> Bearer header
        headers["Authorization"] = "Bearer " + TMDB_KEY
    else:                                        # short v3 key -> query parameter
        params = {**params, "api_key": TMDB_KEY}
    url = "https://api.themoviedb.org/3" + path + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=8) as r:
        return json.load(r)

@app.get("/api/poster-check")
def poster_check():
    """Open /api/poster-check in the browser to see why posters are missing."""
    if not TMDB_KEY:
        return jsonify(ok=False, problem="TMDB_API_KEY is not set on this service (check the name and redeploy).")
    try:
        data = tmdb_get("/search/movie", {"query": "Inception"})
        return jsonify(ok=True, key_length=len(TMDB_KEY), results=len(data.get("results", [])))
    except Exception as e:
        return jsonify(ok=False, key_length=len(TMDB_KEY), problem=str(e))

@app.get("/api/poster")
def poster():
    title, year = request.args.get("title", ""), request.args.get("year", "")
    key = f"{title}|{year}"
    if key in poster_cache:
        return jsonify(url=poster_cache[key])
    url = None
    if TMDB_KEY:
        try:
            results = tmdb_get("/search/movie", {"query": title, "year": year}).get("results", [])
            path = next((x["poster_path"] for x in results if x.get("poster_path")), None)
            url = f"https://image.tmdb.org/t/p/w342{path}" if path else None
            poster_cache[key] = url          # cache only successful lookups
        except Exception:
            url = None
    return jsonify(url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
