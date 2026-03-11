from django.shortcuts import render
import requests,random
# Create your views here.
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Profile, Movie,Cast,Profile,Movielist
from .forms import ProfileForm
from .models import Profile
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.http import HttpResponse

def create_admin(request):
    User = get_user_model()

    if not User.objects.filter(email="admin@gmail.com").exists():
        User.objects.create_superuser(
            email="admin@gmail.com",
            password="admin123"
        )
        return HttpResponse("Admin created")

    return HttpResponse("Admin already exists")





def import_tmdb_movies(request):

    url = f"{settings.TMDB_BASE_URL}/discover/movie"

    languages = ['en',"ta", "ml", "te", "hi"]
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

            movies = data["results"]

            genre_names = set()
            for m in movies:
                for gid in m["genre_ids"]:
                    if gid in GENRE_MAP:
                        genre_names.add(GENRE_MAP[gid])

                genre_string = ", ".join(genre_names)

                if not m["poster_path"] or not m['backdrop_path']:
                    continue
                movie = Movie.objects.create(
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
                cast_data = cast_response.json()["cast"][:6]
                for actor in cast_data:
                    if not actor["profile_path"]:
                      continue
                    Cast.objects.create(
                    movie=movie,
                    name=actor["name"],
                    character=actor["character"],
                    image=actor["profile_path"]
                )      
    return HttpResponse('added')

def home(request):
    if request.user.is_authenticated:
        return redirect('Visionapp:profile-list')
    return render(request, 'index.html')


@login_required
def movie_list(request):
    profile_id=request.session.get("profile_id")
    if not profile_id:
        return redirect('Visionapp:profile-list')
    
    profile = Profile.objects.get(uuid=profile_id)
    
    if profile not in request.user.profiles.all():
        return redirect('Visionapp:profile-list')
    movies = Movie.objects.all().order_by('?')
   
    random_movie = random.choice(movies)
    trending = movies.order_by('-popularity')[:10]
    top_rated = movies.order_by('-rating')[:10]
    action_movies =movies.filter(genre__icontains="Action")[:10]
    comedy_movies = movies.filter(genre__icontains="Comedy")[:10]
    context = {
        "movies": movies,
        "random_movie": random_movie,
        "trending": trending,
        "top_rated": top_rated,
        "action_movies": action_movies,
        "comedy_movies": comedy_movies
    }

    return render(request, "movielist.html", context)
    
    
@login_required
def movie_detail(request, movie_id):
    try:
        movie = Movie.objects.get(uuid=movie_id)
        movies = Movie.objects.all()
        cast = movie.casts.all()
        
        
        context = {
            'movie': movie,
            'movies':movies,
            'cast':cast
        }
        return render(request, 'moviedetail.html', context)
    except Movie.DoesNotExist:
        return redirect('Visionapp:profile-list')
    
    
@login_required
def profile_list(request):
    profiles = request.user.profiles.all()
    context = {
        'profiles': profiles
    }

    return render(request, 'profilelist.html', context)

@login_required
def set_profile(request, profile_id):
    request.session["profile_id"] = str(profile_id)
    return redirect("Visionapp:movie-list")

@login_required
def profile_create(request):

    if request.method == "POST":
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            request.user.profiles.add(profile)
    else:
        form = ProfileForm()
    context = {
        'form': form
    }

    return render(request, 'profilecreate.html', context)

@login_required
def play_movie(request, movie_id):
    
        movie = get_object_or_404(Movie, uuid=movie_id)
        movie = movie.video.values()
        context = {'movie': list(movie)}
        return render(request, 'play.html', context)
    
# 'Visionapp:play-movie' movie_id=random_movie.uuid
# url 'Visionapp:play-movie' movie_id=movie.uuid 

def search_movies(request):
    language = request.GET.get("language")
    if language!='all':
        movies = Movie.objects.filter(language=language) 
        print(movies)   
    search = request.GET.get("search")
    if search:
        movies = Movie.objects.filter(
            title__icontains=search
           )
    random_movie = random.choice(movies)
  
    return render(request, "search.html", {"movies": movies,'random_movie':random_movie})

   
   
def add_list(request,movie_id):
    movies=get_object_or_404(Movie,uuid=movie_id)
    profile_id=request.session.get("profile_id")
    profile=get_object_or_404(Profile,uuid=profile_id)
    Movielist.objects.get_or_create(profile=profile,movie=movies)
    return redirect(request.META.get('HTTP_REFERER'))

def del_list(request,movie_id):
    movies=get_object_or_404(Movie,uuid=movie_id)
    profile_id=request.session.get("profile_id")
    profile=get_object_or_404(Profile,uuid=profile_id)
    Movielist.objects.filter(profile=profile,movie=movies).delete()
    return redirect(request.META.get('HTTP_REFERER'))

def my_list(request):
    profile_id=request.session.get("profile_id")
    profile=get_object_or_404(Profile,uuid=profile_id)
    movies=Movielist.objects.filter(profile=profile)
    context={'movies':movies}
    return render(request,'mylist.html',context)


