"""NLP engine: text cleaning -> TF-IDF vectors -> cosine similarity."""
import csv, re
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity

SUFFIXES = ("ing", "ed", "es", "ly", "s")

def stem(word):
    """Very small suffix-stripping stemmer (e.g. 'travels' -> 'travel')."""
    for suf in SUFFIXES:
        if word.endswith(suf) and len(word) - len(suf) >= 3:
            return word[: -len(suf)]
    return word

def analyze(text):
    """Lowercase -> tokenise -> remove stop words -> stem."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return [stem(t) for t in tokens if t not in ENGLISH_STOP_WORDS and len(t) > 2]

class Recommender:
    def __init__(self, path="movies.csv"):
        with open(path, encoding="utf-8") as f:
            self.movies = list(csv.DictReader(f))
        # Genres and keywords are repeated so they weigh more than the plot text.
        docs = [f"{m['overview']} {(m['genres'] + ' ') * 3} {(m['keywords'] + ' ') * 2} {m['language']}" for m in self.movies]
        self.vectorizer = TfidfVectorizer(analyzer=analyze)
        self.matrix = self.vectorizer.fit_transform(docs)
        self.index = {m["title"].lower(): i for i, m in enumerate(self.movies)}

    def _pack(self, scores, n, skip=None, lang=""):
        order = scores.argsort()[::-1]
        out = []
        for i in order:
            if i == skip or scores[i] <= 0 or (lang and self.movies[i]["language"] != lang):
                continue
            m = dict(self.movies[i]); m["score"] = round(float(scores[i]) * 100)
            out.append(m)
            if len(out) == n:
                break
        return out

    def similar(self, title, n=6, lang=""):
        i = self.index.get(title.strip().lower())
        if i is None:
            return None
        return self._pack(cosine_similarity(self.matrix[i], self.matrix).ravel(), n, skip=i, lang=lang)

    def search(self, text, n=6, lang=""):
        vec = self.vectorizer.transform([text])
        return self._pack(cosine_similarity(vec, self.matrix).ravel(), n, lang=lang)
