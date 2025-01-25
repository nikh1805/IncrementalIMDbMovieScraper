from rest_framework import serializers
from .models import Movies


class MovieListSerializer(serializers.ModelSerializer):
    """ Serializer for Movie model """

    class Meta:
        model = Movies
        fields = ['id', 'title', 'rating', 'year', 'summary']


class MovieDetailSerializer(serializers.ModelSerializer):
    """ Serializer for Movie detail """
    tags = serializers.StringRelatedField(many=True)  # Return tag names

    class Meta:
        model = Movies
        fields = '__all__'
