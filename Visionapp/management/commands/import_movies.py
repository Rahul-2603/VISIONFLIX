from django.core.management.base import BaseCommand
from django.conf import settings
from Visionapp.models import Movie, Cast
import requests


class Command(BaseCommand):

    help = "Import movies from TMDB"

    def handle(self, *args, **kwargs):

        url = f"{settings.TMDB_BASE_URL}/discover/movie"

        languages = ['en', 'ta', 'ml', 'te', 'hi']

        GENRE_MAP = {
            28: "Action",
            12: "Adventure",
            16: "Animation",
            35: "Comedy",
            80: "Crime",
            18: "Drama",
            10749: "Romance",
            53: "Thriller",
            878: "Sci-Fi",
            27: "Horror"
        }

        for lang in languages:
            for page in range(1,11):

                params = {
                    "api_key": settings.TMDB_API_KEY,
                    "with_original_language": lang,
                    "sort_by": "popularity.desc",
                    "primary_release_date.gte": "2020-01-01",
                    "vote_count.gte": 100,
                    "page": page
                }

                response = requests.get(url, params=params)
                data = response.json()

                movies = data.get("results", [])

                for m in movies:

                    genre_names = set()

                    for gid in m["genre_ids"]:
                        if gid in GENRE_MAP:
                            genre_names.add(GENRE_MAP[gid])

                    genre_string = ", ".join(genre_names)

                    if not m.get("poster_path") or not m.get("backdrop_path"):
                        continue

                    movie = Movie.objects.get_or_create(
                        title=m["title"],
                        description=m["overview"],
                        poster=m["poster_path"],
                        backdrop=m["backdrop_path"],
                        rating=m["vote_average"],
                        release_date=m["release_date"],
                        language=m["original_language"],
                        popularity=m["popularity"],
                        genre=genre_string
                    )

                    # Fetch Cast
                    cast_url = f"https://api.themoviedb.org/3/movie/{m['id']}/credits"

                    cast_response = requests.get(cast_url, params=params)

                    cast_data = cast_response.json().get("cast", [])[:6]

                    for actor in cast_data:

                        if not actor.get("profile_path"):
                            continue

                        Cast.objects.create(
                            movie=movie,
                            name=actor["name"],
                            character=actor["character"],
                            image=actor["profile_path"]
                        )

        self.stdout.write(self.style.SUCCESS("Movies imported successfully"))

