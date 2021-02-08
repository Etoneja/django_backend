from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):

    def test_ok(self):

        user1 = User.objects.create(username="test_username1")
        user2 = User.objects.create(username="test_username2")
        user3 = User.objects.create(username="test_username3")

        book1 = Book.objects.create(name="The Collector 1", price=24)
        book2 = Book.objects.create(name="The Collector 2", price=25)

        UserBookRelation.objects.create(user=user1, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=book1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=book2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=book2, like=True, rate=4)
        UserBookRelation.objects.create(user=user3, book=book2, like=False)

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            annotated_rating=Avg("userbookrelation__rate")
        ).order_by("id")
        data = BookSerializer(books, many=True).data

        expected_data = [
            {
                "id": book1.id,
                "name": "The Collector 1",
                "price": "24.00",
                "author_name": "",
                "likes_count": 3,
                "annotated_likes": 3,
                "annotated_rating": "4.67"
            },
            {
                "id": book2.id,
                "name": "The Collector 2",
                "price": "25.00",
                "author_name": "",
                "likes_count": 2,
                "annotated_likes": 2,
                "annotated_rating": "3.50"
            },
        ]
        self.assertEqual(expected_data, data)
