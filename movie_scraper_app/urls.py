from django.urls import path

from .views import MovieListView, MovieDetailView

urlpatterns = [
    path('api/movies/', MovieListView.as_view(), name='movie-list'),
    path('api/movie/<int:id>', MovieDetailView.as_view(), name='movie-detail'),
]