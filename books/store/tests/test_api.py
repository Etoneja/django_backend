from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from store.models import Book
from store.serializers import BookSerializer


class BooksAPITestCase(APITestCase):

    def test_get(self):
        url = reverse("book-list")
        book1 = Book.objects.create(name="The Collector 1", price=24)
        book2 = Book.objects.create(name="The Collector 2", price=25)
        response = self.client.get(url)

        serialized_data = BookSerializer([book1, book2], many=True).data

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(
            serialized_data, response.data
        )
