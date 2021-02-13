from django.contrib.auth.models import User
from django.db.models import Count, Case, When, Avg, F, Value
from django.db.models.functions import Coalesce
from django.test import TestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):

    def setUp(self):
        self.user1 = User.objects.create(username="test_username1")
        self.user2 = User.objects.create(username="test_username2")
        self.user3 = User.objects.create(username="test_username3")

        self.book1 = Book.objects.create(name="The Collector 1", price=24, owner=self.user1)
        self.book2 = Book.objects.create(name="The Collector 2", price=25)

        UserBookRelation.objects.create(user=self.user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=self.user3, book=self.book1, like=True, rate=4)

        UserBookRelation.objects.create(user=self.user1, book=self.book2, like=True, rate=3)
        UserBookRelation.objects.create(user=self.user2, book=self.book2, like=True, rate=4)
        self.user_book6 = UserBookRelation.objects.create(user=self.user3, book=self.book2, like=False)
        self.user_book6.rate = 4
        self.user_book6.save()

    def test_ok(self):

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            owner_name=Coalesce(F("owner__username"), Value(""))
        ).order_by("id")
        data = BookSerializer(books, many=True).data

        expected_data = [
            {
                "id": self.book1.id,
                "name": "The Collector 1",
                "price": "24.00",
                "author_name": "",
                "annotated_likes": 3,
                "rating": "4.67",
                "owner_name": "test_username1",
                "readers": [
                    {
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "first_name": "",
                        "last_name": ""
                    }
                ]
            },
            {
                "id": self.book2.id,
                "name": "The Collector 2",
                "price": "25.00",
                "author_name": "",
                "annotated_likes": 2,
                "rating": "3.67",
                "owner_name": "",
                "readers": [
                    {
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "first_name": "",
                        "last_name": ""
                    },
                    {
                        "first_name": "",
                        "last_name": ""
                    }
                ]
            },
        ]
        self.assertEqual(expected_data, data)
