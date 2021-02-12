from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from store.models import Book, UserBookRelation


class BookReaderSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")


class BookSerializer(ModelSerializer):

    # likes_count = serializers.SerializerMethodField(read_only=True)
    annotated_likes = serializers.IntegerField(read_only=True)
    annotated_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    owner_name = serializers.CharField(read_only=True, default="")
    readers = BookReaderSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = (
            "id", "name", "price", "author_name",
            "annotated_likes", "annotated_rating",
            "owner_name", "readers"
        )

    # def get_likes_count(self, instance):
    #     likes_count = UserBookRelation.objects.filter(book=instance, like=True).count()
    #     return likes_count


class UserBookSerializer(ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ("book", "like", "in_bookmarks", "rate")



