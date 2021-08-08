from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions
from rest_framework.response import Response

from applications.offer.models import Offer, Store, Review
from applications.offer import serializers, tasks
from applications.offer.services import OfferFilter, IsOwnerOrReadOnly


class OfferListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    model = Offer
    queryset = Offer.objects.all()
    serializer_class = serializers.OfferListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = OfferFilter


class OfferDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    model = Offer
    queryset = Offer.objects.filter()
    serializer_class = serializers.OfferDetailSerializer


class OwnerReviewsListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    model = Review
    serializer_class = serializers.ReviewListSerializer

    def get_owner_class(self):
        class_name = self.request.path.split("/")[2]
        owner_class = {"offer": Offer, "store": Store}.get(class_name)

        if not owner_class:
            raise KeyError("Owner class for this review list isn't found.")

        return owner_class

    def get_queryset(self):
        owner_class = self.get_owner_class()

        pk = self.kwargs.get("pk")

        queryset = owner_class.objects.get(pk=pk).reviews.all()

        return queryset

    def perform_create(self, serializer):
        owner_class = self.get_owner_class()

        pk = self.kwargs.get("pk")
        owner = owner_class.objects.get(pk=pk)
        user = self.request.user

        serializer.save(author_id=user.pk, owner=owner)

        owner.update_rating()


# //////////////////////// STORE ///////////////////////////////
class StoreListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]

    model = Store
    queryset = Store.objects.all()
    serializer_class = serializers.StoreListSerializer
    # filter_backends = (DjangoFilterBackend,)
    # filterset_class = OfferFilter


class StoreDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    model = Store
    queryset = Store.objects.filter()
    serializer_class = serializers.StoreDetailSerializer


# //////////////////////// REVIEWS ///////////////////////////////
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    model = Review
    serializer_class = serializers.ReviewDetailSerializer
    queryset = Review.objects.filter()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        instance.owner.update_rating()
        super().perform_destroy(instance)

    def perform_update(self, serializer):
        super().perform_update(serializer)

        review = self.get_object()
        review.owner.update_rating()


class ReviewLikeView(generics.views.APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = self.request.user
        pk = kwargs["pk"]

        review = Review.objects.filter(pk=pk).first()

        if not review:
            raise ModuleNotFoundError(f"Review with pk={pk} is not found")

        if review.likers.filter(pk=user.pk).exists():
            review.likers.remove(user.pk)
        else:
            review.likers.add(user)
        return Response({"ok": True})


# //////////////////////// ADMIN ///////////////////////////////
class DataUpdateView(generics.views.APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        tasks.update_data_file.delay()
        return Response({"update": True})


class UploadToTheDBView(generics.views.APIView):

    permission_classes = [permissions.IsAdminUser]

    def get(self, request, *args, **kwargs):
        tasks.upload_data_from_file_to_the_db.delay()
        return Response({"upload": True})
