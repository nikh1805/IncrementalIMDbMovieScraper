from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView

from .models import Movies, Tag
from .movie_scraper_adapter import scrape_movies
from .serializers import MovieListSerializer, MovieDetailSerializer


class MovieListView(ListAPIView):
    """ List movies with pagination and filtering by tag """
    serializer_class = MovieListSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """ Get movies, optionally filtered by tag. """
        tag_filter = self.request.query_params.get('tag', None)
        if tag_filter:
            tag = Tag.objects.filter(name__icontains=tag_filter)
            if tag:
                tag = tag.first()
                filtered_movies = Movies.objects.filter(tags=tag)
                if filtered_movies.exists():
                    return filtered_movies
                else:
                    pos_kwargs = {'genre': tag.name} if tag.is_genre else {'keyword': tag.name}
                    scrape_movies(movies_count=tag.movies_count, **pos_kwargs)
                    return Movies.objects.filter(tags=tag)
        else:
            return Movies.objects.all()

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            return Response({
                "status": "SUCCESS",
                "message": "Available Movies fetched successfully. More movies are adding in the background.",
                "data": response.data
            })
        except Exception as e:
            return Response({
                "status": "FAILED",
                "message": str(e),
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MovieDetailView(RetrieveAPIView):
    """ List movies with pagination and filtering by tag """
    serializer_class = MovieDetailSerializer
    pagination_class = LimitOffsetPagination

    def get_object(self):
        return Movies.objects.get(id=self.kwargs.get('id'))

    def retrieve(self, request, *args, **kwargs):
        try:
            response = super().retrieve(request, *args, **kwargs)
            return Response({
                "status": "SUCCESS",
                "message": "Movie detail fetched successfully.",
                "data": response.data
            })
        except Exception as e:
            return Response({
                "status": "FAILED",
                "message": str(e),
                "data": []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
