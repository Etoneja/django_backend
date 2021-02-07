from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Book(models.Model):

    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author_name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="my_books")
    readers = models.ManyToManyField(User, through="UserBookRelation", related_name="books")

    def __str__(self):
        return f"id: {self.id}, name: {self.name}"


class UserBookRelation(models.Model):

    RATE_CHOICES = (
        (1, "ok"),
        (2, "fine"),
        (3, "good"),
        (4, "amazing"),
        (5, "incredible")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    like = models.BooleanField(default=False)
    in_bookmarks = models.BooleanField(default=False)
    rate = models.PositiveIntegerField(choices=RATE_CHOICES, null=True)

    def __str__(self):
        return f"{self.user.username}: book - {self.book.name}, rating - {self.rate}"
