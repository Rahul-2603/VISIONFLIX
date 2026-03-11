from django.urls import path
from .views import *



app_name = "Visionapp"

urlpatterns = [
    path('', home, name="home"),
    path("search/", search_movies, name="search"),
    path('movies/', movie_list, name='movie-list'),
    path('profiles/', profile_list, name='profile-list'),
    path('profiles/create/', profile_create, name='profile-create'),
    path('movie/<uuid:movie_id>/', movie_detail, name='movie-detail'),
    path('play/<uuid:movie_id>/', play_movie, name='play-movie'),
    path("import-movies/", import_tmdb_movies, name="import-movies"),
    path('set_profile/<uuid:profile_id>/',set_profile,name='set_profile'),
    path('Mylist/',my_list,name='Mylist'),
    path('add_list/<uuid:movie_id>/',add_list,name='add_list'),
    path('del_list/<uuid:movie_id>/',del_list,name='del_list'),
    ]