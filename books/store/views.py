from django.db.models import Count, Case, When, Avg
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from rest_framework.viewsets import ModelViewSet, GenericViewSet

# Create your views here.
from store.models import Book, UserBookRelation
from store.permissions import IsOwnerOrReadOnly
from store.serializers import BookSerializer, UserBookSerializer


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all().annotate(
        annotated_likes=Count(Case(When(userbookrelation__like=True, then=1))),
        annotated_rating=Avg("userbookrelation__rate")
    )
    serializer_class = BookSerializer
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    permission_classes = [IsOwnerOrReadOnly]
    filter_fields = ["price"]
    search_fields = ["name", "author_name"]
    ordering_fields = ["price", "author_name"]

    def perform_create(self, serializer):
        serializer.validated_data["owner"] = self.request.user
        serializer.save()


class UserBookRelationView(mixins.UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "book"

    def get_object(self):
        obj, _ = UserBookRelation.objects.get_or_create(
            user=self.request.user,
            book_id=self.kwargs["book"]  # from lookup_field
        )
        return obj


def auth(request):
    return render(request, "oauth.html")
