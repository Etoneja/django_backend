from django.test import TestCase

from store.models import Book
from store.serializers import BookSerializer


class BookSerializerTestCase(TestCase):

    def test_ok(self):

        book1 = Book.objects.create(name="The Collector 1", price=24)
        book2 = Book.objects.create(name="The Collector 2", price=25)
        data = BookSerializer([book1, book2], many=True).data

        expected_data = [
            {
                "id": book1.id,
                "name": "The Collector 1",
                "price": "24.00"
            },
            {
                "id": book2.id,
                "name": "The Collector 2",
                "price": "25.00"
            },
        ]
        self.assertEqual(expected_data, data)
