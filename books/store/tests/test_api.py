import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username="test_username")

        self.book1 = Book.objects.create(
            name="The Collector 1", price=24, author_name="Author 1"
        )
        self.book2 = Book.objects.create(
            name="The Collector 2", price=25, author_name="Author 1"
        )
        self.book3 = Book.objects.create(
            name="The Collector 3", price=26, author_name="Collector 2"
        )

    def test_get(self):
        url = reverse("book-list")
        response = self.client.get(url)

        serialized_data = BookSerializer(
            [self.book1, self.book2, self.book3], many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_filter(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"price": 25})

        serialized_data = BookSerializer(
            [self.book2], many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_search(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"search": "Collector 2"})

        serialized_data = BookSerializer(
            [self.book2, self.book3], many=True
        ).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )

    def test_ordering(self):
        url = reverse("book-list")
        response = self.client.get(url, data={"ordering": "-price"})

        serialized_data = BookSerializer(
            [self.book3, self.book2, self.book1], many=True
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
        self.client.force_login(self.user)
        response = self.client.post(
            url, data=json_data,
            content_type="application/json"
        )
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(4, Book.objects.all().count())

    def test_update(self):
        url = reverse("book-detail", args=(self.book3.id,))
        data = {
            "name": "extra book yo",
            "price": 24.25,
            "author_name": "Bizzle"
        }
        json_data = json.dumps(data)
        self.client.force_login(self.user)
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
        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(2, Book.objects.all().count())
        self.assertRaises(Book.DoesNotExist, self.book3.refresh_from_db)
