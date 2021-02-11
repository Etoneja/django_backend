import json

from django.contrib.auth.models import User
from django.db import connection
from django.db.models import Count, Case, When, Avg
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book, UserBookRelation
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.user1 = User.objects.create(username="test_username1")
        self.user2 = User.objects.create(username="test_username2")
        self.user3 = User.objects.create(username="test_username3", is_staff=True)

        self.book1 = Book.objects.create(
            name="The Collector 1",
            price=24,
            author_name="Author 1",

        )
        self.book2 = Book.objects.create(
            name="The Collector 2",
            price=25,
            author_name="Author 1"
        )
        self.book3 = Book.objects.create(
            name="The Collector 3",
            price=26,
            author_name="Collector 2",
            owner=self.user1
        )
        UserBookRelation.objects.create(
            user=self.user1, book=self.book3, like=True, rate=3
        )

    def test_get(self):
        url = reverse("book-list")

        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(url)
            self.assertEqual(2, len(queries))

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            annotated_rating=Avg("userbookrelation__rate")
        ).order_by("id")

        serialized_data = BookSerializer(
            books, many=True
        ).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )
        # self.assertEqual(serialized_data[0]["likes_count"], 1)
        self.assertEqual(serialized_data[2]["annotated_likes"], 1)
        self.assertEqual(serialized_data[2]["annotated_rating"], "3.00")

    def test_filter(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"price": 25})

        books = Book.objects.filter(price=25).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            annotated_rating=Avg("userbookrelation__rate")
        ).order_by("id")

        serialized_data = BookSerializer(
            books, many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_search(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"search": "Collector 2"})

        books = Book.objects.filter(id__in=[self.book2.id, self.book3.id]).annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            annotated_rating=Avg("userbookrelation__rate")
        ).order_by("id")

        serialized_data = BookSerializer(
            books, many=True
        ).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_ordering(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"ordering": "-price"})

        books = Book.objects.all().annotate(
            annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
            annotated_rating=Avg("userbookrelation__rate")
        ).order_by("id").order_by("-price")

        serialized_data = BookSerializer(
            books, many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse("book-list")
        data = {
            "name": "extra book yo",
            "price": 24.25,
            "author_name": "Bizzle"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.post(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

        self.assertEqual(self.user1, Book.objects.last().owner)

    def test_update(self):
        url = reverse("book-detail", args=(self.book3.id,))
        data = {
            "name": "extra book yo",
            "price": 24.25,
            "author_name": "Bizzle"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.put(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.book3.refresh_from_db()
        self.assertEqual(24.25, self.book3.price)

    def test_delete(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse("book-detail", args=(self.book3.id,))
        self.client.force_login(self.user1)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())
        self.assertRaises(Book.DoesNotExist, self.book3.refresh_from_db)

    def test_update_not_owner_but_staff(self):
        url = reverse("book-detail", args=(self.book3.id,))
        data = {
            "name": "extra book yo",
            "price": 24.25,
            "author_name": "Bizzle"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user3)
        response = self.client.put(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        self.book3.refresh_from_db()
        self.assertEqual(24.25, self.book3.price)

    def test_update_not_owner_but_staff(self):
        url = reverse("book-detail", args=(self.book3.id,))
        data = {
            "name": "extra book yo",
            "price": 24.25,
            "author_name": "Bizzle"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user2)
        response = self.client.put(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_not_owner(self):
        url = reverse("book-detail", args=(self.book3.id,))
        self.client.force_login(self.user2)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_delete_not_owner_but_staff(self):
        self.assertEqual(3, Book.objects.all().count())
        url = reverse("book-detail", args=(self.book3.id,))
        self.client.force_login(self.user3)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())
        self.assertRaises(Book.DoesNotExist, self.book3.refresh_from_db)


class BooksRelationsAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.user1 = User.objects.create(username="test_username1")
        self.user2 = User.objects.create(username="test_username2")
        self.user3 = User.objects.create(username="test_username3", is_staff=True)

        self.book1 = Book.objects.create(
            name="The Collector 1",
            price=24,
            author_name="Author 1"
        )
        self.book2 = Book.objects.create(
            name="The Collector 2",
            price=25,
            author_name="Author 1"
        )
        self.book3 = Book.objects.create(
            name="The Collector 3",
            price=26,
            author_name="Collector 2",
            owner=self.user1
        )

    def test_like(self):
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = {
            "like": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user1, book=self.book1
        )
        self.assertTrue(relation.like)

    def test_in_bookmarks(self):
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = {
            "in_bookmarks": True,
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user1, book=self.book1
        )
        self.assertTrue(relation.in_bookmarks)

    def test_rate(self):
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = {
            "rate": 3
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        relation = UserBookRelation.objects.get(
            user=self.user1, book=self.book1
        )
        self.assertEqual(3, relation.rate)

    def test_rate_wrong(self):
        url = reverse("userbookrelation-detail", args=(self.book1.id,))
        data = {
            "rate": 6
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user1)
        response = self.client.patch(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code, response.data)
