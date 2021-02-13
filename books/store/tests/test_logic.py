from unittest import mock

from django.contrib.auth.models import User
from django.db import connection
from django.test import TestCase, SimpleTestCase

from store.logic import set_rating
from store.models import Book, UserBookRelation
from django.test.utils import CaptureQueriesContext


class SetRatingTestCase(TestCase):

    def setUp(self):
        user1 = User.objects.create(username="test_username1")
        user2 = User.objects.create(username="test_username2")
        user3 = User.objects.create(username="test_username3")

        self.book1 = Book.objects.create(name="The Collector 1", price=24, owner=user1)
        self.book2 = Book.objects.create(name="The Collector 2", price=25)

        UserBookRelation.objects.create(user=user1, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user2, book=self.book1, like=True, rate=5)
        UserBookRelation.objects.create(user=user3, book=self.book1, like=True, rate=4)

        UserBookRelation.objects.create(user=user1, book=self.book2, like=True, rate=3)
        UserBookRelation.objects.create(user=user2, book=self.book2, like=True, rate=4)
        self.user_book3 = UserBookRelation.objects.create(user=user3, book=self.book2, like=False, rate=2)

    def test_set_rating(self):
        set_rating(self.book1)
        self.book1.refresh_from_db()
        self.assertEqual("4.67", str(self.book1.rating))

    @mock.patch('store.logic.set_rating')
    def test_not_save_book_on_same_rating(self, set_rating):
        self.user_book3.rate = 2
        self.user_book3.save()
        self.assertFalse(set_rating.called)

    @mock.patch('store.logic.set_rating')
    def test_save_book_on_different_rating(self, set_rating):
        self.user_book3.rate = 3
        self.user_book3.save()
        self.assertTrue(set_rating.called)
