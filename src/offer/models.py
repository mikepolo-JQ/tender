from django.db import models
from django.conf import settings
from typing import Union
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL

"""
lmd_id : Unique ID of the offer maintained by LinkMyDeals
Status : In case of Incremental Feed, this will be new/updated/suspended
Title : Offer title
Description : Offer description stating all important Terms & Conditions
Type : Coupon Code or Deal
Coupon Code : Code to be applied to avail the offer. Empty in case of a deal
Offer : Type of offer, i.e. Percentage Off, Price Off, Cashback, BOGO, Sign-Up, etc
Offer Value : The exact percentage or price that is discounted on using the offer
Store : Name of the Online store
Categories : Comma separated list of all categories
URL : URL of the Landing page
Image : Image URL
Affiliate Link : Deeplink by your preferred Affiliate Network
Start Date : Date from which offer is applicable
End Date : Date when the offer expires
"""


class AbstractOfferProperty(models.Model):
    name = models.CharField(null=False, blank=False, unique=True, max_length=50)
    description = models.TextField(null=True, blank=True, default=None)

    class Meta:
        abstract = True


class Category(AbstractOfferProperty):
    pass


class Type(AbstractOfferProperty):
    pass


class Review(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, default=None
    )
    object_id = models.PositiveIntegerField(default=None)
    owner = GenericForeignKey()

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="my_reviews"
    )

    content = models.TextField(null=False, blank=False, default=None)
    rating_value = models.IntegerField(default=0)

    likers = models.ManyToManyField(User)

    def get_likes_count(self):
        return self.likes.count()


class AbstractClassModel(models.Model):
    rating = models.FloatField(default=0)
    reviews = GenericRelation(Review)

    class Meta:
        abstract = True


class Store(AbstractOfferProperty, AbstractClassModel):
    pass


class Offer(AbstractClassModel):
    categories = models.ManyToManyField(Category, related_name="offers")
    types = models.ManyToManyField(Type, related_name="offers")
    users = models.ManyToManyField(User, related_name="offers")
    is_active = models.BooleanField(default=True)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, related_name="offers", default=None
    )

    lmd_id = models.CharField(
        null=False, blank=False, unique=True, max_length=25, default=None
    )

    offer_text = models.TextField(null=True, blank=True, default=None)
    offer_value = models.CharField(null=False, blank=False, max_length=1000)
    description = models.TextField(null=True, blank=True)

    code = models.CharField(null=True, blank=True, max_length=100)

    title = models.TextField(null=False, blank=False)

    featured = models.BooleanField(null=False, blank=False)
    url = models.URLField(max_length=1000)
    smart_link = models.URLField(max_length=1000)
    image_url = models.URLField(max_length=1000)

    status = models.CharField(null=False, blank=False, max_length=25)

    start_date = models.DateField()
    end_date = models.DateField()
